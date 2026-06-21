import re
import random
from urllib.parse import urlparse
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.modules.analysis.models import (
    Response, Citation, CitationSource, Domain, 
    VisibilityScore, VisibilityHistory, ShareOfVoice, Topic, TopicCluster
)
from app.modules.prompts.models import PromptRun, Prompt
from app.modules.workspaces.models import Project, Brand, Competitor

_hdbscan = None

def get_hdbscan():
    global _hdbscan
    if _hdbscan is None:
        try:
            import hdbscan
            _hdbscan = hdbscan
        except Exception:
            _hdbscan = False
    return _hdbscan

kw_model = None
embedding_model = None

def get_kw_model():
    global kw_model
    if kw_model is None:
        try:
            from keybert import KeyBERT
            kw_model = KeyBERT('all-MiniLM-L6-v2')
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to lazy load KeyBERT model: {e}")
            kw_model = None
    return kw_model

def get_embedding_model():
    global embedding_model
    if embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to lazy load SentenceTransformer model: {e}")
            embedding_model = None
    return embedding_model


class AnalysisService:
    @staticmethod
    def extract_links_with_position(text: str) -> list[tuple[str, int]]:
        """Returns unique URLs and their relative character position (0 to 1)"""
        pattern = r'\[[^\]]+\]\((https?://[^\s\)]+)\)'
        matches = []
        seen = set()
        for match in re.finditer(pattern, text):
            url = match.group(1)
            if url not in seen:
                seen.add(url)
                position = match.start() / max(1, len(text))
                matches.append((url, position))
        return matches

    @staticmethod
    def get_base_domain(url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")

    @staticmethod
    def calculate_sentiment(text: str) -> float:
        pos_words = r'(best|great|recommend|fast|secure|love|excellent|superior|top|amazing)'
        neg_words = r'(bad|slow|error|expensive|flaw|avoid|terrible|worst|fail|issue)'
        pos = len(re.findall(pos_words, text, re.IGNORECASE))
        neg = len(re.findall(neg_words, text, re.IGNORECASE))
        if pos + neg == 0: return 0.0
        return (pos - neg) / (pos + neg)
        
    @staticmethod
    def get_model_weight(model_id: str) -> float:
        model_weights = {
            "chatgpt-4": 1.0,
            "gpt-4o": 1.0,
            "claude-3-opus": 0.9,
            "claude-3-haiku": 0.7,
            "gemini-pro": 0.8,
            "perplexity-sonar": 0.85
        }
        for k, v in model_weights.items():
            if k in model_id.lower():
                return v
        return 0.5 

    @staticmethod
    def get_mock_domain_authority(domain: str) -> int:
        if domain.endswith('.gov'): return 95
        if domain.endswith('.edu'): return 85
        if domain.endswith('.org'): return 70
        if domain.endswith('.io'): return 65
        return 50

    @staticmethod
    async def process_raw_response(
        db: AsyncSession, 
        prompt_run_id: str, 
        raw_text: str, 
        tokens: int, 
        latency: int,
        cost: float = 0.0,
        provider_requested: str = None,
        provider_used: str = None
    ) -> Response:
        sentiment = AnalysisService.calculate_sentiment(raw_text)
            
        res = Response(
            prompt_run_id=prompt_run_id,
            raw_text=raw_text,
            tokens_used=tokens,
            latency_ms=latency,
            sentiment_score=sentiment,
            cost_usd=cost,
            provider_requested=provider_requested,
            provider_used=provider_used
        )
        db.add(res)
        await db.flush()

        run_res = await db.execute(select(PromptRun).where(PromptRun.id == prompt_run_id))
        run = run_res.scalar_one()
        run.status = "COMPLETED"
        run.executed_at = datetime.utcnow()

        prompt_res = await db.execute(select(Prompt).where(Prompt.id == run.prompt_id))
        prompt = prompt_res.scalar_one()
        
        # Accumulate cost to Workspace
        from app.modules.workspaces.models import Workspace
        project_res = await db.execute(select(Project).where(Project.id == prompt.project_id))
        project_obj = project_res.scalar_one_or_none()
        if project_obj:
            ws_res = await db.execute(select(Workspace).where(Workspace.id == project_obj.workspace_id))
            workspace = ws_res.scalar_one_or_none()
            if workspace:
                if workspace.api_cost_used is None:
                    workspace.api_cost_used = 0.0
                workspace.api_cost_used = float(workspace.api_cost_used) + cost
        
        brand_res = await db.execute(select(Brand).where(Brand.project_id == prompt.project_id))
        brands = brand_res.scalars().all()

        links_with_pos = AnalysisService.extract_links_with_position(raw_text)
        for url, pos in links_with_pos:
            base_domain = AnalysisService.get_base_domain(url)
            
            dom_res = await db.execute(select(Domain).where(Domain.domain == base_domain))
            domain = dom_res.scalar_one_or_none()
            if not domain:
                domain = Domain(domain=base_domain, domain_authority=AnalysisService.get_mock_domain_authority(base_domain))
                db.add(domain)
                await db.flush()
                
            src_res = await db.execute(select(CitationSource).where(CitationSource.url == url))
            source = src_res.scalar_one_or_none()
            if not source:
                source = CitationSource(url=url, domain_id=domain.id)
                db.add(source)
                await db.flush()
                
            is_anchor = any(brand.name.lower() in raw_text.lower() for brand in brands)
            
            citation = Citation(
                response_id=res.id,
                source_id=source.id,
                is_anchor_citation=is_anchor,
                citation_text=raw_text[:200],
                position_index=int(pos * 100) 
            )
            db.add(citation)
            
        await db.flush()

        for brand in brands:
            await AnalysisService.update_visibility_metrics(db, brand, run.model_id)

        kw_m = get_kw_model()
        emb_m = get_embedding_model()
        if kw_m and emb_m:
            keywords = kw_m.extract_keywords(raw_text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=5)
            for kw, weight in keywords:
                emb = emb_m.encode(kw).tolist()
                topic = Topic(
                    name=kw,
                    embedding=emb
                )
                db.add(topic)
            await db.flush()

        return res

    @staticmethod
    async def update_visibility_metrics(db: AsyncSession, brand: Brand, model_id: str):
        prompts_res = await db.execute(select(Prompt).where(Prompt.project_id == brand.project_id))
        prompts = prompts_res.scalars().all()
        prompt_ids = [p.id for p in prompts]
        
        if not prompt_ids: return
            
        runs_res = await db.execute(
            select(PromptRun)
            .where(PromptRun.prompt_id.in_(prompt_ids))
            .where(PromptRun.model_id == model_id)
            .where(PromptRun.status == "COMPLETED")
        )
        runs = runs_res.scalars().all()
        run_ids = [r.id for r in runs]
        
        if not run_ids: return
            
        resp_res = await db.execute(select(Response).where(Response.prompt_run_id.in_(run_ids)))
        responses = resp_res.scalars().all()
        
        model_weight = AnalysisService.get_model_weight(model_id)
        
        total_score = 0.0
        for resp in responses:
            matches_name = brand.name.lower() in resp.raw_text.lower()
            matches_domain = brand.domain.lower() in resp.raw_text.lower()
            if matches_name or matches_domain:
                base_mention = 1.0
                
                idx_name = resp.raw_text.lower().find(brand.name.lower())
                idx_dom = resp.raw_text.lower().find(brand.domain.lower())
                
                valid_idxs = [i for i in [idx_name, idx_dom] if i >= 0]
                first_idx = min(valid_idxs) if valid_idxs else len(resp.raw_text)
                relative_pos = first_idx / max(1, len(resp.raw_text))
                
                position_weight = 1.0 + (1.0 - relative_pos)
                sentiment_weight = 1.0 + float(resp.sentiment_score)
                has_citation = 1.2 if matches_domain else 1.0
                
                resp_vis = base_mention * position_weight * sentiment_weight * has_citation * model_weight
                total_score += resp_vis
                
        max_possible_per_resp = 4.8
        score = (total_score / (len(responses) * max_possible_per_resp)) * 100.0 if responses else 0.0
        
        today = date.today()
        hist_res = await db.execute(
            select(VisibilityHistory)
            .where(VisibilityHistory.brand_id == brand.id)
            .where(VisibilityHistory.model_id == model_id)
            .where(VisibilityHistory.recorded_date == today)
        )
        hist = hist_res.scalar_one_or_none()
        if not hist:
            hist = VisibilityHistory(brand_id=brand.id, model_id=model_id, recorded_date=today)
            db.add(hist)
        hist.visibility_score = score
        
        avg_sentiment = sum(float(r.sentiment_score) for r in responses) / len(responses) if responses else 0.0
        hist.sentiment_score = avg_sentiment
        
        score_rec = VisibilityScore(brand_id=brand.id, visibility_score=score)
        db.add(score_rec)
        
        comp_res = await db.execute(select(Competitor).where(Competitor.brand_id == brand.id))
        competitors = comp_res.scalars().all()
        
        total_mentions = 0
        player_mentions = {brand.id: 0}
        
        for resp in responses:
            if brand.name.lower() in resp.raw_text.lower():
                player_mentions[brand.id] += 1
                total_mentions += 1
        
        for comp in competitors:
            comp_mentions = 0
            for resp in responses:
                if comp.name.lower() in resp.raw_text.lower() or comp.domain.lower() in resp.raw_text.lower():
                    comp_mentions += 1
            total_mentions += comp_mentions
            player_mentions[comp.id] = comp_mentions
            
        for player_id, p_mentions in player_mentions.items():
            sov_percentage = (p_mentions / total_mentions) * 100.0 if total_mentions > 0 else 0.0
            is_comp = player_id != brand.id
            
            sov_res = await db.execute(
                select(ShareOfVoice)
                .where(ShareOfVoice.project_id == brand.project_id)
                .where(ShareOfVoice.brand_id == (None if is_comp else brand.id))
                .where(ShareOfVoice.competitor_id == (player_id if is_comp else None))
                .where(ShareOfVoice.recorded_date == today)
            )
            sov = sov_res.scalar_one_or_none()
            if not sov:
                sov = ShareOfVoice(
                    project_id=brand.project_id,
                    brand_id=None if is_comp else brand.id,
                    competitor_id=player_id if is_comp else None,
                    recorded_date=today
                )
                db.add(sov)
            sov.share_percentage = sov_percentage
            
        await db.flush()

    @staticmethod
    async def get_visibility_overview(db: AsyncSession, project_id: str) -> dict:
        brand_res = await db.execute(select(Brand).where(Brand.project_id == project_id))
        brand = brand_res.scalar_one_or_none()
        if not brand: return {"visibility_score": 0.0, "weekly_change": 0.0, "history": [], "rankings": [], "share_of_voice": 0.0, "share_of_voice_breakdown": []}
            
        score_res = await db.execute(
            select(VisibilityScore)
            .where(VisibilityScore.brand_id == brand.id)
            .order_by(VisibilityScore.recorded_at.desc())
            .limit(1)
        )
        latest_rec = score_res.scalar_one_or_none()
        score = float(latest_rec.visibility_score) if latest_rec else 0.0

        last_week = date.today() - timedelta(days=7)
        old_score_res = await db.execute(
            select(VisibilityHistory)
            .where(VisibilityHistory.brand_id == brand.id)
            .where(VisibilityHistory.recorded_date <= last_week)
            .order_by(VisibilityHistory.recorded_date.desc())
            .limit(1)
        )
        old_rec = old_score_res.scalar_one_or_none()
        old_score = float(old_rec.visibility_score) if old_rec else 0.0
        weekly_change = score - old_score

        hist_res = await db.execute(
            select(VisibilityHistory.recorded_date, func.avg(VisibilityHistory.visibility_score))
            .where(VisibilityHistory.brand_id == brand.id)
            .group_by(VisibilityHistory.recorded_date)
            .order_by(VisibilityHistory.recorded_date.asc())
            .limit(30)
        )
        history = [{"date": str(row[0]), "score": float(row[1])} for row in hist_res.all()]

        competitors_res = await db.execute(select(Competitor).where(Competitor.brand_id == brand.id))
        competitors = competitors_res.scalars().all()
        
        # Get prompt runs and responses to calculate competitor visibility and SOV dynamically
        prompts_res = await db.execute(select(Prompt).where(Prompt.project_id == project_id))
        prompt_ids = [p.id for p in prompts_res.scalars().all()]
        responses = []
        runs = []
        if prompt_ids:
            runs_res = await db.execute(select(PromptRun).where(PromptRun.prompt_id.in_(prompt_ids)).where(PromptRun.status == "COMPLETED"))
            runs = runs_res.scalars().all()
            run_ids = [r.id for r in runs]
            if run_ids:
                resp_res = await db.execute(select(Response).where(Response.prompt_run_id.in_(run_ids)))
                responses = resp_res.scalars().all()

        rankings = [{"rank": 1, "brand": brand.name, "score": score, "change": weekly_change}]
        
        max_possible_per_resp = 4.8
        for idx, comp in enumerate(competitors, start=2):
            total_comp_score = 0.0
            for resp in responses:
                matches_name = comp.name.lower() in resp.raw_text.lower()
                matches_domain = comp.domain.lower() in resp.raw_text.lower()
                if matches_name or matches_domain:
                    base_mention = 1.0
                    idx_name = resp.raw_text.lower().find(comp.name.lower())
                    idx_dom = resp.raw_text.lower().find(comp.domain.lower())
                    valid_idxs = [i for i in [idx_name, idx_dom] if i >= 0]
                    first_idx = min(valid_idxs) if valid_idxs else len(resp.raw_text)
                    relative_pos = first_idx / max(1, len(resp.raw_text))
                    
                    position_weight = 1.0 + (1.0 - relative_pos)
                    sentiment_weight = 1.0 + float(resp.sentiment_score)
                    has_citation = 1.2 if matches_domain else 1.0
                    
                    # Estimate model weight
                    resp_run_id = resp.prompt_run_id
                    run_obj = next((r for r in runs if r.id == resp_run_id), None)
                    model_id = run_obj.model_id if run_obj else "gpt-4o"
                    model_weight = AnalysisService.get_model_weight(model_id)
                    
                    resp_vis = base_mention * position_weight * sentiment_weight * has_citation * model_weight
                    total_comp_score += resp_vis
                    
            comp_score = (total_comp_score / (len(responses) * max_possible_per_resp)) * 100.0 if responses else 0.0
            
            rankings.append({
                "rank": idx,
                "brand": comp.name,
                "score": comp_score,
                "change": 0.0
            })
            
        rankings = sorted(rankings, key=lambda x: x["score"], reverse=True)
        for idx, rank_item in enumerate(rankings, start=1):
            rank_item["rank"] = idx

        # Fetch Share of Voice from Database
        sov_res = await db.execute(
            select(ShareOfVoice)
            .where(ShareOfVoice.project_id == project_id)
            .order_by(ShareOfVoice.recorded_date.desc())
        )
        sov_records = sov_res.scalars().all()
        
        brand_sov = 0.0
        sov_breakdown = []
        latest_date = None
        
        if sov_records:
            latest_date = sov_records[0].recorded_date
            latest_records = [r for r in sov_records if r.recorded_date == latest_date]
            
            for r in latest_records:
                name = brand.name
                if r.competitor_id:
                    comp_obj = next((c for c in competitors if c.id == r.competitor_id), None)
                    name = comp_obj.name if comp_obj else "Unknown Competitor"
                else:
                    brand_sov = float(r.share_percentage)
                
                sov_breakdown.append({
                    "name": name,
                    "share": float(r.share_percentage)
                })
        else:
            # Dyn count SOV if no records
            total_mentions = 0
            brand_mentions = sum(1 for resp in responses if brand.name.lower() in resp.raw_text.lower())
            total_mentions += brand_mentions
            sov_breakdown.append({"name": brand.name, "share": 0.0}) # placeholder
            
            for comp in competitors:
                comp_mentions = sum(1 for resp in responses if comp.name.lower() in resp.raw_text.lower() or comp.domain.lower() in resp.raw_text.lower())
                total_mentions += comp_mentions
                sov_breakdown.append({"name": comp.name, "share": float(comp_mentions)})
                
            brand_sov = (brand_mentions / total_mentions) * 100.0 if total_mentions > 0 else 0.0
            sov_breakdown[0]["share"] = brand_sov
            for item in sov_breakdown[1:]:
                item["share"] = (item["share"] / total_mentions) * 100.0 if total_mentions > 0 else 0.0

        return {
            "visibility_score": score,
            "weekly_change": weekly_change,
            "history": history if history else [{"date": str(date.today()), "score": score}],
            "rankings": rankings,
            "share_of_voice": brand_sov,
            "share_of_voice_breakdown": sov_breakdown
        }

    @staticmethod
    async def get_citations(db: AsyncSession, project_id: str) -> list:
        brand_res = await db.execute(select(Brand).where(Brand.project_id == project_id))
        brand = brand_res.scalar_one_or_none()
        if not brand: return []
            
        prompts_res = await db.execute(select(Prompt).where(Prompt.project_id == project_id))
        prompt_ids = [p.id for p in prompts_res.scalars().all()]
        if not prompt_ids: return []
            
        runs_res = await db.execute(select(PromptRun).where(PromptRun.prompt_id.in_(prompt_ids)))
        runs = runs_res.scalars().all()
        run_ids = [r.id for r in runs]
        
        run_models = {r.id: r.model_id for r in runs}
        if not run_ids: return []
            
        resp_res = await db.execute(select(Response).where(Response.prompt_run_id.in_(run_ids)))
        responses = resp_res.scalars().all()
        resp_ids = [rp.id for rp in responses]
        
        resp_run_map = {rp.id: rp.prompt_run_id for rp in responses}
        if not resp_ids: return []
            
        citations_res = await db.execute(
            select(CitationSource.url, Domain.domain_authority, Citation.position_index, Citation.response_id)
            .join(CitationSource, Citation.source_id == CitationSource.id)
            .join(Domain, CitationSource.domain_id == Domain.id)
            .where(Citation.response_id.in_(resp_ids))
        )
        
        impacts = {}
        for row in citations_res.all():
            url = row.url
            da = row.domain_authority
            pos_index = row.position_index or 50 
            resp_id = row.response_id
            
            run_id = resp_run_map.get(resp_id)
            model_id = run_models.get(run_id, "chatgpt")
            
            model_weight = AnalysisService.get_model_weight(model_id)
            pos_weight = 1.0 + (1.0 - (pos_index / 100.0)) 
            
            impact_val = da * pos_weight * model_weight
            
            if url not in impacts:
                impacts[url] = {"count": 0, "impact": 0.0}
                
            impacts[url]["count"] += 1
            impacts[url]["impact"] += float(impact_val)
            
        results = []
        for url, data in impacts.items():
            results.append({
                "url": url,
                "mentions_count": data["count"],
                "visibility_gain": round(data["impact"] / max(1, data["count"]), 2), 
                "last_observed": datetime.utcnow(),
                "status": "Effective" if data["impact"] > 50 else "Validating"
            })
            
        results = sorted(results, key=lambda x: x["visibility_gain"], reverse=True)
        return results[:10]

    @staticmethod
    async def get_explorer_data(db: AsyncSession, keyword: str = "general") -> dict:
        topic_res = await db.execute(select(Topic).limit(100))
        topics = topic_res.scalars().all()
        
        if not topics:
            return {
                "total_volume": "0",
                "frequency_rank": "New",
                "platforms": {"SearchGPT": "0", "Other": "0"},
                "geos": {"US": "0", "Rest": "0"},
                "variations": [{"text": keyword, "weight": 1}],
                "graph_nodes": [{"id": keyword, "parent": "root"}]
            }
            
        emb_m = get_embedding_model()
        hdb = get_hdbscan()
        if emb_m and hdb:
            embeddings = [t.embedding for t in topics if t.embedding]
            if len(embeddings) > 5:
                clusterer = hdb.HDBSCAN(min_cluster_size=2)
                labels = clusterer.fit_predict(embeddings)
                
                # Map topics to labels
                clustered_topics = [t for t in topics if t.embedding]
                clusters_map = {}
                for idx, label in enumerate(labels):
                    if label != -1:
                        if label not in clusters_map:
                            clusters_map[label] = []
                        clusters_map[label].append(clustered_topics[idx])
                
                # Persist clusters
                for label, t_list in clusters_map.items():
                    cluster_name = f"Cluster {label + 1}: " + ", ".join([t.name for t in t_list[:2]])
                    db_cluster = TopicCluster(name=cluster_name, description=f"HDBSCAN generated cluster {label}")
                    db.add(db_cluster)
                    await db.flush()
                    
                    for t in t_list:
                        t.cluster_id = db_cluster.id
                await db.commit()
                
        topic_counts = {}
        for t in topics:
            topic_counts[t.name] = topic_counts.get(t.name, 0) + 1
            
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        
        variations = [{"text": k, "weight": v} for k,v in sorted_topics[:5]]
        
        graph_nodes = []
        seen_nodes = set()
        for t in topics:
            if t.cluster_id:
                cluster_res = await db.execute(select(TopicCluster).where(TopicCluster.id == t.cluster_id))
                cluster = cluster_res.scalar_one_or_none()
                if cluster:
                    graph_nodes.append({"id": t.name, "parent": cluster.name})
                    seen_nodes.add(t.name)
        
        # Fallback for unclustered topics
        for k, v in sorted_topics[:6]:
            if k not in seen_nodes:
                graph_nodes.append({"id": k, "parent": keyword})
            
        return {
            "total_volume": str(len(topics)),
            "frequency_rank": "Trending",
            "platforms": {"SearchGPT": str(len(topics)), "Other": "0"},
            "geos": {"US": str(len(topics)), "Rest": "0"},
            "variations": variations,
            "graph_nodes": graph_nodes
        }
 
    @staticmethod
    async def trigger_scheduled_runs(ctx=None):
        from app.core.database import AsyncSessionLocal
        from app.modules.prompts.models import Prompt, AIModel
        from app.modules.prompts.service import PromptService
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info("Starting daily scheduled scan from worker")
        
        async with AsyncSessionLocal() as db:
            prompts_res = await db.execute(select(Prompt))
            prompts = prompts_res.scalars().all()
            
            models_res = await db.execute(select(AIModel).where(AIModel.is_active == 1))
            models = [m.id for m in models_res.scalars().all()]
            
            if not models:
                models = ["gpt-4o", "claude-3-haiku", "gemini-pro"]
                
            project_prompts = {}
            for p in prompts:
                if p.project_id not in project_prompts:
                    project_prompts[p.project_id] = []
                project_prompts[p.project_id].append(p)
                
            for project_id in project_prompts.keys():
                try:
                    await PromptService.trigger_run(db, project_id, models)
                except Exception as exc:
                    logger.error(f"Failed scheduled run for project {project_id}: {exc}")
            await db.commit()
        logger.info("Daily scheduled scan completed")

    @staticmethod
    async def perform_heuristic_audit(db: AsyncSession, audit_id: str):
        """
        Runs an async crawler over the submitted URL, extracts structured elements,
        calculates scores out of 100, generates recommendations, and emails reports.
        """
        import httpx
        from html.parser import HTMLParser
        import json
        import logging
        from datetime import datetime
        from app.modules.analysis.models import PageAudit

        logger = logging.getLogger(__name__)
        logger.info(f"Starting heuristic audit for ID {audit_id}")

        # Fetch audit record
        audit_res = await db.execute(select(PageAudit).where(PageAudit.id == audit_id))
        audit = audit_res.scalar_one_or_none()
        if not audit:
            logger.error(f"PageAudit {audit_id} not found in database.")
            return

        audit.status = "RUNNING"
        await db.commit()

        # HTML Parser implementation
        class AuditHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_script = False
                self.json_ld_contents = []
                self.headings = []
                self.current_tag = ""
                self.text_content = []
                self.title = ""
                self.meta_description = ""

            def handle_starttag(self, tag, attrs):
                self.current_tag = tag
                if tag == "script":
                    attrs_dict = dict(attrs)
                    if attrs_dict.get("type") == "application/ld+json":
                        self.in_script = True
                elif tag in ["h1", "h2", "h3"]:
                    self.headings.append({"tag": tag, "text": ""})
                elif tag == "meta":
                    attrs_dict = dict(attrs)
                    if attrs_dict.get("name") == "description":
                        self.meta_description = attrs_dict.get("content", "")

            def handle_endtag(self, tag):
                if tag == "script":
                    self.in_script = False
                self.current_tag = ""

            def handle_data(self, data):
                if self.in_script:
                    self.json_ld_contents.append(data)
                elif self.current_tag in ["h1", "h2", "h3"] and self.headings:
                    self.headings[-1]["text"] += data
                elif self.current_tag == "title":
                    self.title += data
                
                if self.current_tag not in ["script", "style"]:
                    self.text_content.append(data)

        # 1. Fetch HTML content
        html_content = ""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                headers = {"User-Agent": "ProfoundAEOBot/1.0"}
                resp = await client.get(audit.url, headers=headers)
                resp.raise_for_status()
                html_content = resp.text
        except Exception as exc:
            logger.exception(f"Failed to crawl URL: {audit.url} (Audit ID: {audit.id}) due to exception: {exc}")
            audit.status = "FAILED"
            audit.error_message = str(exc)
            audit.completed_at = datetime.utcnow()
            await db.commit()
            return

        # 2. Parse HTML
        parser = AuditHTMLParser()
        try:
            parser.feed(html_content)
        except Exception as exc:
            logger.error(f"HTML parsing failed: {exc}")

        # 3. Calculate Scores
        # Schema Markup Heuristics (25 pts max)
        schema_score = 0
        has_json_ld = len(parser.json_ld_contents) > 0
        has_rich_schema = False
        
        for content in parser.json_ld_contents:
            try:
                schema_data = json.loads(content)
                schema_types = str(schema_data).lower()
                if any(t in schema_types for t in ["faqpage", "howto", "organization", "aggregaterating"]):
                    has_rich_schema = True
            except Exception:
                pass
                
        if has_rich_schema:
            schema_score = 25
        elif has_json_ld:
            schema_score = 15
        else:
            schema_score = 0

        # Heading and Content Structure Heuristics (25 pts max)
        structure_score = 0
        h1_count = sum(1 for h in parser.headings if h["tag"] == "h1")
        h2_count = sum(1 for h in parser.headings if h["tag"] == "h2")
        has_question_heading = any(
            h["text"].strip().endswith("?") or 
            any(w in h["text"].lower() for w in ["what", "how", "why", "compare", "best"]) 
            for h in parser.headings
        )
        
        if h1_count == 1:
            structure_score += 10
        if h2_count >= 1:
            structure_score += 5
        if has_question_heading:
            structure_score += 10
            
        structure_score = min(25, structure_score)

        # Keyword Stuffing Heuristics (25 pts max)
        stuffing_score = 25
        raw_text = " ".join(parser.text_content)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', raw_text.lower())
        stopwords = {
            "the", "and", "for", "with", "that", "this", "you", "your", "from", 
            "are", "was", "were", "has", "have", "had", "but", "not", "they"
        }
        filtered_words = [w for w in words if w not in stopwords]
        
        word_counts = {}
        for w in filtered_words:
            word_counts[w] = word_counts.get(w, 0) + 1
            
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        total_filtered_words = len(filtered_words)
        
        if total_filtered_words > 10:
            top_word_density = sorted_words[0][1] / total_filtered_words
            if top_word_density > 0.08: # Stuffing penalty
                stuffing_score = 5
            elif top_word_density > 0.05:
                stuffing_score = 15

        # Semantic Alignment Heuristics (25 pts max)
        semantic_score = 0
        if parser.title:
            semantic_score += 10
        if parser.meta_description:
            semantic_score += 10
        if len(parser.headings) > 2:
            semantic_score += 5
            
        semantic_score = min(25, semantic_score)

        # Totals
        overall_score = schema_score + structure_score + stuffing_score + semantic_score
        
        # Recommendations Generation
        recs = {}
        if schema_score < 25:
            recs["schema_markup"] = "Add JSON-LD structured schemas like FAQPage or HowTo to allow direct search engine extraction."
        else:
            recs["schema_markup"] = "Structured schema tags look solid."
            
        if structure_score < 25:
            recs["content_structure"] = "Ensure exactly one H1 exists and phrase sub-headings as customer questions (e.g. using 'how to' or 'best')."
        else:
            recs["content_structure"] = "Heading distributions and structure look solid."
            
        if stuffing_score < 25:
            recs["keyword_stuffing"] = "Reduce the density of top repeated terms. Maintain a natural phrasing balance (below 5% frequency density)."
        else:
            recs["keyword_stuffing"] = "Keyword distribution checks passed."
            
        if semantic_score < 25:
            recs["semantic_alignment"] = "Add a comprehensive page title and meta description utilizing relevant category search keywords."
        else:
            recs["semantic_alignment"] = "Semantic alignment indicators look solid."

        # Save results
        audit.overall_score = overall_score
        audit.schema_markup_score = schema_score
        audit.content_structure_score = structure_score
        audit.keyword_stuffing_score = stuffing_score
        audit.semantic_alignment_score = semantic_score
        audit.recommendations = recs
        audit.status = "COMPLETED"
        audit.completed_at = datetime.utcnow()
        await db.commit()

        # Send audit email report
        try:
            await AnalysisService.send_audit_email(audit, recs)
        except Exception as e:
            logger.error(f"Failed to send audit email for run {audit_id}: {e}")

    @staticmethod
    async def send_audit_email(audit, recs: dict):
        """
        Renders a premium visual HTML table email.
        If RESEND_API_KEY environment variable is configured, dispatches email;
        else fallbacks to writing the HTML payload locally under docs/implementation/logs/emails/.
        """
        import os
        import logging

        logger = logging.getLogger(__name__)

        # Premium Dark-theme HSL color styling
        email_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    background-color: #0a0a0a;
                    color: #ffffff;
                    font-family: 'Inter', Arial, sans-serif;
                    padding: 40px;
                }}
                .card {{
                    background: rgba(24, 24, 27, 0.85);
                    border: 1px solid #27272a;
                    border-radius: 12px;
                    padding: 30px;
                    max-width: 600px;
                    margin: 0 auto;
                    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 1px solid #27272a;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .score {{
                    font-size: 48px;
                    font-weight: bold;
                    color: #10b981;
                    margin: 10px 0;
                }}
                .rating {{
                    font-size: 14px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    color: #a1a1aa;
                }}
                .metrics {{
                    margin: 25px 0;
                }}
                .metric-row {{
                    display: flex;
                    justify-content: space-between;
                    margin: 12px 0;
                    font-size: 14px;
                }}
                .progress-bar {{
                    background: #27272a;
                    border-radius: 4px;
                    height: 8px;
                    width: 100px;
                    overflow: hidden;
                    margin-left: 10px;
                }}
                .progress-fill {{
                    background: #10b981;
                    height: 100%;
                }}
                .recs {{
                    border-top: 1px solid #27272a;
                    padding-top: 20px;
                    margin-top: 30px;
                }}
                .rec-item {{
                    font-size: 14px;
                    color: #d4d4d8;
                    margin: 10px 0;
                    line-height: 1.5;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="header">
                    <div class="rating">GEO Readiness Audit Report</div>
                    <div class="score">{audit.overall_score}/100</div>
                    <div style="font-size: 13px; color: #a1a1aa; margin-top: 8px;">Target URL: {audit.url}</div>
                </div>
                
                <div class="metrics">
                    <div class="metric-row">
                        <span>Semantic Alignment</span>
                        <div style="display: flex; align-items: center;">
                            <span>{audit.semantic_alignment_score}/25</span>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {int(audit.semantic_alignment_score / 25 * 100)}%;"></div>
                            </div>
                        </div>
                    </div>
                    <div class="metric-row">
                        <span>Schema Markup</span>
                        <div style="display: flex; align-items: center;">
                            <span>{audit.schema_markup_score}/25</span>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {int(audit.schema_markup_score / 25 * 100)}%;"></div>
                            </div>
                        </div>
                    </div>
                    <div class="metric-row">
                        <span>Content Structure</span>
                        <div style="display: flex; align-items: center;">
                            <span>{audit.content_structure_score}/25</span>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {int(audit.content_structure_score / 25 * 100)}%;"></div>
                            </div>
                        </div>
                    </div>
                    <div class="metric-row">
                        <span>Keyword Stuffing Check</span>
                        <div style="display: flex; align-items: center;">
                            <span>{audit.keyword_stuffing_score}/25</span>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {int(audit.keyword_stuffing_score / 25 * 100)}%;"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="recs">
                    <h3 style="font-size: 16px; margin-bottom: 15px;">Prioritized Recommendations</h3>
                    <div class="rec-item"><strong>Semantic:</strong> {recs.get("semantic_alignment")}</div>
                    <div class="rec-item"><strong>Schema:</strong> {recs.get("schema_markup")}</div>
                    <div class="rec-item"><strong>Structure:</strong> {recs.get("content_structure")}</div>
                    <div class="rec-item"><strong>Stuffing:</strong> {recs.get("keyword_stuffing")}</div>
                </div>
            </div>
        </body>
        </html>
        """

        resend_key = os.environ.get("RESEND_API_KEY")
        if resend_key:
            import httpx
            logger.info("Sending audit report via Resend API")
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        "https://api.resend.com/emails",
                        headers={
                            "Authorization": f"Bearer {resend_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "from": "audit@tryprofound.com",
                            "to": audit.email,
                            "subject": f"GEO Readiness Audit Report: {audit.overall_score}/100",
                            "html": email_html
                        }
                    )
            except Exception as e:
                logger.error(f"Resend dispatch failed: {e}. Falling back to file.")
        
        # Always write to file in dev for validation auditing
        # Resolve log_dir relative to the repository root
        current_dir = os.path.abspath(__file__)
        for _ in range(5):
            current_dir = os.path.dirname(current_dir)
        log_dir = os.path.join(current_dir, "docs", "implementation", "logs", "emails")
        os.makedirs(log_dir, exist_ok=True)
        file_path = os.path.join(log_dir, f"audit_{audit.id}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(email_html)
        logger.info(f"Local audit email log written to: {file_path}")


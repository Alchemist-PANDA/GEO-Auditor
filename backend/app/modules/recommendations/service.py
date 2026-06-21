"""
Hybrid Recommendation Engine for GEO Platform.
Default: Rule-based engine (zero cost, runs locally).
On-demand: LLM-powered strategic recommendations (costs API credits).
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.modules.recommendations.models import Recommendation, RecommendationAction
from app.modules.workspaces.models import Brand, Competitor
from app.modules.analysis.models import (
    Citation, CitationSource, Domain, Response, Topic,
    VisibilityScore, VisibilityHistory
)
from app.modules.prompts.models import Prompt, PromptRun
import logging

logger = logging.getLogger(__name__)


class RecommendationService:

    # ──────────────────────────────────────────
    # Rule-Based Engine (default, $0 cost)
    # ──────────────────────────────────────────

    @staticmethod
    async def generate_recommendations(db: AsyncSession, project_id: str) -> list[Recommendation]:
        """
        Generate recommendations using local rule engine.
        Rules:
        1. Brand mention rate analysis
        2. Competitor gap analysis
        3. Citation gap analysis
        4. Topic gap analysis
        5. Technical GEO best practices
        """
        brand_res = await db.execute(select(Brand).where(Brand.project_id == project_id))
        brand = brand_res.scalar_one_or_none()
        if not brand:
            return []

        recs = []

        # Gather data for analysis
        responses, competitors = await RecommendationService._gather_project_data(db, project_id, brand)

        # Rule 1: Brand Mention Rate Analysis
        brand_recs = await RecommendationService._analyze_brand_mentions(db, project_id, brand, responses)
        recs.extend(brand_recs)

        # Rule 2: Competitor Gap Analysis
        comp_recs = await RecommendationService._analyze_competitor_gaps(db, project_id, brand, competitors, responses)
        recs.extend(comp_recs)

        # Rule 3: Citation Gap Analysis
        cite_recs = await RecommendationService._analyze_citation_gaps(db, project_id, brand, competitors, responses)
        recs.extend(cite_recs)

        # Rule 4: Topic Gap Analysis
        topic_recs = await RecommendationService._analyze_topic_gaps(db, project_id, brand, responses)
        recs.extend(topic_recs)

        # Rule 5: Technical GEO
        tech_recs = await RecommendationService._generate_technical_recs(db, project_id)
        recs.extend(tech_recs)

        await db.flush()
        return recs

    @staticmethod
    async def _gather_project_data(db: AsyncSession, project_id: str, brand: Brand):
        """Fetch all responses and competitors for analysis."""
        prompts_res = await db.execute(select(Prompt).where(Prompt.project_id == project_id))
        prompt_ids = [p.id for p in prompts_res.scalars().all()]

        responses = []
        if prompt_ids:
            runs_res = await db.execute(
                select(PromptRun)
                .where(PromptRun.prompt_id.in_(prompt_ids))
                .where(PromptRun.status == "COMPLETED")
            )
            run_ids = [r.id for r in runs_res.scalars().all()]
            if run_ids:
                resp_res = await db.execute(select(Response).where(Response.prompt_run_id.in_(run_ids)))
                responses = resp_res.scalars().all()

        comp_res = await db.execute(select(Competitor).where(Competitor.brand_id == brand.id))
        competitors = comp_res.scalars().all()

        return responses, competitors

    @staticmethod
    async def _analyze_brand_mentions(db: AsyncSession, project_id: str, brand: Brand, responses: list) -> list:
        """Rule 1: If brand mention rate < 30%, recommend improvement."""
        if not responses:
            rec = Recommendation(
                project_id=project_id,
                title="Start Monitoring Brand Visibility",
                description=f"No responses have been collected yet for {brand.name}. Run prompts across AI models to begin tracking your brand's visibility in AI-generated content.",
                priority="HIGH",
                status="active",
                estimated_visibility_gain=0.00
            )
            db.add(rec)
            await db.flush()
            act = RecommendationAction(
                recommendation_id=rec.id,
                action_text="Navigate to Prompts page and add at least 5 industry-relevant prompts."
            )
            db.add(act)
            return [rec]

        mentions = sum(1 for r in responses if brand.name.lower() in r.raw_text.lower())
        mention_rate = (mentions / len(responses)) * 100.0

        recs = []
        if mention_rate < 30.0:
            rec = Recommendation(
                project_id=project_id,
                title=f"Improve Brand Mention Rate (currently {mention_rate:.0f}%)",
                description=(
                    f"{brand.name} is mentioned in only {mention_rate:.0f}% of AI responses. "
                    f"Target: >50%. Create authoritative content that AI models can reference "
                    f"when answering queries about your industry."
                ),
                priority="CRITICAL" if mention_rate < 15 else "HIGH",
                status="active",
                estimated_visibility_gain=round((50 - mention_rate) * 0.05, 2)
            )
            db.add(rec)
            await db.flush()

            actions = [
                RecommendationAction(
                    recommendation_id=rec.id,
                    action_text="Publish authoritative FAQ content on your website covering top industry queries."
                ),
                RecommendationAction(
                    recommendation_id=rec.id,
                    action_text="Create detailed comparison guides positioning your brand against alternatives."
                ),
                RecommendationAction(
                    recommendation_id=rec.id,
                    action_text="Build backlinks from high-authority domains (.edu, .gov, .org) to boost AI training signal."
                ),
            ]
            db.add_all(actions)
            recs.append(rec)

        return recs

    @staticmethod
    async def _analyze_competitor_gaps(db, project_id, brand, competitors, responses) -> list:
        """Rule 2: For each competitor mentioned MORE than brand, generate gap recommendation."""
        if not responses or not competitors:
            return []

        brand_mentions = sum(1 for r in responses if brand.name.lower() in r.raw_text.lower())
        recs = []

        for comp in competitors:
            comp_mentions = sum(
                1 for r in responses
                if comp.name.lower() in r.raw_text.lower() or comp.domain.lower() in r.raw_text.lower()
            )

            if comp_mentions > brand_mentions:
                gap = comp_mentions - brand_mentions
                rec = Recommendation(
                    project_id=project_id,
                    title=f"Close visibility gap with {comp.name} ({gap} more mentions)",
                    description=(
                        f"{comp.name} appears in {comp_mentions} AI responses vs {brand.name}'s {brand_mentions}. "
                        f"Create targeted content that positions {brand.name} as a direct alternative."
                    ),
                    priority="HIGH",
                    status="active",
                    estimated_visibility_gain=round(gap * 0.15, 2)
                )
                db.add(rec)
                await db.flush()

                actions = [
                    RecommendationAction(
                        recommendation_id=rec.id,
                        action_text=f"Draft comparison article: '{brand.name} vs {comp.name}' highlighting key differentiators."
                    ),
                    RecommendationAction(
                        recommendation_id=rec.id,
                        action_text=f"Create FAQ content targeting '{comp.name} alternatives' queries."
                    ),
                    RecommendationAction(
                        recommendation_id=rec.id,
                        action_text=f"Seek reviews and mentions on platforms where {comp.name} is already cited."
                    ),
                ]
                db.add_all(actions)
                recs.append(rec)

        return recs

    @staticmethod
    async def _analyze_citation_gaps(db, project_id, brand, competitors, responses) -> list:
        """Rule 3: Find domains citing competitors but not the brand."""
        if not responses:
            return []

        resp_ids = [r.id for r in responses]
        citations_res = await db.execute(
            select(CitationSource.url, Domain.domain)
            .join(Citation, Citation.source_id == CitationSource.id)
            .join(Domain, CitationSource.domain_id == Domain.id)
            .where(Citation.response_id.in_(resp_ids))
        )
        all_citations = citations_res.all()

        # Find domains that appear in citations but don't link to brand domain
        cited_domains = set()
        brand_cited_domains = set()
        for row in all_citations:
            cited_domains.add(row.domain)
            if brand.domain.lower() in row.url.lower():
                brand_cited_domains.add(row.domain)

        gap_domains = cited_domains - brand_cited_domains
        recs = []

        if gap_domains:
            top_gaps = list(gap_domains)[:5]
            rec = Recommendation(
                project_id=project_id,
                title=f"Get cited on {len(gap_domains)} new domains",
                description=(
                    f"These domains cite your competitors but not {brand.name}: "
                    f"{', '.join(top_gaps)}. Getting listed on these platforms can significantly "
                    f"boost your visibility in AI-generated responses."
                ),
                priority="HIGH",
                status="active",
                estimated_visibility_gain=round(len(gap_domains) * 0.1, 2)
            )
            db.add(rec)
            await db.flush()

            for domain in top_gaps:
                act = RecommendationAction(
                    recommendation_id=rec.id,
                    action_text=f"Submit {brand.name} for listing/review on {domain}."
                )
                db.add(act)
            recs.append(rec)

        return recs

    @staticmethod
    async def _analyze_topic_gaps(db, project_id, brand, responses) -> list:
        """Rule 4: Find trending topics where brand has zero mentions."""
        topic_res = await db.execute(
            select(Topic.name, func.count(Topic.id).label("cnt"))
            .group_by(Topic.name)
            .order_by(func.count(Topic.id).desc())
            .limit(10)
        )
        trending_topics = topic_res.all()

        if not trending_topics or not responses:
            return []

        brand_lower = brand.name.lower()
        recs = []

        missing_topics = []
        for topic_name, count in trending_topics:
            # Check if brand appears in responses containing this topic
            topic_brand_found = False
            for r in responses:
                if topic_name.lower() in r.raw_text.lower() and brand_lower in r.raw_text.lower():
                    topic_brand_found = True
                    break
            if not topic_brand_found:
                missing_topics.append(topic_name)

        if missing_topics:
            rec = Recommendation(
                project_id=project_id,
                title=f"Create content for {len(missing_topics)} trending topics",
                description=(
                    f"{brand.name} is absent from AI responses about these trending topics: "
                    f"{', '.join(missing_topics[:5])}. Creating authoritative content on these subjects "
                    f"can capture new visibility."
                ),
                priority="MEDIUM",
                status="active",
                estimated_visibility_gain=round(len(missing_topics) * 0.08, 2)
            )
            db.add(rec)
            await db.flush()

            for topic in missing_topics[:5]:
                act = RecommendationAction(
                    recommendation_id=rec.id,
                    action_text=f"Write an authoritative guide covering '{topic}' with {brand.name} positioning."
                )
                db.add(act)
            recs.append(rec)

        return recs

    @staticmethod
    async def _generate_technical_recs(db, project_id) -> list:
        """Rule 5: Always-applicable technical GEO best practices."""
        recs = []

        # robots.txt
        rec1 = Recommendation(
            project_id=project_id,
            title="Optimize robots.txt for AI Search Crawlers",
            description=(
                "Ensure AI scrapers (GPTBot, ClaudeBot, Google-Extended, PerplexityBot) "
                "can access your product pages and knowledge base. Blocked crawlers = zero visibility."
            ),
            priority="CRITICAL",
            status="active",
            estimated_visibility_gain=1.50
        )
        db.add(rec1)
        await db.flush()
        db.add_all([
            RecommendationAction(
                recommendation_id=rec1.id,
                action_text="Verify robots.txt allows GPTBot, ClaudeBot, Google-Extended, PerplexityBot."
            ),
            RecommendationAction(
                recommendation_id=rec1.id,
                action_text="Test crawler access using each bot's user-agent string."
            ),
        ])
        recs.append(rec1)

        # Schema markup
        rec2 = Recommendation(
            project_id=project_id,
            title="Add Structured Data for AI Parsing",
            description=(
                "Implement FAQ, HowTo, and Product schema markup on key pages. "
                "Structured data helps AI models extract accurate information about your brand."
            ),
            priority="HIGH",
            status="active",
            estimated_visibility_gain=0.80
        )
        db.add(rec2)
        await db.flush()
        db.add_all([
            RecommendationAction(
                recommendation_id=rec2.id,
                action_text="Add FAQ schema to top 10 landing pages."
            ),
            RecommendationAction(
                recommendation_id=rec2.id,
                action_text="Implement Product schema on all product/service pages."
            ),
            RecommendationAction(
                recommendation_id=rec2.id,
                action_text="Add HowTo schema to tutorial and guide content."
            ),
        ])
        recs.append(rec2)

        return recs

    # ──────────────────────────────────────────
    # LLM-Powered Engine (on-demand, costs $)
    # ──────────────────────────────────────────

    @staticmethod
    async def generate_advanced_recommendations(db: AsyncSession, project_id: str) -> list[Recommendation]:
        """
        Generate strategic GEO recommendations using LLM reasoning.
        Only called on-demand when user requests advanced analysis.
        """
        from app.core.llm import call_llm_for_recommendations

        brand_res = await db.execute(select(Brand).where(Brand.project_id == project_id))
        brand = brand_res.scalar_one_or_none()
        if not brand:
            return []

        responses, competitors = await RecommendationService._gather_project_data(db, project_id, brand)

        # Build context for LLM
        brand_mentions = sum(1 for r in responses if brand.name.lower() in r.raw_text.lower()) if responses else 0
        total_responses = len(responses)

        comp_data = []
        for comp in competitors:
            c_mentions = sum(
                1 for r in responses
                if comp.name.lower() in r.raw_text.lower()
            ) if responses else 0
            comp_data.append(f"- {comp.name} ({comp.domain}): {c_mentions}/{total_responses} mentions")

        context = (
            f"Brand: {brand.name} ({brand.domain})\n"
            f"Brand Mention Rate: {brand_mentions}/{total_responses} responses\n"
            f"Competitors:\n" + "\n".join(comp_data) + "\n\n"
            f"Generate 3-5 specific, actionable GEO optimization recommendations."
        )

        llm_output = await call_llm_for_recommendations(context)

        recs = []
        for line in llm_output.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("|")
            if len(parts) >= 3:
                title = parts[0].strip()
                description = parts[1].strip()
                priority = parts[2].strip().upper()
                if priority not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
                    priority = "MEDIUM"

                rec = Recommendation(
                    project_id=project_id,
                    title=title[:200],
                    description=description[:500],
                    priority=priority,
                    status="active",
                    estimated_visibility_gain=0.50
                )
                db.add(rec)
                await db.flush()

                # Parse actions if provided
                if len(parts) >= 4:
                    action_texts = [a.strip() for a in parts[3].split(";") if a.strip()]
                    for a_text in action_texts:
                        act = RecommendationAction(
                            recommendation_id=rec.id,
                            action_text=a_text[:300]
                        )
                        db.add(act)

                recs.append(rec)

        await db.flush()
        return recs

    # ──────────────────────────────────────────
    # Query Methods
    # ──────────────────────────────────────────

    @staticmethod
    async def get_recommendations_by_project(db: AsyncSession, project_id: str) -> list[Recommendation]:
        from sqlalchemy.orm import selectinload
        res = await db.execute(
            select(Recommendation)
            .where(Recommendation.project_id == project_id)
            .options(selectinload(Recommendation.actions))
            .order_by(Recommendation.created_at.desc())
        )
        recommendations = res.scalars().all()
        if not recommendations:
            await RecommendationService.generate_recommendations(db, project_id)
            res = await db.execute(
                select(Recommendation)
                .where(Recommendation.project_id == project_id)
                .options(selectinload(Recommendation.actions))
                .order_by(Recommendation.created_at.desc())
            )
            recommendations = res.scalars().all()
        return recommendations

    @staticmethod
    async def update_recommendation_status(db: AsyncSession, rec_id: str, new_status: str) -> Recommendation:
        res = await db.execute(select(Recommendation).where(Recommendation.id == rec_id))
        rec = res.scalar_one_or_none()
        if rec:
            rec.status = new_status
            await db.flush()
        return rec

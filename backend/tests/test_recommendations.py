"""
Unit tests for the hybrid recommendation engine.
Mocks the AsyncSession database calls to verify rule engine outputs.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.modules.recommendations.service import RecommendationService
from app.modules.workspaces.models import Brand, Competitor
from app.modules.recommendations.models import Recommendation, RecommendationAction
from app.modules.prompts.models import Prompt, PromptRun
from app.modules.analysis.models import Response, Topic
from app.modules.agency.models import Client, Report

@pytest.mark.asyncio
async def test_generate_recommendations_rules():
    # Setup mock session
    db = AsyncMock()
    db.add = MagicMock()
    db.add_all = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    # Create dummy data structures
    brand = Brand(id="brand-1", name="Rho", domain="rho.co")
    prompts = [Prompt(id="prompt-1", project_id="proj-1")]
    runs = [
        PromptRun(id="run-1", prompt_id="prompt-1", status="COMPLETED"),
        PromptRun(id="run-2", prompt_id="prompt-1", status="COMPLETED")
    ]
    responses = [
        Response(
            id="resp-1", 
            prompt_run_id="run-1", 
            raw_text="Rho is a decent option, but Brex is the absolute best credit card for startups."
        ),
        Response(
            id="resp-2", 
            prompt_run_id="run-2", 
            raw_text="Brex offers high limits and fast cashback features."
        )
    ]
    competitors = [Competitor(id="comp-1", name="Brex", domain="brex.com", brand_id="brand-1")]
    
    # Mocking different queries by inspection of query string or simple order
    # Queries in order of execution:
    # 1. select(Brand)
    # 2. select(Prompt)
    # 3. select(PromptRun)
    # 4. select(Response)
    # 5. select(Competitor)
    # 6. select(CitationSource.url, Domain.domain)
    # 7. select(Topic.name, func.count(Topic.id))
    
    mock_brand_res = MagicMock()
    mock_brand_res.scalar_one_or_none.return_value = brand

    mock_prompts_res = MagicMock()
    mock_prompts_res.scalars().all.return_value = prompts

    mock_runs_res = MagicMock()
    mock_runs_res.scalars().all.return_value = runs

    mock_resp_res = MagicMock()
    mock_resp_res.scalars().all.return_value = responses

    mock_comp_res = MagicMock()
    mock_comp_res.scalars().all.return_value = competitors

    from collections import namedtuple
    CitationRow = namedtuple("CitationRow", ["url", "domain"])

    mock_citations_res = MagicMock()
    mock_citations_res.all.return_value = [
        CitationRow("https://brex.com/blog/comparison", "brex.com")
    ]

    mock_topics_res = MagicMock()
    mock_topics_res.all.return_value = [
        ("credit cards", 5)
    ]

    # Assign side effects for db.execute calls
    db.execute.side_effect = [
        mock_brand_res,      # select(Brand)
        mock_prompts_res,    # select(Prompt)
        mock_runs_res,       # select(PromptRun)
        mock_resp_res,       # select(Response)
        mock_comp_res,       # select(Competitor)
        mock_citations_res,  # select(CitationSource...)
        mock_topics_res,     # select(Topic...)
    ]

    # Generate recommendations
    recs = await RecommendationService.generate_recommendations(db, "proj-1")

    # Verify recommendations generated
    assert len(recs) > 0

    # 1. Technical GEO recommendations should always be generated
    tech_recs = [r for r in recs if "robots.txt" in r.title or "Structured Data" in r.title]
    assert len(tech_recs) == 2

    # 2. Competitor gap recommendation should exist for Brex (mentioned, and brand mentions < competitor mentions)
    comp_recs = [r for r in recs if "Brex" in r.title]
    assert len(comp_recs) == 1
    assert comp_recs[0].priority == "HIGH"

    # 3. Citation gap recommendation should exist (domain brex.com cited, but not rho.co)
    cite_recs = [r for r in recs if "Get cited on" in r.title]
    assert len(cite_recs) == 1
    assert cite_recs[0].priority == "HIGH"

    # 4. Topic gap recommendation should exist ("credit cards" is trending, but brand Rho not mentioned in that topic context)
    topic_recs = [r for r in recs if "trending topics" in r.title]
    assert len(topic_recs) == 1
    assert topic_recs[0].priority == "MEDIUM"

    # 5. Brand mention rate is 100% (since "Rho" is in response raw_text), so NO brand mention rate recommendation
    brand_recs = [r for r in recs if "Brand Mention Rate" in r.title]
    assert len(brand_recs) == 0

    # Verify db.add / db.add_all were called to persist objects
    assert db.add.call_count > 0
    assert db.add_all.call_count > 0

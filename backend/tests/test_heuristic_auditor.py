import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.modules.analysis.service import AnalysisService
from app.modules.analysis.models import (
    Response, Citation, CitationSource, Domain, 
    VisibilityScore, VisibilityHistory, ShareOfVoice, Topic, TopicCluster, PageAudit
)
from app.modules.prompts.models import Prompt, PromptRun, AIModel
from app.modules.workspaces.models import Organization, Workspace, Project, Brand, Competitor, User
from app.modules.agency.models import Agency, Client, Report, Notification, AuditLog
from app.modules.recommendations.models import Recommendation, RecommendationAction


@pytest.mark.asyncio
@patch("httpx.AsyncClient")
async def test_perform_heuristic_audit_success(mock_client_class):
    # Setup mock httpx client response
    mock_client = AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.text = """
    <html>
      <head>
        <title>Best Startup Accounting Software - Rho Review</title>
        <meta name="description" content="Read our review of Rho, the best startup credit card and business banking solution.">
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "FAQPage",
          "mainEntity": []
        }
        </script>
      </head>
      <body>
        <h1>Best Startup Accounting Software</h1>
        <h2>How to choose startup accounting?</h2>
        <p>Rho is a great platform for startup accounting. We recommend it. It's secure and fast.</p>
        <h2>What are the alternatives?</h2>
        <p>There are some alternatives but Rho is top tier.</p>
        <p>This article provides an in-depth review of financial platforms. We evaluate transaction fees, credit quality, customer service responsiveness, rewards program flexibility, ease of onboarding, dashboard interface speed, multi-entity support capabilities, and corporate credit limit underwriting logic. Our team spent over fifty hours testing various cash management accounts, checking balances, exporting CSV files, generating monthly statements, analyzing merchant category code multipliers, and comparing yield percentages on idle company cash deposits. In addition to our financial research, we also enjoy gardening, cooking delicious meals, hiking in the mountains, reading classic literature, playing acoustic guitar, learning new foreign languages, painting watercolor landscapes, and exploring local history museums.</p>
      </body>
    </html>
    """
    mock_client.get.return_value = mock_response

    # Setup mock DB session
    db = AsyncMock()
    audit_record = PageAudit(
        id="audit-uuid-1",
        url="https://rho.co/blog/accounting",
        email="test@example.com",
        status="PENDING"
    )
    
    mock_execute_res = MagicMock()
    mock_execute_res.scalar_one_or_none.return_value = audit_record
    db.execute.return_value = mock_execute_res

    # Run the audit
    with patch("app.modules.analysis.service.AnalysisService.send_audit_email", new_callable=AsyncMock) as mock_send_email:
        await AnalysisService.perform_heuristic_audit(db, "audit-uuid-1")
        
        # Assertions
        assert audit_record.status == "COMPLETED"
        assert audit_record.overall_score > 70
        assert audit_record.schema_markup_score == 25  # FAQPage schema
        assert audit_record.content_structure_score == 25  # H1 + H2 + Question
        assert audit_record.semantic_alignment_score == 25  # Title + Description + Headings
        assert audit_record.keyword_stuffing_score == 25  # Healthy density
        
        db.commit.assert_called()
        mock_send_email.assert_called_once_with(audit_record, audit_record.recommendations)

@pytest.mark.asyncio
@patch("httpx.AsyncClient")
async def test_perform_heuristic_audit_stuffing_penalty(mock_client_class):
    # Setup mock httpx client response with stuffed keywords
    mock_client = AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_client
    
    mock_response = MagicMock()
    # Repeating "accounting" multiple times in the text to trigger stuffing penalty
    mock_response.text = """
    <html>
      <head>
        <title>Accounting</title>
      </head>
      <body>
        <h1>Accounting</h1>
        <p>accounting accounting accounting accounting accounting accounting accounting accounting accounting accounting</p>
      </body>
    </html>
    """
    mock_client.get.return_value = mock_response

    # Setup mock DB session
    db = AsyncMock()
    audit_record = PageAudit(
        id="audit-uuid-2",
        url="https://rho.co/blog/stuffing",
        email="test@example.com",
        status="PENDING"
    )
    
    mock_execute_res = MagicMock()
    mock_execute_res.scalar_one_or_none.return_value = audit_record
    db.execute.return_value = mock_execute_res

    # Run the audit
    with patch("app.modules.analysis.service.AnalysisService.send_audit_email", new_callable=AsyncMock) as mock_send_email:
        await AnalysisService.perform_heuristic_audit(db, "audit-uuid-2")
        
        # Assertions
        assert audit_record.status == "COMPLETED"
        assert audit_record.keyword_stuffing_score <= 15  # Stuffing penalty should trigger
        assert "Reduce the density of top repeated terms" in audit_record.recommendations["keyword_stuffing"]

@pytest.mark.asyncio
@patch("httpx.AsyncClient")
async def test_perform_heuristic_audit_failure(mock_client_class):
    # Setup mock httpx client response to throw exception
    mock_client = AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_client
    mock_client.get.side_effect = Exception("Connection timed out")

    # Setup mock DB session
    db = AsyncMock()
    audit_record = PageAudit(
        id="audit-uuid-3",
        url="https://rho.co/blog/nonexistent",
        email="test@example.com",
        status="PENDING"
    )
    
    mock_execute_res = MagicMock()
    mock_execute_res.scalar_one_or_none.return_value = audit_record
    db.execute.return_value = mock_execute_res

    # Run the audit
    with patch("app.modules.analysis.service.AnalysisService.send_audit_email", new_callable=AsyncMock) as mock_send_email:
        await AnalysisService.perform_heuristic_audit(db, "audit-uuid-3")
        
        # Assertions
        assert audit_record.status == "FAILED"
        assert "Connection timed out" in audit_record.error_message
        assert audit_record.completed_at is not None
        
        db.commit.assert_called()
        mock_send_email.assert_not_called()

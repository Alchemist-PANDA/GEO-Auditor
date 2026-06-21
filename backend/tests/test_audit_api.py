import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from app.main import app
from app.modules.analysis.models import PageAudit

# Import all models to resolve mapper relationships
from app.modules.workspaces.models import Organization, Workspace, Project, Brand, Competitor, User
from app.modules.agency.models import Agency, Client, Report, Notification, AuditLog
from app.modules.recommendations.models import Recommendation, RecommendationAction
from app.modules.analysis.models import (
    Response, Citation, CitationSource, Domain, 
    VisibilityScore, VisibilityHistory, ShareOfVoice, Topic, TopicCluster, PageAudit
)

@pytest.mark.asyncio
@patch("app.modules.analysis.router.create_pool")
async def test_request_page_audit_success(mock_create_pool):
    from app.core.database import get_db
    from app.core.security import get_current_user, UserSession
    
    # Setup mock DB session
    mock_db = AsyncMock()
    
    async def override_get_db():
        yield mock_db
        
    async def override_get_current_user():
        return UserSession(id="mock-user-id", email="user@profound-aeo.com", role="org_admin")
        
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Setup mock ARQ Redis pool
    mock_redis = AsyncMock()
    mock_create_pool.return_value = mock_redis
    
    # Request body
    payload = {
        "url": "https://example.com/best-credit-card",
        "email": "user@profound-aeo.com"
    }
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/v1/audit/request", json=payload)
            
        assert response.status_code == 202
        res_data = response.json()
        audit_id = res_data["audit_id"]
        assert audit_id is not None
        assert len(audit_id) > 10
        assert res_data["status"] == "PENDING"
        assert "received and queued" in res_data["message"]
        
        # Verify DB logging
        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()
        
        # Verify ARQ queueing
        mock_create_pool.assert_called_once()
        mock_redis.enqueue_job.assert_called_once_with(
            "run_heuristic_audit",
            {"audit_id": audit_id},
            _job_id=f"audit_{audit_id}"
        )
        mock_redis.close.assert_called_once()
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_request_page_audit_invalid_url():
    from app.core.security import get_current_user, UserSession
    
    async def override_get_current_user():
        return UserSession(id="mock-user-id", email="user@profound-aeo.com", role="org_admin")
        
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    payload = {
        "url": "invalid-url-scheme.com",
        "email": "user@profound-aeo.com"
    }
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/v1/audit/request", json=payload)
            
        assert response.status_code == 400
        assert "URL must start with http:// or https://" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()

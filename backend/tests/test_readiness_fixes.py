import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.rate_limit import RateLimiter
from app.modules.analysis.service import AnalysisService
from app.core.security import get_current_user, UserSession
from fastapi import Request, HTTPException

@pytest.mark.anyio
async def test_rate_limiter_bypass_in_testing():
    # If environment is testing, it should bypass and return None
    limiter = RateLimiter(requests_limit=1, window_seconds=60)
    mock_request = MagicMock(spec=Request)
    
    with patch("app.core.rate_limit.settings") as mock_settings:
        mock_settings.ENVIRONMENT = "testing"
        res = await limiter(mock_request)
        assert res is None

@pytest.mark.anyio
@patch("app.core.database.AsyncSessionLocal")
@patch("app.modules.prompts.service.PromptService.trigger_run")
async def test_scheduled_runs_trigger(mock_trigger_run, mock_db_local):
    # Setup mock session
    mock_db = AsyncMock()
    mock_db_local.return_value.__aenter__.return_value = mock_db
    
    # Mock models
    mock_prompt = MagicMock()
    mock_prompt.project_id = "proj_123"
    
    mock_model = MagicMock()
    mock_model.id = "gpt-4o"
    
    # Setup mock DB responses
    mock_prompt_res = MagicMock()
    mock_prompt_res.scalars().all.return_value = [mock_prompt]
    
    mock_model_res = MagicMock()
    mock_model_res.scalars().all.return_value = [mock_model]
    
    mock_db.execute.side_effect = [mock_prompt_res, mock_model_res]
    
    # Execute trigger
    await AnalysisService.trigger_scheduled_runs()
    
    # Assert
    mock_trigger_run.assert_called_once_with(mock_db, "proj_123", ["gpt-4o"])
    mock_db.commit.assert_called_once()

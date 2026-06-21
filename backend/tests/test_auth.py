import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from jose import jwt
from app.core.config import settings
from app.core.database import get_db
from app.modules.workspaces.models import Organization, User
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import pytest_asyncio

# Setup a test database engine
test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", pool_pre_ping=True)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    from app.core.database import Base
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with TestSessionLocal() as session:
        # Seed test user
        org = Organization(id=str(uuid.uuid4()), name="Test Org")
        session.add(org)
        
        hashed_password = pwd_context.hash("password123")
        user = User(
            id="test-user-uuid",
            email="test@profound-aeo.com",
            hashed_password=hashed_password,
            full_name="Test User",
            organization_id=org.id,
            role="org_admin"
        )
        session.add(user)
        await session.commit()
        
    async def override_get_db():
        async with TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
                
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_login_success():
    payload = {
        "email": "test@profound-aeo.com",
        "password": "password123"
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/workspaces/token", json=payload)
        
    assert response.status_code == 200
    res_data = response.json()
    assert "access_token" in res_data
    assert res_data["token_type"] == "bearer"
    
    # Verify we can decode the token with SUPABASE_JWT_SECRET
    decoded = jwt.decode(
        res_data["access_token"],
        settings.SUPABASE_JWT_SECRET,
        algorithms=["HS256"],
        audience="authenticated"
    )
    assert decoded["email"] == "test@profound-aeo.com"
    assert decoded["role"] == "org_admin"

@pytest.mark.asyncio
async def test_login_invalid_password():
    payload = {
        "email": "test@profound-aeo.com",
        "password": "wrongpassword"
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/workspaces/token", json=payload)
        
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.modules.workspaces.router import router as workspaces_router
from app.modules.prompts.router import router as prompts_router
from app.modules.analysis.router import router as analysis_router, audit_router
from app.modules.recommendations.router import router as recommendations_router
from app.modules.agency.router import router as agency_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize global Redis client connection pool on startup
    from redis.asyncio import ConnectionPool, Redis
    from arq import create_pool
    from arq.connections import RedisSettings
    
    pool = ConnectionPool.from_url(settings.REDIS_URL, max_connections=50)
    app.state.redis_client = Redis(connection_pool=pool)
    
    # Initialize global Arq queue connection pool on startup
    try:
        app.state.arq_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Could not connect to Redis/Arq pool on startup: {e}")
        app.state.arq_pool = None
        
    yield
    
    # Cleanup pools on shutdown
    if getattr(app.state, "arq_pool", None):
        await app.state.arq_pool.close()
    if getattr(app.state, "redis_client", None):
        await app.state.redis_client.close()
    await pool.disconnect()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Generative Engine Optimization (GEO) Analysis & Tracking Platform inspired by Profound",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Set CORS middleware parameters
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount module routers
app.include_router(workspaces_router, prefix=settings.API_V1_STR)
app.include_router(prompts_router, prefix=settings.API_V1_STR)
app.include_router(analysis_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(recommendations_router, prefix=settings.API_V1_STR)
app.include_router(agency_router, prefix=settings.API_V1_STR)

from fastapi import Response, status, Request
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
import time
import logging

@app.get("/health", tags=["System Health"])
async def get_health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

@app.get("/ready", tags=["System Health"])
async def get_readiness_check(request: Request, response: Response):
    db_status = "DOWN"
    redis_status = "DOWN"
    worker_status = "DOWN"
    ready = True
    
    # 1. Check Database
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_status = "UP"
    except Exception as e:
        logging.getLogger(__name__).error(f"Readiness check: DB failed: {e}")
        ready = False
        
    # 2. Check Redis & Worker Heartbeat
    redis_client = getattr(request.app.state, "redis_client", None)
    if redis_client:
        try:
            await redis_client.ping()
            redis_status = "UP"
            
            # Check Worker Heartbeat
            heartbeat = await redis_client.get("worker_heartbeat")
            if heartbeat:
                last_heartbeat = int(heartbeat)
                if int(time.time()) - last_heartbeat <= 15:
                    worker_status = "UP"
                else:
                    logging.getLogger(__name__).warning(f"Readiness check: worker heartbeat stale: {int(time.time()) - last_heartbeat}s ago")
                    ready = False
            else:
                logging.getLogger(__name__).warning("Readiness check: worker heartbeat key not found")
                ready = False
        except Exception as e:
            logging.getLogger(__name__).error(f"Readiness check: Redis/Worker failed: {e}")
            ready = False
    else:
        # If in non-production environments and redis not configured, we allow it,
        # but in production, missing redis pool makes us unready.
        if settings.ENVIRONMENT == "production":
            logging.getLogger(__name__).warning("Readiness check: redis_client not configured on app state")
            ready = False
        else:
            redis_status = "BYPASS"
            worker_status = "BYPASS"
        
    payload = {
        "status": "ready" if ready else "not_ready",
        "components": {
            "database": db_status,
            "redis": redis_status,
            "worker": worker_status
        }
    }
    
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        
    return payload


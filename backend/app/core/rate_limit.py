from fastapi import Request, HTTPException, status
from redis.asyncio import Redis
from app.core.config import settings
import time
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, requests_limit: int = 100, window_seconds: int = 60):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        
    async def __call__(self, request: Request):
        if settings.ENVIRONMENT == "testing":
            return
            
        client_ip = request.client.host if request.client else "unknown"
        route_path = request.url.path
        
        try:
            # Reuse persistent pool connection from FastAPI application state if registered
            redis_conn = getattr(request.app.state, "redis_client", None)
            should_close = False
            
            if redis_conn is None:
                redis_conn = Redis.from_url(settings.REDIS_URL)
                should_close = True
                
            key = f"rate_limit:{client_ip}:{route_path}"
            current_time = int(time.time())
            
            async with redis_conn.pipeline(transaction=True) as pipe:
                pipe.zremrangebyscore(key, 0, current_time - self.window_seconds)
                pipe.zadd(key, {str(current_time): current_time})
                pipe.zcard(key)
                pipe.expire(key, self.window_seconds)
                res = await pipe.execute()
                
            request_count = res[2]
            if should_close:
                await redis_conn.close()
            
            if request_count > self.requests_limit:
                logger.warning(f"Rate limit exceeded for client IP: {client_ip} on path: {route_path}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later."
                )
        except HTTPException as exc:
            raise exc
        except Exception as exc:
            # Fail closed in production for security, fail open in other environments
            if settings.ENVIRONMENT == "production":
                logger.error(f"Rate Limiter connection failure in production: {exc}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Rate limiting service currently unavailable."
                )
            else:
                logger.warning(f"Rate Limiter bypassed due to Redis connectivity issue: {exc}")
                pass

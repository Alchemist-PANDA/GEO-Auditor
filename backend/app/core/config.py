from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Profound GEO Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", validation_alias="ENVIRONMENT")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/geo_db",
        validation_alias="DATABASE_URL"
    )
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL"
    )
    
    # Auth
    SUPABASE_JWT_SECRET: str = Field(
        default="supabase_jwt_secret_placeholder_change_in_prod",
        validation_alias="SUPABASE_JWT_SECRET"
    )
    
    # CORS
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        validation_alias="ALLOWED_ORIGINS"
    )
    
    # LLM API Keys
    OPENAI_API_KEY: str = Field(default="", validation_alias="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(default="", validation_alias="ANTHROPIC_API_KEY")
    GEMINI_API_KEY: str = Field(default="", validation_alias="GEMINI_API_KEY")
    PERPLEXITY_API_KEY: str = Field(default="", validation_alias="PERPLEXITY_API_KEY")
    
    # Model defaults & swapping configurations
    DEFAULT_LLM_PROVIDER: str = Field(default="gemini", validation_alias="DEFAULT_LLM_PROVIDER")
    LLM_PROVIDER_PRIORITY_DEV: str = Field(default="gemini,openai,claude", validation_alias="LLM_PROVIDER_PRIORITY_DEV")
    LLM_PROVIDER_PRIORITY_PROD: str = Field(default="openai,gemini,claude", validation_alias="LLM_PROVIDER_PRIORITY_PROD")
    
    @model_validator(mode="after")
    def validate_production_secrets(self) -> 'Settings':
        if self.ENVIRONMENT == "production":
            if not self.SUPABASE_JWT_SECRET or "placeholder" in self.SUPABASE_JWT_SECRET.lower():
                raise ValueError("SUPABASE_JWT_SECRET must be configured with a secure non-placeholder secret in production.")
        return self
        
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()


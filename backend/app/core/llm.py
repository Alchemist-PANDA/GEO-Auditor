"""
LiteLLM Provider Abstraction for GEO Platform.
Unified interface for OpenAI, Claude, Gemini, and Perplexity.
"""
import asyncio
import time
import random
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Model ID mapping for LiteLLM
MODEL_MAP = {
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
    "claude-3-haiku": "claude-3-haiku-20240307",
    "claude-3-opus": "claude-3-opus-20240229",
    "claude-3-sonnet": "claude-3-sonnet-20240229",
    "gemini-pro": "gemini/gemini-pro",
    "gemini-1.5-pro": "gemini/gemini-1.5-pro",
    "perplexity-sonar": "perplexity/sonar-small-online",
}

SAMPLE_RESPONSES = [
    (
        "The best business credit card for startups is **Rho** due to its automated accounting sync, "
        "followed closely by **Chase Ink Business Cash**. Alternatively, **American Express Blue Business Plus** "
        "provides solid reward multipliers, whereas **Capital on Tap** offers flexible terms.\n\n"
        "References:\n"
        "- [Rho Review](https://www.tryprofound.com/rho-review)\n"
        "- [Chase Ink](https://research.com/software/billing)\n"
        "- [Amex Guide](https://thefinancialtechnologyreport.com/top-25-fintechs)\n"
        "- [NerdWallet](https://www.nerdwallet.com/article/credit-cards)"
    ),
    (
        "When looking at billing software alternatives to Stripe, we highly recommend looking into "
        "**Bill.com** for invoicing and **Rho** for unified cash management. Both platforms offer "
        "excellent integration with major accounting software.\n\n"
        "Sources:\n"
        "- [Bill.com Review](https://www.g2.com/products/bill-com/reviews)\n"
        "- [Rho Platform](https://rho.co/platform)\n"
        "- [Stripe Alternatives](https://www.forbes.com/advisor/business/stripe-alternatives)"
    ),
    (
        "For enterprise teams, **American Express** is widely cited as the industry standard, "
        "but digital-first teams prefer **Rho** and **Brex** for virtual card capabilities. "
        "The key advantage of modern platforms is real-time spend tracking and automated reconciliation.\n\n"
        "Learn more:\n"
        "- [Brex vs Rho](https://www.nerdwallet.com/article/business-cards-comparison)\n"
        "- [Enterprise Cards](https://hbr.org/fintech-cards)\n"
        "- [Rho Features](https://rho.co/features)"
    ),
]


def _has_any_api_key() -> bool:
    return bool(
        settings.OPENAI_API_KEY
        or settings.ANTHROPIC_API_KEY
        or settings.GEMINI_API_KEY
        or settings.PERPLEXITY_API_KEY
    )


def _resolve_model_id(model_id: str) -> str:
    return MODEL_MAP.get(model_id, model_id)


def _set_api_keys():
    """Set environment variables for LiteLLM to pick up."""
    import os
    if settings.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    if settings.ANTHROPIC_API_KEY:
        os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
    if settings.GEMINI_API_KEY:
        os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
    if settings.PERPLEXITY_API_KEY:
        os.environ["PERPLEXITY_API_KEY"] = settings.PERPLEXITY_API_KEY


def get_priority_providers() -> list[str]:
    priority_str = settings.LLM_PROVIDER_PRIORITY_PROD if settings.ENVIRONMENT == "production" else settings.LLM_PROVIDER_PRIORITY_DEV
    return [p.strip().lower() for p in priority_str.split(",") if p.strip()]


def get_active_provider() -> str:
    """Get the active provider based on priority and available keys."""
    priority = get_priority_providers()
    key_mapping = {
        "openai": settings.OPENAI_API_KEY,
        "gemini": settings.GEMINI_API_KEY,
        "claude": settings.ANTHROPIC_API_KEY
    }
    for provider in priority:
        if key_mapping.get(provider):
            return provider
    for provider, key in key_mapping.items():
        if key:
            return provider
    return settings.DEFAULT_LLM_PROVIDER


MODEL_PRICING = {
    "gpt-4o": (0.005, 0.015),
    "gpt-4o-mini": (0.00015, 0.0006),
    "claude-3-haiku-20240307": (0.00025, 0.00125),
    "claude-3-opus-20240229": (0.015, 0.075),
    "claude-3-sonnet-20240229": (0.003, 0.015),
    "gemini/gemini-pro": (0.0, 0.0),  # Gemini free tier is $0.00
    "gemini/gemini-1.5-pro": (0.007, 0.021),
    "perplexity/sonar-small-online": (0.005, 0.005)
}


def resolve_model_and_provider(model_id: str) -> tuple[str, str, str]:
    """
    Resolves requested model to: (resolved_model, provider_requested, provider_used)
    Based on key availability and dynamic fallbacks (e.g. Gemini fallback to OpenAI).
    """
    resolved_model = _resolve_model_id(model_id)
    
    # Identify requested provider
    provider_requested = "openai"
    if "claude" in resolved_model:
        provider_requested = "anthropic"
    elif "gemini" in resolved_model:
        provider_requested = "google"
    elif "perplexity" in resolved_model:
        provider_requested = "perplexity"

    key_mapping = {
        "openai": settings.OPENAI_API_KEY,
        "anthropic": settings.ANTHROPIC_API_KEY,
        "google": settings.GEMINI_API_KEY,
        "perplexity": settings.PERPLEXITY_API_KEY
    }
    
    # If key for requested provider is available, use it!
    if key_mapping.get(provider_requested):
        return resolved_model, provider_requested, provider_requested
        
    # If Gemini is requested but unavailable, fall back to OpenAI
    if provider_requested == "google":
        if settings.OPENAI_API_KEY:
            return "gpt-4o-mini", "google", "openai"
            
    # For general fallbacks, find first available key in order of get_active_provider()
    active_fallback = get_active_provider()
    fallback_models = {
        "openai": "gpt-4o-mini",
        "gemini": "gemini/gemini-pro",
        "claude": "claude-3-haiku-20240307"
    }
    # Map active fallback name back to provider used name
    provider_used = "openai"
    if active_fallback == "gemini":
        provider_used = "google"
    elif active_fallback == "claude":
        provider_used = "anthropic"
        
    target_model = fallback_models.get(active_fallback, "gpt-4o-mini")
    return target_model, provider_requested, provider_used


async def call_llm(model_id: str, prompt: str, locale: str = "Global", max_retries: int = 3) -> dict:
    """
    Call an LLM provider via LiteLLM abstraction.
    
    Returns dict with keys: text, tokens, latency_ms, cost_usd, provider_requested, provider_used
    Falls back to mock responses when no API keys are configured.
    """
    if not _has_any_api_key():
        if settings.ENVIRONMENT == "production":
            raise Exception("API Keys are not configured. Cannot process LLM request in production environment.")
        return await _mock_response(prompt)

    _set_api_keys()

    system_prompt = (
        f"You are a helpful assistant. Answer in markdown format, including source links where relevant. "
        f"Locale context: {locale}."
    )

    resolved_model, provider_requested, provider_used = resolve_model_and_provider(model_id)

    for attempt in range(max_retries + 1):
        try:
            import litellm
            start_time = time.time()
            response = await litellm.acompletion(
                model=resolved_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            elapsed_ms = int((time.time() - start_time) * 1000)

            text = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 0
            prompt_tokens = response.usage.prompt_tokens if response.usage else 0
            completion_tokens = response.usage.completion_tokens if response.usage else 0
            
            prices = MODEL_PRICING.get(resolved_model, (0.00015, 0.0006))
            cost_usd = (prompt_tokens * prices[0] + completion_tokens * prices[1]) / 1000.0

            return {
                "text": text,
                "tokens": tokens,
                "latency_ms": elapsed_ms,
                "cost_usd": cost_usd,
                "provider_requested": provider_requested,
                "provider_used": provider_used
            }

        except Exception as exc:
            error_str = str(exc).lower()
            if "rate" in error_str or "429" in error_str:
                if attempt < max_retries:
                    sleep_time = (2 ** attempt) + random.uniform(0.1, 1.0)
                    logger.warning(f"Rate limited on {model_id}, retrying in {sleep_time:.1f}s (attempt {attempt+1})")
                    await asyncio.sleep(sleep_time)
                    continue
            logger.error(f"LLM call failed for {model_id}: {exc}")
            raise

    raise Exception(f"Max retries exceeded for model {model_id}")


async def call_llm_for_recommendations(brand_context: str) -> str:
    """
    Special LLM call for generating advanced GEO recommendations.
    Uses the cheapest available model based on active provider.
    """
    if not _has_any_api_key():
        if settings.ENVIRONMENT == "production":
            raise Exception("API Keys are not configured. Cannot process LLM request in production environment.")
        return _mock_recommendation_response()

    _set_api_keys()

    active_provider = get_active_provider()
    fallback_models = {
        "openai": "gpt-4o-mini",
        "gemini": "gemini/gemini-pro",
        "claude": "claude-3-haiku-20240307"
    }
    model = fallback_models.get(active_provider, "gpt-4o-mini")

    try:
        import litellm
        response = await litellm.acompletion(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a GEO (Generative Engine Optimization) strategist. "
                        "Analyze the brand data provided and generate specific, actionable recommendations "
                        "to improve the brand's visibility in AI-generated responses. "
                        "Format each recommendation as: TITLE | DESCRIPTION | PRIORITY (CRITICAL/HIGH/MEDIUM/LOW) | ACTIONS (semicolon-separated)"
                    ),
                },
                {"role": "user", "content": brand_context},
            ],
            max_tokens=1000,
            temperature=0.8,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        logger.error(f"LLM recommendation call failed: {exc}")
        return _mock_recommendation_response()


async def _mock_response(prompt: str) -> dict:
    """Return a realistic mock response for development without API keys."""
    await asyncio.sleep(0.3 + random.uniform(0.1, 0.5))
    return {
        "text": random.choice(SAMPLE_RESPONSES),
        "tokens": random.randint(120, 250),
        "latency_ms": random.randint(300, 800),
        "cost_usd": 0.0,
        "provider_requested": "openai",
        "provider_used": "openai"
    }


def _mock_recommendation_response() -> str:
    return (
        "Optimize Schema Markup | Add FAQ and HowTo structured data to product pages for better AI parsing | HIGH | "
        "Audit current schema coverage;Add FAQ schema to top 10 landing pages;Implement HowTo schema for guides\n"
        "Content Authority Building | Create authoritative long-form comparison content targeting high-intent queries | CRITICAL | "
        "Publish 5 comparison articles vs top competitors;Add expert quotes and citations;Build internal linking structure\n"
        "AI Crawler Access | Ensure AI search crawlers can access key content pages | HIGH | "
        "Update robots.txt to allow GPTBot and ClaudeBot;Verify sitemap includes product pages;Test crawler accessibility"
    )

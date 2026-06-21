# Crawler & Agent Analytics Specification

This document defines the architecture of the server-side log analytics system, detailing how AI bot crawler events are ingested, verified, and analyzed.

---

## 1. CDN Log Ingestion Channels

The platform tracks crawler events without client-side JavaScript. Logs are streamed directly from CDN providers:

* **Cloudflare**: Ingested via Cloudflare Workers (real-time forwarding) or Logpush (batched buffers).
* **AWS CloudFront**: Log streaming via CloudFront Real-Time Logs connected to Amazon Kinesis Data Firehose.
* **Fastly**: Integrated using Fastly Log Streaming targets directed to the platform endpoint.
* **Vercel & Netlify**: Log integrations configured via marketplace connectors or webhook functions.
* **Shopify**: Gated environment; requires a third-party CDN wrapper (e.g., Nostra AI or Cloudflare Proxy) to forward origin traffic.

---

## 2. Bot Identity & IP Verification Pipeline

To prevent analytical spoofing, incoming request headers are verified against provider records. If a request claims to be an AI bot but its IP address does not match verified ranges, the request is flagged as spoofed and excluded from analytics.

```
       [CDN Log Push] ──> [Match User-Agent]
                                │
                                ▼
                   [Look Up Provider Registry]
                   Is IP in cached range or PTR?
                     ├── Yes ──> Mark bot_verified = true
                     └── No  ──> Mark spoofed_traffic = true
```

### 2.1 Verification Python Pipeline

```python
import ipaddress
import socket
import httpx
from functools import lru_cache

# Known bot strings matching User-Agent signatures
KNOWN_BOT_TOKENS = {
    "GPTBot": "openai_gptbot",
    "OAI-SearchBot": "openai_searchbot",
    "ChatGPT-User": "openai_chatgpt_user",
    "ClaudeBot": "anthropic_claudebot",
    "Claude-User": "anthropic_claude_user",
    "PerplexityBot": "perplexity_bot",
    "Google-Extended": "google_extended",
    "Googlebot": "google_bot",
    "Bingbot": "bing_bot"
}

@lru_cache(maxsize=16)
def get_cached_cidr_ranges(provider_key: str) -> list[ipaddress.IPv4Network]:
    endpoints = {
        "openai_gptbot": "https://openai.com/gptbot.json",
        "openai_searchbot": "https://openai.com/searchbot.json",
        "openai_chatgpt_user": "https://openai.com/chatgpt-user.json",
        "perplexity_bot": "https://perplexity.ai/perplexitybot.json" # Simulated url path
    }
    url = endpoints.get(provider_key)
    if not url:
        return []
    try:
        r = httpx.get(url, timeout=5)
        return [ipaddress.ip_network(p) for p in r.json().get("prefixes", [])]
    except Exception:
        return []

def verify_ip_published_range(ip_str: str, provider_key: str) -> bool:
    addr = ipaddress.ip_address(ip_str)
    networks = get_cached_cidr_ranges(provider_key)
    return any(addr in net for net in networks)

def verify_ip_reverse_dns(ip_str: str, domain_suffix: str) -> bool:
    """Runs PTR verification (used for Anthropic / Google standard bots)"""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip_str)
        if not hostname.endswith(domain_suffix):
            return False
        # Forward confirm IP match
        resolved_ips = socket.gethostbyname_ex(hostname)[2]
        return ip_str in resolved_ips
    except (socket.herror, socket.gaierror):
        return False
```

---

## 3. Crawler Telemetry Metrics

Metrics are written to ClickHouse and computed daily:

1. **Crawl Frequency & Trends**: Raw request count per bot family over a 7/30/90-day time horizon.
2. **Response Latency Distribution**: Tracks crawler-experienced latencies. High response latencies (e.g., >1000ms) increase the risk of bots abandoning crawls.
3. **Bot Access Error Rate**: Ingestion counts of `4xx` and `5xx` status codes. Indicates pages blocked by authorization gates or server failures.
4. **Crawl Depth & Coverage**: The ratio of crawled URLs to total indexable pages.
5. **Time-to-First-Crawl (TFC)**: Time delta between publishing a page (via CMS adapter webhook) and the first verified bot request.
6. **Crawl-to-Citation Correlation**: Time-series cross-correlation showing if crawl increases precede citation mentions.

---

## 4. Benchmark Analytics (The Profound Network)

The platform evaluates client performance metrics against the **Profound Network** corpus (covering 800,000+ benchmarked pages).

$$\text{Crawl Percentile} = \left( \frac{\text{Count of Network Pages with Lower Crawl Rate for Category}}{\text{Total Network Pages in Category}} \right) \times 100$$

* A crawl frequency of 1 request/day might look deficient in isolation, but can be classified as "Good" if the category median is 0.2 requests/day.
* Highly crawled domains within the network serve as priority targets for outreach recommendations.

---

## 5. Architectural Summary Table

| Dimension | [CONFIRMED] Findings | [INFERRED] Systems Behavior | [ASSUMPTION] System Limits | [RECOMMENDATION] Optimization |
|---|---|---|---|---|
| **Crawl Analytics** | Tracks crawler events at the server level, requiring no front-end JS. | Logs capture actual RAG bot behavior, which ignores typical JS tags. | Log volumes during crawls saturate analytical database storage. | Batch ingest logs using a staging pipeline before committing to ClickHouse. |
| **Bot Verification** | Telemetry filters out spoofed bots by checking IPs. | Reverse DNS checks run dynamically during routing. | DNS checks during hot routing cycles introduce processing lag. | Check UA strings first; resolve IP checks asynchronously using background queues. |
| **Integrations** | Cloudflare Workers or Logpush streams log events directly. | Cloudflare handles high log throughput via batch configurations. | Custom platforms (Shopify) restrict standard CDN modifications. | Guide Shopify clients to route traffic through a custom Cloudflare setup. |
| **Benchmarking** | Benchmarks compare rates against a network of 800,000+ pages. | Benchmark datasets are pooled across all tracked accounts. | Merging global profiles violates enterprise tenant isolation policies. | Anonymize metadata domains before adding them to the network index. |

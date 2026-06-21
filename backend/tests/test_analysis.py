import pytest
from app.modules.analysis.service import AnalysisService

def test_extract_links_from_markdown():
    text = (
        "We recommend checking out [Rho Card](https://www.tryprofound.com/rho-review) and "
        "[Chase Ink](https://research.com/software/billing) for startup accounting."
    )
    links = AnalysisService.extract_links_with_position(text)
    urls = [url for url, pos in links]
    assert len(urls) == 2
    assert "https://www.tryprofound.com/rho-review" in urls
    assert "https://research.com/software/billing" in urls

def test_get_base_domain():
    url = "https://www.nerdwallet.com/article/credit-cards"
    domain = AnalysisService.get_base_domain(url)
    assert domain == "nerdwallet.com"

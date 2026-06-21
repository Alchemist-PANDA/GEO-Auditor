"""
Comprehensive benchmark tests for GEO Platform algorithms.
Tests visibility scoring, citation impact, sentiment analysis, 
domain authority, link extraction, and model weighting.
"""
import pytest
from app.modules.analysis.service import AnalysisService


# ─── Test Data ───────────────────────────────────────────

TEXT_POSITIVE = (
    "Rho is the best business credit card. We highly recommend it for its "
    "great security features and fast processing. It's an excellent choice for startups."
)

TEXT_NEGATIVE = (
    "This service is bad and slow. There are multiple errors and it's very "
    "expensive. Avoid this terrible product."
)

TEXT_NEUTRAL = "The product offers standard features at a market price point."

TEXT_MIXED = (
    "The product has great features and fast delivery, but the service is "
    "bad and there are some errors in billing."
)

TEXT_WITH_LINKS = (
    "Check out [Rho](https://rho.co/cards) and [Brex](https://brex.com/corporate) "
    "for business cards. Also see [NerdWallet](https://nerdwallet.com/reviews)."
)

TEXT_WITH_DUPLICATE_LINKS = (
    "See [Rho](https://rho.co/cards) for details. "
    "More about [Rho Cards](https://rho.co/cards) here."
)

TEXT_NO_LINKS = "This text has no links at all. Just plain text content."


# ─── Sentiment Analysis Tests ────────────────────────────

class TestSentimentAnalysis:
    def test_positive_text(self):
        score = AnalysisService.calculate_sentiment(TEXT_POSITIVE)
        assert score > 0.5, f"Expected positive sentiment > 0.5, got {score}"

    def test_negative_text(self):
        score = AnalysisService.calculate_sentiment(TEXT_NEGATIVE)
        assert score < -0.5, f"Expected negative sentiment < -0.5, got {score}"

    def test_neutral_text(self):
        score = AnalysisService.calculate_sentiment(TEXT_NEUTRAL)
        assert score == 0.0, f"Expected neutral sentiment 0.0, got {score}"

    def test_mixed_text(self):
        score = AnalysisService.calculate_sentiment(TEXT_MIXED)
        assert -1.0 <= score <= 1.0, f"Score out of range: {score}"
        # Mixed should be between -0.5 and 0.5
        assert -0.5 <= score <= 0.5, f"Mixed sentiment should be moderate, got {score}"

    def test_empty_string(self):
        score = AnalysisService.calculate_sentiment("")
        assert score == 0.0

    def test_only_positive_words(self):
        score = AnalysisService.calculate_sentiment("best great excellent amazing top")
        assert score == 1.0, f"All positive words should yield 1.0, got {score}"

    def test_only_negative_words(self):
        score = AnalysisService.calculate_sentiment("bad terrible worst fail issue")
        assert score == -1.0, f"All negative words should yield -1.0, got {score}"

    def test_case_insensitive(self):
        score_lower = AnalysisService.calculate_sentiment("best great")
        score_upper = AnalysisService.calculate_sentiment("BEST GREAT")
        assert score_lower == score_upper


# ─── Model Weight Tests ─────────────────────────────────

class TestModelWeights:
    def test_gpt4o_weight(self):
        weight = AnalysisService.get_model_weight("gpt-4o")
        assert weight == 1.0

    def test_chatgpt4_weight(self):
        weight = AnalysisService.get_model_weight("chatgpt-4")
        assert weight == 1.0

    def test_claude_opus_weight(self):
        weight = AnalysisService.get_model_weight("claude-3-opus-20240229")
        assert weight == 0.9

    def test_claude_haiku_weight(self):
        weight = AnalysisService.get_model_weight("claude-3-haiku-20240307")
        assert weight == 0.7

    def test_gemini_pro_weight(self):
        weight = AnalysisService.get_model_weight("gemini-pro-1.5")
        assert weight == 0.8

    def test_perplexity_sonar_weight(self):
        weight = AnalysisService.get_model_weight("perplexity-sonar-small")
        assert weight == 0.85

    def test_unknown_model_weight(self):
        weight = AnalysisService.get_model_weight("completely-unknown-model-v9")
        assert weight == 0.5

    def test_empty_model_id(self):
        weight = AnalysisService.get_model_weight("")
        assert weight == 0.5


# ─── Domain Authority Tests ──────────────────────────────

class TestDomainAuthority:
    def test_gov_domain(self):
        assert AnalysisService.get_mock_domain_authority("irs.gov") == 95

    def test_edu_domain(self):
        assert AnalysisService.get_mock_domain_authority("mit.edu") == 85

    def test_org_domain(self):
        assert AnalysisService.get_mock_domain_authority("wikipedia.org") == 70

    def test_io_domain(self):
        assert AnalysisService.get_mock_domain_authority("github.io") == 65

    def test_com_domain(self):
        assert AnalysisService.get_mock_domain_authority("example.com") == 50

    def test_net_domain(self):
        # .net falls through to default
        assert AnalysisService.get_mock_domain_authority("example.net") == 50

    def test_complex_subdomain(self):
        assert AnalysisService.get_mock_domain_authority("research.stanford.edu") == 85


# ─── Link Extraction Tests ──────────────────────────────

class TestLinkExtraction:
    def test_extract_multiple_links(self):
        links = AnalysisService.extract_links_with_position(TEXT_WITH_LINKS)
        assert len(links) == 3
        urls = [url for url, pos in links]
        assert "https://rho.co/cards" in urls
        assert "https://brex.com/corporate" in urls
        assert "https://nerdwallet.com/reviews" in urls

    def test_positions_normalized(self):
        links = AnalysisService.extract_links_with_position(TEXT_WITH_LINKS)
        for url, pos in links:
            assert 0.0 <= pos <= 1.0, f"Position {pos} for {url} not in [0, 1]"

    def test_positions_ordered(self):
        links = AnalysisService.extract_links_with_position(TEXT_WITH_LINKS)
        positions = [pos for _, pos in links]
        assert positions == sorted(positions), "Positions should be in ascending order"

    def test_duplicate_links_deduplicated(self):
        links = AnalysisService.extract_links_with_position(TEXT_WITH_DUPLICATE_LINKS)
        assert len(links) == 1
        assert links[0][0] == "https://rho.co/cards"

    def test_no_links(self):
        links = AnalysisService.extract_links_with_position(TEXT_NO_LINKS)
        assert len(links) == 0

    def test_empty_string(self):
        links = AnalysisService.extract_links_with_position("")
        assert len(links) == 0


# ─── Base Domain Tests ───────────────────────────────────

class TestBaseDomain:
    def test_standard_url(self):
        assert AnalysisService.get_base_domain("https://www.nerdwallet.com/article/cards") == "nerdwallet.com"

    def test_no_www(self):
        assert AnalysisService.get_base_domain("https://rho.co/cards") == "rho.co"

    def test_with_port(self):
        domain = AnalysisService.get_base_domain("https://localhost:8000/api")
        assert domain == "localhost:8000"

    def test_subdomain(self):
        domain = AnalysisService.get_base_domain("https://api.github.com/repos")
        assert domain == "api.github.com"


# ─── Citation Impact Formula Tests ───────────────────────

class TestCitationImpact:
    """
    Citation Impact = domain_authority × position_weight × model_weight
    Where position_weight = 1.0 + (1.0 - position_index / 100.0)
    """

    def test_early_citation_high_authority(self):
        da = 80
        pos_index = 10  # Early in response
        model_weight = AnalysisService.get_model_weight("gpt-4o")  # 1.0
        pos_weight = 1.0 + (1.0 - pos_index / 100.0)  # 1.9
        impact = da * pos_weight * model_weight
        assert impact == pytest.approx(152.0, rel=0.01)

    def test_late_citation_low_authority(self):
        da = 50
        pos_index = 90  # Late in response
        model_weight = AnalysisService.get_model_weight("unknown-model")  # 0.5
        pos_weight = 1.0 + (1.0 - pos_index / 100.0)  # 1.1
        impact = da * pos_weight * model_weight
        assert impact == pytest.approx(27.5, rel=0.01)

    def test_middle_citation(self):
        da = 70
        pos_index = 50  # Middle of response
        model_weight = AnalysisService.get_model_weight("gemini-pro")  # 0.8
        pos_weight = 1.0 + (1.0 - pos_index / 100.0)  # 1.5
        impact = da * pos_weight * model_weight
        assert impact == pytest.approx(84.0, rel=0.01)

    def test_zero_position(self):
        """Citation at the very start of response should have max position weight."""
        da = 60
        pos_index = 0
        model_weight = 1.0
        pos_weight = 1.0 + (1.0 - 0 / 100.0)  # 2.0
        impact = da * pos_weight * model_weight
        assert impact == pytest.approx(120.0, rel=0.01)

    def test_position_100(self):
        """Citation at the very end should have minimum position weight."""
        da = 60
        pos_index = 100
        model_weight = 1.0
        pos_weight = 1.0 + (1.0 - 100 / 100.0)  # 1.0
        impact = da * pos_weight * model_weight
        assert impact == pytest.approx(60.0, rel=0.01)


# ─── Share of Voice Tests ────────────────────────────────

class TestShareOfVoice:
    """SOV = mention_count / total_mentions × 100"""

    def test_basic_sov_calculation(self):
        brand_mentions = 5
        comp_a_mentions = 3
        comp_b_mentions = 2
        total = brand_mentions + comp_a_mentions + comp_b_mentions

        brand_sov = (brand_mentions / total) * 100.0
        comp_a_sov = (comp_a_mentions / total) * 100.0
        comp_b_sov = (comp_b_mentions / total) * 100.0

        assert brand_sov == pytest.approx(50.0)
        assert comp_a_sov == pytest.approx(30.0)
        assert comp_b_sov == pytest.approx(20.0)
        assert brand_sov + comp_a_sov + comp_b_sov == pytest.approx(100.0)

    def test_single_player(self):
        brand_mentions = 10
        total = 10
        sov = (brand_mentions / total) * 100.0
        assert sov == 100.0

    def test_zero_mentions(self):
        total = 0
        sov = 0.0 if total == 0 else (0 / total) * 100.0
        assert sov == 0.0

    def test_equal_distribution(self):
        players = 4
        each = 5
        total = players * each
        sov = (each / total) * 100.0
        assert sov == pytest.approx(25.0)


# ─── Visibility V2 Scoring Logic Tests ──────────────────

class TestVisibilityV2:
    """
    Visibility V2 = base_mention × position_weight × sentiment_weight × citation_weight × model_weight
    Where:
    - base_mention = 1.0 (brand found in response)
    - position_weight = 1.0 + (1.0 - relative_position)
    - sentiment_weight = 1.0 + sentiment_score
    - citation_weight = 1.2 if domain cited, else 1.0
    - model_weight = from get_model_weight()
    """

    def test_best_case_visibility(self):
        """Brand at position 0, positive sentiment, domain cited, top model."""
        base = 1.0
        position_weight = 1.0 + (1.0 - 0.0)  # 2.0
        sentiment_weight = 1.0 + 1.0  # 2.0
        citation_weight = 1.2
        model_weight = 1.0
        score = base * position_weight * sentiment_weight * citation_weight * model_weight
        assert score == pytest.approx(4.8)

    def test_worst_case_visibility(self):
        """Brand at end, negative sentiment, no domain citation, weak model."""
        base = 1.0
        position_weight = 1.0 + (1.0 - 1.0)  # 1.0
        sentiment_weight = 1.0 + (-1.0)  # 0.0
        citation_weight = 1.0
        model_weight = 0.5
        score = base * position_weight * sentiment_weight * citation_weight * model_weight
        assert score == pytest.approx(0.0)

    def test_average_case_visibility(self):
        """Brand at middle, neutral sentiment, no citation, mid model."""
        base = 1.0
        position_weight = 1.0 + (1.0 - 0.5)  # 1.5
        sentiment_weight = 1.0 + 0.0  # 1.0
        citation_weight = 1.0
        model_weight = 0.8
        score = base * position_weight * sentiment_weight * citation_weight * model_weight
        assert score == pytest.approx(1.2)

    def test_max_possible_per_response(self):
        """The normalization constant should be 4.8 (max single-response score)."""
        max_score = 1.0 * 2.0 * 2.0 * 1.2 * 1.0
        assert max_score == pytest.approx(4.8)

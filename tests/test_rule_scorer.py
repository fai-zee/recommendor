from __future__ import annotations

from services.ranking.scorers import RuleScorer


def test_rule_scorer():
    scorer = RuleScorer()
    score, reason = scorer.score(
        {"bio_keyword": 1.0, "website_nl": 1.0, "followers_bucket": 2.0}
    )
    assert score > 0.8
    assert "bio keyword" in reason

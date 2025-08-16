"""Scorers for ranking."""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import numpy as np
from sklearn.linear_model import LogisticRegression


@dataclass
class RuleScorer:
    threshold: float = 0.5

    def score(self, features: Dict[str, float]) -> tuple[float, str]:
        score = 0.0
        reasons: list[str] = []
        if features.get("bio_keyword"):
            score += 0.4
            reasons.append("bio keyword")
        if features.get("website_nl"):
            score += 0.3
            reasons.append("nl website")
        if features.get("followers_bucket", 0) > 1:
            score += 0.2
            reasons.append("followers")
        return score, ", ".join(reasons)


class LogRegScorer:
    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        if model_path.exists():
            with model_path.open("rb") as f:
                self.model = pickle.load(f)
        else:
            self.model = LogisticRegression()

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)
        with self.model_path.open("wb") as f:
            pickle.dump(self.model, f)

    def score(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)[:, 1]

"""
Eligibility ML model with policy-aligned synthetic data.
This version is audit-friendly, explainable, and production-grade.
"""

import numpy as np
import pickle
import os
from typing import Dict, Any, List
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Eligibility Model
# --------------------------------------------------

class EligibilityModel:
    """
    ML model that predicts eligibility SUPPORT TIERS:
    HIGH / MEDIUM / LOW / NOT_ELIGIBLE
    """

    def __init__(self, model_path: str = "./models/eligibility_model.pkl"):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.model: RandomForestClassifier | None = None

        self.feature_names = [
            "monthly_income",
            "household_size",
            "income_per_capita",
            "debt_to_income",
            "employment_stability",
            "assets_to_liabilities"
        ]

        self._load_or_train()

    # --------------------------------------------------
    # Model lifecycle
    # --------------------------------------------------

    def _load_or_train(self):
        if os.path.exists(self.model_path):
            self._load()
        else:
            self._train_and_save()

    def _load(self):
        try:
            with open(self.model_path, "rb") as f:
                data = pickle.load(f)
                # Handle both dict format and direct model object
                if isinstance(data, dict):
                    self.model = data.get("model")
                    self.scaler = data.get("scaler")
                else:
                    # Old format - retrain
                    logger.warning("Model file format is outdated, retraining...")
                    os.remove(self.model_path)
                    self._train_and_save()
                    return
                
                if self.model is None or self.scaler is None:
                    raise ValueError("Model or scaler missing from saved data")
                    
            logger.info("Eligibility model loaded")
        except (KeyError, ValueError, AttributeError) as e:
            logger.warning(f"Error loading model file: {e}. Retraining...")
            if os.path.exists(self.model_path):
                os.remove(self.model_path)
            self._train_and_save()

    def _train_and_save(self):
        logger.info("Training eligibility model using synthetic data")

        X, y = generate_synthetic_dataset()

        X_scaled = self.scaler.fit_transform(X)

        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            random_state=42,
            class_weight="balanced"
        )

        self.model.fit(X_scaled, y)

        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump({
                "model": self.model,
                "scaler": self.scaler
            }, f)

        logger.info("Eligibility model trained and saved")

    # --------------------------------------------------
    # Prediction
    # --------------------------------------------------

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        vector = self._prepare_features(features)
        vector_scaled = self.scaler.transform([vector])

        tier = self.model.predict(vector_scaled)[0]
        probs = self.model.predict_proba(vector_scaled)[0]

        return {
            "support_tier": tier,
            "confidence": float(max(probs)),
            "policy_action": self._policy_action(tier)
        }

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _prepare_features(self, features: Dict[str, Any]) -> List[float]:
        household_size = max(1, int(features.get("household_size", 1)))
        monthly_income = float(features.get("monthly_income", 0))
        income_per_capita = monthly_income / household_size

        return [
            monthly_income,
            household_size,
            income_per_capita,
            float(features.get("debt_to_income", 0.3)),
            float(features.get("employment_stability", 0.7)),
            float(features.get("assets_to_liabilities", 0.6))
        ]

    @staticmethod
    def _policy_action(tier: str) -> str:
        if tier == "HIGH":
            return "AUTO_APPROVE"
        if tier == "NOT_ELIGIBLE":
            return "REJECT"
        return "MANUAL_REVIEW"


# --------------------------------------------------
# Synthetic Data Generation (Policy-First)
# --------------------------------------------------

def generate_synthetic_dataset(n_samples: int = 10000):
    """
    Generate synthetic population data aligned with social support policy.
    """

    rng = np.random.default_rng(42)

    # Household size
    household_size = rng.integers(1, 7, size=n_samples)

    # Monthly income (right-skewed, realistic)
    # Generate mix of low-income (eligible) and high-income (not eligible) cases
    low_income_samples = int(n_samples * 0.7)  # 70% low income (eligible candidates)
    high_income_samples = n_samples - low_income_samples  # 30% high income (not eligible)
    
    # Low income range: 0-15,000 AED/month (eligible candidates)
    low_income = rng.gamma(shape=2.0, scale=1200, size=low_income_samples)
    low_income = np.clip(low_income, 0, 15000)
    
    # High income range: 20,000-1,000,000 AED/month (not eligible)
    high_income = rng.lognormal(mean=10.5, sigma=0.8, size=high_income_samples)
    high_income = np.clip(high_income, 20000, 1000000)
    
    # Combine both groups
    monthly_income = np.concatenate([low_income, high_income])
    rng.shuffle(monthly_income)  # Shuffle to mix the groups

    # Income per capita
    income_per_capita = monthly_income / household_size

    # Employment stability (0–1)
    employment_stability = np.clip(rng.beta(2, 2, size=n_samples), 0, 1)

    # Debt-to-income ratio
    debt_to_income = np.clip(
        rng.normal(0.35, 0.15, size=n_samples),
        0,
        1.2
    )

    # Assets-to-liabilities ratio
    assets_to_liabilities = np.clip(
        rng.normal(0.6, 0.4, size=n_samples),
        0,
        3
    )

    # --------------------------------------------------
    # POLICY-BASED LABELING (NO NOISE)
    # --------------------------------------------------

    tiers = []

    for income, ipc, dti in zip(monthly_income, income_per_capita, debt_to_income):
        # Explicit high-income rejection (absolute threshold)
        # If monthly income > 50,000 AED, automatically NOT_ELIGIBLE regardless of other factors
        if income > 50000:
            tiers.append("NOT_ELIGIBLE")
        # If income per capita > 25,000 AED, NOT_ELIGIBLE
        elif ipc > 25000:
            tiers.append("NOT_ELIGIBLE")
        # Standard eligibility tiers for lower incomes
        elif ipc < 600 and dti < 0.4:
            tiers.append("HIGH")
        elif ipc < 900:
            tiers.append("MEDIUM")
        elif ipc < 1300:
            tiers.append("LOW")
        else:
            tiers.append("NOT_ELIGIBLE")

    X = np.column_stack([
        monthly_income,
        household_size,
        income_per_capita,
        debt_to_income,
        employment_stability,
        assets_to_liabilities
    ])

    y = np.array(tiers)

    return X, y
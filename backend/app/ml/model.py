import os
import logging
from typing import Dict, Any, Tuple, Optional
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV

from app.config import settings
from app.ml.dataset import get_training_data

logger = logging.getLogger(__name__)


class ScamMLClassifier:
    """
    NLP and Machine Learning Classifier for Scam Detection.
    Uses TF-IDF feature extraction with calibrated logistic regression.
    """

    def __init__(self):
        self.model_path = settings.MODEL_DIR / settings.MODEL_FILENAME
        self.pipeline: Optional[Pipeline] = None
        self.classes_ = ["Safe", "Suspicious", "High Risk Scam"]
        self._initialize_or_load()

    def _build_pipeline(self) -> Pipeline:
        """Construct the ML text classification pipeline."""
        return Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 3),
                max_features=15000,
                sublinear_tf=True,
                lowercase=True,
                token_pattern=r'(?u)\b\w+\b|[!$%?@#]'
            )),
            ('clf', LogisticRegression(
                C=2.5,
                max_iter=1000,
                class_weight='balanced',
                solver='lbfgs',
                random_state=42
            ))
        ])

    def train(self, custom_data=None) -> Dict[str, Any]:
        """Train the classifier on the curated dataset and persist to disk."""
        data = custom_data or get_training_data()
        texts = [item["text"] for item in data]
        labels = [item["label"] for item in data]

        logger.info(f"Training ML Scam Classifier on {len(texts)} samples...")
        pipeline = self._build_pipeline()
        pipeline.fit(texts, labels)

        self.pipeline = pipeline
        self.classes_ = list(pipeline.classes_)

        # Persist to disk
        try:
            os.makedirs(settings.MODEL_DIR, exist_ok=True)
            joblib.dump(self.pipeline, self.model_path)
            logger.info(f"Model successfully saved to {self.model_path}")
        except Exception as e:
            logger.warning(f"Could not persist model to disk: {e}")

        return {
            "status": "success",
            "samples_count": len(texts),
            "classes": self.classes_
        }

    def _initialize_or_load(self):
        """Load saved model if exists, otherwise train a fresh one."""
        if os.path.exists(self.model_path) and not settings.AUTO_RETRAIN_ON_STARTUP:
            try:
                self.pipeline = joblib.load(self.model_path)
                self.classes_ = list(self.pipeline.classes_)
                logger.info(f"Loaded existing ML model from {self.model_path}")
                return
            except Exception as e:
                logger.warning(f"Failed to load model from disk: {e}. Re-training...")

        # Train on startup
        self.train()

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Classify input text into Safe, Suspicious, or High Risk Scam
        with class probabilities and confidence score.
        """
        if not self.pipeline:
            self.train()

        # Clean text basic
        clean_text = text.strip()
        if not clean_text:
            return {
                "predicted_label": "Safe",
                "probabilities": {"Safe": 1.0, "Suspicious": 0.0, "High Risk Scam": 0.0},
                "confidence": 1.0,
                "top_features": []
            }

        probabilities = self.pipeline.predict_proba([clean_text])[0]
        class_prob_map = {cls: float(prob) for cls, prob in zip(self.pipeline.classes_, probabilities)}

        # Ensure all 3 standard classes exist in map
        for standard_cls in ["Safe", "Suspicious", "High Risk Scam"]:
            if standard_cls not in class_prob_map:
                class_prob_map[standard_cls] = 0.0

        predicted_idx = int(np.argmax(probabilities))
        predicted_label = self.pipeline.classes_[predicted_idx]
        confidence = float(probabilities[predicted_idx])

        # Extract top influential tokens for explainability
        top_tokens = self._extract_influential_tokens(clean_text)

        return {
            "predicted_label": predicted_label,
            "probabilities": class_prob_map,
            "confidence": round(confidence, 4),
            "top_features": top_tokens
        }

    def _extract_influential_tokens(self, text: str, max_tokens: int = 5) -> list[str]:
        """Extract words/n-grams present in the text that most strongly point toward scam."""
        try:
            tfidf: TfidfVectorizer = self.pipeline.named_steps['tfidf']
            clf: LogisticRegression = self.pipeline.named_steps['clf']

            feature_names = tfidf.get_feature_names_out()
            feature_vector = tfidf.transform([text]).toarray()[0]
            non_zero_indices = np.where(feature_vector > 0)[0]

            if len(non_zero_indices) == 0:
                return []

            # If "High Risk Scam" is in classes, get its index
            if "High Risk Scam" in self.pipeline.classes_:
                scam_class_idx = list(self.pipeline.classes_).index("High Risk Scam")
                weights = clf.coef_[scam_class_idx]
                
                # Score tokens by tfidf * coefficient
                token_scores = []
                for idx in non_zero_indices:
                    token = feature_names[idx]
                    score = feature_vector[idx] * weights[idx]
                    token_scores.append((token, score))

                # Sort by highest scam correlation
                token_scores.sort(key=lambda x: x[1], reverse=True)
                return [t[0] for t in token_scores[:max_tokens] if t[1] > 0]
        except Exception as e:
            logger.debug(f"Could not extract top tokens: {e}")

        return []


# Global singleton instance
ml_classifier = ScamMLClassifier()

from app.services.scoring_service import ScoringService

class DummyPredictor:
    def predict(self, features):
        return 0.95, 1

def test_status_declined():
    service = ScoringService(DummyPredictor())
    status = service.determine_status(0.95)

    assert status == "DECLINED"

def test_status_review():
    service = ScoringService(DummyPredictor())
    status = service.determine_status(0.70)

    assert status == "REVIEW"

def test_status_approved():
    service = ScoringService(DummyPredictor())
    status = service.determine_status(0.30)

    assert status == "APPROVED"


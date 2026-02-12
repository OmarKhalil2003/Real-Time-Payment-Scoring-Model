from app.services.scoring_service import ScoringService

class DummyPredictor:
    def predict(self, features):
        return 0.95, 1

def test_status_declined():
    service = ScoringService(DummyPredictor())
    status = service.determine_status(0.95, 1)

    assert status == "DECLINED"

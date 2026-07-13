from app.api.logic import determine_status


def test_determine_status_approved():
    assert determine_status(0.10) == "APPROVED"


def test_determine_status_review():
    assert determine_status(0.70) == "REVIEW"


def test_determine_status_declined():
    assert determine_status(0.90) == "DECLINED"

from producer.events import base_event, generate_event


def test_base_event_has_required_fields():
    event = base_event("purchase", is_fraud=False)
    required = {
        "transaction_id", "customer_id", "merchant_id", "timestamp",
        "amount", "currency", "payment_method", "country",
        "device", "ip", "fraud_label", "feature_1", "feature_2", "feature_3",
    }
    assert required.issubset(event.keys())


def test_generate_event_returns_valid_topic():
    topic, payload = generate_event()
    assert topic in ("payments", "refunds", "alerts")
    assert isinstance(payload, dict)
    if topic == "alerts":
        assert "alert_id" in payload or "transaction_id" in payload
    else:
        assert "transaction_id" in payload

"""
Tests for MCP Servers — testing tool logic directly (no MCP transport).

Validates:
- Customer History: deterministic profile generation
- Fraud Rules: all five rules and edge cases
- Explanation: template-based output for various scenarios
"""

import json


# =============================================
# Customer History Server Tests
# =============================================

class TestCustomerHistory:

    def test_deterministic_profile(self):
        """Same customer_id should always produce the same profile."""
        from app.mcp.customer_history_server import _generate_customer_profile

        profile_1 = _generate_customer_profile("CUST_42")
        profile_2 = _generate_customer_profile("CUST_42")

        assert profile_1 == profile_2

    def test_different_customers_different_profiles(self):
        """Different customer_ids should produce different profiles."""
        from app.mcp.customer_history_server import _generate_customer_profile

        profile_a = _generate_customer_profile("CUST_1")
        profile_b = _generate_customer_profile("CUST_999")

        # Extremely unlikely to be identical
        assert profile_a != profile_b

    def test_profile_fields(self):
        """Profile should contain all required fields."""
        from app.mcp.customer_history_server import _generate_customer_profile

        profile = _generate_customer_profile("CUST_100")

        assert "total_transactions" in profile
        assert "average_amount" in profile
        assert "usual_country" in profile
        assert "previous_fraud_flags" in profile
        assert "last_transaction_hours" in profile
        assert "customer_id" in profile

    def test_profile_value_ranges(self):
        """Profile values should be within expected ranges."""
        from app.mcp.customer_history_server import _generate_customer_profile

        profile = _generate_customer_profile("CUST_50")

        assert 50 <= profile["total_transactions"] <= 2000
        assert 50 <= profile["average_amount"] <= 800
        assert profile["usual_country"] in ["Egypt", "Saudi Arabia", "UAE", "Jordan", "Turkey"]
        assert profile["previous_fraud_flags"] >= 0
        assert profile["last_transaction_hours"] >= 0


# =============================================
# Fraud Rules Engine Tests
# =============================================

class TestFraudRules:

    def test_high_amount_rule(self):
        """Amount > 3000 should trigger high_amount rule."""
        from app.mcp.fraud_rules_server import _apply_rules

        result = _apply_rules(
            {"amount": 5000, "country": "Egypt"},
            {"average_amount": 200, "usual_country": "Egypt",
             "previous_fraud_flags": 0, "last_transaction_hours": 10}
        )

        assert "high_amount" in result["triggered_rules"]
        assert result["risk_score"] >= 20

    def test_foreign_country_rule(self):
        """Country mismatch should trigger foreign_country rule."""
        from app.mcp.fraud_rules_server import _apply_rules

        result = _apply_rules(
            {"amount": 100, "country": "Russia"},
            {"average_amount": 200, "usual_country": "Egypt",
             "previous_fraud_flags": 0, "last_transaction_hours": 10}
        )

        assert "foreign_country" in result["triggered_rules"]
        assert result["risk_score"] >= 30

    def test_fraud_flags_rule(self):
        """Previous fraud flags should trigger previous_fraud_flags rule."""
        from app.mcp.fraud_rules_server import _apply_rules

        result = _apply_rules(
            {"amount": 100, "country": "Egypt"},
            {"average_amount": 200, "usual_country": "Egypt",
             "previous_fraud_flags": 2, "last_transaction_hours": 10}
        )

        assert "previous_fraud_flags" in result["triggered_rules"]
        assert result["risk_score"] >= 25

    def test_amount_spike_rule(self):
        """Amount > 10x average should trigger amount_spike rule."""
        from app.mcp.fraud_rules_server import _apply_rules

        result = _apply_rules(
            {"amount": 5000, "country": "Egypt"},
            {"average_amount": 200, "usual_country": "Egypt",
             "previous_fraud_flags": 0, "last_transaction_hours": 10}
        )

        assert "amount_spike" in result["triggered_rules"]

    def test_rapid_transactions_rule(self):
        """Last transaction < 1 hour ago should trigger rapid_transactions."""
        from app.mcp.fraud_rules_server import _apply_rules

        result = _apply_rules(
            {"amount": 100, "country": "Egypt"},
            {"average_amount": 200, "usual_country": "Egypt",
             "previous_fraud_flags": 0, "last_transaction_hours": 0.3}
        )

        assert "rapid_transactions" in result["triggered_rules"]
        assert result["risk_score"] >= 10

    def test_no_rules_triggered(self):
        """Normal transaction should trigger no rules."""
        from app.mcp.fraud_rules_server import _apply_rules

        result = _apply_rules(
            {"amount": 100, "country": "Egypt"},
            {"average_amount": 200, "usual_country": "Egypt",
             "previous_fraud_flags": 0, "last_transaction_hours": 10}
        )

        assert result["triggered_rules"] == []
        assert result["risk_score"] == 0

    def test_multiple_rules_combined(self):
        """Multiple violations should accumulate risk."""
        from app.mcp.fraud_rules_server import _apply_rules

        result = _apply_rules(
            {"amount": 5000, "country": "Russia"},
            {"average_amount": 200, "usual_country": "Egypt",
             "previous_fraud_flags": 1, "last_transaction_hours": 0.5}
        )

        # high_amount(20) + foreign_country(30) + fraud_flags(25) +
        # amount_spike(25) + rapid(10) = 110 → capped at 100
        assert result["risk_score"] == 100
        assert len(result["triggered_rules"]) == 5

    def test_risk_score_capped_at_100(self):
        """Risk score should never exceed 100."""
        from app.mcp.fraud_rules_server import _apply_rules

        result = _apply_rules(
            {"amount": 50000, "country": "Nigeria"},
            {"average_amount": 10, "usual_country": "Egypt",
             "previous_fraud_flags": 5, "last_transaction_hours": 0.1}
        )

        assert result["risk_score"] <= 100


# =============================================
# Explanation Service Tests
# =============================================

class TestExplanation:

    def test_amount_anomaly_explanation(self):
        """Should mention amount multiplier in explanation."""
        from app.mcp.explanation_server import _generate_explanation

        explanation = _generate_explanation(
            {"amount": 5000, "country": "Egypt"},
            {"average_amount": 200, "usual_country": "Egypt",
             "previous_fraud_flags": 0, "last_transaction_hours": 10},
            score=0.85
        )

        assert "5,000" in explanation or "5000" in explanation
        assert "25.0x" in explanation or "25x" in explanation or "average" in explanation

    def test_geographic_anomaly_explanation(self):
        """Should mention country mismatch."""
        from app.mcp.explanation_server import _generate_explanation

        explanation = _generate_explanation(
            {"amount": 100, "country": "Russia"},
            {"average_amount": 200, "usual_country": "Egypt",
             "previous_fraud_flags": 0, "last_transaction_hours": 10},
            score=0.70
        )

        assert "Russia" in explanation
        assert "Egypt" in explanation

    def test_clean_transaction_explanation(self):
        """Normal transactions should get a clean explanation."""
        from app.mcp.explanation_server import _generate_explanation

        explanation = _generate_explanation(
            {"amount": 100, "country": "Egypt"},
            {"average_amount": 200, "usual_country": "Egypt",
             "previous_fraud_flags": 0, "last_transaction_hours": 10},
            score=0.15
        )

        assert "normal" in explanation.lower() or "no anomalies" in explanation.lower()

    def test_declined_decision_label(self):
        """High risk score should show DECLINED label."""
        from app.mcp.explanation_server import _generate_explanation

        explanation = _generate_explanation(
            {"amount": 5000, "country": "Russia"},
            {"average_amount": 200, "usual_country": "Egypt",
             "previous_fraud_flags": 0, "last_transaction_hours": 10},
            score=0.90
        )

        assert "DECLINED" in explanation

"""
Great Expectations validation for operational transaction data.
Run: python great_expectations/validate_data.py
"""

from __future__ import annotations

import os
import sys

import pandas as pd
from sqlalchemy import create_engine, text


def _db_url() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "password")
    db = os.getenv("POSTGRES_DB", "payment_scoring")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def validate() -> bool:
    try:
        import great_expectations as gx
    except ImportError:
        print("great_expectations not installed; skipping validation")
        return True

    engine = create_engine(_db_url())
    with engine.connect() as conn:
        if not conn.execute(text(
            "SELECT to_regclass('public.scored_transactions')"
        )).scalar():
            print("Table scored_transactions not found; skipping")
            return True
        df = pd.read_sql("SELECT * FROM scored_transactions LIMIT 10000", conn)

    if df.empty:
        print("No data to validate yet")
        return True

    context = gx.get_context(mode="ephemeral")
    validator = context.sources.pandas_default.read_dataframe(df)

    validator.expect_table_row_count_to_be_between(min_value=1)
    validator.expect_column_values_to_not_be_null("transaction_id")
    validator.expect_column_values_to_be_unique("transaction_id")
    validator.expect_column_values_to_be_between("score", min_value=0, max_value=1)
    validator.expect_column_values_to_be_in_set(
        "status", value_set=["APPROVED", "REVIEW", "DECLINED"]
    )

    result = validator.validate()
    success = result.success
    print(f"Great Expectations validation: {'PASSED' if success else 'FAILED'}")
    if not success:
        for r in result.results:
            if not r.success:
                print(f"  FAILED: {r.expectation_config.type}")
    return success


if __name__ == "__main__":
    ok = validate()
    sys.exit(0 if ok else 1)

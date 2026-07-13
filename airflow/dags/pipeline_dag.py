from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


def validate_with_great_expectations():
    import sys
    sys.path.insert(0, "/opt/airflow")
    from great_expectations.validate_data import validate
    if not validate():
        raise RuntimeError("Great Expectations validation failed")


with DAG(
    dag_id="fraud_platform_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule_interval=timedelta(hours=1),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["fraud", "dbt", "ml", "validation"],
) as dag:

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command="cd /opt/airflow/dbt && dbt deps --profiles-dir .",
    )

    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command="cd /opt/airflow/dbt && dbt seed --profiles-dir .",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run --profiles-dir .",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test --profiles-dir .",
    )

    validate_data = PythonOperator(
        task_id="great_expectations_validate",
        python_callable=validate_with_great_expectations,
    )

    train_model = BashOperator(
        task_id="train_fraud_model",
        bash_command="cd /opt/airflow && python ml/train_model.py",
    )

    reporting = BashOperator(
        task_id="generate_reporting_snapshot",
        bash_command=(
            "psql postgresql://postgres:password@postgres:5432/payment_scoring -c "
            "\"SELECT status, COUNT(*) FROM scored_transactions GROUP BY status;\""
        ),
    )

    dbt_deps >> dbt_seed >> dbt_run >> dbt_test >> validate_data >> train_model >> reporting

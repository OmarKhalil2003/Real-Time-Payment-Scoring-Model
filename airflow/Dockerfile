FROM apache/airflow:2.9.3-python3.10

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl postgresql-client \
    && rm -rf /var/lib/apt/lists/*

USER airflow

RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres==5.12.0 \
    apache-airflow-providers-docker==3.12.0 \
    dbt-core==1.8.6 \
    dbt-postgres==1.8.2 \
    psycopg2-binary==2.9.9 \
    great-expectations==0.18.19 \
    xgboost==2.0.3 \
    scikit-learn==1.3.2 \
    joblib==1.3.2 \
    pandas==2.1.4

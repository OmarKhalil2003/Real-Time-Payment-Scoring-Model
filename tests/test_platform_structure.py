def test_dbt_project_parses():
    from pathlib import Path
    assert (Path("dbt") / "dbt_project.yml").exists()
    assert (Path("dbt") / "models" / "marts" / "fact_transactions.sql").exists()


def test_monitoring_configs_exist():
    from pathlib import Path
    assert (Path("monitoring") / "prometheus" / "prometheus.yml").exists()
    assert (Path("monitoring") / "grafana" / "provisioning" / "datasources" / "datasource.yml").exists()

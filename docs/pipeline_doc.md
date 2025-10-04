## Orchestration Prefect / dbt / Power BI

Diagramme de séquence du pipeline quotidien, modélisé en Mermaid :

```mermaid
flowchart TB
    subgraph PrefectCloud["Prefect Cloud (SaaS)\n• Scheduler daily_pipeline @ 02:00\n• Monitoring UI\n• Managed agent queue default"]
        subgraph Flow["Flow run: daily_pipeline.py"]
            Step1["2️⃣ load_csv_to_bigquery()\n→ subprocess.run('python ingest.py')"]
            Step2["3️⃣ run_dbt()\n→ subprocess.run('dbt run')"]
            Step3["4️⃣ run_dbt_tests()\n→ subprocess.run('dbt test')"]
        end
    end

    subgraph dbtCLI["dbt CLI\n• Reads profiles.yml\n• Compiles Jinja → SQL\n• Uses dbt-bigquery adapter"]
    end

    subgraph BigQuery["Google BigQuery\nDatasets\n• raw: viewing_logs, social_interactions\n• analytics: mart_users, mart_content_performance\nExecutes SQL & returns results"]
    end

    PowerBI["Power BI Desktop\n• DirectQuery to BigQuery\n• Displays dashboards"]

    PrefectCloud -->|1️⃣ Triggers flow run| Step1
    Step1 -->|2️⃣ Loads CSV data| BigQuery
    Step1 --> Step2
    Step2 -->|3️⃣ Invokes dbt run| dbtCLI
    Step2 --> Step3
    Step3 -->|4️⃣ Invokes dbt test| dbtCLI
    dbtCLI -->|5️⃣ HTTPS via google-cloud-bigquery| BigQuery
    BigQuery -->|6️⃣ DirectQuery| PowerBI
```

## Architecture globale du POC

Vue d'ensemble des composants (provisionnement, orchestration, stockage et restitution) :

```mermaid
flowchart LR
    subgraph Sources[Sources de données]
        CSV["Fichiers CSV\n(journalier)"]
    end

    subgraph Orchestration[Orchestration]
        PrefectCloud["Prefect Cloud\nScheduler + UI"]
        Flow["Flow daily_pipeline.py\n• ingest.py\n• dbt run\n• dbt test"]
    end

    subgraph Transformation[Transformation]
        dbtProject["Projet dbt\nmodèles + tests"]
    end

    subgraph Stockage["Google Cloud Platform"]
        Raw["BigQuery dataset raw\n(viewing_logs, social_interactions)"]
        Analytics["BigQuery dataset analytics\n(mart_users, mart_content_performance)"]
    end

    subgraph Infra[Infrastructure as Code]
        Terraform["Terraform / OpenTofu\nProvisionne BigQuery + IAM"]
    end

    subgraph Consommation[Consommation]
        PowerBI["Power BI\nDashboards DirectQuery"]
    end

    CSV -->|Ingestion| Flow
    PrefectCloud -->|Planifie et surveille| Flow
    Flow -->|Charge donnees| Raw
    Raw -->|Sources dbt| dbtProject
    Flow -->|Declenche| dbtProject
    dbtProject -->|Materialise| Analytics
    Analytics -->|DirectQuery| PowerBI
    Terraform --> Raw
    Terraform --> Analytics
    Terraform --> PrefectCloud
```

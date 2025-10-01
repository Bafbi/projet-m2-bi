┌──────────────────────────────────────────────────────────────────┐
│                      PREFECT CLOUD (SaaS)                        │
│  - Scheduler : "Lance daily_pipeline tous les jours à 2h"        │
│  - UI de monitoring                                              │
│  - API pour envoyer les instructions aux agents                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ ➊ API Call: "Execute flow X"
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│            AGENT PREFECT (VM Google Cloud / Local)               │
│                                                                  │
│  prefect agent start --work-queue "default"                      │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  FLOW: daily_pipeline.py                                   │  │
│  │                                                            │  │
│  │  1. load_csv_to_bigquery()                                 │  │
│  │     └─➋ subprocess.run(["python", "ingest.py"])            │  │
│  │                                                            │  │
│  │  2. run_dbt()                                              │  │
│  │     └─➌ subprocess.run(["dbt", "run"])                     │  │
│  │                                                            │  │
│  │  3. run_dbt_tests()                                        │  │
│  │     └─➍ subprocess.run(["dbt", "test"])                    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             │ ➌ Exécution de dbt CLI             │
│                             ↓                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  DBT CLI                                                   │  │
│  │  - Lit profiles.yml pour credentials                       │  │
│  │  - Compile les modèles Jinja → SQL                         │  │
│  │  - Utilise dbt-bigquery adapter                            │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               │ ➍ API HTTPS
                               │    (google-cloud-bigquery)
                               ↓
┌──────────────────────────────────────────────────────────────────┐
│                     GOOGLE BIGQUERY (Cloud)                      │
│                                                                  │
│  Dataset: raw                  Dataset: analytics                │
│  └─ viewing_logs              └─ mart_users                      │
│  └─ social_interactions       └─ mart_content_performance        │
│                                                                  │
│  ➎ Exécute le SQL reçu, retourne les résultats                   │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               │ ➏ Connexion DirectQuery
                               ↓
┌──────────────────────────────────────────────────────────────────┐
│                         POWER BI DESKTOP                         │
│  - Se connecte à BigQuery                                        │
│  - Lit les tables marts finales                                  │
│  - Affiche les dashboards                                        │
└──────────────────────────────────────────────────────────────────┘
# Projet M2 BI

This is a project for M2 BI, featuring infrastructure as code using Terraform/OpenTofu for GCP resources and dbt for data transformation.

## Infrastructure deployment

Detailed prerequisites and step-by-step deployment instructions now live in [`infrastructure/README.md`](infrastructure/README.md).

## Usage

- **dbt:** Use the generated `dbt/profiles.yml` for development and production environments.
- **BigQuery:** Access the dev and prod datasets as specified in the Terraform outputs.

### Local environment with uv

- Install [uv](https://docs.astral.sh/uv/getting-started/installation/) to manage the Python environment described by `pyproject.toml` and `uv.lock`.
- Run commands inside the managed environment with `uv run`, which keeps the virtual environment and lockfile in sync automatically. For example:

	```bash
	uv run scripts/generate_profiles.py
	uv run -- dbt debug
	```

- If you prefer to activate the virtual environment manually, first synchronize dependencies and then source `.venv`:

	```bash
	uv sync
	source .venv/bin/activate
	dbt debug
	```

	See the [uv running commands guide](https://docs.astral.sh/uv/guides/projects/#running-commands) for more patterns.

## Notes

- Service account keys are not committed to version control (ignored in `.gitignore`).
- For production deployments, consider using CI/CD pipelines with secure credential management.
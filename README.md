# CS450_Team_Repo
Group contains: Ethan, Ali, Fahd, and Taiwo

# Part two according to GitHub doc
Make a dummy commit for each member
- Can just edit this text doc and "commit changes"
- Ali Afrose (Part 4)
- Ali Afrose (Part 2).
- Taiwo Olawore (commit test)
- Taiwo Olawore (merge test)
- Fahd Laniyan (commit test)

### Quickstart

```bash
# 1) Install pip (Python package manager)
#    macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
#    Windows:     powershell -c "iwr https://astral.sh/uv/install.ps1 -useb | iex"

# 2) Install project + dev deps
pip install -e ".[dev]"

# 3) Enable git hooks
pre-commit install

# 4) Run the CLI // Recently fixed, ignore discord comment
catalog --owner huggingface --repo transformers

# 5) Run checks
pylint src tests
pytest -q


## Here is the Repo Structure
.
├─ src/ai_model_catalog/          # your package (Typer CLI lives here)
│  ├─ __init__.py
│  └─ cli.py
├─ tests/                         # pytest tests
├─ pyproject.toml                 # deps + tool configs
├─ requirements.lock              # optional: pinned lockfile (uv pip compile)
├─ .pre-commit-config.yaml        # git hooks runner
├─ .pylintrc                      # pylint rules (or embed in pyproject)
├─ pytest.ini                     # pytest options
├─ README.md                      # install & usage
├─ .github/workflows/ci.yml       # CI
└─ .env.example                   # sample env vars for GitHub API etc.

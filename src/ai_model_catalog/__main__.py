"""
Entry point for running the package as a module: python -m src.ai_model_catalog
"""

from ai_model_catalog.logging_config import configure_logging
from .cli import app


def main() -> None:
    configure_logging()
    app()


if __name__ == "__main__":
    main()

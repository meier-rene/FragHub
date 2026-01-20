"""Application entry point for the Kedro project."""
from pathlib import Path
from typing import Any

from kedro.config import OmegaConfigLoader
from kedro.framework.context import KedroContext
from kedro.framework.hooks import _create_hook_manager
from kedro.framework.project import settings


class FragHubContext(KedroContext):
    """Kedro context for FragHub project."""

    def _get_pipelines(self) -> dict:
        """Get all pipelines for this project.
        
        Returns:
            A dictionary of pipeline names to Pipeline objects.
        """
        from src.fraghub_pipeline import create_pipeline
        
        return {
            "__default__": create_pipeline(),
            "fraghub": create_pipeline(),
        }


def run_package():
    """Entry point for running the Kedro project as a package."""
    from kedro.framework.session import KedroSession
    
    with KedroSession.create() as session:
        session.run()


if __name__ == "__main__":
    run_package()

#!/usr/bin/env python3
"""
Command-line interface for running FragHub as a Kedro pipeline.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project


def main():
    """Main entry point for running the FragHub Kedro pipeline."""
    
    # Bootstrap the Kedro project
    metadata = bootstrap_project(project_root)
    
    print("=" * 60)
    print("FragHub - Mass Spectrometry Data Processing Pipeline")
    print("Running as Kedro Pipeline")
    print("=" * 60)
    
    # Create and run a Kedro session
    with KedroSession.create(project_path=project_root) as session:
        print("\nStarting pipeline execution...")
        session.run()
        print("\nPipeline execution completed!")
    
    print("=" * 60)
    print("FragHub pipeline finished successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()

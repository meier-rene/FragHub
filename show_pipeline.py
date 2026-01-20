#!/usr/bin/env python3
"""
Simple example to demonstrate the Kedro pipeline structure.
This shows the pipeline nodes without actually running them.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def main():
    """Display the pipeline structure."""
    
    print("=" * 70)
    print("FragHub Kedro Pipeline Structure")
    print("=" * 70)
    print()
    
    # Import the pipeline
    try:
        from src.fraghub_pipeline.pipeline import create_pipeline
        
        pipeline = create_pipeline()
        
        print(f"Total number of nodes: {len(pipeline.nodes)}")
        print()
        print("Pipeline Nodes:")
        print("-" * 70)
        
        for i, node in enumerate(pipeline.nodes, 1):
            print(f"{i:2d}. {node.name}")
            print(f"    Inputs:  {', '.join(str(inp) for inp in node.inputs)}")
            print(f"    Outputs: {', '.join(str(out) for out in node.outputs)}")
            print()
        
        print("=" * 70)
        print("Pipeline structure created successfully!")
        print("=" * 70)
        print()
        print("To run the pipeline:")
        print("  1. Place input files in the INPUT/ directory")
        print("  2. Configure parameters in conf/base/parameters.yml")
        print("  3. Run: python run_kedro.py")
        print()
        
    except Exception as e:
        print(f"Note: Full pipeline initialization requires all dependencies.")
        print(f"Error: {e}")
        print()
        print("Pipeline nodes (as designed):")
        print("-" * 70)
        nodes = [
            "parse_input_files",
            "generate_splash_ids",
            "remove_duplicates",
            "check_updates",
            "clean_spectra",
            "calculate_mols",
            "complete_pubchem",
            "complete_ontologies",
            "de_novo_calculation",
            "normalize_data",
            "split_ion_mode",
            "split_chromatography",
            "split_experimental",
            "convert_to_msp",
            "write_outputs"
        ]
        
        for i, node in enumerate(nodes, 1):
            print(f"{i:2d}. {node}")
        
        print()
        print("=" * 70)
        print("To use the pipeline, install all requirements:")
        print("  pip install -r requirements.txt")
        print("=" * 70)


if __name__ == "__main__":
    main()

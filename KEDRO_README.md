# FragHub Kedro Pipeline

This document describes how to use FragHub as a Kedro pipeline.

## Overview

FragHub has been converted into a modular Kedro pipeline, which provides:
- Clear separation of processing steps
- Reproducible data pipelines
- Easy configuration management
- Parallel execution capabilities
- Better debugging and monitoring

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Install the package in development mode:
```bash
pip install -e .
```

## Project Structure

```
FragHub/
├── conf/
│   └── base/
│       ├── catalog.yml          # Data catalog configuration
│       └── parameters.yml       # Pipeline parameters
├── src/
│   └── fraghub_pipeline/
│       ├── __init__.py
│       ├── nodes.py             # Individual processing nodes
│       ├── pipeline.py          # Pipeline definition
│       ├── run.py              # Application entry point
│       └── settings.py         # Kedro settings
├── data/                        # Data directories (gitignored)
│   ├── 01_raw/
│   ├── 02_intermediate/
│   ├── 03_primary/
│   ├── 04_feature/
│   ├── 05_model_input/
│   ├── 06_models/
│   ├── 07_model_output/
│   └── 08_reporting/
├── INPUT/                       # Input files directory
├── OUTPUT/                      # Output files directory
├── pyproject.toml              # Project configuration
└── run_kedro.py                # CLI entry point
```

## Pipeline Steps

The FragHub pipeline consists of the following steps:

1. **parse_input_files**: Parse MSP, CSV, JSON, or MGF input files
2. **generate_splash_ids**: Generate unique SPLASH identifiers for spectra
3. **remove_duplicates**: Remove duplicate spectra based on SPLASH IDs
4. **check_updates**: Filter previously processed spectra
5. **clean_spectra**: Apply quality filters to spectra
6. **calculate_mols**: Perform molecular derivation and mass calculations
7. **complete_pubchem**: Enrich metadata from PubChem database
8. **complete_ontologies**: Add ontology classifications
9. **de_novo_calculation**: Calculate de novo fragment formulas (optional)
10. **normalize_data**: Normalize missing values
11. **split_ion_mode**: Split by positive/negative ion mode
12. **split_chromatography**: Split by LC/GC chromatography
13. **split_experimental**: Split experimental vs in-silico spectra
14. **convert_to_msp**: Convert to MSP format (optional)
15. **write_outputs**: Write output files in selected formats

## Configuration

### Parameters (`conf/base/parameters.yml`)

Configure pipeline behavior:

```yaml
# Input/Output directories
input_directory: "INPUT"
output_directory: "OUTPUT"

# Processing options
reset_updates: 0.0
calculate_de_novo: 1.0

# Output formats
csv: 1.0
msp: 1.0
json: 1.0

# Filter parameters
minimum_peak_requiered: 3
reduce_peak_list: 100
entropy_score: 0.5
# ... (see file for all parameters)
```

### Data Catalog (`conf/base/catalog.yml`)

Defines data sources and intermediate datasets. The catalog uses pickle format for intermediate data to preserve Python objects.

## Running the Pipeline

### Method 1: Using the CLI script (Recommended)

```bash
python run_kedro.py
```

### Method 2: Using Kedro CLI

```bash
kedro run
```

### Method 3: Using Python directly

```python
from kedro.framework.session import KedroSession
from pathlib import Path

project_path = Path.cwd()

with KedroSession.create(project_path=project_path) as session:
    session.run()
```

## Configuration Customization

You can modify the pipeline behavior by editing configuration files:

1. **Input/Output Directories**: Edit `conf/base/parameters.yml`
2. **Filter Parameters**: Edit `conf/base/parameters.yml`
3. **Data Storage**: Edit `conf/base/catalog.yml`

Example: Change input directory
```yaml
# conf/base/parameters.yml
input_directory: "path/to/your/input"
output_directory: "path/to/your/output"
```

## Running Specific Pipeline Steps

You can run specific nodes or ranges:

```bash
# Run only up to the clean_spectra node
kedro run --to-nodes=clean_spectra

# Run only from split_ion_mode onwards
kedro run --from-nodes=split_ion_mode

# Run only a specific node
kedro run --nodes=calculate_mols
```

## Pipeline Visualization

Generate a pipeline visualization:

```bash
kedro viz
```

This will open an interactive visualization in your browser showing the pipeline structure and data flow.

## Debugging

To see detailed logging:

```bash
kedro run --log-level=DEBUG
```

## Advantages of Kedro Pipeline

1. **Modularity**: Each processing step is isolated and testable
2. **Reproducibility**: Configuration is separated from code
3. **Flexibility**: Easy to modify pipeline without changing code
4. **Debugging**: Run specific steps independently
5. **Monitoring**: Track data lineage and execution
6. **Scalability**: Can be deployed on various platforms (local, cloud, distributed)

## Comparison with Original Implementation

| Feature | Original | Kedro Pipeline |
|---------|----------|----------------|
| Execution | Single monolithic function | Modular nodes |
| Configuration | Hardcoded/GUI | YAML files |
| Data Flow | In-memory passing | Catalog management |
| Debugging | Full re-run | Step-by-step |
| Testing | Difficult | Easy per-node testing |
| Deployment | Local GUI | Multiple platforms |

## Migration Notes

The Kedro pipeline maintains full compatibility with the original FragHub implementation:
- All processing logic remains unchanged
- The same algorithms and filters are used
- Output format is identical
- GUI can still be used with the original `scripts/FragHub.py`

## Troubleshooting

### Issue: Import errors
**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Data not found
**Solution**: Check that INPUT and OUTPUT directories exist and paths in `parameters.yml` are correct

### Issue: Pipeline fails at specific node
**Solution**: Run with debug logging to see detailed error:
```bash
kedro run --log-level=DEBUG
```

## Advanced Usage

### Custom Environments

Create environment-specific configurations:

```bash
mkdir conf/local
cp conf/base/parameters.yml conf/local/
# Edit conf/local/parameters.yml with your settings
kedro run --env=local
```

### Parallel Execution

Some nodes can run in parallel. Configure in `settings.py` or use plugins like `kedro-airflow`.

## Next Steps

- Explore the codebase in `src/fraghub_pipeline/`
- Customize parameters in `conf/base/parameters.yml`
- Run the pipeline with your data
- Visualize the pipeline with `kedro viz` (requires `pip install kedro-viz`)

## Support

For issues or questions about:
- **Kedro functionality**: See [Kedro documentation](https://kedro.readthedocs.io/)
- **FragHub processing**: See main README.md or contact developers

## License

Same as FragHub main project (CeCILL License).

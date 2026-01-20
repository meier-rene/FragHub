# FragHub Kedro Architecture

## Overview

This document describes the architectural design of the FragHub Kedro pipeline conversion.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FragHub Kedro Pipeline                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  INPUT Directory ──► [parse_input_files] ──► parsed_data             │
│                              │                                        │
│                              ▼                                        │
│                    [generate_splash_ids] ──► splash_generated_data   │
│                              │                                        │
│                              ▼                                        │
│                    [remove_duplicates] ──► deduplicated_data         │
│                              │                                        │
│                              ▼                                        │
│                    [check_updates] ──► updated_data (+ update_flag)  │
│                              │                                        │
│                              ▼                                        │
│                    [clean_spectra] ──► cleaned_spectra               │
│                              │                                        │
│                              ▼                                        │
│                    [calculate_mols] ──► calculated_mols              │
│                              │                                        │
│                              ▼                                        │
│                    [complete_pubchem] ──► pubchem_completed          │
│                              │                                        │
│                              ▼                                        │
│                    [complete_ontologies] ──► ontology_completed      │
│                              │                                        │
│                              ▼                                        │
│                    [de_novo_calculation] ──► de_novo_calculated      │
│                              │                                        │
│                              ▼                                        │
│                    [normalize_data] ──► normalized_data              │
│                              │                                        │
│                              ▼                                        │
│                    [split_ion_mode] ──► POS/NEG split               │
│                              │                                        │
│                              ▼                                        │
│                    [split_chromatography] ──► LC/GC split           │
│                              │                                        │
│                              ▼                                        │
│                    [split_experimental] ──► EXP/In-Silico split    │
│                              │                                        │
│                              ▼                                        │
│                    [convert_to_msp] ──► MSP format (optional)       │
│                              │                                        │
│                              ▼                                        │
│                    [write_outputs] ──► OUTPUT Directory              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
FragHub/
├── conf/                          # Kedro configuration
│   └── base/
│       ├── catalog.yml           # Data catalog (datasets)
│       └── parameters.yml        # Pipeline parameters
│
├── src/
│   └── fraghub_pipeline/         # Pipeline source code
│       ├── __init__.py
│       ├── nodes.py              # Individual processing nodes
│       ├── pipeline.py           # Pipeline definition
│       ├── run.py                # Application entry point
│       └── settings.py           # Kedro settings
│
├── data/                          # Data storage (gitignored)
│   ├── 01_raw/                   # Raw input data
│   ├── 02_intermediate/          # Intermediate processing
│   ├── 03_primary/               # Primary datasets
│   ├── 04_feature/               # Feature datasets
│   ├── 05_model_input/           # Model input data
│   ├── 06_models/                # Model data
│   ├── 07_model_output/          # Model outputs
│   └── 08_reporting/             # Final reports
│
├── scripts/                       # Original FragHub code
│   ├── MAIN.py                   # Original processing logic
│   ├── convertors/
│   ├── normalizer/
│   ├── peaks_filters/
│   └── ...                       # Other modules
│
├── INPUT/                         # Input files directory
├── OUTPUT/                        # Output files directory
├── pyproject.toml                # Project configuration
├── run_kedro.py                  # CLI entry point
├── show_pipeline.py              # Pipeline structure display
├── README.md                     # Main documentation
└── KEDRO_README.md               # Kedro-specific docs
```

## Node Design

Each node in the pipeline follows this pattern:

```python
def node_name(inputs: types, params: types) -> outputs:
    """
    Node description.
    
    Args:
        inputs: Input data description
        params: Parameter description
        
    Returns:
        Output data description
    """
    logger.info("Processing step...")
    result = process_data(inputs, params)
    return result
```

### Key Design Principles

1. **Single Responsibility**: Each node performs one specific task
2. **Stateless**: Nodes don't maintain state between runs
3. **Type Hints**: Clear input/output types for documentation
4. **Logging**: Comprehensive logging at each step
5. **Error Handling**: Graceful handling of empty/None data

## Data Flow

### update_flag Propagation

The `update_flag` is a critical piece of state that indicates whether the pipeline is processing new data or updating existing data. It propagates through nodes as follows:

1. **check_updates** node generates `update_flag`
2. Passed as tuple with data: `(spectrum_list, update_flag)`
3. Each subsequent node extracts, uses, and passes it forward
4. **write_outputs** uses it to determine append vs overwrite mode

### Data Format Transitions

1. **Parse** → Dictionary of lists (by file type)
2. **SPLASH** → Same structure with IDs added
3. **Duplicates** → Single pandas DataFrame
4. **Cleaning** → Filtered DataFrame
5. **Splitting** → Multiple DataFrames (by category)
6. **MSP** → MSP-formatted strings (optional)
7. **Write** → Files on disk

## Configuration

### Parameters (parameters.yml)

Controls pipeline behavior:
- Input/output directories
- Filter thresholds
- Output format flags
- Processing options

### Catalog (catalog.yml)

Defines datasets:
- Format (pickle, CSV, JSON, etc.)
- Storage location
- Load/save arguments

## Extensibility

### Adding New Nodes

1. Create function in `src/fraghub_pipeline/nodes.py`
2. Add to pipeline in `src/fraghub_pipeline/pipeline.py`
3. Update catalog if needed in `conf/base/catalog.yml`

### Adding Parameters

1. Add to `conf/base/parameters.yml`
2. Reference in node: `inputs="params:your_param"`

### Custom Data Storage

1. Edit `conf/base/catalog.yml`
2. Specify dataset type and location
3. Kedro handles serialization automatically

## Comparison: Original vs Kedro

| Aspect | Original | Kedro Pipeline |
|--------|----------|---------------|
| **Execution** | Single function | Modular nodes |
| **State** | In-memory passing | Catalog management |
| **Configuration** | GUI/parameters_dict | YAML files |
| **Debugging** | Full re-run | Node-by-node |
| **Logging** | Print statements | Structured logging |
| **Testing** | Difficult | Unit testable |
| **Monitoring** | Limited | Built-in tracking |
| **Deployment** | Local only | Multiple platforms |
| **Parallelization** | Manual | Automatic (potential) |
| **Reproducibility** | Version control | Config + code versioning |

## Benefits of Kedro Architecture

1. **Modularity**: Independent, testable components
2. **Reproducibility**: Configuration separated from code
3. **Flexibility**: Easy to modify pipeline structure
4. **Debugging**: Run and debug individual nodes
5. **Monitoring**: Track data lineage and execution
6. **Scalability**: Can be deployed on various platforms
7. **Collaboration**: Clear structure for team development
8. **Documentation**: Self-documenting pipeline structure

## Integration with Original Code

The Kedro pipeline **wraps** the original FragHub code:
- Original functions remain unchanged
- Nodes call existing processing functions
- No duplication of business logic
- GUI application still functional

This means:
- Both implementations can coexist
- Easy to maintain consistency
- Gradual migration possible
- Original code can still be used directly

## Performance Considerations

### Intermediate Data Storage

- Uses pickle format for Python objects
- Enables restart from any point
- Trade-off: disk space vs memory
- Can be configured per dataset

### Parallelization Potential

While not implemented in this version, Kedro supports:
- Parallel node execution
- Distributed computing (with plugins)
- Cloud deployment (AWS, GCP, Azure)

## Future Enhancements

Possible extensions:
1. Add unit tests for each node
2. Implement parallel execution
3. Add data validation layers
4. Create custom dataset types
5. Add pipeline visualization (kedro-viz)
6. Implement CI/CD integration
7. Add experiment tracking
8. Create Docker containerization

## Maintenance

### Updating Processing Logic

1. Modify functions in `scripts/` directory
2. Kedro nodes automatically use updated code
3. No changes needed to pipeline structure

### Updating Pipeline Structure

1. Edit `src/fraghub_pipeline/pipeline.py`
2. Add/remove/reorder nodes as needed
3. Update catalog if new datasets required

### Configuration Changes

1. Edit YAML files in `conf/base/`
2. No code changes needed
3. Version control configuration separately

## Support and Resources

- **Kedro Documentation**: https://kedro.readthedocs.io/
- **FragHub Original**: See main README.md
- **Kedro Usage**: See KEDRO_README.md
- **Issue Reporting**: GitHub Issues

## Conclusion

The Kedro pipeline architecture provides a robust, scalable, and maintainable framework for FragHub's mass spectrometry data processing workflow, while preserving all original functionality and allowing for future growth and enhancement.

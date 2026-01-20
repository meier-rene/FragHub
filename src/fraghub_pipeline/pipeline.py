"""
FragHub Kedro Pipeline Definition.
This pipeline orchestrates the mass spectrometry data processing workflow.
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    parse_input_files_node,
    generate_splash_ids_node,
    remove_duplicates_node,
    check_updates_node,
    clean_spectra_node,
    calculate_mols_node,
    complete_pubchem_node,
    complete_ontologies_node,
    de_novo_calculation_node,
    normalize_data_node,
    split_ion_mode_node,
    split_chromatography_node,
    split_experimental_node,
    convert_to_msp_node,
    write_outputs_node,
)


def create_pipeline(**kwargs) -> Pipeline:
    """
    Create the FragHub processing pipeline.
    
    Returns:
        A Kedro Pipeline object containing all processing steps
    """
    return pipeline([
        # Step 1: Parse input files
        node(
            func=parse_input_files_node,
            inputs="params:input_directory",
            outputs="parsed_data",
            name="parse_input_files",
        ),
        
        # Step 2: Generate SPLASH IDs
        node(
            func=generate_splash_ids_node,
            inputs="parsed_data",
            outputs="splash_generated_data",
            name="generate_splash_ids",
        ),
        
        # Step 3: Remove duplicates
        node(
            func=remove_duplicates_node,
            inputs=["splash_generated_data", "params:output_directory"],
            outputs="deduplicated_data",
            name="remove_duplicates",
        ),
        
        # Step 4: Check for updates
        node(
            func=check_updates_node,
            inputs=["deduplicated_data", "params:output_directory"],
            outputs="updated_data",
            name="check_updates",
        ),
        
        # Step 5: Clean spectra
        node(
            func=clean_spectra_node,
            inputs=["updated_data", "params:output_directory"],
            outputs="cleaned_spectra",
            name="clean_spectra",
        ),
        
        # Step 6: Calculate molecular properties
        node(
            func=calculate_mols_node,
            inputs=["cleaned_spectra", "params:output_directory"],
            outputs="calculated_mols",
            name="calculate_mols",
        ),
        
        # Step 7: Complete from PubChem
        node(
            func=complete_pubchem_node,
            inputs="calculated_mols",
            outputs="pubchem_completed",
            name="complete_pubchem",
        ),
        
        # Step 8: Complete ontologies
        node(
            func=complete_ontologies_node,
            inputs="pubchem_completed",
            outputs="ontology_completed",
            name="complete_ontologies",
        ),
        
        # Step 9: De novo calculation (conditional)
        node(
            func=de_novo_calculation_node,
            inputs=["ontology_completed", "params:calculate_de_novo"],
            outputs="de_novo_calculated",
            name="de_novo_calculation",
        ),
        
        # Step 10: Normalize data
        node(
            func=normalize_data_node,
            inputs="de_novo_calculated",
            outputs="normalized_data",
            name="normalize_data",
        ),
        
        # Step 11: Split by ion mode
        node(
            func=split_ion_mode_node,
            inputs="normalized_data",
            outputs="pos_neg_split",
            name="split_ion_mode",
        ),
        
        # Step 12: Split by chromatography
        node(
            func=split_chromatography_node,
            inputs="pos_neg_split",
            outputs="lc_gc_split",
            name="split_chromatography",
        ),
        
        # Step 13: Split experimental vs in-silico
        node(
            func=split_experimental_node,
            inputs="lc_gc_split",
            outputs="exp_insilico_split",
            name="split_experimental",
        ),
        
        # Step 14: Convert to MSP (conditional)
        node(
            func=convert_to_msp_node,
            inputs=["exp_insilico_split", "params:msp"],
            outputs="msp_converted",
            name="convert_to_msp",
        ),
        
        # Step 15: Write outputs
        node(
            func=write_outputs_node,
            inputs={
                "exp_split": "exp_insilico_split",
                "msp_data": "msp_converted",
                "output_directory": "params:output_directory",
                "csv_enabled": "params:csv",
                "msp_enabled": "params:msp",
                "json_enabled": "params:json",
                "reset_updates": "params:reset_updates",
            },
            outputs="output_status",
            name="write_outputs",
        ),
    ])

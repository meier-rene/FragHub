"""
Kedro nodes for FragHub pipeline.
These nodes wrap the existing FragHub processing functions.
"""

from scripts.convertors.parsing_to_dict import parsing_to_dict
from scripts.splash_generator import generate_splash_id
from scripts.duplicatas_remover import remove_duplicatas
from scripts.update import check_for_update_processing
from scripts.spectrum_normalizer import spectrum_cleaning_processing
from scripts.normalizer.mols_calculation import mols_derivation_and_calculation
from scripts.complete_from_pubchem_datas import complete_from_pubchem_datas
from scripts.ontologies_completion import ontologies_completion
from scripts.de_novo_calculation import de_novo_calculation
from scripts.normalize_to_not_found import normalize_to_not_found
from scripts.splitter import split_pos_neg, split_LC_GC, exp_in_silico_splitter
from scripts.convertors.csv_to_msp import csv_to_msp
from scripts.writers import writting_csv, writting_msp, writting_json
from scripts.report import report
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Define ordered columns as in MAIN.py
ordered_columns = ["FILENAME",
                   "FILEHASH",
                   "PREDICTED",
                   "SPLASH",
                   "SPECTRUMID",
                   "RESOLUTION",
                   "SYNON",
                   "IONIZATION",
                   "MSLEVEL",
                   "FRAGMENTATIONMODE",
                   "NAME",
                   "PRECURSORMZ",
                   "EXACTMASS",
                   "AVERAGEMASS",
                   "PRECURSORTYPE",
                   "INSTRUMENTTYPE",
                   "INSTRUMENT",
                   "SMILES",
                   "INCHI",
                   "INCHIKEY",
                   "COLLISIONENERGY",
                   "FORMULA",
                   "RT",
                   "IONMODE",
                   "COMMENT",
                   "ENTROPY",
                   "CLASSYFIRE_SUPERCLASS",
                   "CLASSYFIRE_CLASS",
                   "CLASSYFIRE_SUBCLASS",
                   "NPCLASS_PATHWAY",
                   "NPCLASS_SUPERCLASS",
                   "NPCLASS_CLASS",
                   "NUM PEAKS",
                   "PEAKS_LIST"]


def parse_input_files_node(input_directory: str) -> dict:
    """
    Node 1: Parse input files to dictionary format.
    
    Args:
        input_directory: Path to input directory containing MSP, CSV, JSON, or MGF files
        
    Returns:
        Dictionary containing parsed data from different file formats
    """
    logger.info(f"Parsing input files from: {input_directory}")
    FINAL_MSP, FINAL_CSV, FINAL_JSON, FINAL_MGF = parsing_to_dict(input_directory)
    
    return {
        'FINAL_MSP': FINAL_MSP,
        'FINAL_CSV': FINAL_CSV,
        'FINAL_JSON': FINAL_JSON,
        'FINAL_MGF': FINAL_MGF
    }


def generate_splash_ids_node(parsed_data: dict) -> dict:
    """
    Node 2: Generate SPLASH unique IDs for spectra.
    
    Args:
        parsed_data: Dictionary containing parsed data
        
    Returns:
        Dictionary with SPLASH IDs generated
    """
    logger.info("Generating SPLASH unique IDs")
    FINAL_MSP, FINAL_CSV, FINAL_JSON, FINAL_MGF = generate_splash_id(
        parsed_data['FINAL_MSP'], 
        parsed_data['FINAL_CSV'], 
        parsed_data['FINAL_JSON'], 
        parsed_data['FINAL_MGF']
    )
    
    return {
        'FINAL_MSP': FINAL_MSP,
        'FINAL_CSV': FINAL_CSV,
        'FINAL_JSON': FINAL_JSON,
        'FINAL_MGF': FINAL_MGF
    }


def remove_duplicates_node(splash_data: dict, output_directory: str) -> pd.DataFrame:
    """
    Node 3: Remove duplicate spectra based on SPLASH IDs.
    
    Args:
        splash_data: Dictionary containing data with SPLASH IDs
        output_directory: Path to output directory
        
    Returns:
        DataFrame with duplicates removed
    """
    logger.info("Removing duplicates")
    
    # Combine all data into a single list
    spectrum_list = []
    spectrum_list.extend(splash_data['FINAL_MSP'])
    spectrum_list.extend(splash_data['FINAL_CSV'])
    spectrum_list.extend(splash_data['FINAL_JSON'])
    spectrum_list.extend(splash_data['FINAL_MGF'])
    
    # Convert to DataFrame
    spectrum_list = pd.DataFrame(spectrum_list)[ordered_columns]
    spectrum_list = spectrum_list.astype({col: str for col in ordered_columns if col != 'PEAKS_LIST'})
    
    # Remove duplicates
    spectrum_list = remove_duplicatas(spectrum_list, output_directory)
    
    return spectrum_list


def check_updates_node(spectrum_list: pd.DataFrame, output_directory: str) -> tuple:
    """
    Node 4: Check for previously processed spectra and filter updates.
    
    Args:
        spectrum_list: DataFrame containing spectra
        output_directory: Path to output directory
        
    Returns:
        Tuple of (filtered spectrum list, update flag)
    """
    logger.info("Checking for updates")
    spectrum_list, update_flag = check_for_update_processing(spectrum_list, output_directory)
    
    return spectrum_list, update_flag


def clean_spectra_node(update_data: tuple, output_directory: str) -> pd.DataFrame:
    """
    Node 5: Clean and filter spectra based on quality criteria.
    
    Args:
        update_data: Tuple containing (spectrum_list, update_flag)
        output_directory: Path to output directory
        
    Returns:
        DataFrame with cleaned spectra
    """
    spectrum_list, update_flag = update_data
    
    if spectrum_list is None or len(spectrum_list) == 0:
        logger.warning("No spectra to clean")
        return None
    
    logger.info("Cleaning spectra")
    spectrum_list = spectrum_cleaning_processing(spectrum_list, output_directory)
    
    if spectrum_list is None or len(spectrum_list) == 0:
        logger.warning("No spectra remaining after cleaning")
        return None
    
    return pd.DataFrame(spectrum_list)[ordered_columns].astype(str)


def calculate_mols_node(spectrum_list: pd.DataFrame, output_directory: str) -> pd.DataFrame:
    """
    Node 6: Perform molecular derivation and mass calculations.
    
    Args:
        spectrum_list: DataFrame containing cleaned spectra
        output_directory: Path to output directory
        
    Returns:
        DataFrame with calculated molecular properties
    """
    if spectrum_list is None:
        return None
        
    logger.info("Calculating molecular properties")
    spectrum_list = mols_derivation_and_calculation(spectrum_list, output_directory)
    
    return spectrum_list


def complete_pubchem_node(spectrum_list: pd.DataFrame) -> pd.DataFrame:
    """
    Node 7: Complete missing metadata from PubChem database.
    
    Args:
        spectrum_list: DataFrame containing spectra
        
    Returns:
        DataFrame with completed metadata from PubChem
    """
    if spectrum_list is None:
        return None
        
    logger.info("Completing from PubChem data")
    spectrum_list = complete_from_pubchem_datas(spectrum_list)
    
    return spectrum_list


def complete_ontologies_node(spectrum_list: pd.DataFrame) -> pd.DataFrame:
    """
    Node 8: Complete ontology classifications.
    
    Args:
        spectrum_list: DataFrame containing spectra
        
    Returns:
        DataFrame with completed ontologies
    """
    if spectrum_list is None:
        return None
        
    logger.info("Completing ontologies")
    spectrum_list = ontologies_completion(spectrum_list)
    
    return spectrum_list


def de_novo_calculation_node(spectrum_list: pd.DataFrame, calculate_de_novo: float) -> pd.DataFrame:
    """
    Node 9: Perform de novo fragment formula calculations (conditional).
    
    Args:
        spectrum_list: DataFrame containing spectra
        calculate_de_novo: Flag to enable/disable de novo calculation
        
    Returns:
        DataFrame with de novo calculations (if enabled)
    """
    if spectrum_list is None:
        return None
        
    if calculate_de_novo == 1.0:
        logger.info("Performing de novo calculations")
        spectrum_list = de_novo_calculation(spectrum_list)
    else:
        logger.info("Skipping de novo calculations")
    
    return spectrum_list


def normalize_data_node(spectrum_list: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize data to handle 'not found' values.
    
    Args:
        spectrum_list: DataFrame containing spectra
        
    Returns:
        Normalized DataFrame
    """
    if spectrum_list is None:
        return None
        
    logger.info("Normalizing data")
    spectrum_list = normalize_to_not_found(spectrum_list)
    
    return spectrum_list


def split_ion_mode_node(spectrum_list: pd.DataFrame) -> tuple:
    """
    Node 10: Split spectra by ion mode (Positive/Negative).
    
    Args:
        spectrum_list: DataFrame containing all spectra
        
    Returns:
        Tuple of (POS_df, NEG_df)
    """
    if spectrum_list is None:
        return None, None
        
    logger.info("Splitting by ion mode (POS/NEG)")
    POS_df, NEG_df = split_pos_neg(spectrum_list)
    
    return POS_df, NEG_df


def split_chromatography_node(ion_split: tuple) -> tuple:
    """
    Node 11: Split spectra by chromatography type (LC/GC).
    
    Args:
        ion_split: Tuple of (POS_df, NEG_df)
        
    Returns:
        Tuple of (POS_LC_df, POS_GC_df, NEG_LC_df, NEG_GC_df)
    """
    POS_df, NEG_df = ion_split
    
    if POS_df is None and NEG_df is None:
        return None, None, None, None
        
    logger.info("Splitting by chromatography (LC/GC)")
    POS_LC_df, POS_GC_df, NEG_LC_df, NEG_GC_df = split_LC_GC(POS_df, NEG_df)
    
    return POS_LC_df, POS_GC_df, NEG_LC_df, NEG_GC_df


def split_experimental_node(lc_gc_split: tuple) -> tuple:
    """
    Node 12: Split spectra by experimental vs in-silico.
    
    Args:
        lc_gc_split: Tuple of (POS_LC_df, POS_GC_df, NEG_LC_df, NEG_GC_df)
        
    Returns:
        Tuple of 8 DataFrames (experimental and in-silico for each combination)
    """
    POS_LC_df, POS_GC_df, NEG_LC_df, NEG_GC_df = lc_gc_split
    
    if all(df is None for df in [POS_LC_df, POS_GC_df, NEG_LC_df, NEG_GC_df]):
        return (None,) * 8
        
    logger.info("Splitting experimental vs in-silico")
    result = exp_in_silico_splitter(POS_LC_df, POS_GC_df, NEG_LC_df, NEG_GC_df)
    
    return result


def convert_to_msp_node(exp_split: tuple, msp_enabled: float) -> tuple:
    """
    Node 13: Convert CSV data to MSP format (conditional).
    
    Args:
        exp_split: Tuple of 8 DataFrames from experimental split
        msp_enabled: Flag to enable/disable MSP conversion
        
    Returns:
        Tuple of 8 MSP-formatted data structures (if enabled)
    """
    if all(df is None for df in exp_split):
        return (None,) * 8
        
    if msp_enabled == 1.0:
        logger.info("Converting to MSP format")
        result = csv_to_msp(*exp_split)
        return result
    else:
        logger.info("Skipping MSP conversion")
        return (None,) * 8


def write_outputs_node(
    exp_split: tuple,
    msp_data: tuple,
    output_directory: str,
    update_flag: bool,
    csv_enabled: float,
    msp_enabled: float,
    json_enabled: float
) -> dict:
    """
    Node 14: Write output files in requested formats.
    
    Args:
        exp_split: Tuple of 8 DataFrames
        msp_data: Tuple of 8 MSP-formatted data
        output_directory: Path to output directory
        update_flag: Whether this is an update operation
        csv_enabled: Flag to enable CSV output
        msp_enabled: Flag to enable MSP output
        json_enabled: Flag to enable JSON output
        
    Returns:
        Dictionary with output status
    """
    (POS_LC_df, POS_LC_In_Silico_df, POS_GC_df, POS_GC_In_Silico_df,
     NEG_LC_df, NEG_LC_In_Silico_df, NEG_GC_df, NEG_GC_In_Silico_df) = exp_split
    
    if all(df is None for df in exp_split):
        logger.warning("No data to write")
        return {"status": "no_data"}
    
    # Write CSV
    if csv_enabled == 1.0:
        logger.info("Writing CSV files")
        writting_csv(
            POS_LC_df, POS_GC_df, NEG_LC_df, NEG_GC_df,
            POS_LC_In_Silico_df, POS_GC_In_Silico_df,
            NEG_LC_In_Silico_df, NEG_GC_In_Silico_df,
            output_directory, update_flag
        )
    
    # Write MSP
    if msp_enabled == 1.0 and msp_data is not None:
        logger.info("Writing MSP files")
        (POS_LC, POS_LC_insilico, POS_GC, POS_GC_insilico,
         NEG_LC, NEG_LC_insilico, NEG_GC, NEG_GC_insilico) = msp_data
        writting_msp(
            POS_LC, POS_LC_insilico, POS_GC, POS_GC_insilico,
            NEG_LC, NEG_LC_insilico, NEG_GC, NEG_GC_insilico,
            output_directory, update_flag
        )
    
    # Write JSON
    if json_enabled == 1.0:
        logger.info("Writing JSON files")
        writting_json(
            update_flag,
            POS_LC_df, POS_GC_df, NEG_LC_df, NEG_GC_df,
            POS_LC_In_Silico_df, POS_GC_In_Silico_df,
            NEG_LC_In_Silico_df, NEG_GC_In_Silico_df,
            output_directory
        )
    
    # Generate report
    logger.info("Generating report")
    report(
        output_directory,
        POS_LC_df, POS_LC_In_Silico_df, POS_GC_df, POS_GC_In_Silico_df,
        NEG_LC_df, NEG_LC_In_Silico_df, NEG_GC_df, NEG_GC_In_Silico_df
    )
    
    return {"status": "complete"}

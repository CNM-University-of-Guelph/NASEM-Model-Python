"""
Add the code below to the end of the "NRC Dairy 2020 Model Fn" script in R 
(Line 3338) to create a JSON file. Then run the create_end_to_end_json.py 
and pass the JSON file from R to create a new JSON file formatted to run an 
end to end test.  

library(jsonlite)
var_names <- ls()
var_values <- mget(var_names)
json_data <- toJSON(var_values, pretty = TRUE)
write(json_data, file="R_values.json")
"""

import argparse
import json
import os
from typing import Tuple, Dict, Union, List

import numpy as np
import pandas as pd

import nasem_dairy.ration_balancer.default_values_dictionaries as constants


####################
# Define Functions
####################
def load_R_json(R_json_path: str) -> Tuple[Dict, Dict]:
    with open(R_json_path, "r") as file:
        data = json.load(file)

    variables_to_extract = ["efficiency_input", "f", "i", "f_Imb"]    
    dictionaries = {}
    r_data = {}

    for variable, value in data.items():
        if variable in variables_to_extract:
            dictionaries[variable] = value
        elif isinstance(value, list):
            if len(value) == 1:
                if isinstance(value[0], (int, float)):
                    r_data[variable] = float(value[0])
                elif isinstance(value[0], str):
                    r_data[variable] = value[0]
        else:
            r_data[variable] = value
    return dictionaries, r_data


def check_input_length(r_json_path: Union[List[str], str], 
                       test_name: Union[List[str], str]
) -> bool:
    return bool(len(r_json_path) == len(test_name))


def find_project_root(start_path: str, root_dir_name: str="NASEM-Model-Python"
) -> str:
    current_path = start_path
    while True:
        if os.path.basename(current_path) == root_dir_name:
            return current_path
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            raise FileNotFoundError(
                f"Project root directory {root_dir_name} not found.")
        current_path = parent_path


def update_file_names(test_name: str, add_to_tests: bool) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = find_project_root(script_dir, "NASEM-Model-Python")
    if add_to_tests:
        integration_dir = os.path.join(project_root, "tests", "integration")
        return [
            os.path.join(integration_dir, name + ".json") for name in test_name
        ]
    else:
        return [os.path.join(script_dir, name + ".json") for name in test_name]


def get_user_diet(dictionaries: dict, r_data: dict) -> dict:
    user_diet = {}
    Trg_Dt_DMIn = r_data["Trg_Dt_DMIn"]
    feed_input = dictionaries["f"]
    for feed in feed_input:
        user_diet[feed["Fd_Name"]] = Trg_Dt_DMIn * (feed["Fd_DMInp"] / 100)
    return user_diet


def get_animal_input(r_data: dict) -> Union[Dict, Dict]:
    animal_input_variables = [
        "An_Parity_rl", "Trg_MilkProd", "An_BW", "An_BCS", "An_LactDay",
        "Trg_MilkFatp", "Trg_MilkTPp", "Trg_MilkLacp", "Trg_Dt_DMIn",
        "An_BW_mature", "Trg_FrmGain", "An_GestDay", "An_GestLength",
        "Trg_RsrvGain", "Fet_BWbrth", "An_AgeDay", "An_305RHA_MlkTP",
        "An_StatePhys", "An_Breed", "An_AgeDryFdStart", "Env_TempCurr",
        "Env_DistParlor", "Env_TripsParlor", "Env_Topo"
    ]
    animal_input_in = {}
    for key in animal_input_variables:
        value = r_data.pop(key, None)
        if key == "Trg_Dt_DMIn":
            animal_input_in["DMI"] = value
        else:
            animal_input_in[key] = value
    return animal_input_in, r_data


def get_equation_selection(r_data: dict) -> Union[Dict, Dict]:
    equation_selection_variables = [
        "Use_DNDF_IV", "DMIn_eqn", "mProd_eqn", "MiN_eqn", "NonMilkCP_ClfLiq",
        "Monensin_eqn", "mPrt_eqn", "mFat_eqn", "RumDevDisc_Clf"
    ]
    equation_selection_in = {}
    for key in equation_selection_variables:
        equation_selection_in[key] = r_data.pop(key)
    return equation_selection_in, r_data


def create_AA_values(r_data: dict) -> Union[pd.DataFrame, Dict]:
    AA_list = [
        "Arg", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Thr", "Trp", "Val"
    ]
    columns = [
        "Du_AAMic", "Du_IdAAMic", "Du_AAEndP", "Du_AA", "DuAA_DtAA", "Du_AA24h",
        "Abs_AA_g", "mPrtmx_AA", "mPrtmx_AA2", "AA_mPrtmx", "mPrt_AA_0.1",
        "mPrt_k_AA", "IdAA_DtAA", "Abs_AA_MPp", "Abs_AA_p", "Abs_AA_DEI",
        "Abs_AA_mol", "Mlk_AA_g", "MlkAA_AbsAA", "MlkAA_DtAA", "Gest_AA_g",
        "GestAA_AbsAA", "Body_AAGain_g", "BodyAA_AbsAA", "An_AAUse_g",
        "AnAAUse_AbsAA", "An_AABal_g", "An_AAEff_EAAEff", "Imb_AA",
        "Trg_Mlk_AA_g", "Trg_AAUse_g", "Trg_AbsAA_g", "MlkNP_AbsAA",
        "AnNPxAA_AbsAA", "AnNPxAAUser_AbsAA"
    ]
    AA_values = {}
    for column in columns:
        AA_values[column] = []
        for AA in AA_list:
            parts = column.split("EAA")
            new_key = "EAA".join([part.replace("AA", AA) for part in parts])
            value = r_data.pop(new_key, None)
            AA_values[column].append(value)
    return AA_values, r_data


def create_arrays(r_data: dict) -> Union[Dict, Dict]:
    AA_list = [
        "Arg", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Thr", "Trp", "Val"
    ]
    array_names = [
        "Fe_AAMet_AbsAA", "Ur_AAEnd_AbsAA", "ScrfAA_AbsAA", "Fe_AAMet_g",
        "Ur_AAEnd_g", "Scrf_AA_g", "Trg_AbsAA_NPxprtAA", "Trg_AAEff_EAAEff"
    ]
    arrays = {}
    for name in array_names:
        arrays[name] = []
        for AA in AA_list:
            parts = name.split("EAA")
            new_key = "EAA".join([part.replace("AA", AA) for part in parts])
            value = r_data.pop(new_key, np.nan)
            arrays[name].append(value)
    return arrays, r_data


def get_constants(r_data: dict, mPrt_eqn: int, dictionaries: dict) -> dict:
    input_coeff_dict = {
        key: r_data.pop(key, None) for key in constants.coeff_dict.keys()
        }
    input_coeff_dict["Fd_dcrOM"] = 96 # This constant gets added to feed array in R
    
    r_MP_NP_efficiency = dictionaries["efficiency_input"][0]
    input_MP_NP_efficiency_dict = {
        key: r_MP_NP_efficiency.pop(key, None) 
        for key in constants.MP_NP_efficiency_dict.keys()
        }
    
    input_mPrt_coeff_list = constants.mPrt_coeff_list
    selected_dict = input_mPrt_coeff_list[int(mPrt_eqn)]
    for key in selected_dict.keys():
        updated_key = key.removesuffix("_src")
        selected_dict[key] = r_data[updated_key]

    r_infusions = dictionaries["i"][0]
    input_infusion_dict = {
        key: r_infusions.pop(key, None) for key in constants.infusion_dict.keys()
        }
    
    input_f_Imb = dictionaries.pop("f_Imb", None)
    
    return (r_data, input_coeff_dict, input_MP_NP_efficiency_dict, 
            input_mPrt_coeff_list, input_infusion_dict, input_f_Imb)


def remove_untested_values(r_data: dict) -> dict:
    # Removed due to differences in Python implementation. R code calculates
    # everything then picks a value. In our code we select the equation and
    # only calculate required values. Also inlcudes variables that have no
    # use, such as equations selections
    values_to_remove = [
        "Abs_EAA2_HILKM_g", "Abs_EAA2_HILKMT_g", "Abs_EAA2_RHILKM_g",
        "An_AgeConcept1st", "An_DIMConcept", "An_GasEOut_Clf", "An_GasEOut_Dry",
        "An_GasEOut_Heif", "An_GasEOut_Lact", "An_SWlact", "An_WaIn_Dry",
        "An_WaIn_Lact", "DietID", "Dt_DMIn", "Dt_DMIn_BW_LateGest_i",
        "Dt_DMIn_Heif_LateGestInd", "Dt_DMIn_BW_LateGest_p", "Dt_DMIn_Calf1",
        "Dt_DMIn_DryCow_AdjGest", "Dt_DMIn_DryCow1", "Dt_DMIn_DryCow1_Close",
        "Dt_DMIn_DryCow1_FarOff", "Dt_DMIn_DryCow2", "Dt_DMIn_Heif_H1",
        "Dt_DMIn_Heif_H1i", "Dt_DMIn_Heif_H1p", "Dt_DMIn_Heif_H2",
        "Dt_DMIn_Heif_H2i", "Dt_DMIn_Heif_H2p", "Dt_DMIn_Heif_HJ1",
        "Dt_DMIn_Heif_HJ1i", "Dt_DMIn_Heif_HJ1p", "Dt_DMIn_Heif_HJ2",
        "Dt_DMIn_Heif_HJ2i", "Dt_DMIn_Heif_HJ2p", "Dt_DMIn_Heif_LateGestPen",
        "Dt_DMIn_Heif_NRCa", "Dt_DMIn_Heif_NRCad", "Dt_DMIn_Heif_NRCadi",
        "Dt_DMIn_Heif_NRCadp", "Dt_DMIn_Heif_NRCai", "Dt_DMIn_Heif_NRCap",
        "Dt_DMIn_Lact1", "Dt_DMIn_Lact2", "Dt_GasEOut_Clf", "Dt_GasEOut_Dry",
        "Dt_GasEOut_Lact", "Dt_GasEOut_Heif", "Dt_NDF_drylim", "Dt_NDFdev_DMI",
        "Du_MiN_NRC2021_g", "Du_MiN_VTln_g", "Du_MiN_VTnln_g", "Fd_DMInp_Sum",
        "FrmGain_eqn", "RsrvGain_eqn", "K_DE_ME_ClfDry", "K_FeCPend_ClfLiq",
        "Ky_ME_NE", "mLac_eqn", "mPrt_parmset", "numFdProp", "numIngrs",
        "RUP_eqn", "SIDigArgRUPf", "SIDigHisRUPf", "SIDigIleRUPf",
        "SIDigLeuRUPf", "SIDigLysRUPf", "SIDigMetRUPf", "SIDigPheRUPf",
        "SIDigThrRUPf", "SIDigTrpRUPf", "SIDigValRUPf", "Trg_MP_NPxprt",
        "Trg_NEmilkOut", "Kf_ME_RE_Clf", "Kf_ME_RE_ClfDry", "Kf_ME_RE_ClfLiq", 
        "Km_ME_NE_Clf", "Km_ME_NE_Cow", "Km_ME_NE_Heif"
    ]
    # Variables are missing or have issues with naming/feed library (DNDF48)
    # TODO Recreate integration tests once these values are added
    values_not_calculated = [
        "An_ME_ClfDry", "An_MEIn_ClfDry", "An_NE_ClfDry",
        "Dt_DE_ClfLiq", "Dt_ME_ClfLiq", "Dt_ForDNDF48", "Dt_ForDNDF48_ForNDF", # Need to fix Fd_DNDF48 in feed library as affecting calculation
        "Dt_RUPIn.dt"
    ]
    for name in values_to_remove:
        r_data.pop(name, np.nan)
    for name in values_not_calculated:
        r_data.pop(name, np.nan)

    # Rename key
    r_data["Dt_DigrOMa_Dt"] = r_data.pop("Dt_DigrOMa.Dt")
    return r_data


def create_test_json(user_diet_in: dict, 
                     animal_input_in: dict, 
                     equation_selection_in: dict,
                     coeff_dict: dict,
                     infusion_input: dict,
                     MP_NP_efficiency_input: dict,
                     mPrt_coeff_list: list,
                     f_Imb: list,
                     r_data: dict, 
                     AA_values: dict, 
                     arrays: dict, 
                     file_path: str
) -> None:
    data = {
        "input": {
            "user_diet_in": user_diet_in,
            "animal_input_in": animal_input_in,
            "equation_selection_in": equation_selection_in,
            "coeff_dict": coeff_dict,
            "infusion_input": infusion_input,
            "MP_NP_efficiency_input": MP_NP_efficiency_input,
            "mPrt_coeff_list": mPrt_coeff_list,
            "f_Imb": f_Imb
        },
        "output": {
            "output_data": r_data,
            "AA_values": AA_values,
            "arrays": arrays
        }
    }
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


####################
# Main Program
####################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Testing JSON")
    parser.add_argument("--r_json_path",
                        "-r",
                        action="store",
                        dest="r_json_path",
                        nargs="+",
                        required=True,
                        help="Path to the JSON files generated by R")
    parser.add_argument("--test_name",
                        "-n",
                        action="store",
                        dest="test_name",
                        nargs="+",
                        required=True,
                        help="Name of test JSON")
    parser.add_argument("--add_to_tests",
                        "-add",
                        action="store_true",
                        dest="add_to_tests",
                        required=False,
                        default=False,
                        help="Add to the integration directory")

    args = parser.parse_args()
    r_json_path = args.r_json_path
    test_name = args.test_name
    add_to_tests = args.add_to_tests

    if not check_input_length(r_json_path, test_name):
        raise ValueError("Length of r_json_path must match length of test_name")

    path_names = update_file_names(test_name, add_to_tests)
    path_name_map = dict(zip(r_json_path, path_names))

    for path, name in path_name_map.items():
        dictionaries, r_data = load_R_json(path)
        user_diet_in = get_user_diet(dictionaries, r_data)
        animal_input_in, r_data = get_animal_input(r_data)
        equation_selection_in, r_data = get_equation_selection(r_data)
        (
            r_data, input_coeff_dict, input_MP_NP_efficiency_dict, 
            input_mPrt_coeff_list, input_infusion_dict, input_f_Imb
        ) = get_constants(r_data, equation_selection_in["mPrt_eqn"], dictionaries)
        AA_values, r_data = create_AA_values(r_data)
        arrays, r_data = create_arrays(r_data)
        r_data = remove_untested_values(r_data)
        create_test_json(
            user_diet_in, animal_input_in, equation_selection_in, 
            input_coeff_dict, input_infusion_dict, input_MP_NP_efficiency_dict,
            input_mPrt_coeff_list, input_f_Imb, r_data, AA_values, arrays, name
            )

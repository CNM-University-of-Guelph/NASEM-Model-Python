import ast
import glob
import os

import graph_tool.all as graph_tool
import pandas as pd

class nasem_dag:
    ### Initalization ###
    def __init__(self):
        """
        Collect data for DAG and create graph.
        """
        self.aa_list = [
            "Arg", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Thr", "Trp", "Val"
            ]
        self.user_inputs = [
            "Use_DNDF_IV", "DMIn_eqn", "mProd_eqn", "MiN_eqn", "NonMilkCP_ClfLiq", 
            "Monensin_eqn", "mPrt_eqn", "mFat_eqn", "RumDevDisc_Clf", "An_Parity_rl", 
            "Trg_MilkProd", "An_BW", "An_BCS", "An_LactDay", "Trg_MilkFatp", "Trg_MilkTPp", 
            "Trg_MilkLacp", "Trg_Dt_DMIn", "An_BW_mature", "Trg_FrmGain", "An_GestDay", 
            "An_GestLength", "Trg_RsrvGain", "Fet_BWbrth", "An_AgeDay", "An_305RHA_MlkTP", 
            "An_StatePhys", "An_Breed", "An_AgeDryFdStart", "Env_TempCurr", "Env_DistParlor", 
            "Env_TripsParlor", "Env_Topo", "Inf_Acet_g", "Inf_ADF_g", "Inf_Arg_g", "Inf_Ash_g", 
            "Inf_Butr_g", "Inf_CP_g", "Inf_CPARum_CP", "Inf_CPBRum_CP", "Inf_CPCRum_CP", 
            "Inf_dcFA", "Inf_dcRUP", "Inf_DM_g", "Inf_EE_g", "Inf_FA_g", "Inf_Glc_g", 
            "Inf_His_g", "Inf_Ile_g", "Inf_KdCPB", "Inf_Leu_g", "Inf_Lys_g", "Inf_Met_g", 
            "Inf_NDF_g", "Inf_NPNCP_g", "Inf_Phe_g", "Inf_Prop_g", "Inf_St_g", "Inf_Thr_g", 
            "Inf_Trp_g", "Inf_ttdcSt", "Inf_Val_g", "Inf_VFA_g", "Inf_Location", "Fd_DMInp",
            "Fd_Name", "Fd_Category", "Fd_Type", "Fd_DM", "Fd_Conc", "Fd_DE_Base", "Fd_ADF",
            "Fd_NDF", "Fd_DNDF48_input", "Fd_DNDF48_NDF", "Fd_Lg", "Fd_CP", "Fd_St", 
            "Fd_dcSt", "Fd_WSC", "Fd_CPARU", "Fd_CPBRU", "Fd_CPCRU", "Fd_dcRUP",
            "Fd_CPs_CP", "Fd_KdRUP", "Fd_RUP_base", "Fd_NPN_CP", "Fd_NDFIP", 
            "Fd_ADFIP", "Fd_Arg_CP", "Fd_His_CP", "Fd_Ile_CP", "Fd_Leu_CP", "Fd_Lys_CP",
            "Fd_Met_CP", "Fd_Phe_CP", "Fd_Thr_CP", "Fd_Trp_CP", "Fd_Val_CP", "Fd_CFat",
            "Fd_FA", "Fd_dcFA", "Fd_Ash", "Fd_C120_FA", "Fd_C140_FA", "Fd_C160_FA",
            "Fd_C161_FA", "Fd_C180_FA", "Fd_C181t_FA","Fd_C181c_FA", "Fd_C182_FA",
            "Fd_C183_FA", "Fd_OtherFA_FA", "Fd_Ca", "Fd_P", "Fd_Pinorg_P", "Fd_Porg_P", 
            "Fd_Na", "Fd_Cl", "Fd_K", "Fd_Mg", "Fd_S", "Fd_Cr", "Fd_Co", "Fd_Cu", "Fd_Fe",
            "Fd_I", "Fd_Mn", "Fd_Mo", "Fd_Se", "Fd_Zn", "Fd_B_Carotene", "Fd_Biotin",
            "Fd_Choline", "Fd_Niacin", "Fd_VitA", "Fd_VitD", "Fd_VitE", "Fd_acCa_input",
            "Fd_acPtot_input", "Fd_acNa_input", "Fd_acCl_input", "Fd_acK_input", "Fd_acCu_input",
            "Fd_acFe_input", "Fd_acMg_input", "Fd_acMn_input", "Fd_acZn_input", "Trg_Fd_DMIn"
            ]
        self.mutator_function_mapping = {
            "calculate_An_IdAAIn": self.aa_list,
            "calculate_An_XIn": ["NPNCPIn", "FAIn"],
            "calculate_XIn": [
                "Inf_DM", "Inf_St", "Inf_NDF", "Inf_ADF", "Inf_Glc", "Inf_CP",
                "Inf_NPNCP", "Inf_FA", "Inf_Ash", "Inf_VFA", "Inf_Acet", "Inf_Prop",
                "Inf_Butr"
            ],
            "calculate_CPXIn": ["Inf_CPA", "Inf_CPB", "Inf_CPC"],
            "calculate_DMXIn": [
                "Inf_DM", "Inf_OM", "Inf_St", "Inf_NDF", "Inf_ADF", "Inf_Glc", "Inf_CP",
                "Inf_FA", "Inf_VFA", "Inf_Acet", "Inf_Prop", "Inf_Butr"
            ],
            "calculate_InfRum_X": [
                "DM", "OM", "CP", "NPNCP", "CPA", "CPB", "CPC", "St", "NDF", "ADF",
                "FA", "Glc", "VFA", "Acet", "Prop", "Butr", "Ash"
            ],
            "calculate_InfSI_X": [
                "DM", "OM", "CP", "NPNCP", "St", "Glc", "NDF", "ADF", "FA", "VFA",
                "Acet", "Prop", "Butr", "Ash"
            ],
            "calculate_InfArt_X": [
                "DM", "OM", "CP", "NPNCP", "TP", "St", "Glc", "NDF", "ADF", "FA", "VFA",
                "Acet", "Prop", "Butr", "Ash"
            ],
            "calculate_Inf_IdAARUPIn": self.aa_list,
            "calculate_Inf_IdAAIn": self.aa_list,
            "calculate_Fd_XIn": [
                "Fd_ADF", "Fd_NDF", "Fd_St", "Fd_NFC", "Fd_WSC", "Fd_rOM", "Fd_Lg",
                "Fd_Conc", "Fd_For", "Fd_ForNDF", "Fd_ForWet", "Fd_ForDry", "Fd_Past", 
                "Fd_CP", "Fd_TP", "Fd_CFat", "Fd_FA", "Fd_FAhydr", "Fd_Ash"
            ],
            "calculate_Fd_FAIn": [
                "Fd_C120", "Fd_C140", "Fd_C160", "Fd_C161", "Fd_C180", "Fd_C181t",
                "Fd_C181c", "Fd_C182", "Fd_C183", "Fd_OtherFA"
            ],
            "calculate_macroIn": [
                "Fd_Ca", "Fd_P", "Fd_Na", "Fd_Mg", "Fd_K", "Fd_Cl", "Fd_S"
            ],
            "calculate_microIn": [
                "Fd_Co", "Fd_Cr", "Fd_Cu", "Fd_Fe", "Fd_I", "Fd_Mn", "Fd_Mo", "Fd_Se",
                "Fd_Zn", "Fd_VitA", "Fd_VitD", "Fd_VitE", "Fd_Choline", "Fd_Biotin",
                "Fd_Niacin", "Fd_B_Carotene"
            ],
            "calculate_micro_absorbtion": ["Co", "Cu", "Fe", "Mn", "Zn"],
            "calculate_Fd_AAt_CP": self.aa_list,
            "calculate_Fd_AARUPIn": self.aa_list,
            "calculate_Fd_IdAARUPIn": self.aa_list,
            "calculate_Fd_Dig_FAIn": [
                "C120", "C140", "C160", "C161", "C180", "C181t", "C181c", "C182",
                "C183", "OtherFA"
            ],
            "calculate_Fd_AAIn": self.aa_list,
            "calculate_Dt_X": ["ADF", "NDF", "For", "ForNDF"],
            "calculate_DtIn": [
                "DMIn_ClfLiq", "DMIn_ClfFor", "AFIn", "NDFIn", "ADFIn", "LgIn",
                "DigNDFIn_Base", "ForWetIn", "ForDryIn", "PastIn", "ForIn", "ConcIn",
                "NFCIn", "StIn", "WSCIn", "CPIn", "CPIn_ClfLiq", "TPIn", "NPNCPIn",
                "NPNIn", "NPNDMIn", "CPAIn", "CPBIn", "CPCIn", "RUPBIn", "CFatIn",
                "FAIn", "FAhydrIn", "C120In", "C140In", "C160In", "C161In", "C180In",
                "C181tIn", "C181cIn", "C182In", "C183In", "OtherFAIn", "AshIn", "GEIn",
                "DEIn_base", "DEIn_base_ClfLiq", "DEIn_base_ClfDry", "DigStIn_Base",
                "DigrOMtIn", "idRUPIn", "DigFAIn", "DMIn_ClfFor", "ArgIn", "HisIn",
                "IleIn", "LeuIn", "LysIn", "MetIn", "PheIn", "ThrIn", "TrpIn", "ValIn",
                "ArgRUPIn", "HisRUPIn", "IleRUPIn", "LeuRUPIn", "LysRUPIn", "MetRUPIn",
                "PheRUPIn", "ThrRUPIn", "TrpRUPIn", "ValRUPIn"
            ],
            "calculate_Dt_DMI": [
                "RUP", "OM", "NDFnf", "Lg", "NFC", "St", "WSC",
                "rOM", "CFat", "FA", "FAhydr", "CP", "TP", "NPNCP", "NPN", "NPNDM",
                "CPA", "CPB", "CPC", "Ash", "ForWet", "ForDry", "Conc", "C120",
                "C140", "C160", "C161", "C180", "C181t", "C181c", "C182", "C183",
                "OtherFA", "UFA", "MUFA", "PUFA", "SatFA"
            ],
            "calculate_Dt_FA": [
                "C120", "C140", "C160", "C161", "C180", "C181t", "C181c", "C182",
                "C183", "OtherFA", "UFA", "MUFA", "PUFA", "SatFA"
            ],
            "calculate_Dt_microIn": [
                "CaIn", "PIn", "PinorgIn", "PorgIn", "NaIn", "MgIn", "MgIn_min", "KIn",
                "ClIn", "SIn", "CoIn", "CrIn", "CuIn", "FeIn", "IIn", "MnIn", "MoIn",
                "SeIn", "ZnIn", "VitAIn", "VitDIn", "VitEIn", "CholineIn", "BiotinIn",
                "NiacinIn", "B_CaroteneIn"
            ],
            "calculate_Dt_macro": [
                "Dt_Ca", "Dt_P", "Dt_Pinorg", "Dt_Porg", "Dt_Na", "Dt_Mg", "Dt_K",
                "Dt_Cl", "Dt_S"
            ],
            "calculate_Dt_micro": [
                "Dt_Co", "Dt_Cr", "Dt_Cu", "Dt_Fe", "Dt_I", "Dt_Mn", "Dt_Mo", "Dt_Se",
                "Dt_Zn", "Dt_VitA", "Dt_VitD", "Dt_VitE", "Dt_Choline", "Dt_Biotin",
                "Dt_Niacin", "Dt_B_Carotene"
            ],
            "calculate_Dt_IdAARUPIn": self.aa_list,
            "calculate_Dt_DigFAIn": [
                "C120", "C140", "C160", "C161", "C180", "C181t", "C181c", "C182",
                "C183", "OtherFA"
            ],
            "calculate_Abs_micro": [
                "CaIn", "PIn", "NaIn", "KIn", "ClIn", "CoIn", "CuIn", "FeIn", "MnIn",
                "ZnIn"
            ],
            "calculate_Dt_FA_FA": [
                "DigFA", "DigC120", "DigC140", "DigC160", "DigC161", "DigC180",
                "DigC181t", "DigC181c", "DigC182", "DigC183", "DigUFA", "DigMUFA",
                "DigPUFA", "DigSatFA", "DigOtherFA"
            ],
            "calculate_DtAARUP_DtAA": self.aa_list,
            "calculate_Dt_IdAAIn": self.aa_list
        }
        self.module_colour_map = {
            "amino_acid": [1.0, 0.0, 0.0, 0.7],             # Bright Red
            "animal": [0.0, 0.5, 1.0, 0.7],                # Sky Blue
            "body_composition": [0.0, 1.0, 0.0, 0.7],      # Bright Green
            "coefficient_adjustment": [0.6, 0.2, 0.8, 0.7], # Lavender
            "dry_matter_intake": [1.0, 0.5, 0.0, 0.7],     # Orange
            "energy_requirement": [0.2, 0.7, 0.2, 0.7],    # Forest Green
            "fecal": [0.8, 0.4, 0.0, 0.7],                 # Burnt Orange
            "gestation": [1.0, 0.2, 0.6, 0.7],             # Pink
            "infusion": [0.4, 0.0, 0.8, 0.7],              # Deep Purple
            "manure": [0.55, 0.27, 0.07, 0.7],             # Brown
            "methane": [0.2, 0.8, 0.8, 0.7],               # Aqua
            "microbial_protein": [0.6, 0.6, 0.2, 0.7],     # Olive Green
            "micronutrient_requirement": [0.8, 0.2, 0.0, 0.7], # Rust
            "milk": [0.5, 1.0, 0.5, 0.7],                  # Light Green
            "nutrient_intakes": [0.0, 0.4, 0.8, 0.7],      # Royal Blue
            "protein_requirement": [1.0, 0.7, 0.0, 0.7],   # Amber
            "protein": [0.8, 0.0, 0.8, 0.7],               # Magenta
            "report": [0.3, 0.3, 0.3, 0.7],                # Charcoal Gray
            "rumen": [0.2, 0.8, 1.0, 0.7],                 # Cyan
            "urine": [0.4, 0.8, 0.4, 0.7],                 # Sage Green
            "water": [0.0, 0.5, 1.0, 0.7],                 # Deep Sky Blue
            "Constants": [0.6, 0.6, 0.6, 1.0],             # Light Gray
            "Inputs": [0.2, 0.2, 0.2, 1.0]                 # Dark Gray
            }

        # Initalize DataFrame with a row for each variable name 
        with open("./src/nasem_dairy/dag/variable_names.txt", "r") as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]
        lines.extend([
            "Abs_EAA2_HILKM_g" ,"Abs_EAA2_RHILKM_g", "Abs_EAA2_HILKMT_g", 
            "An_GasEOut_Dry", "An_GasEOut_Lact", "An_GasEOut_Heif"
            ])
        variables = pd.DataFrame(lines, columns=["Name"])

        # Get list of module files
        modules = self._get_py_files("./src/nasem_dairy/nasem_equations")  
  
        # Create dag_data
        dag_data = self._parse_NASEM_equations(modules, variables)
        dag_data = dag_data.dropna(axis=0)
        self.dag_data = dag_data

        # Create DAG
        self.dag = self._create_dag(dag_data)

    def _get_py_files(self, path: str) -> list:
        py_files = glob.glob(os.path.join(path, "*.py"))
        py_files = [file for file in py_files if os.path.basename(file) != "__init__.py"]
        return py_files

    def _get_dict_keys(self, node, id_to_check: str, check_fstring: bool = True) -> list:
        coeff_keys = []
        for body_item in node.body:
            for sub_node in ast.walk(body_item):
                if isinstance(sub_node, ast.Subscript):
                    if (isinstance(sub_node.value, ast.Name) and
                        sub_node.value.id == id_to_check):
                        
                        # Get key when key is a string: dictionary["key"]
                        if (isinstance(sub_node.slice, ast.Constant) and 
                            isinstance(sub_node.slice.value, str)):
                            coeff_keys.append(sub_node.slice.value)

                        elif check_fstring:
                            # Create keys when key is an f-string: dictionary[f"text{aa}text]
                            if isinstance(sub_node.slice, ast.JoinedStr):
                                f_string = sub_node.slice.values
                                for section in f_string:

                                    # If ast.FormattedValue == "aa" assume iterating self.aa_list
                                    if (isinstance(section, ast.FormattedValue) and 
                                        section.value.id == "aa"):
                                        for aa in self.aa_list:
                                            formatted_coeff = ""
                                            for val in f_string:
                                                if (isinstance(val, ast.Constant) and 
                                                    isinstance(val.value, str)):
                                                    formatted_coeff += val.value

                                                elif (isinstance(val, ast.FormattedValue) and 
                                                    val.value.id == "aa"):
                                                    formatted_coeff += aa

                                            coeff_keys.append(formatted_coeff)
        return coeff_keys

    def _create_function_entry(self, node):
        """
        Collect required data for regular functions
        """
        args = [arg.arg for arg in node.args.args 
                if arg.arg not in ["aa_list"]]

        # Extract names of constants from function definition
        coeff_keys = []
        dicts_to_check = [
            "coeff_dict", "mPrt_coeff", "MP_NP_efficiency_dict"
            ]
        for dictionary in dicts_to_check:
            if dictionary in args:
                keys = self._get_dict_keys(node, dictionary)
                coeff_keys.extend(keys)
                args.remove(dictionary)
        # Check for f_Imb seperatly as not a dictionary
        constants_series = ["f_Imb", "SIDig_values"]
        for constant in constants_series:
            if constant in args:
                coeff_keys.append(constant)
                args.remove(constant)

        # Extract names of keys when dict is passed as arg
        dicts_to_check = ["infusion_data", "diet_data", "feed_data", "an_data"]
        for dictionary in dicts_to_check:
            if dictionary in args:
                keys = self._get_dict_keys(node, dictionary)
                args.extend(keys)
                args.remove(dictionary)

        # Check if any args are model inputs
        inputs = [arg for arg in args if arg in self.user_inputs]
        args = [arg for arg in args if arg not in self.user_inputs]

        # Get the return value
        return_var = None
        for body_item in node.body:
            if isinstance(body_item, ast.Return):
                if isinstance(body_item.value, ast.Name):
                    return_var = body_item.value.id
        return return_var, args ,coeff_keys, inputs

    def _create_mutator_entry(self, node, list_values: list, module: str):
        def recursive_extract_arguments(node):
            """
            Recursion to extract f-strings from a ast.BinOp object

            Ignores ast.Constant, searches through nested ast.BinOp objects
            """
            arguments = []

            if isinstance(node, ast.BinOp):
                if not isinstance(node.left, ast.Constant):
                    if isinstance(node.left, ast.BinOp):
                        arguments.extend(recursive_extract_arguments(node.left))
                    elif isinstance(node.left, ast.Subscript) and hasattr(node.left.slice, "values"):
                        arguments.append(node.left.slice.values)
                    elif isinstance(node.left, ast.Subscript) and hasattr(node.left.slice, "id"):
                        arguments.append(node.left.slice.id)

                if not isinstance(node.right, ast.Constant):
                    if isinstance(node.right, ast.BinOp):
                        arguments.extend(recursive_extract_arguments(node.right))
                    elif isinstance(node.right, ast.Subscript) and hasattr(node.right.slice, "values"):
                        arguments.append(node.right.slice.values)
                    elif isinstance(node.right, ast.Subscript) and hasattr(node.right.slice, "id"):
                        arguments.append(node.right.slice.id)
            
            return arguments


        name_expression = None
        arguments = []

        # Find the expressions used by mutator functions
        for body_item in node.body:
            # Find the for loop
            if isinstance(body_item, ast.For):
                # If the target of the assign is a JoinedStr this determines the variable names
                if isinstance(body_item.body[0].targets[0].slice, ast.JoinedStr):
                    name_expression = body_item.body[0].targets[0].slice.values
                if isinstance(body_item.body[0].value, ast.BinOp):
                    arguments = recursive_extract_arguments(body_item.body[0].value)
                elif isinstance(body_item.body[0].value.func.value, ast.BinOp):
                    arguments = recursive_extract_arguments(body_item.body[0].value.func.value)
                elif isinstance(body_item.body[0].value.func.value.slice, ast.JoinedStr):
                    arguments.append(body_item.body[0].value.func.value.slice.values)

            # Special case for calculate_Fd_AAIn: np.where inside a lambda makes this one a pain
            elif isinstance(body_item, ast.Return) and node.name == "calculate_Fd_AAIn":
                if isinstance(body_item.value.keywords[0].value.key, ast.JoinedStr):
                    name_expression = body_item.value.keywords[0].value.key.values
                if isinstance(body_item.value.keywords[0].value.value.body.args[1], ast.BinOp):
                    arguments = recursive_extract_arguments(body_item.value.keywords[0].value.value.body.args[1])

            # For the Fd_* mutators
            elif isinstance(body_item, ast.Return) and len(node.body) == 1:
                if isinstance(body_item.value.keywords[0].value.key, ast.JoinedStr):
                    name_expression = body_item.value.keywords[0].value.key.values
                if isinstance(body_item.value.keywords[0].value.value.body, ast.BinOp):
                    arguments = recursive_extract_arguments(body_item.value.keywords[0].value.value.body)

        if not name_expression or not arguments:
            print("ERROR: Did not find all the expressions")
            return pd.DataFrame()
        
        nested_dict = {}

        for val in list_values:
            name = "".join([part.value if isinstance(part, ast.Constant) else val for part in name_expression])
            arg_values = []
            for argument in arguments:
                if argument == "var":
                    arg_value = val
                elif argument == "aa":
                    continue
                else:
                    arg_value = "".join([part.value if isinstance(part, ast.Constant) else val for part in argument])
                arg_values.append(arg_value)        

            # Check for non f-string keys
            function_args = [arg.arg for arg in node.args.args
                            if arg.arg not in ["aa_list", "variables"]]
            coeff_keys = []
            dicts_to_check = [
                "coeff_dict", "mPrt_coeff", "MP_NP_efficiency_dict"
                ]
            for dictionary in dicts_to_check:
                if dictionary in function_args:
                    keys = self._get_dict_keys(node, dictionary)
                    coeff_keys.extend(keys)
                    function_args.remove(dictionary)
            # Check for f_Imb seperatly as not a dictionary
            constants_series = ["f_Imb", "SIDig_values"]
            for constant in constants_series:
                if constant in function_args:
                    coeff_keys.append(constant)
                    function_args.remove(constant)

            # Extract names of keys when dict is passed as arg
            dicts_to_check = ["infusion_data", "diet_data", "feed_data", "an_data"]
            for dictionary in dicts_to_check:
                if dictionary in function_args:
                    keys = self._get_dict_keys(node, dictionary, False)
                    arg_values.extend(keys)
                    function_args.remove(dictionary)

            # Check if any args are model inputs    
            inputs = [arg for arg in arg_values if arg in self.user_inputs]
            arg_values.extend(function_args)
            arg_values = [arg for arg in arg_values if arg not in self.user_inputs]
            arg_values = [arg for arg in arg_values if arg not in coeff_keys]

            nested_dict[name] = {
                "Name": name,
                "Module": module,
                "Function": node.name,
                "Arguments": list(set(arg_values)) if arg_values else arg_values,
                "Constants": list(set(coeff_keys)) if coeff_keys else coeff_keys,
                "Inputs": list(set(inputs)) if inputs else inputs
            }
        df = pd.DataFrame.from_dict(nested_dict, orient="index")
        return df

    def _parse_NASEM_equations(self, py_files: list, variables: pd.DataFrame) -> pd.DataFrame:
        """
        Function to parse through NASEM_equations directory and retrieve data used for plotting the DAG. 
        Returns a DataFrame.  

        This will only include variables in the variables DataFrame
        """
        dag_data = variables.copy()
        dag_data["Module"] = None
        dag_data["Function"] = None
        dag_data["Arguments"] = None
        dag_data["Constants"] = None
        dag_data["Inputs"] = None

        for py_file in py_files:
            with open(py_file, "r") as file:
                tree = ast.parse(file.read())
                module_name = py_file.split("/")[-1].replace(".py", "")

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_name = node.name
                    
                    # Mutator Functions
                    if function_name in self.mutator_function_mapping.keys():
                        mutator_entry = self._create_mutator_entry(
                            node, self.mutator_function_mapping[function_name], 
                            module_name
                            )
                        dag_data = pd.concat(
                            [dag_data, mutator_entry], ignore_index=True
                            )

                    # Regular Functions
                    else:
                        return_var, args ,coeff_keys, inputs = self._create_function_entry(
                            node
                        )
                        if return_var and return_var in dag_data["Name"].values:
                            idx = dag_data[dag_data["Name"] == return_var].index[0]
                            dag_data.at[idx, "Module"] = module_name
                            dag_data.at[idx, "Function"] = function_name
                            dag_data.at[idx, "Arguments"] = list(set(args)) if args else args
                            dag_data.at[idx, "Constants"] = list(set(coeff_keys)) if coeff_keys else coeff_keys
                            dag_data.at[idx, "Inputs"] = list(set(inputs)) if inputs else inputs
                                       
        return dag_data

    def _create_dag(self, data):
        # Create the DAG
        dag = graph_tool.Graph(directed=True)
        # Create a dictionary to map variable names to graph vertices
        name_to_vertex = {}
        vertex_labels = dag.new_vertex_property("string")
        vertex_colors = dag.new_vertex_property("vector<double>")

        # Add vertices for each unique variable name in the Name column
        for index, row in data.iterrows():
            name = row['Name']
            module = row['Module']
            vertex = dag.add_vertex()
            name_to_vertex[name] = vertex
            vertex_labels[vertex] = name
            vertex_colors[vertex] = self.module_colour_map.get(
                module, [0, 0, 0, 0]
                )

        # Add vertices for Constants and Inputs
        for column in ["Constants", "Inputs"]:
            for values in data[column]:
                for value in values:
                    if value not in name_to_vertex:
                        vertex = dag.add_vertex()
                        name_to_vertex[value] = vertex
                        vertex_labels[vertex] = value
                        vertex_colors[vertex] = self.module_colour_map.get(
                            column, [0.5, 0.5, 0.5, 0.5]
                            )

        # Add edges based on the Arguments column
        for index, row in data.iterrows():
            src_vertex = name_to_vertex[row['Name']]
            arguments = row['Arguments']
            constants = row["Constants"]
            inputs = row["Inputs"]

            for arg in arguments:
                if arg in name_to_vertex:
                    dst_vertex = name_to_vertex[arg]
                    dag.add_edge(dst_vertex, src_vertex)

            for constant in constants:
                if constant in name_to_vertex:
                    dst_vertex = name_to_vertex[constant]
                    dag.add_edge(dst_vertex, src_vertex)

            for input_val in inputs:
                if input_val in name_to_vertex:
                    dst_vertex = name_to_vertex[input_val]
                    dag.add_edge(dst_vertex, src_vertex)

            self.name_to_vertex = name_to_vertex 
            self.vertex_labels = vertex_labels 
            self.vertex_colors = vertex_colors
        return dag
        
    ### Visualization ###
    def draw_dag(self, output_path):
        pos = graph_tool.sfdp_layout(self.dag)
        graph_tool.graph_draw(self.dag, 
                              pos=pos,
                              vertex_text=self.vertex_labels, 
                              vertex_font_size=12, 
                              vertex_size=10,
                              vertex_fill_color=self.vertex_colors,
                              output_size=(8000, 8000), 
                              bg_color=[0.9, 0.9, 0.9, 1],
                              output=output_path
                              )
        print("Graph has", self.dag.num_vertices(), "vertices and", self.dag.num_edges(), "edges.")
        print(f"Graph image saved to {output_path}")

    ### Validation ###
    def validate_dag(self):
        """
        Validate the DAG structure
        - Check for cycles
        - Validate topological sort
        - Ensure all nodes and edges are correct
        """
        self._check_for_cycles()
        self._validate_topological_order()
        self._verify_connectivity()

    def _check_for_cycles(self):
        """
        Check for cycles in the DAG. Raises an exception if a cycle is found.
        """
        if graph_tool.is_DAG(self.dag):
            print("No cycles detected.")
        else:
            cycles = list(graph_tool.all_circuits(self.dag))
            if cycles:
                cycle_strs = []
                for cycle in cycles:
                    cycle_vertices = [self.vertex_labels[vertex] for vertex in cycle]
                    cycle_strs.append(" -> ".join(cycle_vertices))
                raise ValueError(f"Cycles detected in the DAG:\n" + "\n".join(cycle_strs))

    def _validate_topological_order(self):
        """
        Attempt a topological sort. Raises an exception if sorting fails, 
        which indicates a cycle or other inconsistency.
        """
        try:
            order = graph_tool.topological_sort(self.dag)
            # print(f"Topological sort successful: {list(order)}")
        except ValueError as e:
            raise ValueError("Topological sort failed. DAG may contain cycles or other inconsistencies.") from e
    
    def _verify_connectivity(self):
        """
        Ensure all vertices are connected according to the DAG data.
        Raises an exception if there are missing or extra connections.
        """
        # TODO After checking for no connections check that each vertex has the 
        # correct number of incoming and outgoing edges
        for name, vertex in self.name_to_vertex.items():
            if vertex.out_degree() == 0 and vertex.in_degree() == 0:
                raise ValueError(f"Vertex {name} is isolated (no edges).")

        for index, row in self.dag_data.iterrows():
            name = row["Name"]
            if name in self.name_to_vertex:
                vertex = self.name_to_vertex[name]
                expected_incoming_edges = (
                    len(row["Arguments"]) + 
                    len(row["Constants"]) + 
                    len(row["Inputs"])
                    )
                actual_incoming_edges = vertex.in_degree()

                if actual_incoming_edges != expected_incoming_edges:
                    actual_incoming_names = [
                        self.vertex_labels[edge.source()] for edge in vertex.in_edges()
                    ]
                    expected_incoming_names = row["Arguments"] + row["Constants"] + row["Inputs"]
                    missing_edges = [edge for edge in expected_incoming_names if edge not in actual_incoming_names]
                    
                    # Print debug information
                    print(f"Vertex {name} has an incorrect number of incoming edges.")
                    print(f"Expected {expected_incoming_edges} incoming edges from: {expected_incoming_names}")
                    print(f"Actual {actual_incoming_edges} incoming edges from: {actual_incoming_names}")
                    if missing_edges:
                        print(f"Missing expected edges from: {missing_edges}")
                    
                    raise ValueError(
                    f"Vertex {name} has {actual_incoming_edges} incoming edges, "
                    f"but {expected_incoming_edges} were expected."
                    )

            else:
                print(f"{name} was not found in self.name_to_vertex")

        print("Connectivity verification completed.")

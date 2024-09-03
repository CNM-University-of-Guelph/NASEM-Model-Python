"""Directed Acyclic Graph (DAG) management for the NASEM model.

This module provides functionality for creating, managing, and visualizing a 
Directed Acyclic Graph (DAG) that represents the dependencies and execution 
order of calculations within the NASEM model. It leverages the `graph-tool` 
library for efficient graph manipulation and visualization.

Classes:
    ModelDAG: Manages the creation and validation of a DAG for the NASEM model, 
              including methods for generating calculation orders and 
              dynamically creating functions.
"""

import ast
import glob
import inspect
import os
from typing import Dict, List, Any, Tuple, Optional, Callable

import pandas as pd

import nasem_dairy as nd
import nasem_dairy.model.input_definitions as expected
import nasem_dairy.model_output.ModelOutput as output

try:
    import graph_tool.all as graph_tool
except ImportError: # pragma: no cover
    raise ImportError(
        "The 'graph-tool' package is required for this module. "
        "Install it with `poetry install --extras dag` or "
        "`pip install nasem-dairy[dag]`."
    )
# NOTE: Since ModelDAG is a subpackage we should inlcude the following code in any 
# modules where it is used. This will ensure a meaningful error is raised in cases
# where graph-tool is not imported (nd.ModelDAG is set to None in __init__.py) but
# a user tries to run code that requires nd.ModelDAG.
# if nd.ModelDAG is None:
#     raise ImportError(
#         "ModelDAG requires the 'graph-tool' package. Please install it with "
#         "`poetry install --extras dag`."
#     )

module_colour_map = {
            "amino_acid": [1.0, 0.0, 0.0, 0.7],            # Bright Red
            "animal": [0.0, 0.5, 1.0, 0.7],                # Sky Blue
            "body_composition": [0.0, 1.0, 0.0, 0.7],      # Bright Green
            "coefficient_adjustment": [0.6, 0.2, 0.8, 0.7],# Lavender
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

class ModelDAG:
    """
    Manages the creation, validation, and visualization of a Directed Acyclic Graph (DAG) 
    for the NASEM model.

    The `ModelDAG` class is responsible for constructing a DAG that represents the 
    dependencies and execution order of calculations within the NASEM model. It uses 
    the `graph-tool` library for efficient graph manipulation and visualization, and 
    provides various methods to validate the structure, generate calculation orders, 
    and create dynamic functions based on the DAG.

    Attributes:
        aa_list (List[str]): A list of essential amino acids used in various calculations.
        module_colour_map (dict): A dictionary mapping module names to RGBA color values 
            for graph visualization.
        possible_user_inputs (Dict[str, Dict[str, Any]]): A dictionary of possible user 
            input structures, mapping names to their respective schema.
        possible_constants (Dict[str, Dict[str, Any]]): A dictionary of possible constants, 
            mapping names to their respective schema.
        user_inputs (List[str]): A list of user input keys extracted from possible user input structures.
        modules (List[str]): A list of Python file paths in the specified directory, excluding `__init__.py`.
        dag_data (pd.DataFrame): A DataFrame containing parsed data for each variable in the DAG.
        dag (graph_tool.Graph): The Directed Acyclic Graph representing the dependencies of variables.

    Methods:
        __init__(self, path: str = "./src/nasem_dairy/nasem_equations", colour_map: dict = module_colour_map):
            Initializes the `ModelDAG` instance by collecting data and creating the DAG.
        
        _get_variable_names(self) -> List[str]:
            Retrieves the variable names needed to build the DAG.
        
        _get_py_files(self, path: str) -> List[str]:
            Retrieves a list of Python files from the specified directory.
        
        _get_dict_keys(self, node: ast.AST, id_to_check: str, check_fstring: bool = True) -> List[str]:
            Extracts keys from a dictionary accessed in an AST node.
        
        _generate_user_inputs_list(self, possible_user_inputs: Dict[str, Any]) -> List[str]:
            Generates a list of user input keys from possible user input structures.
        
        _create_function_entry(self, node: ast.FunctionDef) -> Tuple[Optional[str], List[str], List[str], List[str]]:
            Collects required data for regular functions from an AST node.
        
        _parse_nasem_equations(self, py_files: List[str], variables: pd.DataFrame) -> pd.DataFrame:
            Parses NASEM equations from Python files and extracts data for the DAG.
        
        _create_dag(self, data: pd.DataFrame) -> graph_tool.Graph:
            Creates a Directed Acyclic Graph (DAG) from the provided data.
        
        draw_dag(self, output_path: str) -> None:
            Draws and saves the DAG to the specified output path.
        
        validate_dag(self) -> None:
            Validates the DAG structure by checking for cycles, verifying the topological order, and ensuring connectivity.
        
        get_calculation_order(self, target_variable: str, report: bool = True) -> Dict[List[str], Dict[str, Dict[str, Any]]]:
            Determines the calculation order for a given target variable using depth-first search on the DAG.
        
        create_function(self, target_variable: str) -> Callable[..., Any]:
            Creates a dynamically generated function to calculate the target variable based on the DAG structure.
    """
    ### Initalization ###
    def __init__(
        self, 
        path:str = "./src/nasem_dairy/nasem_equations", 
        colour_map: dict = module_colour_map
    ):
        """
        Collect data for DAG and create graph.
        """
        self.aa_list = [
            "Arg", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Thr", "Trp", "Val"
            ]
        self.module_colour_map = colour_map
        self.possible_user_inputs = {
            "animal_input": expected.AnimalInput.__annotations__.copy(),
            "equation_selection": (
                expected.EquationSelection.__annotations__.copy()
                ),
            "infusion_input": expected.InfusionInput.__annotations__.copy(),
            "user_diet": expected.UserDietSchema.copy(),
            "feed_library": expected.FeedLibrarySchema.copy()
        }
        self.possible_constants = {
            "coeff_dict": expected.CoeffDict.__annotations__.copy(),
            "infusion_dict": expected.InfusionDict.__annotations__.copy(),
            "mpnp_efficiency_dict": (
                expected.MPNPEfficiencyDict.__annotations__.copy()
                ),
            "mprt_coeff_dict": expected.mPrtCoeffDict.__annotations__.copy(),
            "f_imb": expected.f_Imb.copy()
        }
        self.user_inputs = self._generate_user_inputs_list(
            self.possible_user_inputs
            )

        variable_names = self._get_variable_names()
        variables = pd.DataFrame(variable_names, columns=["Name"])

        # Collect data for DAG
        self.modules = self._get_py_files(path)  
        self.dag_data = self._parse_nasem_equations(self.modules, variables)
        self.dag_data = self.dag_data.dropna(axis=0)
        self.dag = self._create_dag(self.dag_data)

    def _get_variable_names(self) -> List[str]:
        """
        Retrieve the variable names needed to build the DAG.

        Returns:
            A list of variable names required for the DAG
        """
        user_diet, animal_input, eqn_selection, inf_input = nd.demo(
            "lactating_cow_test"
            )
        output = nd.nasem(
            user_diet = user_diet, 
            animal_input = animal_input, 
            equation_selection = eqn_selection, 
            coeff_dict = nd.coeff_dict,
            infusion_input=inf_input
            )
        variables = output.export_variable_names()
        # These variables are necessary for the DAG but not directly available
        additional_vars = [
            "Abs_EAA2_HILKM_g" ,"Abs_EAA2_RHILKM_g", "Abs_EAA2_HILKMT_g", 
            "An_GasEOut_Dry", "An_GasEOut_Lact", "An_GasEOut_Heif"
            ]
        variables.extend(additional_vars)
        return variables

    def _get_py_files(self, path: str) -> List[str]:
        """
        Retrieve a list of Python files from the specified directory.

        Args:
            path: A string representing the directory path to search for Python files.

        Returns:
            A list of Python file paths in the specified directory, excluding `__init__.py`.
        """
        py_files = glob.glob(os.path.join(path, "*.py"))
        return [
            file for file in py_files 
            if os.path.basename(file) != "__init__.py"
            ]

    def _get_dict_keys(
        self, 
        node: ast.AST, 
        id_to_check: str, 
        check_fstring: bool = True
    ) -> List[str]:
        """
        Extract keys from a dictionary accessed in an AST node.

        Args:
            node: The AST node to analyze for dictionary key accesses.
            id_to_check: The identifier of the dictionary to check.
            check_fstring: Whether to check for keys formatted with f-strings.
        
        Returns:
            A list of keys accessed from the specified dictionary.
        """
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

    def _generate_user_inputs_list(
        self, 
        possible_user_inputs: Dict[str, Any]
    ) -> List[str]:
        """
        Generate a list of user input keys from possible user input structures.

        This method iterates over the possible user input structures from the
        input definitions module to extract the keys representing user inputs.

        Args:
            possible_user_inputs: A dictionary mapping structure names to their
                corresponding input structures, which can be either dictionaries
                or objects with `__annotations__`.

        Returns:
            A list of all user input keys found in the input structures.
        """
        user_inputs = []
        for structure_name, structure in possible_user_inputs.items():
            if isinstance(structure, dict):
                user_inputs.extend(structure.keys())
        return user_inputs

    def _create_function_entry(
        self, 
        node: ast.FunctionDef
    ) -> Tuple[Optional[str], List[str], List[str], List[str]]:
        """
        Collect required data for regular functions from an AST node.

        This method processes an AST node representing a function definition
        to extract its return variable, arguments, constants, and inputs.

        Args:
            node: An AST node representing a function definition.

        Returns:
            A tuple containing:
                - The return variable name (or None if not found).
                - A list of arguments that are not constants or user inputs.
                - A list of keys related to constants required by the function.
                - A list of arguments identified as user inputs.
        """
        args = [arg.arg for arg in node.args.args if arg.arg not in ["aa_list"]]

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

    def _parse_nasem_equations(
        self, 
        py_files: List[str], 
        variables: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Parse NASEM equations from Python files and extract data for the DAG.

        This function parses through Python files in the NASEM equations directory 
        to retrieve data used for plotting the DAG. It returns a DataFrame with 
        the relevant information for each variable listed in the variables DataFrame.

        Args:
            py_files: A list of Python file paths to parse.
            variables: A DataFrame containing the variables to include in the DAG.

        Returns:
            A DataFrame containing the parsed data, including the module name, 
            function name, arguments, constants, and inputs associated with each 
            variable.
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
                    return_var, args ,coeff_keys, inputs = (
                        self._create_function_entry(node)
                        )
                    if return_var and return_var in dag_data["Name"].values:
                        idx = dag_data[dag_data["Name"] == return_var].index[0]
                        dag_data.at[idx, "Module"] = module_name
                        dag_data.at[idx, "Function"] = function_name
                        dag_data.at[idx, "Arguments"] = (
                            list(set(args)) if args else args
                            )
                        dag_data.at[idx, "Constants"] = (
                            list(set(coeff_keys)) if coeff_keys else coeff_keys
                            )
                        dag_data.at[idx, "Inputs"] = (
                            list(set(inputs)) if inputs else inputs
                            )
                                       
        return dag_data

    def _create_dag(self, data: pd.DataFrame) -> graph_tool.Graph:
        """
        Create a Directed Acyclic Graph (DAG) from the provided data.

        This function constructs a DAG using the variable names, functions, 
        modules, constants, and inputs from the provided data. Each unique 
        variable name, constant, and input is added as a vertex in the graph, 
        and edges are added based on the dependencies specified in the 
        'Arguments', 'Constants', and 'Inputs' columns.

        Args:
            data: A DataFrame containing the variables, functions, modules, 
                constants, and inputs for the DAG.

        Returns:
            A graph-tool Graph object representing the DAG.
        """
        dag = graph_tool.Graph(directed=True)

        # Create a dictionary to map variable names to graph vertices
        name_to_vertex = {}
        vertex_labels = dag.new_vertex_property("string")
        vertex_functions = dag.new_vertex_property("string")
        vertex_module = dag.new_vertex_property("string")
        vertex_colors = dag.new_vertex_property("vector<double>")

        # Add vertices for each unique variable name in the Name column
        for index, row in data.iterrows():
            name = row['Name']
            function = row["Function"]
            module = row['Module']
            vertex = dag.add_vertex()
            name_to_vertex[name] = vertex
            vertex_labels[vertex] = name
            vertex_functions[vertex] = function
            vertex_module[vertex] = module
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
                        vertex_functions[vertex] = ""
                        vertex_module[vertex] = column
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
            self.vertex_functions = vertex_functions
            self.vertex_module = vertex_module
            self.vertex_colors = vertex_colors

        return dag
        
    ### Visualization ###
    def draw_dag(self, output_path: str) -> None:
        """
        Draw and save the DAG to the specified output path.

        This method generates a visual representation of the DAG using the 
        `graph_tool` library, with custom styling for vertices and layout. 
        The graph is saved as an image file at the specified output path.

        Args:
            output_path: The file path where the DAG image will be saved.
        """
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
        print(
            "Graph has", self.dag.num_vertices(), 
            "vertices and", self.dag.num_edges(), "edges."
            )
        print(f"Graph image saved to {output_path}")

    ### Validation ###
    def validate_dag(self) -> None:
        """
        Validate the DAG structure.

        This method performs several checks to ensure the integrity of the DAG:
        - Checks for cycles in the DAG.
        - Validates the topological sort of the DAG.
        - Ensures that all nodes and edges are correctly connected.
        """
        self._check_for_cycles()
        self._validate_topological_order()
        self._verify_connectivity()

    def _check_for_cycles(self) -> None:
        """
        Check for cycles in the DAG.

        This method checks whether the DAG contains any cycles. If a cycle is 
        detected, it raises a ValueError with details of the cycle(s) found.

        Raises:
            ValueError: If one or more cycles are detected in the DAG.
        """
        if graph_tool.is_DAG(self.dag):
            print("No cycles detected.")
        else:
            cycles = list(graph_tool.all_circuits(self.dag))
            if cycles:
                cycle_strs = []
                for cycle in cycles:
                    cycle_vertices = [
                        self.vertex_labels[vertex] for vertex in cycle
                        ]
                    cycle_strs.append(" -> ".join(cycle_vertices))
                raise ValueError(
                    f"Cycles detected in the DAG:\n" + "\n".join(cycle_strs)
                    )

    def _validate_topological_order(self) -> None:
        """
        Validate the topological order of the DAG.

        This method attempts a topological sort of the DAG. If the sort fails, 
        it raises a ValueError, which may indicate the presence of cycles or 
        other inconsistencies in the DAG structure.

        Raises:
            ValueError: If the topological sort fails
        """
        try:
            order = graph_tool.topological_sort(self.dag)
        except ValueError as e:
            raise ValueError(
                "Topological sort failed. DAG may contain cycles or other "
                "inconsistencies."
                ) from e
    
    def _verify_connectivity(self) -> None:
        """
        Ensure all vertices are correctly connected according to the DAG data.

        This method verifies the connectivity of the DAG by checking that:
        - All vertices are connected according to the expected inputs.
        - There are no isolated vertices (vertices with no edges).
        - Each vertex has the correct number of incoming and outgoing edges.

        Raises:
            ValueError: If any vertex is isolated or has an incorrect number 
            of incoming or outgoing edges.
        """
        vertex_data = {
            row["Name"]: {
                "expected_inputs": (
                    row["Arguments"] + row["Constants"] + row["Inputs"]
                    ),
                "outgoing_count": 0
                }
                for index, row in self.dag_data.iterrows()
            }
        # Populate outgoing_count based on references in other vertices' expected_inputs
        for name, data in vertex_data.items():
            for reference in data["expected_inputs"]:
                if reference in vertex_data:
                    vertex_data[reference]["outgoing_count"] += 1
       
        # Check for isolated vertices
        for name, vertex in self.name_to_vertex.items():
            if vertex.out_degree() == 0 and vertex.in_degree() == 0:
                raise ValueError(f"Vertex {name} is isolated (no edges).")

        # Check each vertex has expected number of incoming edges
        for name, data in vertex_data.items():
            if name in self.name_to_vertex:
                vertex = self.name_to_vertex[name]
                expected_incoming_edges = len(data["expected_inputs"])
                actual_incoming_edges = vertex.in_degree()

                if actual_incoming_edges != expected_incoming_edges:
                    actual_incoming_names = [
                        self.vertex_labels[edge.source()] 
                        for edge in vertex.in_edges()
                    ]
                    missing_edges = [
                        edge for edge in data["expected_inputs"] 
                        if edge not in actual_incoming_names
                        ]

                    if missing_edges:
                        print(f"Missing expected edges from: {missing_edges}")

                    raise ValueError(
                        f"Vertex {name} has {actual_incoming_edges} incoming edges, "
                        f"but {expected_incoming_edges} were expected."
                    )
            else:
                print(f"{name} was not found in self.name_to_vertex")

        # Check each vertex has the expected number of outgoing edges
        for name, data in vertex_data.items():
            if name in self.name_to_vertex:
                vertex = self.name_to_vertex[name]
                expected_outgoing_edges = data["outgoing_count"]
                actual_outgoing_edges = vertex.out_degree()

                if actual_outgoing_edges != expected_outgoing_edges:
                    print(
                        f"Vertex {name} has an incorrect number of outgoing edges."
                        )
                    print(f"Expected {expected_outgoing_edges} outgoing edges.")
                    print(f"Actual {actual_outgoing_edges} outgoing edges.")

                    raise ValueError(
                        f"Vertex {name} has {actual_outgoing_edges} outgoing edges, "
                        f"but {expected_outgoing_edges} were expected."
                    )

        print("Connectivity verification completed.")

    ### Tools ###
    def get_calculation_order(
        self, 
        target_variable: str, 
        report: bool = True
    ) -> Dict[List[str], Dict[str, Dict[str, Any]]]:
        """
        Determine the calculation order for a given target variable.

        This method performs a depth-first search (DFS) on the DAG to determine
        the order of function calls and the required inputs and constants needed
        to calculate the specified target variable.

        Args:
            target_variable: The name of the target variable to calculate.
            report: Whether to print a report of the calculation order. 
                Default is True.

        Returns:
            dict:
                - 'functions_order': A list of functions in the order they should 
                be called.
                - 'user_inputs': A dictionary of required user input structures 
                and their respective fields.
                - 'constants': A dictionary of required constants and their 
                respective fields.
        """
        def depth_first_search(vertex: graph_tool.Vertex) -> None: # type:ignore
            """
            Perform a depth-first search to determine dependencies.

            This helper function traverses the graph to find all dependencies for
            the given vertex, recording user inputs, constants, and functions 
            necessary to calculate the target variable.

            Args:
                vertex: The current vertex in the graph being explored.
            """
            if vertex in visited:
                return
            visited.add(vertex)

            # Traverse all incoming edges to find dependencies
            for edge in vertex.in_edges():
                source_vertex = edge.source()
                depth_first_search(source_vertex)

            vertex_name = self.vertex_labels[vertex]
            vertex_function = self.vertex_functions[vertex]
            vertex_module = self.vertex_module[vertex]

            if vertex_module == "Inputs":
                user_inputs.add(vertex_name)
            elif vertex_module == "Constants":
                constants.add(vertex_name)
            elif vertex_function: 
                functions_order.append(vertex_function)


        def print_report(
            target_variable: str, 
            functions_order: List[str], 
            sorted_user_inputs: Dict[str, Dict[str, Optional[str]]], 
            sorted_constants: Dict[str, Optional[Dict[str, Optional[str]]]]
        ) -> None:
            """
            Print a formatted report of the calculation requirements.

            This function generates a report detailing the order of functions to 
            be called, as well as the required user inputs and constants for 
            calculating the specified target variable.

            Args:
                target_variable: The name of the target variable.
                functions_order: A list of functions in the order they should be called.
                sorted_user_inputs: A dictionary of required user input structures 
                    and their respective fields.
                sorted_constants: A dictionary of required constants and their 
                    respective fields or special structures.
            """
            print(f"\nRequirements for Calculating {target_variable}")
            print("\nOrder of Functions to Call:")
            for i, function in enumerate(functions_order, 1):
                print(f"  {i}. {function}")
            
            if sorted_user_inputs:
                print("\nRequired User Inputs:")
                for key in sorted_user_inputs:
                    print(f"  {key}:")
                    for field in sorted_user_inputs[key]:
                        print(f"    - {field}")
            
            if sorted_constants:
                print("\nRequired Constants:")
                for key in sorted_constants:
                    print(f"  {key}:")
                    if isinstance(sorted_constants[key], dict):
                        for field in sorted_constants[key]:
                            print(f"    - {field}")
                    else:
                        print(f"    - {key}")


        if target_variable not in self.name_to_vertex:
            raise ValueError(
                f"Variable '{target_variable}' not found in the DAG."
                )

        target_vertex = self.name_to_vertex[target_variable]
        functions_order = []
        user_inputs = set()
        constants = set()
        visited = set()

        depth_first_search(target_vertex)

        # Remove duplicates while preserving order
        functions_order = list(dict.fromkeys(functions_order))

        # Sort inputs and constants
        sorted_user_inputs = {}
        sorted_constants = {}

        # Filter and include only the necessary user inputs
        for input_var in user_inputs:
            for key, schema in self.possible_user_inputs.items():
                if input_var in schema:
                    if key not in sorted_user_inputs:
                        sorted_user_inputs[key] = {}
                    sorted_user_inputs[key][input_var] = None

        # Filter and include only the necessary constants
        for const_var in constants:
            for key, schema in self.possible_constants.items():
                if const_var in schema:
                    if key not in sorted_constants:
                        sorted_constants[key] = {}
                    sorted_constants[key][const_var] = None
                elif key == "f_imb" and const_var in schema.index:
                    if key not in sorted_constants:
                        sorted_constants[key] = schema 

        if report:
            print_report(
                target_variable, functions_order, sorted_user_inputs, 
                sorted_constants
                )

        return {
            "functions_order": functions_order,
            "user_inputs": sorted_user_inputs,
            "constants": sorted_constants
        }

    def create_function(self, target_variable: str) -> Callable[..., Any]:
        """
        Create a dynamically generated function to calculate the target variable.

        This method generates and returns a function that can be used to calculate 
        the specified target variable. The returned function will have all required 
        arguments and the necessary logic to calculate the target variable based on 
        the DAG structure.

        Args:
            target_variable: The name of the target variable being calculated.

        Returns:
            Callable: A function that calculates the target variable.
        """
        def create_docstring(
            target_variable: str, 
            arg_names: List[str], 
            user_inputs: Dict[str, Dict[str, Optional[str]]], 
            constants: Dict[str, Dict[str, Optional[str]]], 
            functions_order: List[str], 
            generated_func_return: str
        ) -> str:
            """
            Generate a docstring for a dynamically generated function.

            This function creates a docstring that describes the dynamically 
            generated function used to calculate the specified target variable. 
            The docstring includes information about the function's arguments, 
            the order of function calls, and the return value.

            Args:
                target_variable: The name of the target variable being calculated.
                arg_names: A list of argument names required by the function.
                user_inputs: A dictionary of required user input structures and 
                    their respective fields.
                constants: A dictionary of required constants and their respective 
                    fields, excluding special cases like "aa_list".
                functions_order: A list of functions in the order they should be called.
                generated_func_return: The name of the variable that the function 
                    returns.

            Returns:
                A string representing the docstring for the generated function.
            """
            docstring = (
                f'"""Dynamically generated function to calculate '
                f'{target_variable}.\n\n'
                )
            docstring += 'Arguments:\n'
            for arg in arg_names:
                docstring += (
                    f'    {arg} (dict): A dictionary containing the following '
                    'keys:\n'
                    )
                if arg in user_inputs:
                    for key in user_inputs[arg].keys():
                        docstring += f'            - {key}\n'
                elif arg in constants and arg != "aa_list":
                    for key in constants[arg].keys():
                        docstring += f'            - {key}\n'
            
            docstring += '\nOrder of function calls:\n'
            for i, func in enumerate(functions_order, 1):
                docstring += f'    {i}. {func}\n'

            docstring += '\nReturns:\n'
            docstring += (
                f'    {generated_func_return} (float): The calculated value for '
                f'{target_variable}.\n')
            docstring += '"""'
            return docstring


        def check_for_constants(
            functions_order: List[str], 
            constants: Dict[str, Dict[str, str]]
        ) -> bool:
            """
            Check for 'coeff_dict' and 'aa_list' in function arguments.

            This function checks if 'coeff_dict' and 'aa_list' are required by any 
            function in the given order. For some wrapper functions, such as 
            calculate_Dt_DMIn, 'coeff_dict' might be passed to other functions 
            without accessing any keys, so it won't appear in the Constants list 
            in dag_data. The function returns a boolean indicating whether 
            'aa_list' is required.

            Args:
                functions_order: A list of function names to check.
                constants: A dictionary of constants already identified.

            Returns:
                bool: True if 'aa_list' is required by any function, False otherwise.
            """
            aa_list_required = False
            for function_name in functions_order:
                func = getattr(nd, function_name)
                func_args = inspect.signature(func).parameters.keys()
                if "coeff_dict" in func_args and "coeff_dict" not in constants:
                    constants["coeff_dict"] = {} 
                if "aa_list" in func_args and "aa_list" not in constants:
                    aa_list_required = True
            return aa_list_required


        def _identify_dict_args(
            dag_data: pd.DataFrame, 
            functions_order: List[str]
        ) -> Dict[str, Dict[str, List[Any]]]:
            """
            Identify functions that require dictionaries as arguments.

            This function examines the functions in the given order to identify 
            which ones require dictionaries as arguments, excluding 'coeff_dict'. 
            It uses type annotations to determine if an argument is a dictionary 
            and retrieves the associated arguments from the DAG data.

            Args:
                dag_data: A DataFrame containing information about the DAG, 
                    including function names and their arguments.
                functions_order: A list of function names to check.

            Returns:
                A dictionary where each key is a function name, and each value 
                is another dictionary that maps the dictionary argument name 
                to a list of required arguments.
            """
            dict_inputs = {}

            for function_name in functions_order:
                func = getattr(nd, function_name)
                func_signature = inspect.signature(func)
                dict_inputs[function_name] = {}
               
                # Check each parameter's type annotation to see if it is a dict (excluding 'coeff_dict')
                for param_name, param in func_signature.parameters.items():
                    annotation = param.annotation
                    if (param_name != "coeff_dict" and 
                       (annotation is dict or 
                        annotation is Dict)
                       ):
                        dag_row = dag_data[dag_data['Function'] == function_name]
                        
                        if not dag_row.empty:
                            arguments_list = dag_row['Arguments'].values[0]
                            dict_inputs[function_name][param_name] = arguments_list
                        else:
                            print(
                                f"Warning: No entry found in DAG data for "
                                f"function '{function_name}'"
                                )
            
                if not dict_inputs[function_name]:
                    del dict_inputs[function_name]

            return dict_inputs


        # Call get_calculation_order to get requirements
        requirements = self.get_calculation_order(target_variable, report=False)
        functions_order = requirements["functions_order"]
        user_inputs = requirements["user_inputs"]
        constants = requirements["constants"]

        dict_inputs = _identify_dict_args(self.dag_data, functions_order)
        aa_list_required = check_for_constants(functions_order, constants)

        arg_names = sorted(list(user_inputs.keys()) + list(constants.keys()))

        func_name_to_result_name = {}
        for func in functions_order:
            result_name = (
                self.dag_data[self.dag_data['Function'] == func]['Name'].values[0]
                )
            func_name_to_result_name[func] = result_name
        
        # Define the function dynamically using exec
        func_args = ", ".join(arg_names)
        generated_func_name = f"wrapper_{target_variable}"
        #NOTE Update return
        generated_func_return = list(func_name_to_result_name.values())[-1]
        docstring = create_docstring(
            target_variable, arg_names, user_inputs, constants, functions_order,
            generated_func_return
            )
        func_body = f"""
def {generated_func_name}({func_args}):
    {docstring}
    dict_inputs = {dict_inputs}    
    if {aa_list_required}:
        aa_list = {self.aa_list.copy()}

    # Step 1: Unpack nested values from user inputs and constants
    for input_dict_name, input_dict in {user_inputs}.items():
        for key in input_dict:
            locals()[key] = locals()[input_dict_name].get(key, None)
    
    for const_dict_name in {constants}.keys():
        locals()[const_dict_name] = const_dict_name
  
    # Step 2: Call each function in order and store the results
    for function_name in {functions_order}:
        func = getattr(nd, function_name)
        func_args = inspect.signature(func).parameters.keys()

        # Create dictionary if requried
        if function_name in dict_inputs.keys():
            for dict_name, required_keys in dict_inputs[function_name].items():
                locals()[dict_name] = {{
                    key: locals()[key] for key in required_keys
                    }}
                
        # Resolve arguments for the function call
        func_call_args = {{}}
        for arg in func_args:
            if arg in locals():
                func_call_args[arg] = locals()[arg]
                
        # Call the function and store the result with the correct name
        result = func(**func_call_args)
        result_name = {func_name_to_result_name}[function_name]
        locals()[result_name] = result
   
    exclude_keys = {
        'dict_inputs', 'input_dict_name', 'input_dict', 'function_name', 
        'func', 'func_args', 'func_call_args', 'result', 'result_name', 
        'exclude_keys'
        }
    locals_dict = {{
        key: value for key, value in locals().items() if key not in exclude_keys
    }}
    model_output = output.ModelOutput(locals_input=locals_dict)
    return model_output
"""
        # Execute the dynamic function definition
        exec_namespace = {}
        exec(func_body, globals(), exec_namespace)
        generated_function = exec_namespace[generated_func_name]

        return generated_function
    
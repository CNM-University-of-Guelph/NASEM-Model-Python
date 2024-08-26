import os
import unittest

import pandas as pd
import pytest

try:
    import graph_tool.all as graph_tool
except ImportError:
    gt = None

import nasem_dairy.model_output.ModelOutput as output
import nasem_dairy as nd

demo_colour_map = {
    "module1": [1.0, 0.0, 0.0, 0.7],
    "module2": [0.0, 1.0, 0.0, 0.7],
    "module3": [0.8, 0.4, 0.0, 0.7]
}

demo_model_data = {
    "Name": [
        "Mlk_Prod", "MlkNP_Milk", "An_IdTrpIn", "CH4L_Milk", "Rsrv_MEgain", 
        "An_DigTPtIn", "TT_dcDtCPt", "Mlk_NP_g", "Body_NPgain_g", "An_NELgain", 
        "Du_idMiTP_g", "Scrf_NP_g", "MlkFat_Milk", "An_BW_protein", 
        "Dt_DigC161_FA"
    ],
    "Module": [
        "module2", "module1", "module1", "module3", "module2", 
        "module2", "module3", "module1", "module2", "module2", 
        "module1", "module3", "module1", "module3", "module3"
    ],
    "Function": [
        "calculate_Mlk_Prod", "calculate_MlkNP_Milk", "calculate_An_IdTrpIn", 
        "calculate_CH4L_Milk", "calculate_Rsrv_MEgain", "calculate_An_DigTPtIn", 
        "calculate_TT_dcDtCPt", "calculate_Mlk_NP_g", "calculate_Body_NPgain_g", 
        "calculate_An_NELgain", "calculate_Du_idMiTP_g", "calculate_Scrf_NP_g", 
        "calculate_MlkFat_Milk", "calculate_An_BW_protein", 
        "calculate_Dt_DigC161_FA"
    ],
    "Arguments": [
        ['Body_NPgain_g'], ['MlkFat_Milk'], ['Du_idMiTP_g'], 
        ['An_BW_protein', 'Dt_DigC161_FA'], [], ['An_NELgain'], ['Scrf_NP_g'], 
        ['MlkNP_Milk'], ['An_DigTPtIn'], ['Rsrv_MEgain', 'MlkNP_Milk'], 
        ['Mlk_NP_g'], ['Dt_DigC161_FA'], [], ['TT_dcDtCPt'], ['An_NELgain']
    ],
    "Constants": [
        [], [], [], [], ['Body_Leu_TP'], 
        ['MiTPValProf'], ['En_FA'], [], [], 
        [], ['MiTPMetProf'], ['RecArg'], ['Body_NP_CP'], [], ['MiTPIleProf']
    ],
    "Inputs": [
        ['Trg_MilkLacp'], ['An_BCS'], ['An_GestDay'], [], ['Trg_MilkProd'], 
        [], [], ['An_Parity_rl'], ['Trg_MilkTPp'], [], 
        [], [], ['An_BW'], ['Trg_Dt_DMIn'], []
    ]
}
expected_dag_data = pd.DataFrame(demo_model_data)

@unittest.skipUnless(
    graph_tool, "Skipping DAG tests because graph-tool is not installed"
    )
class TestModelDAG():
    @pytest.fixture
    def demo_model_dag(self):
        """Fixture to create a ModelDAG instance."""
        return nd.ModelDAG(
            path="./tests/model_dag/demo_model", colour_map=demo_colour_map
            )
    
    def test_aa_list_initialization(self, demo_model_dag):
        """Test that aa_list is initialized correctly."""
        expected_aa_list = [
            "Arg", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Thr", "Trp", "Val"
        ]
        assert (demo_model_dag.aa_list == expected_aa_list, 
                "aa_list is not initialized correctly.")

    def test_module_colour_map_initialization(self, demo_model_dag):
        """Test that module_colour_map is initialized correctly."""
        expected_module_colour_map = demo_colour_map
        for key, value in expected_module_colour_map.items():
            assert (demo_model_dag.module_colour_map[key] == value, 
                    f"module_colour_map[{key}] is not initialized correctly.")
    
    def test_possible_user_inputs_initialization(self, demo_model_dag):
        """Test that possible_user_inputs is initialized correctly."""
        expected_keys = [
            "animal_input", "equation_selection", "infusion_input", "user_diet", 
            "feed_library"
            ]
        assert (
            set(demo_model_dag.possible_user_inputs.keys()) == set(expected_keys), 
            "possible_user_inputs keys are incorrect."
            )

    def test_possible_constants_initialization(self, demo_model_dag):
        """Test that possible_constants is initialized correctly."""
        expected_keys = [
            "coeff_dict", "infusion_dict", "mpnp_efficiency_dict", 
            "mprt_coeff_dict", "f_imb"
            ]
        assert (
            set(demo_model_dag.possible_constants.keys()) == set(expected_keys), 
            "possible_constants keys are incorrect."
            )

    def test_user_inputs_initialization(self, demo_model_dag):
        """Test that user_inputs is initialized correctly."""
        assert (isinstance(demo_model_dag.user_inputs, list), 
                "user_inputs should be a list.")
        
        assert (len(demo_model_dag.user_inputs) > 0, 
                "user_inputs list should not be empty.")

    def test_get_py_files(self, demo_model_dag):
        expected_modules = [
            "./tests/model_dag/demo_model/module1.py", 
            "./tests/model_dag/demo_model/module2.py", 
            "./tests/model_dag/demo_model/module3.py"
            ]
        assert len(expected_modules) == len(demo_model_dag.modules)
        assert set(demo_model_dag.modules) == set(expected_modules)

    def test_dag_data_initialization(self, demo_model_dag):
        """Test that dag_data is initialized correctly."""
        def sort_lists_in_column(df, column_name):
            """Sort lists in the specified column of the DataFrame."""
            df[column_name] = df[column_name].apply(
                lambda x: sorted(x) if isinstance(x, list) else x
                )
            return df


        actual_dag_data_sorted = (
            demo_model_dag.dag_data.sort_values(by="Name").reset_index(drop=True)
            )
        expected_dag_data_sorted = (
            expected_dag_data.sort_values(by="Name").reset_index(drop=True)
            )
        actual_dag_data_sorted = sort_lists_in_column(
            actual_dag_data_sorted, 'Arguments'
            )
        expected_dag_data_sorted = sort_lists_in_column(
            expected_dag_data_sorted, 'Arguments'
            )
        pd.testing.assert_frame_equal(
            actual_dag_data_sorted, expected_dag_data_sorted
            )

    def test_draw_dag(self, demo_model_dag, tmpdir):
        """Test that the draw_dag method generates an image file successfully."""
        output_path = os.path.join(tmpdir, "dag_output.png")
        demo_model_dag.draw_dag(output_path)
        assert os.path.exists(output_path), "Graph image file was not created."

    def test_validate_dag(self, demo_model_dag):
        """Test that validate_dag method passes on a valid DAG."""
        try:
            demo_model_dag.validate_dag()
        except Exception as e:
            pytest.fail(f"validate_dag raised an exception on a valid DAG: {e}")

    @pytest.fixture
    def demo_model_dag_with_cycle(self):
        """Fixture to create a ModelDAG instance with a cycle."""
        dag = nd.ModelDAG(
            path="./tests/model_dag/demo_model", colour_map=demo_colour_map
            )
        # Introduce a cycle manually
        vertex1 = dag.name_to_vertex['Mlk_Prod']
        vertex2 = dag.name_to_vertex['Body_NPgain_g']
        dag.dag.add_edge(vertex1, vertex2)
        return dag
    
    def test_check_for_cycles(self, demo_model_dag_with_cycle):
        """
        Test that validate_dag method raises an error when there is a cycle in the DAG.
        """
        with pytest.raises(ValueError, match="Cycles detected in the DAG"):
            demo_model_dag_with_cycle._check_for_cycles()

    def test_validate_topological_order(self, demo_model_dag_with_cycle):
        with pytest.raises(
            ValueError, 
            match="Topological sort failed. DAG may contain cycles or other "
            ):
            demo_model_dag_with_cycle._validate_topological_order()

    def test_verify_connectivity(self, demo_model_dag_with_cycle):
        with pytest.raises(
            ValueError, 
            match="Vertex Body_NPgain_g has 3 incoming edges, but 2 were expected."
            ):
            demo_model_dag_with_cycle._verify_connectivity()

    @pytest.fixture
    def demo_model_dag_isolated_vertex(self):
        """Fixture to create a ModelDAG instance with an isolated vertex."""
        dag = nd.ModelDAG(
            path="./tests/model_dag/demo_model", colour_map=demo_colour_map
            )
        # Manually add an isolated vertex
        isolated_vertex = dag.dag.add_vertex()
        dag.vertex_labels[isolated_vertex] = "Isolated_Vertex"       
        dag.name_to_vertex["Isolated_Vertex"] = isolated_vertex 
        return dag

    def test_validate_dag_with_isolated_vertex(self, 
                                               demo_model_dag_isolated_vertex
    ):
        """
        Test that validate_dag method raises an error for isolated vertices.
        """
        with pytest.raises(
            ValueError, 
            match="Vertex Isolated_Vertex is isolated"
            ):
            demo_model_dag_isolated_vertex._verify_connectivity()

    @pytest.fixture
    def demo_model_dag_with_missing_edges(self):
        """Fixture to create a ModelDAG instance with missing edges."""
        dag = nd.ModelDAG(
            path="./tests/model_dag/demo_model", colour_map=demo_colour_map
            )
        # Remove an edge to simulate a missing edge scenario
        vertex1 = dag.name_to_vertex['Mlk_Prod']
        vertex2 = dag.name_to_vertex['Body_NPgain_g']
        dag.dag.remove_edge(dag.dag.edge(vertex2, vertex1))
        return dag

    def test_validate_dag_with_missing_edges(self, 
                                             demo_model_dag_with_missing_edges, 
                                             capsys
    ):
        """Test for missing expected edges in the DAG."""
        try:
            demo_model_dag_with_missing_edges._verify_connectivity()
        except ValueError as e:
            captured = capsys.readouterr()
            assert "Missing expected edges from:" in captured.out

    @pytest.fixture
    def demo_model_dag_vertex_not_found(self):
        """
        Fixture to create a ModelDAG instance where a vertex is not found in self.name_to_vertex.
        """
        dag = nd.ModelDAG(path="./tests/model_dag/demo_model", colour_map=demo_colour_map)
        del dag.name_to_vertex['Mlk_Prod']
        return dag

    def test_validate_dag_vertex_not_found(self, 
                                           demo_model_dag_vertex_not_found, 
                                           capsys
    ):
        """Test for vertex not found in self.name_to_vertex."""
        demo_model_dag_vertex_not_found._verify_connectivity()
        captured = capsys.readouterr()
        assert "was not found in self.name_to_vertex" in captured.out

    @pytest.fixture
    def demo_model_dag_incorrect_outgoing_edges(self):
        """
        Fixture to create a ModelDAG instance with incorrect outgoing edges.
        """
        dag = nd.ModelDAG(
            path="./tests/model_dag/demo_model", colour_map=demo_colour_map
            )
        new_vertex = dag.dag.add_vertex()
        dag.vertex_labels[new_vertex] = "Untracked_Vertex"
        tracked_vertex = dag.name_to_vertex['Mlk_Prod']
        dag.dag.add_edge(tracked_vertex, new_vertex)
        return dag

    def test_validate_dag_incorrect_outgoing_edges(self, 
                                                   demo_model_dag_incorrect_outgoing_edges, 
                                                   capsys
    ):
        """Test for incorrect number of outgoing edges in the DAG."""
        with pytest.raises(
            ValueError, 
            match="Vertex Mlk_Prod has 1 outgoing edges, but 0 were expected."
            ) as excinfo:
            demo_model_dag_incorrect_outgoing_edges._verify_connectivity()

        captured = capsys.readouterr()

        assert "has an incorrect number of outgoing edges" in captured.out
        assert "Expected 0 outgoing edges." in captured.out
        assert "Actual 1 outgoing edges." in captured.out
        
    def test_get_calculation_order(self, demo_model_dag, capsys):
        expected_functions = {
            "calculate_Rsrv_MEgain",
            "calculate_MlkFat_Milk",
            "calculate_MlkNP_Milk",
            "calculate_An_NELgain",
            "calculate_An_DigTPtIn",
            "calculate_Body_NPgain_g",
            "calculate_Mlk_Prod"
        }

        expected_user_inputs = {
            "animal_input": {
                "An_BW": None, 
                "Trg_MilkProd": None, 
                "An_BCS": None, 
                "Trg_MilkLacp": None, 
                "Trg_MilkTPp": None
                }
        }

        expected_constants = {
            "coeff_dict": {
                "MiTPValProf": None, 
                "Body_NP_CP": None, 
                "Body_Leu_TP": None
                }
        }
        result = demo_model_dag.get_calculation_order("Mlk_Prod", report=True)
        captured = capsys.readouterr()

        assert set(result["functions_order"]) == expected_functions, \
            "The functions order is not as expected."

        assert result["user_inputs"] == expected_user_inputs, \
            "The user inputs are not as expected."

        assert result["constants"] == expected_constants, \
            "The constants are not as expected."
 
        # Verify that each expected function is in the report
        for function in expected_functions:
            assert (function in captured.out, 
                    f"Expected function '{function}' not found in report.")

        # Verify the user inputs and constants sections of the report
        assert ("Required User Inputs:" in captured.out, 
                "User inputs section missing in report.")
        for input_key in expected_user_inputs["animal_input"]:
            assert (f"    - {input_key}" in captured.out, 
                    f"User input '{input_key}' not found in report.")

        assert ("Required Constants:" in captured.out, 
                "Constants section missing in report.")
        for const_key in expected_constants["coeff_dict"]:
            assert (f"    - {const_key}" in captured.out, 
                    f"Constant '{const_key}' not found in report.")

    @pytest.fixture
    def nasem_dag(self):
        return nd.ModelDAG()
    
    def test_create_function(self, nasem_dag):
        """
        Test the create_function method for generating a correct function for Du_MiCP.
        """
        target_variable = "Du_MiCP" 
        generated_function = nasem_dag.create_function(target_variable)

        assert (callable(generated_function), 
                "The generated function is not callable.")

        # Check the function's docstring to ensure it's correctly generated
        docstring = generated_function.__doc__
        assert "Dynamically generated function to calculate" in docstring, \
            "Docstring is not correctly generated."
        assert f"Arguments:" in docstring, \
            "Docstring does not contain the arguments section."
        assert f"Order of function calls:" in docstring, \
            "Docstring does not contain the order of function calls."
        assert f"Returns:" in docstring, \
            "Docstring does not contain the returns section."

        mock_inputs = {
            "infusion_input": {
                "Inf_CP_g": 100,  
                "Inf_CPBRum_CP": 50,
                "Inf_CPARum_CP": 30,
                "Inf_DM_g": 200,
                "Inf_CPCRum_CP": 10,
                "Inf_KdCPB": 0.1,
                "Inf_Location": 1,
                "Inf_NPNCP_g": 20
            },
            "animal_input": {
                "An_BCS": 3,
                "An_LactDay": 150,
                "An_AgeDryFdStart": 60,
                "An_BW_mature": 650,
                "Trg_MilkProd": 30,
                "An_GestDay": 100,
                "Trg_MilkTPp": 3.5,
                "An_StatePhys": 2,
                "An_BW": 600,
                "Trg_MilkFatp": 4.0,
                "Trg_MilkLacp": 0.4,
                "An_Parity_rl": 2,
                "Env_TempCurr": 25,
                "An_GestLength": 280,
                "Trg_Dt_DMIn": 15
            },
            "equation_selection": {
                "DMIn_eqn": 1,
                "MiN_eqn": 1
            },
            "user_diet": pd.DataFrame({
                "Feedstuff": [
                    "Alfalfa meal",
                    "Canola meal",
                    "Corn silage, typical",
                    "Corn grain HM, coarse grind"
                ],
                "kg_user": [4, 5, 2, 4]
            })
        }

        selected_feeds = nd.select_feeds(
            ["Alfalfa meal", "Canola meal", "Corn silage, typical",
             "Corn grain HM, coarse grind"
             ]
        )

        result = generated_function(
            infusion_input=mock_inputs["infusion_input"], 
            animal_input=mock_inputs["animal_input"], 
            equation_selection=mock_inputs["equation_selection"], 
            feed_library=selected_feeds, 
            user_diet=mock_inputs["user_diet"], 
            coeff_dict=nd.coeff_dict
        )

        assert isinstance(result, output.ModelOutput), \
            "The result is not an instance of ModelOutput."
        
        assert result.get_value(target_variable) == 1.4460342969801294

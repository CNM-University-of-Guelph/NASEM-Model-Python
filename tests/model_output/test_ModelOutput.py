import json
import os

import pandas as pd
import pytest

from nasem_dairy.model_output.ModelOutput import ModelOutput

class TestModelOutput:
    @pytest.fixture
    def mock_structure(self, tmp_path):
        structure = {
            "Inputs": {
                "user_diet": None,
                "animal_input": None,
            },
            "Intakes": {
                "diet_info": None,
            }
        }
        structure_path = tmp_path / "model_output_structure.json"
        with open(structure_path, "w") as f:
            json.dump(structure, f)
        return structure_path

    @pytest.fixture
    def mock_report_structure(self, tmp_path):
        report_structure = {
            "report1": {
                "col1": ["var1", "var2"],
                "col2": ["var3"]
            }
        }
        report_path = tmp_path / "report_structure.json"
        with open(report_path, "w") as f:
            json.dump(report_structure, f)
        return report_path

    @pytest.fixture
    def mock_locals_input(self):
        return {
            "user_diet": "value1",
            "animal_input": "value2",
            "diet_info": "value3",
            "key": "value4"
        }

    def test_initialization(self, mock_structure, mock_report_structure, mock_locals_input):
        model_output = ModelOutput(
            locals_input=mock_locals_input,
            config_path=str(mock_structure),
            report_config_path=str(mock_report_structure)
        )
        assert model_output.categories_structure == {
            "Inputs": {
                "user_diet": None,
                "animal_input": None,
            },
            "Intakes": {
                "diet_info": None,
            }
        }
        assert model_output.report_structure == {
            "report1": {
                "col1": ["var1", "var2"],
                "col2": ["var3"]
            }
        }
        assert model_output.dev_out == {"key": "value4"}
        assert model_output.locals_input == {}
        assert model_output.Inputs == {
            "user_diet": "value1",
            "animal_input": "value2",
        }
        assert model_output.Intakes == {
            "diet_info": "value3",
        }
        assert model_output.Uncategorized == {}

    def test_load_structure_file_not_found(self, tmp_path):
        invalid_path = tmp_path / "non_existent_structure.json"
        with pytest.raises(FileNotFoundError):
            ModelOutput(locals_input={}, config_path=str(invalid_path))

    def test_load_structure_invalid_json(self, tmp_path):
        invalid_json_path = tmp_path / "invalid_structure.json"
        with open(invalid_json_path, "w") as f:
            f.write("Invalid JSON Content")
        with pytest.raises(ValueError):
            ModelOutput(locals_input={}, config_path=str(invalid_json_path))
    
    def test_filter_locals_input(self, mock_structure, mock_report_structure):
        locals_input = {
            "key": "value",
            "value": "value",
            "num_value": "value",
            "user_diet": "diet_value",
            "animal_input": "animal_value"
        }
        model_output = ModelOutput(
            locals_input=locals_input,
            config_path=str(mock_structure),
            report_config_path=str(mock_report_structure)
        )
        assert model_output.dev_out == {
            "key": "value",
            "value": "value",
            "num_value": "value",
        }
        assert model_output.locals_input == {}
        assert model_output.Inputs == {
            "user_diet": "diet_value",
            "animal_input": "animal_value"
        }
        assert model_output.Uncategorized == {}

    @pytest.fixture
    def mock_structure_nested(self, tmp_path):
        nested_structure = {
            "Inputs": {
                "user_diet": None,
                "animal_input": None,
                "deep": {
                    "nested1": {
                        "nested2": {
                            "nested3": {
                                "nested4": {
                                    "nested5": {
                                        "deep_value1": None,
                                        "deep_value2": None
                                    },
                                    "value4": None
                                },
                                "value3": None
                            },
                            "value2": None
                        },
                        "value1": None
                    },
                    "value0": None
                }
            },
            "Intakes": {
                "diet_info": None,
            }
        }
        structure_path = tmp_path / "nested_model_output_structure.json"
        with open(structure_path, "w") as f:
            json.dump(nested_structure, f)
        return structure_path

    @pytest.fixture
    def mock_locals_input_nested(self):
        return {
            "user_diet": "value1",
            "animal_input": "value2",
            "diet_info": "value3",
            "deep_value1": "deep_value_data1",
            "deep_value2": "deep_value_data2",
            "value0": "data0",
            "value1": "data1",
            "value2": "data2",
            "value3": "data3",
            "value4": "data4",
            "uncategorized_key1": "uncategorized_value1",
            "uncategorized_key2": "uncategorized_value2"
        }

    def test_initialization_nested(self, mock_structure_nested, mock_report_structure, mock_locals_input_nested):
        model_output = ModelOutput(
            locals_input=mock_locals_input_nested,
            config_path=str(mock_structure_nested),
            report_config_path=str(mock_report_structure)
        )
        assert model_output.categories_structure == {
            "Inputs": {
                "user_diet": None,
                "animal_input": None,
                "deep": {
                    "nested1": {
                        "nested2": {
                            "nested3": {
                                "nested4": {
                                    "nested5": {
                                        "deep_value1": None,
                                        "deep_value2": None
                                    },
                                    "value4": None
                                },
                                "value3": None
                            },
                            "value2": None
                        },
                        "value1": None
                    },
                    "value0": None
                }
            },
            "Intakes": {
                "diet_info": None,
            }
        }
        assert model_output.report_structure == {
            "report1": {
                "col1": ["var1", "var2"],
                "col2": ["var3"]
            }
        }
        assert model_output.locals_input == {}
        assert model_output.Inputs == {
            "user_diet": "value1",
            "animal_input": "value2",
            "deep": {
                "nested1": {
                    "nested2": {
                        "nested3": {
                            "nested4": {
                                "nested5": {
                                    "deep_value1": "deep_value_data1",
                                    "deep_value2": "deep_value_data2"
                                },
                                "value4": "data4"
                            },
                            "value3": "data3"
                        },
                        "value2": "data2"
                    },
                    "value1": "data1"
                },
                "value0": "data0"
            }
        }
        assert model_output.Intakes == {
            "diet_info": "value3",
        }
        assert model_output.Uncategorized == {
            "uncategorized_key1": "uncategorized_value1",
            "uncategorized_key2": "uncategorized_value2"
        }

    @pytest.fixture
    def mock_snapshot_data(self):
        return {
            "Mlk_Prod_comp": 20.5,
            "MlkFat_Milk": 0.04,
            "MlkNP_Milk": 0.035,
            "Mlk_Prod_MPalow": 21.0,
            "Mlk_Prod_NEalow": 19.8,
            "An_MEIn": 250.0,
            "Trg_MEuse": 240.0,
            "An_MPIn_g": 2000,
            "An_MPuse_g_Trg": 1950,
            "An_RDPIn_g": 1800,
            "An_DCADmeq": 300
        }

    @pytest.fixture
    def mock_structure_snapshot(self, tmp_path):
        structure = {
            "Production": {
                "Mlk_Prod_comp": None,
                "MlkFat_Milk": None,
                "MlkNP_Milk": None,
                "Mlk_Prod_MPalow": None,
                "Mlk_Prod_NEalow": None
            },
            "Intakes": {
                "An_MEIn": None,
                "An_MPIn_g": None,
                "An_RDPIn_g": None,
                "An_DCADmeq": None
            },
            "Requirements": {
                "Trg_MEuse": None,
                "An_MPuse_g_Trg": None
            }
        }
        structure_path = tmp_path / "snapshot_model_output_structure.json"
        with open(structure_path, "w") as f:
            json.dump(structure, f)
        return structure_path

    def test_repr_html(self, mock_structure_snapshot, mock_report_structure, mock_snapshot_data):
        model_output = ModelOutput(
            locals_input=mock_snapshot_data,
            config_path=str(mock_structure_snapshot),
            report_config_path=str(mock_report_structure)
        )
        expected_html = """
        <div>
            <h2>Model Output Snapshot</h2>
            <table border="1" class="dataframe">
              <thead>
                <tr style="text-align: right;">
                  <th>Description</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Milk production kg (Mlk_Prod_comp)</td>
                  <td>20.500</td>
                </tr>
                <tr>
                  <td>Milk fat g/g (MlkFat_Milk)</td>
                  <td>0.040</td>
                </tr>
                <tr>
                  <td>Milk protein g/g (MlkNP_Milk)</td>
                  <td>0.035</td>
                </tr>
                <tr>
                  <td>Milk Production - MP allowable kg (Mlk_Prod_MPalow)</td>
                  <td>21.000</td>
                </tr>
                <tr>
                  <td>Milk Production - NE allowable kg (Mlk_Prod_NEalow)</td>
                  <td>19.800</td>
                </tr>
                <tr>
                  <td>Animal ME intake Mcal/d (An_MEIn)</td>
                  <td>250.000</td>
                </tr>
                <tr>
                  <td>Target ME use Mcal/d (Trg_MEuse)</td>
                  <td>240.000</td>
                </tr>
                <tr>
                  <td>Animal MP intake g/d (An_MPIn_g)</td>
                  <td>2000.000</td>
                </tr>
                <tr>
                  <td>Animal MP use g/d (An_MPuse_g_Trg)</td>
                  <td>1950.000</td>
                </tr>
                <tr>
                  <td>Animal RDP intake g/d (An_RDPIn_g)</td>
                  <td>1800.000</td>
                </tr>
                <tr>
                  <td>Diet DCAD meq (An_DCADmeq)</td>
                  <td>300.000</td>
                </tr>
              </tbody>
            </table>
            <hr>
            <details>
                <summary><strong>Click this drop-down for ModelOutput description</strong></summary>
                <p>This is a <code>ModelOutput</code> object returned by <code>nd.nasem()</code>.</p>
                <p>Each of the following categories can be called directly as methods, for example, if the name of my object is <code>output</code>, I would call <code>output.Production</code> to see the contents of Production.</p>
                <p>The following list shows which objects are within each category (most are dictionaries):</p>
                <ul>
                    <li><b>Intakes:</b> An_MEIn, An_MPIn_g, An_RDPIn_g, An_DCADmeq</li>
                    <li><b>Production:</b> Mlk_Prod_comp, MlkFat_Milk, MlkNP_Milk, Mlk_Prod_MPalow, Mlk_Prod_NEalow</li>
                    <li><b>Requirements:</b> Trg_MEuse, An_MPuse_g_Trg</li>
                    <li><b>Uncategorized:</b> </li>
                </ul>
                <div>
                    <p>There is a <code>.search()</code> method which takes a string and will return a dataframe of all outputs with that string (default is not case-sensitive), e.g., <code>output.search('Mlk', case_sensitive=False)</code>.</p>
                    <p>The Path that is returned by the <code>.search()</code> method can be used to access the parent object of the value in that row. 
                    For example, the Path for <code>Mlk_Fat_g</code> is <code>Production['milk']</code> which means that calling 
                    <code>output.Production['milk']</code> would show the dict that contains <code>Mlk_Fat_g</code>.</p>
                    <p>However, the safest way to retrieve an individual output is to do so directly by providing its exact name to the <code>.get_value()</code> method, e.g., <code>output.get_value('Mlk_Fat_g')</code>.</p>
                </div>
            </details>
        </div>
        """

        actual_html = model_output._repr_html_().replace('\n', '').replace('  ', '')

        assert actual_html == expected_html.replace('\n', '').replace('  ', '')

    def test_str(self, mock_structure_snapshot, mock_report_structure, mock_snapshot_data):
        model_output = ModelOutput(
            locals_input=mock_snapshot_data,
            config_path=str(mock_structure_snapshot),
            report_config_path=str(mock_report_structure)
        )
        expected_str = (
        "=====================\n"
        "Model Output Snapshot\n"
        "=====================\n"
        "Milk production kg (Mlk_Prod_comp): 20.5\n"
        "Milk fat g/g (MlkFat_Milk): 0.04\n"
        "Milk protein g/g (MlkNP_Milk): 0.035\n"
        "Milk Production - MP allowable kg (Mlk_Prod_MPalow): 21.0\n"
        "Milk Production - NE allowable kg (Mlk_Prod_NEalow): 19.8\n"
        "Animal ME intake Mcal/d (An_MEIn): 250.0\n"
        "Target ME use Mcal/d (Trg_MEuse): 240.0\n"
        "Animal MP intake g/d (An_MPIn_g): 2000\n"
        "Animal MP use g/d (An_MPuse_g_Trg): 1950\n"
        "Animal RDP intake g/d (An_RDPIn_g): 1800\n"
        "Diet DCAD meq (An_DCADmeq): 300\n"
        "\n"
        "This is a `ModelOutput` object with methods to access all model outputs. See help(ModelOutput)."
        )
        actual_str = str(model_output)
        assert actual_str == expected_str

    @pytest.fixture
    def mock_structure_get_value(self, tmp_path):
        structure = {
            "Inputs": {
                "string_value": None,
                "int_value": None,
                "float_value": None,
                "dict_value": {"nested_key": None},
                "df_value": None
            },
            "Outputs": {
                "another_value": None
            }
        }
        structure_path = tmp_path / "get_value_model_output_structure.json"
        with open(structure_path, "w") as f:
            json.dump(structure, f)
        return structure_path

    @pytest.fixture
    def mock_locals_input_get_value(self):
        return {
            "string_value": "example string",
            "int_value": 123,
            "float_value": 45.67,
            "nested_key": "nested value",
            "df_value": pd.DataFrame({
                "column1": [1, 2, 3],
                "column2": ["a", "b", "c"]
            })
        }

    def test_get_value(self, mock_structure_get_value, mock_report_structure, mock_locals_input_get_value):
        model_output = ModelOutput(
            locals_input=mock_locals_input_get_value,
            config_path=str(mock_structure_get_value),
            report_config_path=str(mock_report_structure)
        )
        assert model_output.get_value("string_value") == "example string"
        assert model_output.get_value("int_value") == 123
        assert model_output.get_value("float_value") == 45.67
        assert model_output.get_value("dict_value") == {"nested_key": "nested value"}
        pd.testing.assert_frame_equal(
            model_output.get_value("df_value"),
            pd.DataFrame({"column1": [1, 2, 3], "column2": ["a", "b", "c"]})
        )
        assert model_output.get_value("nested_key") == "nested value"
        pd.testing.assert_series_equal(
            model_output.get_value("column1"),
            pd.Series([1, 2, 3], name="column1")
        )
        inputs = model_output.get_value("Inputs")
        print("Inputs:", inputs) 
        print(model_output.Uncategorized)
        assert inputs["string_value"] == "example string"
        assert inputs["int_value"] == 123
        assert inputs["float_value"] == 45.67
        assert inputs["dict_value"] == {"nested_key": "nested value"}
        pd.testing.assert_frame_equal(
            inputs["df_value"],
            pd.DataFrame({"column1": [1, 2, 3], "column2": ["a", "b", "c"]})
        )
        assert model_output.get_value("non_existent_value") is None

    @pytest.fixture
    def mock_structure_search(self, tmp_path):
        structure = {
            "Inputs": {
                "string_value": None,
                "int_value": None,
                "float_value": None,
                "dict_value": {"nested_key": None},
                "df_value": None,
                "list_value": None,
            },
            "Outputs": {
                "another_value": None
            }
        }
        structure_path = tmp_path / "search_model_output_structure.json"
        with open(structure_path, "w") as f:
            json.dump(structure, f)
        return structure_path

    @pytest.fixture
    def mock_locals_input_search(self):
        return {
            "string_value": "example string",
            "int_value": 123,
            "float_value": 45.67,
            "nested_key": "nested value",
            "df_value": pd.DataFrame({
                "column1": [1, 2, 3],
                "column2": ["a", "b", "c"]
            }),
            "another_value": "output value",
            "list_value": ["item1", "item2", "item3"],
        }

    def test_search(self, mock_structure_search, mock_report_structure, mock_locals_input_search):
        model_output = ModelOutput(
            locals_input=mock_locals_input_search,
            config_path=str(mock_structure_search),
            report_config_path=str(mock_report_structure)
        )
        search_df = model_output.search("string_value")
        expected_df = pd.DataFrame([{
            "Name": "string_value",
            "Value": "example string",
            "Category": "Inputs",
            "Level 1": "string_value"
        }])
        pd.testing.assert_frame_equal(search_df, expected_df)

        search_df = model_output.search("int_value")
        expected_df = pd.DataFrame([{
            "Name": "int_value",
            "Value": 123,
            "Category": "Inputs",
            "Level 1": "int_value"
        }])
        pd.testing.assert_frame_equal(search_df, expected_df)

        search_df = model_output.search("float_value")
        expected_df = pd.DataFrame([{
            "Name": "float_value",
            "Value": 45.67,
            "Category": "Inputs",
            "Level 1": "float_value"
        }])
        pd.testing.assert_frame_equal(search_df, expected_df)

        search_df = model_output.search("nested_key")
        expected_df = pd.DataFrame([{
            "Name": "nested_key",
            "Value": "nested value",
            "Category": "Inputs",
            "Level 1": "dict_value",
            "Level 2": "nested_key"
        }])
        pd.testing.assert_frame_equal(search_df, expected_df)

        search_df = model_output.search("df_value")
        expected_df = pd.DataFrame([{
            "Name": "df_value",
            "Value": "DataFrame",
            "Category": "Inputs",
            "Level 1": "df_value"
        }])
        pd.testing.assert_frame_equal(search_df, expected_df)

        search_df = model_output.search("column1")
        expected_df = pd.DataFrame([{
            "Name": "column1",
            "Value": "pd.Series",
            "Category": "Inputs",
            "Level 1": "df_value",
            "Level 2": "column1"
        }])
        pd.testing.assert_frame_equal(search_df, expected_df)

        search_df = model_output.search("non_existent_value")
        expected_df = pd.DataFrame(columns=['Name', 'Value', 'Category', 'Level 1', 'Level 2'])
        pd.testing.assert_frame_equal(search_df, expected_df)

        search_df = model_output.search("list_value")
        expected_df = pd.DataFrame([{
            "Name": "list_value",
            "Value": "List",
            "Category": "Inputs",
            "Level 1": "list_value"
        }])
        pd.testing.assert_frame_equal(search_df, expected_df)

        search_df = model_output.search("dict_value")
        expected_df = pd.DataFrame([
            {
                "Name": "dict_value",
                "Value": "Dictionary",
                "Category": "Inputs",
                "Level 1": "dict_value",
                "Level 2": ""
            },
            {
                "Name": "nested_key",
                "Value": "nested value",
                "Category": "Inputs",
                "Level 1": "dict_value",
                "Level 2": "nested_key"
            }
        ])

        pd.testing.assert_frame_equal(search_df, expected_df)

    def test_export_to_dict(self, mock_structure_search, mock_report_structure, mock_locals_input_search):
        model_output = ModelOutput(
            locals_input=mock_locals_input_search,
            config_path=str(mock_structure_search),
            report_config_path=str(mock_report_structure)
        )

        # Export data to dictionary
        exported_dict = model_output.export_to_dict()

        # Expected output dictionary
        expected_dict = {
            "string_value": "example string",
            "int_value": 123,
            "float_value": 45.67,
            "nested_key": "nested value",
            "df_value": pd.DataFrame({
                "column1": [1, 2, 3],
                "column2": ["a", "b", "c"]
            }),
            "another_value": "output value",
            "list_value": ["item1", "item2", "item3"],
        }
        print(exported_dict)
        assert exported_dict["string_value"] == expected_dict["string_value"]
        assert exported_dict["int_value"] == expected_dict["int_value"]
        assert exported_dict["float_value"] == expected_dict["float_value"]
        assert exported_dict["nested_key"] == expected_dict["nested_key"]
        assert exported_dict["another_value"] == expected_dict["another_value"]
        assert exported_dict["list_value"] == expected_dict["list_value"]
        pd.testing.assert_frame_equal(exported_dict["df_value"], expected_dict["df_value"])

    @pytest.fixture
    def mock_report_structure_test(self, tmp_path):
        report_structure = {
            "SampleReport": {
                "Description": ["Description 1", "Description 2"],
                "Target Performance": ["Performance 1", "Performance 2"],
                "Values": ["int_value", "float_value"],
                "Total": ["int_value", "float_value"],
                "Footnote": {"Footnote 1": "This is a footnote."}
            }
        }
        report_path = tmp_path / "report_structure.json"
        with open(report_path, "w") as f:
            json.dump(report_structure, f)
        return report_path

    @pytest.fixture
    def mock_locals_input_report(self):
        return {
            "string_value": "example string",
            "int_value": 123,
            "float_value": 45.67,
            "nested_key": "nested value",
            "df_value": pd.DataFrame({
                "column1": [1, 2, 3],
                "column2": ["a", "b", "c"]
            }),
            "another_value": "output value",
            "list_value": ["item1", "item2", "item3"],
            "nested_list": [[1, 2, {"inner_key": "inner_value"}], ["a", "b", "c"], {"key": "value"}],
            "dict_with_list": {"key": [1, 2, 3, 4]}
        }

    def test_get_report(self, mock_structure_search, mock_report_structure_test, mock_locals_input_report):
        model_output = ModelOutput(
            locals_input=mock_locals_input_report,
            config_path=str(mock_structure_search),
            report_config_path=str(mock_report_structure_test)
        )
        report_df = model_output.get_report("SampleReport")
        expected_data = {
            "Description": ["Description 1", "Description 2", "Total", "Footnote 1"],
            "Target Performance": ["Performance 1", "Performance 2", 123, "This is a footnote."],
            "Values": [123, 45.67, 45.67, ""]
        }
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(report_df, expected_df)

    def test_get_category_list(self, mock_structure, mock_report_structure, mock_locals_input):
        model_output = ModelOutput(
            locals_input=mock_locals_input,
            config_path=str(mock_structure),
            report_config_path=str(mock_report_structure)
        )
        category_list = model_output.categories
        expected_categories = ["Inputs", "Intakes", "Uncategorized"]
        assert category_list == expected_categories
    
    def test_extract_variable_names(self, mock_structure, mock_report_structure, mock_locals_input):
        # Adding a DataFrame to the locals input for testing
        mock_locals_input["df_value"] = pd.DataFrame({
            "column1": [1, 2, 3],
            "column2": ["a", "b", "c"]
        })
        model_output = ModelOutput(
            locals_input=mock_locals_input,
            config_path=str(mock_structure),
            report_config_path=str(mock_report_structure)
        )
        variable_names = model_output.export_variable_names()
        expected_variable_names = [
            "user_diet", "animal_input", "diet_info", "column1", "column2"
        ]
        assert sorted(variable_names) == sorted(expected_variable_names)

import pytest
import pandas as pd
import os
from io import StringIO
import nasem_dairy as nd 


def test_read_csv_input():
    csv_data = """Location,Variable,Value
equation_selection,Use_DNDF_IV,0
equation_selection,DMIn_eqn,0
equation_selection,mProd_eqn,0
equation_selection,MiN_eqn,1
user_diet,Alfalfa meal,8.2101564407
user_diet,Canola meal,6.7323288918
animal_input,An_BW,624.795
infusion_input,Inf_DM_g,0.0
"""

    csv_file = StringIO(csv_data)
    user_diet, animal_input, equation_selection, infusion_input = (
        nd.read_csv_input(csv_file)
        )

    expected_user_diet = pd.DataFrame({
        'Feedstuff': ['Alfalfa meal', 'Canola meal'],
        'kg_user': [8.2101564407, 6.7323288918]
    })

    expected_animal_input = {
        'An_BW': 624.795
    }

    expected_equation_selection = {
        'Use_DNDF_IV': 0.0,
        'DMIn_eqn': 0.0,
        'mProd_eqn': 0.0,
        'MiN_eqn': 1.0
    }

    expected_infusion_input = {
        'Inf_DM_g': 0.0
    }

    pd.testing.assert_frame_equal(user_diet, expected_user_diet)
    assert animal_input == expected_animal_input
    assert equation_selection == expected_equation_selection
    assert infusion_input == expected_infusion_input


def test_adjust_diet():
    diet1 = pd.DataFrame({
        "Feedstuff": [
            "Alfalfa meal", "Blood meal, low dRUP", "Corn and cob meal, dry", 
            "Wheat bran"
        ],
        "kg_user": [6.5, 3.0, 4.7, 5.1]
    })
    
    diet2 = pd.DataFrame({
        "Feedstuff": [
            "Selenium yeast, generic", "Manganese chloride (4H2O)", "Beet pulp, dry",
            "Barley grain, dry, ground", "Millet silage"
        ],
        "kg_user": [1.0, 1.0, 3.0, 4.94, 5.6]
    })
    
    diet3 = pd.DataFrame({
        "Feedstuff": [
            "Triticale grain", "Whey, wet", "Rumen Protected Thr", "Oat hulls",
            "Flaxseed", "Copper oxide"
        ],
        "kg_user": [4.3, 3.534, 2, 4.76, 3.4, 3.1]
    })
    nutrients_to_adjust = [
        ("Fd_CP", "Dt_CP"), 
        ("Fd_NDF", "Dt_NDF")
    ]
    expected_values_1 = {
        "Dt_CP": 19.57,
        "Dt_NDF": 29.0,
    }
    expected_values_2 = {
        "Dt_CP": 24.7,
        "Dt_NDF": 19.2,
    }
    expected_values_3 = {
        "Dt_CP": 26,
        "Dt_NDF": 30,
    }
    diets = [
        (diet1, expected_values_1),
        (diet2, expected_values_2),
        (diet3, expected_values_3)
    ]
    _, animal, equation, _ = nd.demo("lactating_cow_test")
    for diet, expected_values in diets:
        adjusted_feed_library, _ = nd.adjust_diet(
            animal, equation, diet, expected_values, nutrients_to_adjust
        )
        adjusted_output = nd.nasem(
            diet, animal, equation, feed_library=adjusted_feed_library
        )
        for nutrient, expected_value in expected_values.items():
            assert adjusted_output.get_value(nutrient) == pytest.approx(
                expected_value, rel=1e-2
            )

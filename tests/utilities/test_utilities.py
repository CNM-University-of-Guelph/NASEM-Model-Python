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

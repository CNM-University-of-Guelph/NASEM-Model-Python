import pytest

from nasem_dairy.ration_balancer.input_validation import validate_infusion_input

type_mapping = {
    "Inf_Acet_g": float,
    "Inf_ADF_g": float,
    "Inf_Arg_g": float,
    "Inf_Ash_g": float,
    "Inf_Butr_g": float,
    "Inf_CP_g": float,
    "Inf_CPARum_CP": float,
    "Inf_CPBRum_CP": float,
    "Inf_CPCRum_CP": float,
    "Inf_dcFA": float,
    "Inf_dcRUP": float,
    "Inf_DM_g": float,
    "Inf_EE_g": float,
    "Inf_FA_g": float,
    "Inf_Glc_g": float,
    "Inf_His_g": float,
    "Inf_Ile_g": float,
    "Inf_KdCPB": float,
    "Inf_Leu_g": float,
    "Inf_Lys_g": float,
    "Inf_Met_g": float,
    "Inf_NDF_g": float,
    "Inf_NPNCP_g": float,
    "Inf_Phe_g": float,
    "Inf_Prop_g": float,
    "Inf_St_g": float,
    "Inf_Thr_g": float,
    "Inf_Trp_g": float,
    "Inf_ttdcSt": float,
    "Inf_Val_g": float,
    "Inf_VFA_g": float,
    "Inf_Location": str
}


def test_not_a_dictionary():
    with pytest.raises(TypeError, match="must be a dict"):
        validate_infusion_input(["not", "a", "dict"])


def test_missing_key_raises_key_error():
    infusion_input = {
        "Inf_Acet_g": 4.5,
    }
    with pytest.raises(KeyError, match="The following keys are missing: "):
        validate_infusion_input(infusion_input)


def test_invalid_inf_location_value():
    infusion_dict = {
        'Inf_Acet_g': 0.0,
        'Inf_ADF_g': 0.0,
        'Inf_Arg_g': 0.0,
        'Inf_Ash_g': 0.0,
        'Inf_Butr_g': 0.0,
        'Inf_CP_g': 0.0,
        'Inf_CPARum_CP': 0.0,
        'Inf_CPBRum_CP': 0.0,
        'Inf_CPCRum_CP': 0.0,
        'Inf_dcFA': 0.0,
        'Inf_dcRUP': 0.0,
        'Inf_DM_g': 0.0,
        'Inf_EE_g': 0.0,
        'Inf_FA_g': 0.0,
        'Inf_Glc_g': 0.0,
        'Inf_His_g': 0.0,
        'Inf_Ile_g': 0.0,
        'Inf_KdCPB': 0.0,
        'Inf_Leu_g': 0.0,
        'Inf_Lys_g': 0.0,
        'Inf_Met_g': 0.0,
        'Inf_NDF_g': 0.0,
        'Inf_NPNCP_g': 0.0,
        'Inf_Phe_g': 0.0,
        'Inf_Prop_g': 0.0,
        'Inf_St_g': 0.0,
        'Inf_Thr_g': 0.0,
        'Inf_Trp_g': 0.0,
        'Inf_ttdcSt': 0.0,
        'Inf_Val_g': 0.0,
        'Inf_VFA_g': 0.0,
        'Inf_Location': "Stomach"
    }
    with pytest.raises(ValueError, match="Inf_Location must be one of"):
        validate_infusion_input(infusion_dict)


def test_correct_data_types():
    infusion_input = {
        'Inf_Acet_g': "0",
        'Inf_ADF_g': "0",
        'Inf_Arg_g': "0",
        'Inf_Ash_g': "0",
        'Inf_Butr_g': "0",
        'Inf_CP_g': "0",
        'Inf_CPARum_CP': "0",
        'Inf_CPBRum_CP': "0",
        'Inf_CPCRum_CP': "0",
        'Inf_dcFA': "0",
        'Inf_dcRUP': "0",
        'Inf_DM_g': "0",
        'Inf_EE_g': "0",
        'Inf_FA_g': "0",
        'Inf_Glc_g': "0",
        'Inf_His_g': "0",
        'Inf_Ile_g': "0",
        'Inf_KdCPB': "0",
        'Inf_Leu_g': "0",
        'Inf_Lys_g': "0",
        'Inf_Met_g': "0",
        'Inf_NDF_g': "0",
        'Inf_NPNCP_g': "0",
        'Inf_Phe_g': "0",
        'Inf_Prop_g': "0",
        'Inf_St_g': "0",
        'Inf_Thr_g': "0",
        'Inf_Trp_g': "0",
        'Inf_ttdcSt': "0",
        'Inf_Val_g': "0",
        'Inf_VFA_g': "0",
        'Inf_Location': "Rumen"
    }
    result = validate_infusion_input(infusion_input)
    for key, value in infusion_input.items():
        assert isinstance(result[key], type_mapping.get(key, str))


def test_invalid_conversion():
    infusion_input = {
        'Inf_Acet_g': "zero",
        'Inf_ADF_g': "0",
        'Inf_Arg_g': "0",
        'Inf_Ash_g': "0",
        'Inf_Butr_g': "0",
        'Inf_CP_g': "0",
        'Inf_CPARum_CP': "0",
        'Inf_CPBRum_CP': "0",
        'Inf_CPCRum_CP': "0",
        'Inf_dcFA': "0",
        'Inf_dcRUP': "0",
        'Inf_DM_g': "0",
        'Inf_EE_g': "0",
        'Inf_FA_g': "0",
        'Inf_Glc_g': "0",
        'Inf_His_g': "0",
        'Inf_Ile_g': "0",
        'Inf_KdCPB': "0",
        'Inf_Leu_g': "0",
        'Inf_Lys_g': "0",
        'Inf_Met_g': "0",
        'Inf_NDF_g': "0",
        'Inf_NPNCP_g': "0",
        'Inf_Phe_g': "0",
        'Inf_Prop_g': "0",
        'Inf_St_g': "0",
        'Inf_Thr_g': "0",
        'Inf_Trp_g': "0",
        'Inf_ttdcSt': "0",
        'Inf_Val_g': "0",
        'Inf_VFA_g': "0",
        'Inf_Location': "Rumen"
    }
    with pytest.raises(
        TypeError, 
        match="Value for Inf_Acet_g must be of type float. Got str instead "
              "and failed to convert."
         ):
        validate_infusion_input(infusion_input)


def test_valid_input():
    infusion_input = {
        'Inf_Acet_g': 0.0,
        'Inf_ADF_g': 0.0,
        'Inf_Arg_g': 0.0,
        'Inf_Ash_g': 0.0,
        'Inf_Butr_g': 0.0,
        'Inf_CP_g': 0.0,
        'Inf_CPARum_CP': 0.0,
        'Inf_CPBRum_CP': 0.0,
        'Inf_CPCRum_CP': 0.0,
        'Inf_dcFA': 0.0,
        'Inf_dcRUP': 0.0,
        'Inf_DM_g': 0.0,
        'Inf_EE_g': 0.0,
        'Inf_FA_g': 0.0,
        'Inf_Glc_g': 0.0,
        'Inf_His_g': 0.0,
        'Inf_Ile_g': 0.0,
        'Inf_KdCPB': 0.0,
        'Inf_Leu_g': 0.0,
        'Inf_Lys_g': 0.0,
        'Inf_Met_g': 0.0,
        'Inf_NDF_g': 0.0,
        'Inf_NPNCP_g': 0.0,
        'Inf_Phe_g': 0.0,
        'Inf_Prop_g': 0.0,
        'Inf_St_g': 0.0,
        'Inf_Thr_g': 0.0,
        'Inf_Trp_g': 0.0,
        'Inf_ttdcSt': 0.0,
        'Inf_Val_g': 0.0,
        'Inf_VFA_g': 0.0,
        'Inf_Location': "Rumen"
    }
    result = validate_infusion_input(infusion_input)
    assert result == infusion_input

import pytest
from nasem_dairy.ration_balancer.default_values_dictionaries import coeff_dict, infusion_dict
# from nasem_dairy.NASEM_equations.dev_DMI_equations import calculate_Kb_LateGest_DMIn, calculate_An_PrePartWklim, calculate_Dt_DMIn_Heif_LateGestInd, calculate_Dt_DMIn_Heif_LateGestPen, calculate_Dt_NDFdev_DMI, calculate_Dt_DMIn_Heif_NRCa, calculate_Dt_DMIn_Heif_NRCad, calculate_Dt_DMIn_Heif_H1, calculate_Dt_DMIn_Heif_H2, calculate_Dt_DMIn_Heif_HJ1, calculate_Dt_DMIn_Heif_HJ2, calculate_Dt_DMIn_Lact1
from nasem_dairy.NASEM_equations.dev_DMI_equations import (
    calculate_Kb_LateGest_DMIn,
    calculate_An_PrePartWklim,
    calculate_Dt_DMIn_Heif_LateGestInd,
    calculate_Dt_DMIn_Heif_LateGestPen,
    calculate_Dt_NDFdev_DMI,
    calculate_Dt_DMIn_Heif_NRCa,
    calculate_Dt_DMIn_Heif_NRCad,
    calculate_Dt_DMIn_Heif_H1,
    calculate_Dt_DMIn_Heif_H2,
    calculate_Dt_DMIn_Heif_HJ1,
    calculate_Dt_DMIn_Heif_HJ2,
    calculate_Dt_DMIn_Lact1,
    calculate_Dt_DMIn_BW_LateGest_i,
    calculate_Dt_DMIn_BW_LateGest_p,
    calculate_Dt_DMIn_DryCow1_FarOff,
    calculate_Dt_DMIn_DryCow1_Close,
    calculate_Dt_DMIn_DryCow2
)


### Kb_LateGest_DMIn ###
def test_Kb_LateGest_DMIn_below_range():
    result = calculate_Kb_LateGest_DMIn(20)
    assert result == pytest.approx(-0.280999999), "Kb_LateGest_DMIn does not equal -0.280999"

def test_Kb_LateGest_DMIn_at_lower_limit():
    result = calculate_Kb_LateGest_DMIn(30)
    assert result == pytest.approx(-0.280999999), "Kb_LateGest_DMIn does not equal -0.280999"

def test_Kb_LateGest_DMIn_in_range():
    result = calculate_Kb_LateGest_DMIn(45.2)
    assert result == pytest.approx(-0.238439999), "Kb_LateGest_DMIn does not equal -0.238439"

def test_Kb_LateGest_DMIn_at_upper_limit():
    result = calculate_Kb_LateGest_DMIn(55)
    assert result == pytest.approx(-0.211), "Kb_LateGest_DMIn does not equal -0.211"

def test_Kb_LateGest_DMIn_above_range():
    result = calculate_Kb_LateGest_DMIn(70)
    assert result == pytest.approx(-0.211), "Kb_LateGest_DMIn does not equal -0.211"


### An_PrePartWklim ###
def test_An_PrePartWklim_below_range():
    result = calculate_An_PrePartWklim(-7)
    assert result == -3, "An_PrePartWklim does not equal -3"

def test_An_PrePartWklim_at_lower_limit():
    result = calculate_An_PrePartWklim(-3)
    assert result == -3, "An_PrePartWklim does not equal -3"

def test_An_PrePartWklim_in_range():
    result = calculate_An_PrePartWklim(-1)
    assert result == -1, "An_PrePartWklim does not equal -1"

def test_An_PrePartWklim_at_upper_limit():
    result = calculate_An_PrePartWklim(0)
    assert result == 0, "An_PrePartWklim does not equal 0"

def test_An_PrePartWklim_above_range():
    result = calculate_An_PrePartWklim(2)
    assert result == 0, "An_PrePartWklim does not equal 0"


def test_Dt_DMIn_Heif_LateGestInd():
    result = calculate_Dt_DMIn_Heif_LateGestInd(910, 1.8)
    assert result == pytest.approx(14.4144), "Dt_DMIn_Heif_LateGestInd does not equal 13.4134"


def test_Dt_DMIn_Heif_LateGestPen():
    result = calculate_Dt_DMIn_Heif_LateGestPen(645, 1.25)
    assert result == pytest.approx(7.095),"Dt_DMIn_Heif_LateGestPen does not equal 9.67947199"
    

def test_Dt_NDFdev_DMI():
    result = calculate_Dt_NDFdev_DMI(775, 44)
    assert result == pytest.approx(-3.310924999), "Dt_NDFdev_DMI does not equal -3.310924999"


def test_Dt_DMIn_Heif_NRCa():
    result = calculate_Dt_DMIn_Heif_NRCa(873, 750)
    assert result == pytest.approx(13.752200578),"Dt_DMIn_Heif_NRCa does not equal 13.752200578"


def test_Dt_DMIn_Heif_NRCad():
    result = calculate_Dt_DMIn_Heif_NRCad(672, 750, 51)
    assert result == pytest.approx(16.250055265),"Dt_DMIn_Heif_NRCad does not equal 16.250055265"


def test_Dt_DMIn_Heif_H1():
    result = calculate_Dt_DMIn_Heif_H1(719)
    assert result == pytest.approx(12.201912168), "Dt_DMIn_Heif_H1 does not equal 12.201912168"


def test_Dt_DMIn_Heif_H2():
    result = calculate_Dt_DMIn_Heif_H2(842, -3.5)
    assert result == pytest.approx(13.382596542),"Dt_DMIn_Heif_H2 does not equal 13.382596542"


def test_Dt_DMIn_Heif_HJ1():
    result = calculate_Dt_DMIn_Heif_HJ1(757)
    assert result == pytest.approx(11.526173891),"Dt_DMIn_Heif_HJ1 does not equal 11.526173891"


def test_Dt_DMIn_Heif_HJ2():
    result = calculate_Dt_DMIn_Heif_HJ2(794, -3.3)
    assert result == pytest.approx(12.170628031),"Dt_DMIn_Heif_HJ2 does not equal 12.170628031"


def test_Dt_DMIn_Lact1():
    result = calculate_Dt_DMIn_Lact1(30, 700, 3, 160, 1, 0.75)
    assert result == pytest.approx(23.894448), "Dt_DMIn_Lact1 does not equal 23.894448"
    

def test_Dt_DMIn_BW_LateGest_i():
    result = calculate_Dt_DMIn_BW_LateGest_i(-3, -0.5, coeff_dict)
    assert result == pytest.approx(2.655),"Dt_DMIn_BW_LateGest_i should equal 2.655"


def test_Dt_DMIn_BW_LateGest_p():
    result = calculate_Dt_DMIn_BW_LateGest_p(-2, -0.3, coeff_dict)
    assert result == pytest.approx(1.7233333333333334),"Dt_DMIn_BW_LateGest_p should equal 1.72333"


def test_Dt_DMIn_DryCow1_FarOff():
    result = calculate_Dt_DMIn_DryCow1_FarOff(820, 1.9)
    assert result == pytest.approx(15.58),"Dt_DMIn_DryCow1_FarOff should equal 15.58"


def test_Dt_DMIn_DryCow1_Close():
    result = calculate_Dt_DMIn_DryCow1_Close(755, 1.7)
    assert result == pytest.approx(12.835),"Dt_DMIn_DryCow1_Close should equal 12.835"


def test_Dt_DMIn_DryCow2():
    result = calculate_Dt_DMIn_DryCow2(675, 105, 280)
    assert result == pytest.approx(13.35825),"Dt_DMIn_DryCow2 should equal 13.35825"

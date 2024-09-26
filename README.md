# The NASEM 2021 Nutrient Requirements of Dairy Cattle Model in Python

![Build Status](https://github.com/CNM-University-of-Guelph/NASEM-Model-Python/actions/workflows/ci.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/CNM-University-of-Guelph/NASEM-Model-Python/badge.svg?branch=main)](https://coveralls.io/github/CNM-University-of-Guelph/NASEM-Model-Python?branch=main)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/CNM-University-of-Guelph/NASEM-Model-Python/blob/main/LICENSE)


- [Installation](#installation)
- [Using the Model](#using-the-model)
  - [Import package](#import-package)
  - [Get input data](#get-input-data)
  - [Execute Model](#execute-model)

This is a python version of the Nutrient Requirments of Dairy Cattle 8th
revisied edition (NASEM
2021)\[https://nap.nationalacademies.org/catalog/25806/nutrient-requirements-of-dairy-cattle-eighth-revised-edition\]
model. The equations have been copied from the R functions released with the official NASEM software:
https://nap.nationalacademies.org/resource/25806/Installation_Instructions_NASEM_Dairy8.pdf

## License

This project is distributed under the terms of the [MIT License](./LICENSE).

### Code Attribution

The NASEM equations were coppied from the R code that was distributed under different licensing terms. The original R code is distributed under a [separate license](./LICENSE-R_Code).

Please refer to both the [MIT License](./LICENSE) and the [R Code License](./LICENSE-R_Code) for detailed terms.

## Contributing

We welcome contributions! Please read our [Contributing Guidelines](./CONTRIBUTING.md) to get started.

## Installation

This package can be installed through a terminal using:

    pip install nasem_dairy

The environment that this is installed into will require
`python >= 3.10`. It will also install `pandas` and `numpy`
automatically.

The suggested way to install this is inside a virtual environment. For
example, by using [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

1.  Open a terminal window, e.g., Anaconda Prompt.

2.  Create a new conda environment with Python installed:

        conda create --name myenvironment python>=3.10

        conda activate myenvironment

3.  Install this package via pip:

        pip install nasem_dairy

## Using the Model

### Import package

First, import `nasem_dairy`. `pandas` is also required if you want to modify the user_diet input.

``` python
import nasem_dairy as nd
import pandas as pd
```

### Get input data

There are several demo scenarios built into the app which can be used as input to the
model. These can be acessed using `nd.demo()`:

``` python
user_diet, animal_input, equation_selection, infusion_input = nd.demo("lactating_cow_test")
```
These 4 inputs can be modified to simulate different scenarios:
- user_diet (pd.DataFrame): The name and kg/d to feed for each ingredient in the diet.
- animal_input (dict): Parameters to descibe the animal being modelled. 
- equation_selection (dict): Select which equation to use when there are multiple options.
- infusion_input (dict): If simulating infusions specify this here. This is optional.

### Execute Model

To run the model use `nd.nasem` and pass the input data. This will return an instance of the nd.ModelOutput. 
Printing this will provide a snapshot of the results. 

``` python
## RUN MODEL ###
output = nd.nasem(
    user_diet = user_diet_in, 
    animal_input = animal_input_in, 
    equation_selection = equation_selection_in, 
    infusion_input = infusion_input)

print(output)
```

    =====================
    Model Output Snapshot
    =====================
    Milk production kg (Mlk_Prod_comp): 34.197
    Milk fat g/g (MlkFat_Milk): 0.053
    Milk protein g/g (MlkNP_Milk): 0.037
    Milk Production - MP allowable kg (Mlk_Prod_MPalow): 35.906
    Milk Production - NE allowable kg (Mlk_Prod_NEalow): 31.261
    Animal ME intake Mcal/d (An_MEIn): 59.976
    Target ME use Mcal/d (Trg_MEuse): 52.195
    Animal MP intake g/d (An_MPIn_g): 2565.214
    Animal MP use g/d (An_MPuse_g_Trg): 1989.985
    Animal RDP intake g/d (An_RDPIn_g): 3556.058
    Diet DCAD meq (An_DCADmeq): 96.453

    This is a `ModelOutput` object with methods to access all model outputs. See help(ModelOutput).


### Exploring the Results

The `nd.ModelOutput` class provides several methods to help you explore the results.

If you need a specific value you can used `get_value()`.

```python
Du_MiCP = output.get_value("Du_MiCP")
print(Du_MiCP)
```

    2.0524052134583415

If you don't know the exact name of the variable you can use the `search()` method.
For example if you want to see values related to microbial crude protein (MiCP) you
could search for "MiCP".

```python
print(output.search("MiCP"))
```
                    Name                                              Value    Category     Level 1           Level 2
    0           Du_EndCP                                           0.280988  Production        MiCP          Du_EndCP
    1         Du_EndCP_g                                          280.98834  Production        MiCP        Du_EndCP_g
    2            Du_EndN                                            0.04507  Production        MiCP           Du_EndN
    3          Du_EndN_g                                           45.07041  Production        MiCP         Du_EndN_g
    4        Du_IdEAAMic                                         767.796581  Production        MiCP       Du_IdEAAMic
    5            Du_MiCP                                           2.052405  Production        MiCP           Du_MiCP
    6          Du_MiCP_g                                        2052.405213  Production        MiCP         Du_MiCP_g
    7   Du_MiN_NRC2001_g                                         334.939405  Production        MiCP  Du_MiN_NRC2001_g
    8           Du_MiN_g                                         328.384834  Production        MiCP          Du_MiN_g
    9            Du_MiTP                                           1.691182  Production        MiCP           Du_MiTP
    10         Du_MiTP_g                                        1691.181896  Production        MiCP         Du_MiTP_g
    11        Du_NANMN_g                                         302.751473  Production        MiCP        Du_NANMN_g
    12          Du_NAN_g                                         631.136307  Production        MiCP          Du_NAN_g
    13         Du_idMiCP                                           1.641924  Production        MiCP         Du_idMiCP
    14       Du_idMiCP_g                                        1641.924171  Production        MiCP       Du_idMiCP_g
    15         Du_idMiTP                                           1.352946  Production        MiCP         Du_idMiTP
    16       Du_idMiTP_g                                        1352.945517  Production        MiCP       Du_idMiTP_g
    17         EndAAProf  [4.61, 2.9, 4.09, 7.67, 6.23, 1.26, 3.98, 5.18...  Production        MiCP         EndAAProf
    18      Fe_DEMiCPend                                           2.319218   Excretion       fecal      Fe_DEMiCPend
    19        Fe_RumMiCP                                           0.410481   Excretion       fecal        Fe_RumMiCP
    20              MiCP                                         Dictionary  Production        MiCP                  
    21            MiN_Vm                                         340.791931  Production        MiCP            MiN_Vm
    22        MiTPAAProf  [5.47, 2.21, 6.99, 9.23, 9.44, 2.63, 6.3, 6.23...  Production        MiCP        MiTPAAProf
    23      RDPIn_MiNmax                                            2.94252  Production        MiCP      RDPIn_MiNmax
    24   Rum_MiCP_DigCHO                                           0.326383  Production        MiCP   Rum_MiCP_DigCHO
    25         SI_dcMiCP                                               80.0      Inputs  coeff_dict         SI_dcMiCP
    26        fMiTP_MiCP                                              0.824      Inputs  coeff_dict        fMiTP_MiCP

This will print a table with all the variables related to the search string and their value. 
The "Category" and "Level" columns show where the values are stored within ModelOutput. 
In this case "MiCP" is the name of a dictionary containg values related to microbial crude protein
production, so all values in this dictionary are displayed even if "MiCP" is not in the variable name.

The `nasem_dairy` package also includes all of the reports from the R version. These can be
accessed through the `get_report()` method by specifying the report name.

```python
print(output.get_report("table1_1"))
```
                        Description         Values
    0                      Animal Type  Lactating Cow
    1                     Animal Breed       Holstein
    2                  Body Weight, kg        624.795
    3                     Empty BW, kg     512.395561
    4                 Birth Weight, kg           44.1
    5                Mature Weight, kg          700.0
    6              Mature Empty BW, kg          574.0
    7                           Age, d          820.8
    8          Condition Score, 1 to 5            3.0
    9             Percent First Parity          100.0
    10                    Days in Milk            100
    11         Age At First Calving, d               
    12                   Days Pregnant             46
    13                  Temperature, C           22.0
    14         Use In vitro NDF digest              0
    15   Feeding Monensin, 0=No, 1=Yes              0
    16                         Grazing              0
    17                      Topography            0.0
    18    Dist. (Pasture to Parlor, m)            0.0
    19  One-Way Trips to the Parlor, m              0

### The NASEM Directed Acyclic Graph (DAG)

`nasem_dairy` comes with an optional dag subpackage. This subpackage requires you install
the `graph-tool` package. This package has several requirements depending on your operating system.
For instructions on how to install visit their [website](https://graph-tool.skewed.de/installation.html)

This subpackage parses the equations used to build the NASEM model and uses the function arguments to 
build a DAG. This can then be used to explore how varaibles in the model are connected.

Once you have `graph-tool` installed you can create a DAG.

```python
dag = nd.ModelDAG()
```

Once you have created the DAG you can explore how functions are connected using `dag.get_calculation_order()`.

```python
dag.get_calculation_order("GrUter_Wt")
```

    Requirements for Calculating GrUter_Wt

    Order of Functions to Call:
    1. calculate_Uter_Wtpart
    2. calculate_Uter_Wt
    3. calculate_GrUter_Wtpart
    4. calculate_GrUter_Wt

    Required User Inputs:
    animal_input:
        - An_AgeDay
        - An_GestLength
        - An_Parity_rl
        - An_GestDay
        - Fet_BWbrth
        - An_LactDay

    Required Constants:
    coeff_dict:
        - GrUter_Ksyn
        - GrUterWt_FetBWbrth
        - Uter_KsynDecay
        - GrUter_KsynDecay
        - Uter_Ksyn
        - Uter_Kdeg
        - Uter_Wt_coeff
        - UterWt_FetBWbrth

This will display the functions that need to be called in order to calulate the specified value.
It also provides all of the input values that are involved in the calculation.

If you are only interested in calcualting a specific value you can use the `create_function()` method.
This will return a function that takes the required inputs and will call all of the functions
required to calculate the specified value. This returns a ModelOuptut just like the `nd.nasem()` function.

```
GrUter_Wt_function = dag.create_function("GrUter_Wt")
print(inspect.signature(GrUter_Wt_function))
```
    (animal_input, coeff_dict)

By inspecting the signature of the created function we see it requires animal_input and coeff_dict.
The animal_input can be the same as the one used to run `nd.nasem()`, though only the specified keys are required.
The coeff_dict contains default coefficients. The default can be accessed as `nd.coeff_dict`.

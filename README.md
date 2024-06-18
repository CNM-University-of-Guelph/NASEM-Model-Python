# The NASEM 2021 Nutrient Requirements of Dairy Cattle Model in Python

- [Installation](#installation)
- [Using the Model](#using-the-model)
  - [Import package](#import-package)
  - [Get input data](#get-input-data)
  - [Execute Model](#execute-model)

This is a python version of the Nutrient Requirments of Dairy Cattle 8th
revisied edition (NASEM
2021)\[https://nap.nationalacademies.org/catalog/25806/nutrient-requirements-of-dairy-cattle-eighth-revised-edition\]
model. Currently, it is only set up to balance rations for lactating
Holstein cows and doesn’t include any mineral or vitamin equations. The
equations have been copied from the R functions released with the
official NASEM software:
https://nap.nationalacademies.org/resource/25806/Installation_Instructions_NASEM_Dairy8.pdf

## Installation

This package can be installed through a terminal using:

    pip install git+https://github.com/CNM-University-of-Guelph/NASEM-Model-Python

The environment that this is installed into will require
`python >= 3.10`. It will also install `pandas` and `numpy`
automatically.

The suggested way to install this is inside a virtual environment. For
example, by using https://docs.conda.io/en/latest/miniconda.html.

1.  Open a terminal window e.g. Anaconda Prompt

2.  Create new conda environment with python installed

        conda create --name myenvironment python>=3.10

        conda activate myenvironment

3.  Install this package from github
    `pip install git+https://github.com/CNM-University-of-Guelph/NASEM-Model-Python`

## Using the Model

### Import package

Import this package, and `pandas` so that input files can be imported.

``` python
import nasem_dairy as nd
import pandas as pd
```

### Get input data

There are data built in to the app which can be used as input to the
model:

``` python
from importlib.resources import files
path_to_package_data = files("nasem_dairy.data")

# Read_csv to load required data into env
user_diet_in, animal_input_in, equation_selection_in = nd.read_csv_input(path_to_package_data.joinpath("input.csv"))

# Load feed library
feed_library_in = pd.read_csv(path_to_package_data.joinpath("NASEM_feed_library.csv"))
```

### Execute Model

``` python
## RUN MODEL ###
output = nd.execute_model(
    user_diet = user_diet_in, 
    animal_input = animal_input_in, 
    equation_selection = equation_selection_in, 
    feed_library_df = feed_library_in)

print(output)
```

    =====================
    Model Output Snapshot
    =====================
    Milk production kg (Mlk_Prod_comp): 35.569
    Milk fat g/g (MlkFat_Milk): 0.053
    Milk protein g/g (MlkNP_Milk): 0.042
    Milk Production - MP allowable kg (Mlk_Prod_MPalow): 35.906
    Milk Production - NE allowable kg (Mlk_Prod_NEalow): 31.498
    Animal ME intake Mcal/d (An_MEIn): 60.273
    Target ME use Mcal/d (Trg_MEuse): 52.195
    Animal MP intake g/d (An_MPIn_g): 2565.214
    Animal MP use g/d (An_MPuse_g_Trg): 1989.985
    Animal RDP intake g/d (An_RDPIn_g): 3556.058
    Diet DCAD meq (An_DCADmeq): 96.453

    This is a `ModelOutput` object with methods to access all model outputs. See help(ModelOutput).

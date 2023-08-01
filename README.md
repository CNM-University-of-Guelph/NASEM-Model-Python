# The NASEM 2021 Nutrient Requirements of Dairy Cattle Model in Python

This is a python version of the Nutrient Requirments of Dairy Cattle 8th revisied edition (NASEM 2021)[https://nap.nationalacademies.org/catalog/25806/nutrient-requirements-of-dairy-cattle-eighth-revised-edition] model. Currently, it is only set up to balance rations for lactating Holstein cows and doesn't include any mineral or vitamin equations. The equations have been copied from the R functions released with the official NASEM software: https://nap.nationalacademies.org/resource/25806/Installation_Instructions_NASEM_Dairy8.pdf 

## Table of Contents
- [Installation](#installation)
- [Using the Model](#using-the-model)


## Installation 

This package can be installed through a terminal using: 
```
pip install git+https://github.com/CNM-University-of-Guelph/NASEM-Model-Python
```

The environment that this is installed into will require `python >= 3.9`. It will also install `pandas` and `numpy` automatically. 
 
The suggested way to install this is inside a virtual environment. For example, by using  https://docs.conda.io/en/latest/miniconda.html.

1. Open a terminal window e.g. Anaconda Prompt
2. Create new conda environment with python installed

    ```
    conda create --name myenvironment python>=3.9

    conda activate myenvironment
    ```

3. Install this package from github
    ```
    pip install git+https://github.com/CNM-University-of-Guelph/NASEM-Model-Python
    ```

    

## Using the Model
To use the model only two files need to be opened. From the NASEM-Model-Python directory go to script/ration_balancer. From here open "input.txt" and "NASEM_model.ipynb".

### Input.txt
This is where you will put all of the input parameters for the model. This file is read line by line and the first character tells the model where the variables should go. 

- $: These are toggles for calculations that offer multiple equations
- *: These are animal related parameters
- #: This comments out a line so that notes can be added

When entering the diet no leading character is used. For example, to add Alfalfa meal as 30% DM basis you would type "Alfalfa meal: 30".
Note that the feed name entered must match exactly to the feed name in the feed library.

Once you have set all the animal parameters and created a diet save input.txt and go to NASEM_model.ipynb

### NASEM_model.ipynb
This is the file that takes input.txt and performs all of the calculations. To run the model simply hit "Run All" at the top of the page and then scroll to the bottom to view the results. If there is no "Run All" button the three code chunks will need to be run in order. The results will display the intakes of a few important nutrients as well as predictions for milk fat, milk protein, milk production, energy requirements and protein requirements.

There are also a dataframes returned by the model that provide additional information.
- AA_values: Information on individual amino acids
- diet_info: Nutrient intakes for each feedstuff and for diet
- feed_data: Composition of each feedstuff

To adjust the ration make changes to input.txt, save, and then hit "Run All" again and then updated results will display. 

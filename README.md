# The NASEM 8 Model in Python

This is a version of the NASEM 8 model that has been written in Python. Currently, it is only set up to balance rations for lactating cows. 

## Table of Contents
- [Installation](#installation)
- [Using the Model](#using-the-model)


## Installation 

This project can be installed through a terminal or command prompt window. I recommend using [Anaconda Prompt](https://docs.conda.io/en/latest/miniconda.html) as this will later be used
to setup the virtual environment for the project. 

1. Open Anaconda Prompt
2. Navigate to Install Directory

   Use the 'cd' command to navigate to the directory you want to clone the project to. For example, it can be cloned to the "Documents" folder.
   ```
   cd Documents
   ```
3. Clone the Repository

    Run the follwoing code to clone the repository to your current directory
    ```
    git clone https://github.com/CNM-University-of-Guelph/NASEM-Model-Python.git
    ```

4. Set Up the Virtual Environment (Recommended)    

    This project includes a file, "environment.yml", that can be used to set up a virtual environment for this project. While any Python environment with the required packages can be used
    the "environment.yml" file will install all the required packages for you. Run the following code to set up the virtual environment, NASEM_py_env. 

    Navigate to the project directory
    ```
    cd NASEM-Model-Python
    ```
    Create the virtual environment
    ```
    conda env create -f environment.yml
    ```

    Now select "NASEM_py_env" as the interpreter within your code editor.
    

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

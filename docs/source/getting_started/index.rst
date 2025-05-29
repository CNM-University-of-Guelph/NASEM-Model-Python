.. _getting_started:

Getting Started
===============

Installation
------------

The NASEM dairy package can be installed by running this command:

.. code-block:: bash

    pip install nasem_dairy

We recommend installing the package in a virtual environment. The nasem_dairy package
is compatible with Python 3.10 and above.


Using the Model
---------------
This section will go over how to run the model and view the results. The quickest
way to get started is to load one of the demo inputs provided with the package.

First, create a new Python file and import the nasem_dairy package.

.. code-block:: python

    import nasem_dairy as nd

Load a Demo
~~~~~~~~~~~

The NASEM dairy model requires several inputs to run. These inputs include:

- a diet to feed
- animal related parameters
- the equations to use
- infused nutrients (optional)

More details on the inputs can be found on the :ref:`model inputs <model_inputs>` page.
The `nd.demo()` function will load a demo input for a lactating cow. We will be ignoring
infusions for this example.

.. code-block:: python

    diet, animal_input, equation_selection, _ = nd.demo("lactating_cow_test")

Run the model
~~~~~~~~~~~~~~

The model can be run by calling the `nd.nasem()` function. This function will return
a ModelOutput object with the results. Only the diet, animal inputs and equation
selection are required. More details on the optional inputs can be found on the
:ref:`nasem <nasem>` API documentation.

.. code-block:: python

    output = nd.nasem(diet, animal_input, equation_selection)
    print(output)

Printing the output will show a snapshot of the results:

.. code-block::

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

Viewing Results
~~~~~~~~~~~~~~~

The `get_value()` method can be used to get the value of a specific variable.

.. code-block:: python

    print(output.get_value("Mlk_Prod_comp"))
    34.19721330579462

The results can be saved to a JSON file using the `export_to_JSON()` method.

.. code-block:: python

    output.export_to_JSON("output.json")

If you are unsure what variable you are looking for you can use the `search()` method.
This will return a DataFrame with all the variables that contain the search term in the nasem
or are sorted in a category including the search term. For example, searching for "CPgain"
will return all the variables related to crude protein for body weight gain.

.. code-block:: python

    print(output.search("CPgain"))

.. code-block::

                        Name       Value      Category           Level 1                  Level 2
    0              Body_CPgain    0.020052    Production  body_composition              Body_CPgain
    1  Body_CPgain_MPalowTrg_g  481.572362    Production  body_composition  Body_CPgain_MPalowTrg_g
    2            Body_CPgain_g   20.051817    Production  body_composition            Body_CPgain_g
    3           CPGain_FrmGain    0.128702    Production  body_composition           CPGain_FrmGain
    4          CPGain_RsrvGain    0.068000        Inputs        coeff_dict          CPGain_RsrvGain
    5               Frm_CPgain    0.020052    Production         gestation               Frm_CPgain
    6             Frm_CPgain_g   20.051817    Production  body_composition             Frm_CPgain_g
    7           Gest_NCPgain_g    1.008063  Requirements           protein           Gest_NCPgain_g
    8              Rsrv_CPgain    0.000000    Production  body_composition              Rsrv_CPgain
    9            Rsrv_CPgain_g    0.000000    Production  body_composition            Rsrv_CPgain_g


More details on the ModelOutput object can be found on the :ref:`model output <model_output>` page.
For more details on using this package see the :ref:`user guide <user_guide>` page.

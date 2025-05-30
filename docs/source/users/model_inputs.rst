.. _model_inputs:

Model Inputs
============

Animal Inputs
-------------

.. list-table::
   :widths: 20 50 30
   :header-rows: 1

   * - Variable
     - Description
     - Example
   * - Trg_MilkProd
     - Target milk production (kg/day)
     - 25.2
   * - Trg_MilkFatp
     - Target milk fat percentage
     - 4.55 (4.55% milk fat)
   * - Trg_MilkTPp
     - Target milk true protein percentage
     - 3.66 (3.66% milk true protein)
   * - Trg_MilkLacp
     - Target milk lactose percentage
     - 4.85 (4.85% milk lactose)
   * - Trg_Dt_DMIn
     - Target dry matter intake (kg/day)
     - 24.5
   * - An_BW
     - Body weight (kg)
     - 725
   * - An_Parity_rl
     - Proportion of animals that are multiparous (0 for heifers, 1 for all primiparous, 2 for all multiparous)
     - 1.5 for 50% primiparous and 50% multiparous
   * - An_BCS
     - Body condition score (1-5)
     - 3
   * - An_LactDay
     - Days in milk
     - 100
   * - An_BW_mature
     - Mature body weight (kg)
     - 700 (default)
   * - Trg_FrmGain
     - Target frame gain (kg/day)
     - 0.19
   * - Trg_RsrvGain
     - Target body reserves gain (kg/day)
     - 0.2
   * - An_GestDay
     - Days of gestation
     - 46
   * - An_GestLength
     - Gestation length (days)
     - 280
   * - Fet_BWbrth
     - Expected fetal birth weight (kg)
     - 44.1 (default)
   * - An_AgeDay
     - Age of animal (days)
     - 820
   * - An_305RHA_MlkTP
     - 305-day rolling herd average for milk true protein
     - 280 (default)
   * - An_StatePhys
     - Physiological state of the animal ("Lactating Cow", "Dry Cow", "Heifer", "Calf", "Other")
     - "Lactating Cow"
   * - An_Breed
     - Breed of the animal ("Holstein", "Jersey", "Other")
     - "Holstein"
   * - An_AgeDryFdStart
     - Age at dry feeding start (days)
     - 21
   * - An_AgeConcept1st
     - Age at conception for the first pregnancy (days)
     - 650
   * - Env_TempCurr
     - Current mean daily temperature (°C)
     - 15
   * - Env_DistParlor
     - Distance to parlor (m)
     - 100
   * - Env_TripsParlor
     - Number of trips to parlor per day
     - 2
   * - Env_Topo
     - Positive elevation change per day (m)
     - 3

Equation Selection
------------------

.. list-table::
   :widths: 20 50 30
   :header-rows: 1

   * - Variable
     - Description
     - Values
   * - Use_DNDF_IV
     - In vitro NDF digestibility equation
     - 0 for lignin based, 1 for DNDF48 for forages, 2 for DNDF48 for all feeds
   * - DMIn_eqn
     - Dry matter intake prediction equation
     - See :ref:`dmin_eqn_options`
   * - mProd_eqn
     - Milk production prediction equation
     - See :ref:`mProd_eqn_options`
   * - MiN_eqn
     - Microbial nitrogen prediction equation
     - 1 for NRC 2021, 2 for Hanigan (2021), 3 for White (2017)
   * - NonMilkCP_ClfLiq
     - Non-milk protein sources in calf liquid feeds
     - 0 for no non-milk protein, 1 for non-milk protein
   * - Monensin_eqn
     - Use monensin in the diet
     - 0 for no monensin, 1 for monensin
   * - mPrt_eqn
     - Milk protein prediction equation
     - 0 for Trg_MilkTPp, 1 for NRC equation, 2 VT1 equation, 3 VT2 equation
   * - mFat_eqn
     - Milk fat prediction equation
     - 0 for Trg_MilkFatp, 1 predicted milk fat production
   * - RumDevDisc_Clf
     - Dry feed discount for ME due to undeveloped rumen
     - 0 for no discount, 1 for 10% discount if liquid feed > 1.5% of BW

.. _dmin_eqn_options:

DMIn_eqn Options
~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Value
     - Description
   * - 0
     - Use Trg_Dt_DMIn
   * - 1
     - Calf on liquid feed
   * - 2
     - Heifer using animal factors
   * - 3
     - Heifer using animal and feed factors
   * - 4
     - Holstein heifer using animal factors, prepartum prediction for a single animal
   * - 5
     - Holstein heifer using animal factors and diet NDF concentration, prepartum prediction for a single animal
   * - 6
     - Holstein x Jersey crossbred heifer using animal factors, prepartum prediction for a single animal
   * - 7
     - Holstein x Jersey crossbred heifer using animal factors and diet NDF concentration, prepartum prediction for a single animal
   * - 8
     - Lactating cow using animal factors
   * - 9
     - Lactating cow using animal and feed factors
   * - 10
     - Dry cow (NRC 2020)
   * - 11
     - Dry cow (Hayirli et al., 2003)
   * - 12
     - Heifer using animal factors, prepartum prediction for a group
   * - 13
     - Heifer using animal and feed factors, prepartum prediction for a group
   * - 14
     - Holstein heifer using animal factors, prepartum prediction for a group
   * - 15
     - Holstein heifer using animal factors and diet NDF concentration, prepartum prediction for a group
   * - 16 
     - Holstein x Jersey crossbred heifer using animal factors, prepartum prediction for a group
   * - 17
     - Holstein x Jersey crossbred heifer using animal factors and diet NDF concentration, prepartum prediction for a group

.. _mProd_eqn_options:

mProd_eqn Options
~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Value
     - Description
   * - 0
     - Use Trg_MilkProd
   * - 1
     - Milk component based prediction
   * - 2
     - Net energy allowable
   * - 3
     - Metabolisable protein allowable
   * - 4
     - Minimum of net energy and metabolisable protein allowable

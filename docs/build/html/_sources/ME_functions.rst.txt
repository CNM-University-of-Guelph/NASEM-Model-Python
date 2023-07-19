.. Testing how to document functions with Sphinx

Metabolizable Energy Requirements
=================================

A collection of functions that estimate an cows metabolizable energy requirement in Mcal/d.

Calculations
------------

To calculate the total daily metabolizable energy requirement use 
the ``calculate_ME_requirement()`` function:

.. py:function:: calculate_ME_requirement(An_BW, Dt_DMIn, Trg_MilkProd, An_BW_mature, Trg_FrmGain, An_GestDay, An_GestLength, An_AgeDay, Fet_BWbrth, An_LactDay, An_Parity_rl, Trg_MilkFatp, Trg_MilkTPp, Trg_MilkLacp, Trg_RsrvGain)

   Returns a single number, Trg_MEuse, with the units Mcal/d.

   :param An_BW: Animal Body Weight in kg.
   :type An_BW: Number
   :param Dt_DMIn: Animal Dry Matter Intake in kg/day.
   :type Dt_DMIn: Number
   :param Trg_MilkProd: Animal Milk Production in kg/day.
   :type Trg_MilkProd: Number
   :return: Trg_MEuse, the metabolizable energy requirement.
   :rtype: float

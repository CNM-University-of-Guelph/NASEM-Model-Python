#***** Cross-checking Python with this original. Lines starting with #*# have been implemented in python ********************************
#VT 2020 Dairy Model function, created by Mark D. Hanigan, Virginia Tech, 2019

#Added default inputs in the function definition. 20-06-23
#Fd_DNDF48 was added to the feed matrix and Use_dcNDF_IV was added to control its use for TT NDF calcs
#Added DCAD calculation

#Target values for BW, FrmGgain, and RsrvGain should be entered as the pen average over the timeframe considered/simulated.

#To Do: 
#1. Calf protein equations do not follow the RDP/RUP, MiCP scheme, thus many digestive variables that are defined based on RDP are 
#          incorrect as they use the RDP system.  Calf digestion should be sorted out properly within the existing ruminant framework. MDH

#2. The Target allowable production calculations were added late, and frankly are a mess.  The original method used was to predict milk
#         based on nutrient inputs or to sub a target Kl to estimate what would be required to achieve the target production if the target Kl
#         were achieved. Thus predicted production and nutrient allowable production required 2 runs.  A decision to code all of the target
#         predictions as a separate stream in the model was adopted to avoid having to run the model 2x.  In retrospect, I think this was a
#         mistake due to multiple possible scenarios, just with milk.  If an independent, nutrient driven outputs are predicted for other
#         production functions, it will be impossible to follow this approach due to the number of combinations.  Thus I recommend consolidating
#         the target based predictions of allowable milk to a single section, sorting out the abbreviations, consolidating where possible,
#         and replacing all with ifelse statements driven by user selections of the appropriate prediction equations to use.  I think it is
#         quite likely there are mistakes in the nutrient allowable production as coded due to the complexity and the poor abbreviation choices.
#         This will be required to implement such what-if scenarios for individual AA given all the drivers.  The current strategy can't be
#         supported and many errors will occur, if they haven't already. MDH.

#Default inputs and settings.  Limited in scope as most are provided with the data:
#Equation switches
DMIn_eqn <- 0            #User specified DMI
####Use_DNDF_IV <- 0         #don't use 30h in vitro NDF digestibility values
RUP_eqn <- 1             #only the NRC 2021 equation is currently coded, so this switch is inactive
MiN_eqn <- 1             #Use the NRC 2021 prediction equation
mProd_eqn <- 1           #Use the NRC 2021 prediction equation
mLac_eqn <- 0            #Use the user specified lactose concentration. No predictions provided
mPrt_eqn <- 1            #Use the NRC 2021 prediction equation
An_305RHA_MlkTP <- 280   #kg/305d The mean value from the meta data.
mFat_eqn <- 1            #Use the NRC 2021 prediction equation
FrmGain_eqn <- 0         #use user specified value.  No frame gain predictions provided 
RsrvGain_eqn <- 0        #use user specified value.  No frame gain predictions provided
####Monensin_eqn <- 0        #No monensin in the diet
RumDevDisc_Clf <- 0      #0=No dry feed discount for ME due to undeveloped rumen. 1=a 10% discount on dry feed if Liq>1.5% of BW
NonMilkCP_ClfLiq <- 0    #0=no non-milk protein sources in calf liquid feeds, 1=non-milk CP sources used


#Export Protein MP to NP conversion efficiencies for the NRC 2021 model
if(!exists("Eff")) {
     Eff <-  data.frame(Trg_AbsHis_NPHis =   0.75,
                         Trg_AbsIle_NPIle =	0.71,
                         Trg_AbsLeu_NPLeu =	0.73,
                         Trg_AbsLys_NPLys =	0.72,
                         Trg_AbsMet_NPMet =	0.73,
                         Trg_AbsPhe_NPPhe =	0.6,
                         Trg_AbsThr_NPThr =	0.64,
                         Trg_AbsTrp_NPTrp =	0.86,
                         Trg_AbsVal_NPVal =	0.74,
                         Trg_MP_NP        =   0.69)
}



NRC2020 <- function(DietID, An_Breed, An_AgeDay,An_BW, An_BW_mature,Trg_FrmGain, Trg_RsrvGain,  
                    An_Parity_rl, An_BCS, An_GestLength, An_AgeConcept1st, An_DIMConcept, 
                    Fet_BWbrth, An_StatePhys, An_LactDay, An_GestDay, Env_TempCurr, Env_DistParlor, 
                    Env_TripsParlor, Env_Topo, Trg_MilkProd, Trg_MilkLacp, Trg_MilkTPp, Trg_MilkFatp, 
                    Trg_Dt_DMIn, An_AgeDryFdStart, Fd_DMInp=Fd_DMInp, f,i, DMIn_eqn, Use_DNDF_IV, RUP_eqn, 
                    MiN_eqn, mProd_eqn, mLac_eqn, mPrt_eqn, An_305RHA_MlkTP, mFat_eqn, FrmGain_eqn, 
                    RsrvGain_eqn, Monensin_eqn, RumDevDisc_Clf, NonMilkCP_ClfLiq, Eff) {
message("In the NRC2020 function() Use_DNDF_IV = ", Use_DNDF_IV)
#################################################################################################
#This function represents a derivation of code written in support of USDA and Canadian Dairy Research
#Cluster projects and for use by the NRC Dairy 8th revised edition committee.
#
#The work was completed in part with funding from the National Institute of Food and Agriculture, 
#U.S. Department of Agriculture via Comp. Grant #2017-67015-26539, the National Animal Nutrition 
#Program (NRSP-9), and the Virginia Agricultural Experiment Station.  Additional general support was provided
#by the Virginia State Dairymen Association, The Canadian Dairy Research Cluster, The Virginia 
#Agricultural Council, the Pratt Foundation at Virginia Tech, and Papillon Corp.  Intellectual property rights
#reside with VT, USDA, CDRC, and NASEM.  Academic use of the code is encouraged with appropriate acknowledgments.
#Commercial use of this code requires a copyright release from NASEM.
#
#The original data handling and model code and this function were written by Mark D. Hanigan 
#with help from Adelyn Fleming (MS student,VT), Meng Li (PhD student at VT), and Veridiana Daley 
#(postdoc, NANP/NRSP-9, Univ. Ky and VT). The data handling code and general approach 
#originated with Dr. Larry Reutzel, Purina Mills/Land O' Lakes with subsequent updates by M. Hanigan, 
#T. McGill, R. Garnett, and R.R. White. It was subsequently rewritten by M. D. Hanigan and A. Fleming. 
#
##This function represents a single animal or a group of animals fed a single diet. Required inputs
#to the function are breed, physiological state, BW (kg), DIM, days pregnant, temperature, distance from 
#the pen to the parlor (m), climb/elevation change walking to the parlor (m), DMI (kg/d), a feed 
#ingredient composition dataframe (f, Nutrient composition, % of DM), a row vector of the 
#DM proportions of each ingredient in the diet (length=# of Ingredients), and an infusion dataframe (i).
#These inputs should represent the animal or group over the course of the feeding period being evaluated.
#This is typically best represented by the mean of the group.
#
#The function returns a list containing dataframes with dietary nutrient intakes and 
#concentrations (dt); vitamin and mineral intakes, concentrations, requirements, and
#balances (MV); AA intakes, concentrations duodenal flows, intestinal digested flows,
#absorbed flows and balance (AA); gross, digestible, metabolizable, and net energy flows, 
#use for body functions, and balance (en); body growth and gestational (gest), milk (mlk), 
#fecal (fe), urinary (ur), and breathe outputs of nutrients; and feed cost and product 
#value (ec); and efficiencies of use of nutrients (eff).
####################################################################################################

   #################################### List of Required Inputs to the Model #########################################
   #DietID = numeric identifier to be returned with the model data
   #An_BW = live weight, kg
   #An_BWmature = mature liveweight, kg
   #An_BCS = body condition score on the NA dairy 1 to 5 scale
   #An_Breed = primary breed (Holstein, Jersey, Other).  Only Holstein and Jersey are used. Other can be any breed.
   #An_Parity_rl = parity as a real value from 0 to 2 reflecting the proportions in the pen (1-2 only)
   #0=calf/heifer/bull, >=1 = lactating/dry cow
   #An_305RHA_MlkTP = Scalar to adjust the maximum milk protein response to EAA, 280kg/305d= no adjustment
   #Should be scaled using 305ME protein or 305 RHA protein
   #An_GestLength = normal gestation length, days; typically 283 days
   #An_AgeDryFdStart = age when dry calf starter feed is first offered, days
   #An_AgeCalv1st = age at first calving, days
   #An_AgeConcept1st = age at conception for the first pregnancy, days; heifers only
   #An_StatePhys = physiological state; "Calf", "Heifer", "Dry Cow", "Lactating Cow", "Other"
   #An_LactDay = days in milk, lactating cow only
   #An_GestDay = day of gestation
   #An_DIMConcept = days in milk at conception, days; lactating and dry cows only
   #Fet_BWbrth = calf birthweight, kg
   #Trg_FrmGain = the targeted gain in body Frame weight (Live weight - Reserves weight), kg fresh Wt/d
   #Trg_RsrvGain = the targeted BW gain or loss in Body Reserves for lactating cows (66% fat, 8% CP), kg fresh Wt/d
   #Trg_ADG = calculated as Trg_FrmGain + TrgRsrvGain
   #Trg_MilkProd = user desired milk production, kg/d
   #Trg_MilkLacp = user desired milk lactose, %
   #Trg_MilkTPp = user desired milk true protein, %
   #Trg_MilkFatp = user desired milk fat, %
   #mProd_eqn = Milk Production prediction equation (0=Trg_MilkProd, 1=component based predicted, 2=NE Allowable, 3=MP Allowable, 4=min(NE,MPAllow))
   #mLac_eqn = Milk Lactose Production prediction equation (0 = use Trg_MilkLacp, no predictions at present)
   #mPrt_eqn = Milk Protein Production prediction equation (0 = use Trg_MilkTPp, 1 = NRC predicted, 2 = VT predicted)
   #mFat_eqn = Milk Fat prediction equation (0 = use Trg_MilkFatp, 1 = use predicted milk fat production)
   #FrmGain_eqn = Frame gain/growth prediciton equation (= = use Trg_FrmGain, no predictions currently)
   #RsrvGain_eqn = Reserves gain prediciton equation (= = use Trg_RsrvGain, no predictions currently)
   #DMIn_eqn = dry matter intake equation to use for calculations
      #0 = DMI specified by user
      #1 = predicted for a calf on liquid feed
      #2 = predicted for all heifers, animal factors, NRC equation
      #3 = predicted for all heifers, animal and feed factors, NRC equation
      #4 = predicted for a Holstein heifer, animal factors, prepartum predicted for a single animal
      #5 = predicted for a Holstein heifer, animal factors and diet NDF concentration, prepartum predicted for a single animal
      #6 = predicted for a Holstein x Jersey crossbred heifer, animal factors, prepartum predicted for a single animal
      #7 = predicted for a Holstein x Jersey crossbred heifer, animal factors and diet NDF concentration, predicted for a single animal
      #8 = predicted for a lactating cow using animal factors such as BW and BCS
      #9 = predicted for a lactating cow using animal and feed factors
      #10 = predicted for a dry cow, NRC 2020 eqn.
      #11 = predicted for a dry cow, Hayirli et al., 2003 eqn.
      #12 = predicted for a Holstein heifer, animal factors, prepartum predicted for a group
      #13 = predicted for a Holstein heifer, animal factors and diet NDF concentration, prepartum predicted for a group
      #14 = predicted for a Holstein x Jersey crossbred heifer, animal factors, prepartum predicted for a group
      #15 = predicted for a Holstein x Jersey crossbred heifer, animal factors and diet NDF concentration, prepartum predicted for a group
   #Trg_Dt_DMIn = user specified dry matter intake to use if DMIn_eqn = 0 and for calf milk/milk replacer
     #Note that pre-fresh and fresh pens have nonlinear responses vs time and this must be considered by weighting for accurate inputs.
   #Fd_DMInp = a vector containing the proportion of the diet DM contributed by each feed (DM basis). 
   #    Note: Fd_DMInp is contained in the feed table for NANP data. It must be extracted and passed as a vector
   #Env_TempCurr = current mean daily temperature in degrees C
   #MiN_eqn = MiN prediciton equation; 1=NRc2021, 2=VT
   #Env_Grazing = grazing switch; Was an input but now set based on inclusion of pasture in the diet which turns on use of the following 3.
   #Env_DistParlor distance from the barn or paddock to the parlor, meters
   #Env_TripsParlor = number of daily trips to and from the parlor; generally 2 trips per milking times number of milkings
   #Env_Topo = the positive elevation change per day, meters
   #Use_dcNDFIV = dNDF in vitro use switch (0=do not use, 1=use dNDF48h to adjust DE for forages, 2=use to adjust all
   #RUP_eqn = switch to control the RUP prediction equation used. Currently only the NRC 2021 eqn. thus inactive 
   
   #f = feed dataframe containing the feeds available for use in the diet
   #Format:
   # "UID", "Fd_Cost", Fd_Category", "Fd_Type", "Fd_DM", "Fd_Conc", "Fd_NDF", "Fd_DNDF48_NDF", "Fd_ADF", 
   #"Fd_Lg", "Fd_St", "Fd_WSC", "Fd_CP", "Fd_CPARU", "Fd_CPBRU", "Fd_CPCRU", "Fd_KdRUP", "Fd_NPN_CP", "Fd_NDFIP", 
   #"Fd_ADFIP", "Fd_Arg_CP", "Fd_His_CP", "Fd_Ile_CP", "Fd_Leu_CP", "Fd_Lys_CP", "Fd_Met_CP", "Fd_Phe_CP", "Fd_Thr_CP", 
   #"Fd_Trp_CP", "Fd_Val_CP", "Fd_CFat", "Fd_FA", "Fd_Ash", "Fd_C120_FA", "Fd_C140_FA", "Fd_C160_FA", "Fd_C161_FA", 
   #"Fd_C180_FA", "Fd_C181t_FA", "Fd_C181c_FA", "Fd_C182_FA", "Fd_C183_FA", "Fd_OtherFA_FA", "Fd_Ca", "Fd_P",
   #"Fd_Pinorg_P", "Fd_Porg_P", "Fd_Na", "Fd_Cl", "Fd_K", "Fd_Mg", "Fd_Co", "Fd_Cr", "Fd_Cu", "Fd_Fe", 
   #"Fd_I", "Fd_Mn", "Fd_Mo", "Fd_S", "Fd_Se", "Fd_Zn", "Fd_B_Carotene", "Fd_Biotin", "Fd_Choline", "Fd_Niacin", "Fd_VitA",
   #"Fd_VitD", "Fd_VitE", "Fd_dcSt", "Fd_dcRUP", "Fd_dcFA", "Fd_acCa", "Fd_acPtot", "Fd_acNa", "Fd_acCl", "Fd_acK",
   #"Fd_acCu", "Fd_acFe", "Fd_acMg", "Fd_acMn", "Fd_acZn", "Fd_acS", "Fd_acCo", "Fd_acI", "Fd_acSe", "Fd_OM"
   
   #Eff = a named row vector of export protein efficiencies (maintenance plus milk protien). 
   #Format: Eff = c(Name1 = Val, Name2=Val, etc.) 

   #i = vector of infused nutrients and site of infusion.
   #Format:
   #"Inf_Location",    #Options: "Rumen","Abomasum","Duodenum","Jugular","Arterial","Iliac Artery","Blood"
   #"Inf_DM_g","Inf_St_g","Inf_NDF_g","Inf_ADF_g","Inf_Glc_g","Inf_CP_g","Inf_NPNCP_g","Inf_CPARum_CP",
   #"Inf_CPBRum_CP","Inf_CPCRum_CP","Inf_KdCPB","Inf_dcRUP","Inf_FA_g","Inf_Ash_g","Inf_VFA_g","Inf_ttdcSt",
   #"Inf_Acet_g","Inf_Prop_g","Inf_Butr_g","Inf_Arg_g","Inf_His_g","Inf_Ile_g","Inf_Leu_g","Inf_Lys_g","Inf_Met_g",
   #"Inf_Phe_g","Inf_Thr_g","Inf_Trp_g","Inf_Val_g"

#############################################################################################################################
   ######### Provide default inputs to the model if they are missing in the call or global env ##########
if(!exists("Trg_FrmGain") | is.na(Trg_FrmGain)) { Trg_FrmGain <- as.numeric(0) }
if(!exists("Trg_RsrvGain") | is.na(Trg_RsrvGain)) { Trg_RsrvGain <- as.numeric(0) }

                       #   if ( missing(f_Imb) ){  #if these are added to the model call, use the missing function.
   if ( !exists("f_Imb") ){
      #weighting factors for AA imbalances used to create an index for optimization
      f_Imb <- c(Arg=1.0, His=1.0, Ile=1.0, Leu=1.0, Lys=1.0, Met=1.0, Phe=1.0, Thr=1.0, Trp=1.0, Val=1.0)
      }

############ Check for data consistency ########################
numIngrs <- nrow(f)
numFdProp <- length(Fd_DMInp)
if(numIngrs != numFdProp) stop(paste("There are", numIngrs, 
                                     " rows in f, but the length of FD_DMInp is ", numFdProp))

#Make sure the ingredient inclusion percentages for the diet sum to 1
Fd_DMInp_Sum <- sum(Fd_DMInp)  #determine the sum
Fd_DMInp <- Fd_DMInp / as.vector(Fd_DMInp_Sum) #scale to 100
   
##### Fill missing inputs with 0 and add scalars as needed to the f DF for use in Diet Calculations ###########
#Should also check for missing values in the inputs and trap them or stop the function.
f$An_StatePhys <- as.vector(An_StatePhys)

An_GestDay <- ifelse(An_GestDay < 0 | is.na(An_GestDay), 0, An_GestDay);	#Trap NA and negative values
An_GestDay <- ifelse(An_GestDay > An_GestLength + 10, 0,  An_GestDay)

#Determine some additional physiology values
An_PrePartDay <- An_GestDay - An_GestLength
An_PrePartWk <- An_PrePartDay/7

#Calculate day postpartum and trap nonsense values
An_PostPartDay <- ifelse(An_LactDay <= 0, 0, An_LactDay)
An_PostPartDay <- ifelse(An_LactDay > 100, 100, An_LactDay)

An_MBW <- An_BW^0.75
Trg_BWgain <- Trg_FrmGain + Trg_RsrvGain		#This could also be generated by prediction equations
Trg_BWgain_g <- Trg_BWgain * 1000

#Determine lower (LCT) and upper (UCT) critical temperatures, degrees C for thermal stress
LCT <- 15						#calf < 3 wks of age
LCT <- ifelse(An_AgeDay > 21, 5, LCT)	#calf > 3 wks of age
UCT <- 25						#calf


############## Pre-calculate some dietary nutrient concentrations to use with DMI equations
#Lignin based NDF total tract digestibility
f$TT_dcFdNDF_Lg <- 0.75 * (f$Fd_NDF-f$Fd_Lg) * (1-(f$Fd_Lg/ifelse(f$Fd_NDF==0,1e-6,f$Fd_NDF))^0.667) / 
     ifelse(f$Fd_NDF==0,1e-6,f$Fd_NDF) * 100  
f$TT_dcFdNDF_Lg <- ifelse(is.na(f$TT_dcFdNDF_Lg), 0, f$TT_dcFdNDF_Lg)

#48h DNDF based total tract NDF digestibility
#fill missing IV48 DNDF values
f$Fd_DNDF48 <- ifelse(f$Fd_Conc < 100 & (f$Fd_DNDF48 == 0 | is.na(f$Fd_DNDF48)), 48.3, f$Fd_DNDF48) #mean of Mike Allen database used for DMI equation
f$Fd_DNDF48 <- ifelse(f$Fd_Conc == 100 & (f$Fd_DNDF48 == 0 | is.na(f$Fd_DNDF48)), 65, f$Fd_DNDF48)  #mean of concentrates in the feed library

#Scale the in vitro DNDF48 to a true DC
f$TT_dcFdNDF_48h <- 12 + 0.61*f$Fd_DNDF48

#Select NDF Digestibility estimate based on Use_DNDF_IV (0=Lg based, 1=DNDF48 for forages, 2=DNDF48 for all)
f$TT_dcFdNDF_Base <- f$TT_dcFdNDF_Lg  #Prefill with the Lg based predictions as a default
f$TT_dcFdNDF_Base <- ifelse(rep(Use_DNDF_IV,length(f$TT_dcFdNDF_Lg)) == 1 & f$Fd_Conc < 100 & !is.na(f$TT_dcFdNDF_48h), #Forages only
                            f$TT_dcFdNDF_48h, f$TT_dcFdNDF_Base)
f$TT_dcFdNDF_Base <- ifelse(rep(Use_DNDF_IV,length(f$TT_dcFdNDF_Lg)) == 2 & !is.na(f$TT_dcFdNDF_48h), #All Ingredients
                            f$TT_dcFdNDF_48h, f$TT_dcFdNDF_Base)

#dietary ADF, NDF, and ForNDF concentrations (will be repeated below, could remove the ones below)
Dt_ADF <- sum(f$Fd_ADF*Fd_DMInp, na.rm=TRUE);	#% of dietary DM
Dt_NDF <- sum(f$Fd_NDF*Fd_DMInp,  na.rm=TRUE)
Dt_For <- sum((1-f$Fd_Conc/100) * Fd_DMInp,  na.rm=TRUE)
Dt_ForNDF <- sum((1-f$Fd_Conc/100) * f$Fd_NDF*Fd_DMInp,  na.rm=TRUE)
Dt_ForDNDF48 <- sum((1-f$Fd_Conc/100) * f$Fd_NDF*f$Fd_DNDF48/100*Fd_DMInp,  na.rm=TRUE)  #should be updated to use TT_dcFdNDF_Base so it could be referenced to in vivo.
Dt_ForDNDF48_ForNDF <- Dt_ForDNDF48 / Dt_ForNDF * 100
Dt_ADF_NDF <- Dt_ADF/Dt_NDF

############## Gross Energy in each Ingredient ###############
En_FA <- 9.4        #Combustion energies for each nutrient, MCal/kg of nutrient
En_CP <- 5.65		#excludes NPN
En_NFC <- 4.2 
En_NDF <- 4.2
En_NDFnf <- 4.14
En_NPNCP <- 0.89  #per kg of CP equivalent based on urea at 2.5 kcal/g
En_rOM <- 4.0
En_St <- 4.23
En_WSC <- 3.9
En_Acet <- 3.48
En_Prop <- 4.96
En_Butr <- 5.95

f$Fd_GE <- ifelse(An_StatePhys=="Calf" & f$Fd_Category == "Calf Liquid Feed", 
             f$Fd_CP/100*En_CP + f$Fd_FA/100*En_FA + (100-f$Fd_Ash - f$Fd_CP - f$Fd_FA)/100*En_rOM, #liquid feed exception
             f$Fd_CP/100*En_CP + f$Fd_FA/100*En_FA + f$Fd_St/100*En_St + f$Fd_NDF/100*En_NDF + (100-f$Fd_CP-f$Fd_FA-f$Fd_St-f$Fd_NDF-f$Fd_Ash)/100*En_rOM) #the remainder

################### DMI Calculations ###########################
#Calculate calf liquid feed DM and ME intakes from target DMIn
f$Fd_DMIn_ClfLiq <- ifelse(An_StatePhys=="Calf" & f$Fd_Category == "Calf Liquid Feed", as.vector(Trg_Dt_DMIn) * Fd_DMInp, 0)  #milk intake 
f$Fd_DE_ClfLiq <- ifelse(An_StatePhys=="Calf" & f$Fd_Category == "Calf Liquid Feed", 0.95 * f$Fd_GE, 0)  #prelim estimate for DMI only, mcal/kg, nutrients are in %
f$Fd_ME_ClfLiq <- ifelse(An_StatePhys=="Calf" & f$Fd_Category == "Calf Liquid Feed", f$Fd_DE_ClfLiq * 0.96, 0)  #mcal/kg, nutrients are in %
Dt_DMIn_ClfLiq <- sum(f$Fd_DMIn_ClfLiq,  na.rm=TRUE)                                #GE to ME calculates as 0.882  
Dt_DEIn_ClfLiq <- sum(f$Fd_DE_ClfLiq*f$Fd_DMIn_ClfLiq,  na.rm=TRUE) 
Dt_MEIn_ClfLiq <- sum(f$Fd_ME_ClfLiq*f$Fd_DMIn_ClfLiq,  na.rm=TRUE) 
Dt_DE_ClfLiq <- Dt_DEIn_ClfLiq / Dt_DMIn_ClfLiq    #DE content of the liquid feed.
Dt_DE_ClfLiq <- ifelse(is.na(Dt_DE_ClfLiq), 0, Dt_DE_ClfLiq)
Dt_ME_ClfLiq <- Dt_MEIn_ClfLiq / Dt_DMIn_ClfLiq    #ME content of the liquid feed.
Dt_ME_ClfLiq <- ifelse(is.na(Dt_ME_ClfLiq), 0, Dt_ME_ClfLiq)
f$Dt_DMIn_ClfLiq <- as.vector(Dt_DMIn_ClfLiq)  #Add liquid feed intake vector to  the f DF for use in ingredient calculations

#Forage Intake calculated from target DMIn
f$Fd_DMIn_ClfFor <- (1-f$Fd_Conc/100)*as.vector(Trg_Dt_DMIn) * Fd_DMInp
Dt_DMIn_ClfFor <- sum(f$Fd_DMIn_ClfFor,  na.rm=TRUE)

# Predict Calf Starter Intake, kg/d ######
#Temperate Environment Predicted Starter Intake
Dt_DMIn_ClfStrt <- (-652.5 + 14.734*An_BW + 18.896*Dt_MEIn_ClfLiq + 73.3*An_AgeDryFdStart/7 + 
               13.496*(An_AgeDryFdStart/7)^2 - 29.614*An_AgeDryFdStart/7*Dt_MEIn_ClfLiq)/1000

#Tropical Environment Predicted Starter Intake, TempCurr > UCT + 10 degrees C.  
Dt_DMIn_ClfStrt <- ifelse(Env_TempCurr>(UCT+10), 
                         (600.1 * (1 + 14863.7*exp(-1.553*An_AgeDryFdStart/7))^-1 + 9.951*An_BW - 130.434*Dt_MEIn_ClfLiq)/1000,
                    Dt_DMIn_ClfStrt)           	#An_AgeDryFdStart is expressed in days of age
Dt_DMIn_Calf1 <- Dt_DMIn_ClfLiq + Dt_DMIn_ClfStrt + Dt_DMIn_ClfFor #DMI w/ predicted starter

#Adjust Starter Intake based on target intake if DMIeqn=0.
Dt_DMIn_ClfStrt <- ifelse(DMIn_eqn==0 & (Dt_DMIn_ClfLiq+Dt_DMIn_ClfStrt+Dt_DMIn_ClfFor) != Trg_Dt_DMIn,
                          Trg_Dt_DMIn-Dt_DMIn_ClfLiq-Dt_DMIn_ClfFor, Dt_DMIn_ClfStrt) 

###### Growing Heifer Equations, kg/d ######
#NRC 2020 Heifer Eqns. from the Transition Ch.
Dt_NDFdev_DMI <- Dt_NDF - (23.11 + 0.07968*An_BW - 0.00006252*An_BW^2)

Dt_DMIn_Heif_NRCa <- 0.022*An_BW_mature * (1 - exp(-1.54*An_BW/An_BW_mature))	#Animal factors only, eqn. 2-3 NRC
Dt_DMIn_Heif_H1 <- 15.36 * (1 - exp(-0.0022*An_BW))	   #Holstein, animal factors only
Dt_DMIn_Heif_HJ1 <- 12.91 * (1 - exp(-0.00295*An_BW)) 	#Holstein x Jersey, animal factors only
Dt_DMIn_Heif_NRCad <- (0.0226*An_BW_mature*(1-exp(-1.47*An_BW/An_BW_mature))) - (0.082*(Dt_NDF - 
                     (23.1+56*An_BW/An_BW_mature)-30.6*(An_BW/An_BW_mature)^2)) #Anim & diet factors, eqn 2-4 NRC
Dt_DMIn_Heif_H2 <- 15.79 * (1 - exp(-0.0021*An_BW)) - (0.082*Dt_NDFdev_DMI)	#Holstein, animal factors and NDF
Dt_DMIn_Heif_HJ2 <- 13.48 * (1 - exp(-0.0027*An_BW)) - (0.082*Dt_NDFdev_DMI)	#Holstein x Jersey, animal factors and NDF

#Late Gestation eqn. from Hayirli et al., 2003) for dry cows and heifers
An_PrePartWklim <- ifelse(An_PrePartWk < -3, -3, An_PrePartWk)  #constrain to the interval 0 to -3.
An_PrePartWklim <- ifelse(An_PrePartWk > 0, 0, An_PrePartWklim)
An_PrePartWkDurat <- An_PrePartWklim * 2  #the estimated length of time in the close-up pen

Dt_NDF_drylim <- Dt_NDF
Dt_NDF_drylim <- ifelse(Dt_NDF < 30, 30, Dt_NDF_drylim)  #constrain Dt_NDF to the range of 30 to 55% of DM
Dt_NDF_drylim <- ifelse(Dt_NDF > 55, 55, Dt_NDF_drylim)

Ka_LateGest_DMIn <- 1.47 #% of BW
Kb_LateGest_DMIn <- -(0.365-0.0028*Dt_NDF_drylim)
Kc_LateGest_DMIn <- -0.035

#Late gestation individual animal prediction, % of BW.  Use to assess for a specific day for a given animal
Dt_DMIn_BW_LateGest_i <- Ka_LateGest_DMIn + Kb_LateGest_DMIn*An_PrePartWklim + Kc_LateGest_DMIn*An_PrePartWklim^2

#Late gestation Group/Pen mean DMI/BW for an interval of 0 to PrePart_WkDurat.  Assumes pen steady state and PrePart_wk = pen mean
Dt_DMIn_BW_LateGest_p <- (Ka_LateGest_DMIn*An_PrePartWkDurat + Kb_LateGest_DMIn/2*An_PrePartWkDurat^2 + 
                             Kc_LateGest_DMIn/3*An_PrePartWkDurat^3)/An_PrePartWkDurat
#Individual intake for the specified day prepart or the pen mean intake for the interval, 0 to PrePart_WkDurat
Dt_DMIn_Heif_LateGestInd <- 0.88*An_BW * Dt_DMIn_BW_LateGest_i/100 #Individual animal
Dt_DMIn_Heif_LateGestPen <- 0.88*An_BW * Dt_DMIn_BW_LateGest_p/100 #Pen mean

#Switch to the group transition eqn. when less than An_PrePartWkDurat and predicted transition DMI is less than far off DMI
#These equations generally are discontinuous at -3 weeks, as Dt_DMIn_xxx is greater than Dt_DMIn_xxx_LateGest at -3.  
#Should calculate the decline using the far off DMIn as a reference point, or calculate the discontinuity at the
#point of transition and adjust the close-up DMIn by addition of the gap.
#NRC 2020 pen intakes
Dt_DMIn_Heif_NRCap <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                           min(c(Dt_DMIn_Heif_NRCa,Dt_DMIn_Heif_LateGestPen)), Dt_DMIn_Heif_NRCa)
Dt_DMIn_Heif_NRCadp <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                             min(c(Dt_DMIn_Heif_NRCad,Dt_DMIn_Heif_LateGestPen)), Dt_DMIn_Heif_NRCad)
Dt_DMIn_Heif_H1p <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                          min(c(Dt_DMIn_Heif_H1,Dt_DMIn_Heif_LateGestPen)), Dt_DMIn_Heif_H1)
Dt_DMIn_Heif_HJ1p <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                           min(c(Dt_DMIn_Heif_HJ1,Dt_DMIn_Heif_LateGestPen)), Dt_DMIn_Heif_HJ1)
Dt_DMIn_Heif_H2p <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                          min(c(Dt_DMIn_Heif_H2,Dt_DMIn_Heif_LateGestPen)), Dt_DMIn_Heif_H2)
Dt_DMIn_Heif_HJ2p <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                           min(c(Dt_DMIn_Heif_HJ2,Dt_DMIn_Heif_LateGestPen)), Dt_DMIn_Heif_HJ2)
#NRC 2020 individual animal intakes
Dt_DMIn_Heif_NRCai <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                              min(c(Dt_DMIn_Heif_NRCa,Dt_DMIn_Heif_LateGestInd)), Dt_DMIn_Heif_NRCa)
Dt_DMIn_Heif_NRCadi <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                             min(c(Dt_DMIn_Heif_NRCad,Dt_DMIn_Heif_LateGestInd)), Dt_DMIn_Heif_NRCad)
Dt_DMIn_Heif_H1i <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                           min(c(Dt_DMIn_Heif_H1,Dt_DMIn_Heif_LateGestInd)), Dt_DMIn_Heif_H1)
Dt_DMIn_Heif_HJ1i <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                            min(c(Dt_DMIn_Heif_HJ1,Dt_DMIn_Heif_LateGestInd)), Dt_DMIn_Heif_HJ1)
Dt_DMIn_Heif_H2i <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                           min(c(Dt_DMIn_Heif_H2,Dt_DMIn_Heif_LateGestInd)), Dt_DMIn_Heif_H2)
Dt_DMIn_Heif_HJ2i <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                            min(c(Dt_DMIn_Heif_HJ2,Dt_DMIn_Heif_LateGestInd)), Dt_DMIn_Heif_HJ2)

########################### Lactating Cows ###########################
# Calculate Target Milk Energy to use for DMI predictions #
#Needed to predict DMI for lactating cows
Trg_NEmilk_Milk <- 9.29*Trg_MilkFatp/100 + 5.85*Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100
#If milk protein and lactose are not provided, use the Tyrrell and Reid (1965) eqn.
Trg_NEmilk_Milk <- ifelse(is.na(Trg_NEmilk_Milk), 0.36+9.69*Trg_MilkFatp/100, Trg_NEmilk_Milk)
Trg_NEmilkOut <- Trg_NEmilk_Milk * Trg_MilkProd

### Animal factors only, eqn. 2-1 ###
Dt_DMIn_Lact1 <- (3.7 + 5.7*(An_Parity_rl-1) + 0.305*Trg_NEmilkOut + 0.022*An_BW + 
	(-0.689 - 1.87*(An_Parity_rl-1))*An_BCS) * (1 - (0.212 + 0.136*(An_Parity_rl-1)) * 
	exp(-0.053*An_LactDay))

### Animal and diet factors, eqn. 2-2. ###
Dt_DMIn_Lact2 <- 12.0 - 0.107*Dt_ForNDF + 8.17*Dt_ADF/Dt_NDF + 0.0253*Dt_ForDNDF48_ForNDF - 
   0.328*(Dt_ADF/Dt_NDF - 0.602) * (Dt_ForDNDF48_ForNDF - 48.3) + 
   0.225*Trg_MilkProd + 0.00390*(Dt_ForDNDF48_ForNDF - 48.3) * (Trg_MilkProd - 33.1)


########################## Dry Cow Equations  ############################
#NRC 2020, Transition Cow Chapter Eqn.
Dt_DMIn_DryCow1_FarOff <- An_BW * Dt_DMIn_BW_LateGest_i/100
Dt_DMIn_DryCow1_Close <- An_BW * Dt_DMIn_BW_LateGest_p/100  #used to estimate close-up DMIn depression
#Switch to the group transition eqn. when less than An_PrePartWkDurat and predicted transition DMI is less than far off DMI
Dt_DMIn_DryCow1 <- ifelse(An_PrePartWk > An_PrePartWkDurat, 
                          min(c(Dt_DMIn_DryCow1_FarOff,Dt_DMIn_DryCow1_Close)), Dt_DMIn_DryCow1_FarOff)


## from Hayirli et al., 2003 JDS
Dt_DMIn_DryCow_AdjGest <- An_BW * (-0.756*exp(0.154*(An_GestDay-An_GestLength)))/100
Dt_DMIn_DryCow_AdjGest <- ifelse((An_GestDay-An_GestLength) < -21, 0, Dt_DMIn_DryCow_AdjGest)
Dt_DMIn_DryCow2 <- An_BW * 1.979/100 + Dt_DMIn_DryCow_AdjGest

###### Select the appropriate prediction for use by the model #######
#add 1 so that a selection of 0 yields the first choice, etc.
#Only 1, 2, 3, 8, 9, and 10 are NRC eqns. 
Dt_DMIn <- switch(DMIn_eqn + 1,
	Trg_Dt_DMIn,
	Dt_DMIn_Calf1,      #Milk fed calf
	Dt_DMIn_Heif_NRCai, #All heifers, animal factors only, NRC equation, individual animal
	Dt_DMIn_Heif_NRCadi, #All heifers, animal and feed factors, NRC equation, individual animal
	Dt_DMIn_Heif_H1i,   #Holstein heifer, animal factors only, individual prepartum
	Dt_DMIn_Heif_H2i,   #Holstein heifer, animal and feed factors, individual prepartum
	Dt_DMIn_Heif_HJ1i,  #Holstein x Jersey heifer, animal factors only, individual prepartum
	Dt_DMIn_Heif_HJ2i,  #Holstein x Jersey heifer, animal and feed factors, individual prepartum
	Dt_DMIn_Lact1,      #lactating, cow factors only
	Dt_DMIn_Lact2,      #lactating, cow and feed factors
	Dt_DMIn_DryCow1,    #dry, NRC 2020
	Dt_DMIn_DryCow2,    #dry, Hayirli, 2003
	Dt_DMIn_Heif_NRCap, #All heifers, animal factors only, NRC equation, pen based intake
	Dt_DMIn_Heif_NRCadp, #All heifers, animal and feed factors, NRC equation, pen based intake
	Dt_DMIn_Heif_H1p,   #Holstein heifer, animal factors only, pen prepartum
	Dt_DMIn_Heif_H2p,   #Holstein heifer, animal and feed factors, pen prepartum
	Dt_DMIn_Heif_HJ1p,  #Holstein x Jersey heifer, animal factors only, pen prepartum
	Dt_DMIn_Heif_HJ2p  #Holstein x Jersey heifer, animal and feed factors, pen prepartum
)

Dt_DMIn_BW <- Dt_DMIn / An_BW
Dt_DMIn_MBW <- Dt_DMIn / An_BW^0.75

#Calculate DMIn and AFIn for each Ingredient
f$Fd_DMIn <- Fd_DMInp * as.vector(Dt_DMIn)
f$Fd_AFIn <- ifelse(f$Fd_DM == 0, 0, f$Fd_DMIn/(f$Fd_DM / 100))

############ Calculate additional nutrients and fractions #################
#Percent of each ingredient that is Dry and Wet Forage, Pasture, and Calf Liquid feed
f$Fd_For <- 100 - f$Fd_Conc
f$Fd_ForWet <-ifelse(f$Fd_For > 50 & f$Fd_DM < 71, f$Fd_For, 0)
f$Fd_ForDry <-ifelse(f$Fd_For > 50 & f$Fd_DM >= 71, f$Fd_For, 0)
f$Fd_Past <-ifelse(f$Fd_Category == "Pasture", 100, 0); #Identify pasture for grazing calculations.
f$Fd_LiqClf <- ifelse(f$Fd_Category == "Calf Liquid Feed", 100, 0); #Redundant as already calculated in DMIn section.
#Other nutrients
f$Fd_ForNDF <- (1-f$Fd_Conc/100) * f$Fd_NDF
f$Fd_NDFnf <- f$Fd_NDF - f$Fd_NDFIP 			#N free (nf) NDF percent in Feed

f$Fd_NPNCP <- f$Fd_CP * f$Fd_NPN_CP / 100	#calculate the NPN in CP equivalent in the feed DM
                                          #Fd_NPN_CP is the % of CP coming from NPN (0-100)
f$Fd_NPN <- f$Fd_NPNCP / 6.25					#Calculate the N in the NPNCP as a percent of feed DM
f$Fd_NPNDM <- f$Fd_NPNCP / 2.81				#Estimate the mass of NPN based on urea N content
f$Fd_TP <- f$Fd_CP - f$Fd_NPNCP				#subtract the NPNCP from Fd_CP which removes the N mass

f$Fd_fHydr_FA <- 1/1.06						#Corrects for dehydration of FA in TAG
f$Fd_fHydr_FA <- ifelse(f$Fd_Category == "Fatty Acid Supplement", 1, f$Fd_fHydr_FA)
f$Fd_FAhydr <- f$Fd_FA*f$Fd_fHydr_FA 

f$Fd_NFC <- 100-f$Fd_Ash-f$Fd_NDF-f$Fd_TP-f$Fd_NPNDM-f$Fd_FAhydr
f$Fd_NFC <- ifelse(f$Fd_NFC < 0, 0, f$Fd_NFC)		 #corrected for NDFIP and NPN, MDH

f$Fd_rOM <- 100-f$Fd_Ash-f$Fd_NDF-f$Fd_St-(f$Fd_FA*f$Fd_fHydr_FA)-f$Fd_TP-f$Fd_NPNDM
	#results in quite negative values for the protein meals due to NDF: meat, feather, blood...
	#WSC is contained within rOM until soluble starch is cleaned from WSC, MDH


############ Calculate nutrient intakes for each feed ################
f$Fd_ADFIn <- f$Fd_ADF/100 * f$Fd_DMIn
f$Fd_NDFIn <- f$Fd_NDF/100 * f$Fd_DMIn
f$Fd_StIn <- f$Fd_St/100 * f$Fd_DMIn
f$Fd_NFCIn <- f$Fd_NFC/100 * f$Fd_DMIn
f$Fd_WSCIn <- f$Fd_WSC/100 * f$Fd_DMIn
f$Fd_rOMIn <- f$Fd_rOM/100 * f$Fd_DMIn
f$Fd_LgIn <- f$Fd_Lg/100 * f$Fd_DMIn
f$Fd_DigNDFIn_Base <- f$TT_dcFdNDF_Base/100 * f$Fd_NDFIn

f$Fd_ConcIn <- f$Fd_Conc/100 * f$Fd_DMIn
f$Fd_ForIn <- f$Fd_For/100 * f$Fd_DMIn 
f$Fd_ForWetIn <- f$Fd_ForWet/100  * f$Fd_DMIn
f$Fd_ForDryIn <- f$Fd_ForDry/100 * f$Fd_DMIn
f$Fd_PastIn <- f$Fd_Past/100 * f$Fd_DMIn
#Calculate Protein fraction intakes for each feed
f$Fd_CPIn <- f$Fd_CP/100 * f$Fd_DMIn 
f$Fd_TPIn <- f$Fd_TP/100 * f$Fd_DMIn 
f$Fd_NPNCPIn <- f$Fd_CPIn * f$Fd_NPN_CP/100 #Fd_NPN_CP is the % of CP that is from NPN
f$Fd_NPNIn <- f$Fd_NPNCPIn * 0.16 
f$Fd_NPNDMIn <- f$Fd_NPNCPIn / 2.81
f$Fd_CPAIn <- f$Fd_CPIn*f$Fd_CPARU/100
f$Fd_CPBIn <- f$Fd_CPIn*f$Fd_CPBRU/100
f$Fd_CPBIn_For <- f$Fd_CPIn*f$Fd_CPBRU/100*f$Fd_For/100
f$Fd_CPBIn_Conc <- f$Fd_CPIn*f$Fd_CPBRU/100*f$Fd_Conc/100
f$Fd_CPCIn <- f$Fd_CPIn*f$Fd_CPCRU/100
f$Fd_CPIn_ClfLiq <-ifelse(f$Fd_Category == "Calf Liquid Feed", f$Fd_DMIn * f$Fd_CP/100, 0)
f$Fd_CPIn_ClfDry <-ifelse(f$Fd_Category == "Calf Liquid Feed",0, f$Fd_DMIn * f$Fd_CP/100)

#### Rumen Degraded and Undegraded Protein ####
#Bayesian equation developed by Hanigan and NRC Protein Subcomm
#Note, the units are kg/d not g/d as for the NRC2001 equations
#Moved this section up from Digestion to allow calculation of DE_base.

#Calculate RUP and the fraction of B passing for each feed, kg/d
KpConc <- 5.28	   #From Bayesian fit to Digesta Flow data with Seo Kp as priors, eqn. 26 in Hanigan et al.
KpFor <- 4.87     #%/h
fCPAdu <- 0.064	#kg CPA passaing/kg of CPA
IntRUP <- -0.086 	#Intercept, kg/d
refCPIn <- 3.39  	#average CPIn for the DigestaFlow dataset, kg/d.  3/21/18, MDH

f$Fd_rdcRUPB <- 100 - (f$Fd_For * KpFor/(f$Fd_KdRUP+KpFor) + f$Fd_Conc * 
                            KpConc/(f$Fd_KdRUP+KpConc))
f$Fd_RUPBIn <- f$Fd_CPBIn * f$Fd_For/100 * KpFor/(f$Fd_KdRUP+KpFor) + 
     f$Fd_CPBIn * f$Fd_Conc/100 * KpConc/(f$Fd_KdRUP+KpConc)
f$Fd_RUPIn <- (f$Fd_CPAIn-f$Fd_NPNCPIn) * fCPAdu + f$Fd_RUPBIn + f$Fd_CPCIn + 
     IntRUP/refCPIn*f$Fd_CPIn   #refCPIn should really be the CPIn for the diet rather than a static value. Int is scaling with CPI 
#as written rather than being a true constant, but this may be better for young heifers.
f$Fd_RUP_CP <- ifelse(f$Fd_CPIn > 0, f$Fd_RUPIn/f$Fd_CPIn*100, 0)
f$Fd_RUP <- ifelse(f$Fd_CPIn > 0, f$Fd_RUPIn/f$Fd_DMIn*100, 0)
f$Fd_RDP <- ifelse(f$Fd_CPIn > 0, f$Fd_CP - f$Fd_RUP, 0)

#Calculate total fat and fatty acid intakes
f$Fd_CFatIn <- f$Fd_CFat/100 * f$Fd_DMIn
f$Fd_FAIn <- f$Fd_FA/100*f$Fd_DMIn
f$Fd_FAhydrIn <- f$Fd_FAhydr/100*f$Fd_DMIn

#Calculate intakes of specific FA for each feed
f$Fd_C120In <- f$Fd_C120_FA/100 * f$Fd_FA/100 * f$Fd_DMIn 
f$Fd_C140In <- f$Fd_C140_FA/100 * f$Fd_FA/100 * f$Fd_DMIn 
f$Fd_C160In <- f$Fd_C160_FA/100 * f$Fd_FA/100 * f$Fd_DMIn
f$Fd_C161In <- f$Fd_C161_FA/100 * f$Fd_FA/100 * f$Fd_DMIn 
f$Fd_C180In <- f$Fd_C180_FA/100 * f$Fd_FA/100 * f$Fd_DMIn 
f$Fd_C181tIn <- f$Fd_C181t_FA/100 * f$Fd_FA/100 * f$Fd_DMIn 
f$Fd_C181cIn <- f$Fd_C181c_FA/100 * f$Fd_FA/100 * f$Fd_DMIn 
f$Fd_C182In <- f$Fd_C182_FA/100 * f$Fd_FA/100 * f$Fd_DMIn 
f$Fd_C183In <- f$Fd_C183_FA/100 * f$Fd_FA/100 * f$Fd_DMIn 
f$Fd_OtherFAIn <- f$Fd_OtherFA_FA/100 * f$Fd_FA/100 * f$Fd_DMIn 

f$Fd_AshIn <- f$Fd_Ash/100 * f$Fd_DMIn
f$Fd_OMIn <- f$Fd_DMIn - f$Fd_AshIn
f$Fd_GEIn <- f$Fd_GE * f$Fd_DMIn

#Base Digestible Energy values calculated from nutrients.  Also calculated in software interface and provided in the Feed Library. Not discounted.
#Standard Equation 1 - IVNDF not used
f$Fd_DE_base_1 <- 0.75*(f$Fd_NDF-f$Fd_Lg)*(1-((f$Fd_Lg / ifelse(f$Fd_NDF==0, 1e-9, f$Fd_NDF))^0.667))*0.042 +
     f$Fd_St*f$Fd_dcSt/100*0.0423 + f$Fd_FA*f$Fd_dcFA/100*0.094 + 
     (100-(f$Fd_FA/1.06)-f$Fd_Ash-f$Fd_NDF-f$Fd_St-(f$Fd_CP-(f$Fd_NPNCP-f$Fd_NPNCP/2.81)))*0.96*0.04 + 
     ((f$Fd_CP-f$Fd_RUP/100*f$Fd_CP)+f$Fd_RUP/100*f$Fd_CP*f$Fd_dcRUP/100-f$Fd_NPNCP)*0.0565 + 
     f$Fd_NPNCP*0.0089 - (0.137+0.093+0.088)
#Standard equation 2 - based on setting of IVNDF use switch
f$Fd_DE_base_2 <- ((0.12+0.0061*f$Fd_DNDF48_NDF)*f$Fd_NDF*0.042) + (f$Fd_St*f$Fd_dcSt/100*0.0423) + 
     (f$Fd_FA*f$Fd_dcFA/100*0.094) + ((100-(f$Fd_FA/1.06)-(f$Fd_CP-(f$Fd_NPNCP-f$Fd_NPNCP/2.81))-f$Fd_Ash-f$Fd_NDF-
     f$Fd_St)*0.96*0.04) + ((f$Fd_CP-f$Fd_RUP/100*f$Fd_CP)+f$Fd_RUP/100*f$Fd_CP*f$Fd_dcRUP/100-f$Fd_NPNCP)*0.0565 + 
     f$Fd_NPNCP*0.0089 - (0.137+0.093+0.088)
f$Use_DNDF_IV <- as.vector(Use_DNDF_IV)
f$Fd_DE_base <- ifelse(f$Use_DNDF_IV == 0, f$Fd_DE_base_1, f$Fd_DE_base_2)
f$Fd_DE_base <- ifelse(f$Use_DNDF_IV == 1 & f$Fd_For == 0, f$Fd_DE_base_1, f$Fd_DE_base)
f$Fd_DE_base <- ifelse(f$Fd_Category == "Animal Protein",
                    0.73*f$Fd_FA*0.094 + (f$Fd_RDP + (f$Fd_RUP*f$Fd_dcRUP))*0.056 + (0.96*(100-
                    f$Fd_FA/1.06-f$Fd_CP-f$Fd_Ash)*0.04)-0.318, f$Fd_DE_base) #where RDP and RUP are % of CP
f$Fd_DE_base <- ifelse(f$Fd_Category == "Fat Supplement",
                    f$Fd_FA*f$Fd_dcFA/100*0.094 + (100-f$Fd_Ash-(f$Fd_FA/1.06)*0.96)*0.043-0.318, f$Fd_DE_base)
f$Fd_DE_base <- ifelse(f$Fd_Category == "Fatty Acid Supplement", f$Fd_FA*f$Fd_dcFA/100*0.094-0.318, f$Fd_DE_base)
f$Fd_DE_base <- ifelse(f$Fd_Category == "Calf Liquid Feed", (0.094*f$Fd_FA+0.057*f$Fd_CP+0.04*(100-f$Fd_Ash-f$Fd_CP-f$Fd_FA))*0.95, f$Fd_DE_base)
f$Fd_DE_base <- ifelse(f$Fd_Category == "Sugar/Sugar Alcohol", (100-f$Fd_Ash)*0.04*0.96-0.318, f$Fd_DE_base)
f$Fd_DE_base <- ifelse(f$Fd_Category == "Vitamin/Mineral", 0, f$Fd_DE_base)
f$Fd_DE_base <- ifelse(f$Fd_Category == "Vitamin/Mineral" & f$Fd_NPN>0, (f$Fd_CP*0.089)-0.318, f$Fd_DE_base)
#According to Weiss, need to set urea, ammonium phoshate and other NPN sources to: (Fd_CP * 0.089) - 0.318. 
#It appears they are set to 0 in the software, rather than as Bill specified. MDH

f$Fd_DEIn_base <- f$Fd_DE_base * f$Fd_DMIn
f$Fd_DEIn_base_ClfLiq <-ifelse(f$Fd_Category == "Calf Liquid Feed",f$Fd_DEIn_base, 0)
f$Fd_DEIn_base_ClfDry <-ifelse(f$Fd_Category == "Calf Liquid Feed",0, f$Fd_DEIn_base)

############### Calculate Dietary DM and AF Intakes ##################
Dt_DMInSum <- sum(f$Fd_DMIn, na.rm=TRUE)
Dt_AFIn <- sum(f$Fd_AFIn, na.rm=TRUE)

# Calculate the AF and DM ingredient inclusion rates
f$Fd_DMInp <- f$Fd_DMIn / Dt_DMIn * 100
f$Fd_AFInp <- f$Fd_AFIn / Dt_AFIn * 100

#Calculate Dietary Nutrient Intakes
Dt_NDFIn <- sum(f$Fd_NDFIn, na.rm=TRUE)
Dt_NDFnfIn <- sum(f$Fd_NDFnf/100*f$Fd_DMIn, na.rm=TRUE)
Dt_ADFIn <- sum(f$Fd_ADFIn, na.rm=TRUE)
Dt_LgIn <- sum(f$Fd_LgIn, na.rm=TRUE)
Dt_Lg_NDF <- Dt_LgIn / Dt_NDFIn * 100
Dt_ForNDFIn <- sum(f$Fd_ForNDF/100*f$Fd_DMIn, na.rm=TRUE)
Dt_DigNDFIn_Base <- sum(f$Fd_DigNDFIn_Base, na.rm=TRUE)
Dt_ForWetIn <- sum(f$Fd_ForWetIn, na.rm=TRUE)
Dt_ForDryIn <- sum(f$Fd_ForDryIn, na.rm=TRUE)
Dt_PastIn <- sum(f$Fd_PastIn, na.rm=TRUE)
Dt_PastSupplIn <- Dt_DMInSum - Dt_PastIn;		#Could be supplemental concentrate or forage.
Dt_ForIn <- sum(f$Fd_ForIn, na.rm=TRUE)
Dt_ConcIn <- sum(f$Fd_ConcIn, na.rm=TRUE)

Dt_NFCIn <- sum(f$Fd_NFCIn, na.rm=TRUE)
Dt_StIn <- sum(f$Fd_StIn, na.rm=TRUE)
Dt_WSCIn <- sum(f$Fd_WSCIn, na.rm=TRUE)

Dt_CPIn <- sum(f$Fd_CPIn, na.rm=TRUE)
Dt_CPIn_ClfLiq <- sum(f$Fd_CPIn_ClfLiq, na.rm=TRUE)
Dt_TPIn <- sum(f$Fd_TPIn, na.rm=TRUE)
Dt_NPNCPIn <- sum(f$Fd_NPNCPIn, na.rm=TRUE)
Dt_NPNIn <- sum(f$Fd_NPNIn, na.rm=TRUE)
Dt_NPNDMIn <- sum(f$Fd_NPNDMIn, na.rm=TRUE)
Dt_CPAIn <- sum(f$Fd_CPAIn, na.rm=TRUE)
Dt_CPBIn <- sum(f$Fd_CPBIn, na.rm=TRUE)
Dt_CPCIn <- sum(f$Fd_CPCIn, na.rm=TRUE)
Dt_NIn <- Dt_CPIn / 6.25
Dt_RUPBIn <- sum(f$Fd_RUPBIn, na.rm=TRUE)
Dt_RUPIn <- sum(f$Fd_RUPIn, na.rm=TRUE)
Dt_RUPIn <- ifelse(Dt_RUPIn < 0, 0, Dt_RUPIn)
#The following diet level RUPIn is slightly more accurate than the feed level summation as the intercept exactly matches the regression equations, but feed level is very close.
Dt_RUPIn.dt <- (Dt_CPAIn-Dt_NPNIn) * fCPAdu + Dt_RUPBIn + Dt_CPCIn + IntRUP  #if concerned about intercept, switch to using this eqn for RUP
Dt_RUP <- Dt_RUPIn / Dt_DMIn *100
Dt_RUP_CP <- Dt_RUPIn / Dt_CPIn * 100
Dt_fCPBdu <- Dt_RUPBIn / Dt_CPBIn



Dt_CFatIn <- sum(f$Fd_CFatIn, na.rm=TRUE)
Dt_FAIn <- sum(f$Fd_FAIn, na.rm=TRUE)
Dt_FAhydrIn <- sum(f$Fd_FAhydrIn, na.rm=TRUE)
Dt_C120In <- sum(f$Fd_C120In, na.rm=TRUE)
Dt_C140In <- sum(f$Fd_C140In, na.rm=TRUE)
Dt_C160In <- sum(f$Fd_C160In, na.rm=TRUE)
Dt_C161In <- sum(f$Fd_C161In, na.rm=TRUE)
Dt_C180In <- sum(f$Fd_C180In, na.rm=TRUE)
Dt_C181tIn <- sum(f$Fd_C181tIn, na.rm=TRUE)
Dt_C181cIn <- sum(f$Fd_C181cIn, na.rm=TRUE)
Dt_C182In <- sum(f$Fd_C182In, na.rm=TRUE)
Dt_C183In <- sum(f$Fd_C183In, na.rm=TRUE)
Dt_OtherFAIn <- sum(f$Fd_OtherFAIn, na.rm=TRUE)
Dt_UFAIn <- Dt_C161In + Dt_C181tIn+ Dt_C181cIn + Dt_C182In + Dt_C183In
Dt_MUFAIn <- Dt_C161In + Dt_C181tIn+ Dt_C181cIn
Dt_PUFAIn <- Dt_UFAIn - (Dt_C161In + Dt_C181tIn+ Dt_C181cIn)
Dt_SatFAIn <- Dt_FAIn - Dt_UFAIn

Dt_AshIn <- sum(f$Fd_AshIn, na.rm=TRUE)
Dt_OMIn <- Dt_DMIn - Dt_AshIn
Dt_rOMIn <- Dt_DMIn-Dt_AshIn-Dt_NDFIn-Dt_StIn-Dt_FAhydrIn-Dt_TPIn-Dt_NPNDMIn #Is negative on some diets. Some Ash and CP in NDF, and
Dt_rOMIn <- ifelse(Dt_rOMIn < 0, 0, Dt_rOMIn)                                #water from FAhydr in TAG contributes.  Trap negative Dt values.
                                                                             #More likely due to entry errors or bad analyses of other nutrients.
Dt_GEIn <- sum(f$Fd_GEIn, na.rm=TRUE)
Dt_DEIn_base <- sum(f$Fd_DEIn_base, na.rm=TRUE)
Dt_DEIn_base_ClfLiq <- sum(f$Fd_DEIn_base_ClfLiq, na.rm=TRUE)
Dt_DEIn_base_ClfDry <- sum(f$Fd_DEIn_base_ClfDry, na.rm=TRUE)

#Calculate Dietary Nutrient Concentrations
Dt_DM <- Dt_DMIn / Dt_AFIn * 100
Dt_OM <- Dt_OMIn / Dt_DMIn * 100
Dt_NDF <- Dt_NDFIn / Dt_DMIn * 100
Dt_NDFIn_BW <- Dt_NDFIn / An_BW * 100
Dt_NDFnf <- Dt_NDFnfIn / Dt_DMIn * 100
Dt_ADF <- Dt_ADFIn / Dt_DMIn * 100
Dt_Lg <- Dt_LgIn / Dt_DMIn * 100
Dt_ForNDF <- Dt_ForNDFIn / Dt_DMIn * 100
Dt_ForNDF_NDF <- Dt_ForNDF/Dt_NDF*100
Dt_ForNDFIn_BW <- Dt_ForNDFIn / An_BW * 100

Dt_NFC <- Dt_NFCIn / Dt_DMIn * 100
Dt_St <- Dt_StIn / Dt_DMIn * 100
Dt_WSC <- Dt_WSCIn / Dt_DMIn * 100
Dt_rOM <- Dt_rOMIn / Dt_DMIn * 100

Dt_CFat <- Dt_CFatIn / Dt_DMIn * 100
Dt_FA <- Dt_FAIn / Dt_DMIn * 100
Dt_FAhydr <- Dt_FAhydrIn / Dt_DMIn * 100

Dt_CP <- Dt_CPIn / Dt_DMIn * 100
Dt_TP <- Dt_TPIn / Dt_DMIn * 100
Dt_NPNCP <- Dt_NPNCPIn / Dt_DMIn * 100
Dt_NPN <- Dt_NPNIn / Dt_DMIn * 100
Dt_NPNDM <- Dt_NPNDMIn / Dt_DMIn * 100

Dt_CPA <- Dt_CPAIn / Dt_DMIn * 100
Dt_CPB <- Dt_CPBIn / Dt_DMIn * 100
Dt_CPC <- Dt_CPCIn / Dt_DMIn * 100
Dt_CPA_CP <- Dt_CPAIn / Dt_CPIn * 100
Dt_CPB_CP <- Dt_CPBIn / Dt_CPIn * 100
Dt_CPC_CP <- Dt_CPCIn / Dt_CPIn * 100

Dt_Ash <- Dt_AshIn / Dt_DMIn * 100

Dt_ForWet <- Dt_ForWetIn / Dt_DMIn * 100
Dt_ForDry <- Dt_ForDryIn / Dt_DMIn * 100
Dt_For <- Dt_ForIn / Dt_DMIn * 100
Dt_Conc <- Dt_ConcIn / Dt_DMIn * 100

#FA as a % of DM
Dt_C120 <- Dt_C120In / Dt_DMIn * 100
Dt_C140 <- Dt_C140In / Dt_DMIn * 100
Dt_C160 <- Dt_C160In / Dt_DMIn * 100
Dt_C161 <- Dt_C161In / Dt_DMIn * 100
Dt_C180 <- Dt_C180In / Dt_DMIn * 100
Dt_C181t <- Dt_C181tIn / Dt_DMIn * 100
Dt_C181c <- Dt_C181cIn / Dt_DMIn * 100
Dt_C182 <- Dt_C182In / Dt_DMIn * 100
Dt_C183 <- Dt_C183In / Dt_DMIn * 100
Dt_OtherFA <- Dt_OtherFAIn / Dt_DMIn * 100
Dt_UFA <- Dt_UFAIn / Dt_DMIn * 100
Dt_MUFA <- Dt_MUFAIn / Dt_DMIn * 100
Dt_PUFA <- Dt_PUFAIn / Dt_DMIn * 100
Dt_SatFA <- Dt_SatFAIn / Dt_DMIn * 100

#FA as a percent of total FA
Dt_C120_FA <- Dt_C120In / Dt_FAIn * 100
Dt_C140_FA <- Dt_C140In / Dt_FAIn * 100
Dt_C160_FA <- Dt_C160In / Dt_FAIn * 100
Dt_C161_FA <- Dt_C161In / Dt_FAIn * 100
Dt_C180_FA <- Dt_C180In / Dt_FAIn * 100
Dt_C181t_FA <- Dt_C181tIn / Dt_FAIn * 100
Dt_C181c_FA <- Dt_C181cIn / Dt_FAIn * 100
Dt_C182_FA <- Dt_C182In / Dt_FAIn * 100
Dt_C183_FA <- Dt_C183In / Dt_FAIn * 100
Dt_OtherFA_FA <- Dt_OtherFAIn / Dt_FAIn * 100
Dt_UFA_FA <- Dt_UFAIn / Dt_FAIn * 100
Dt_MUFA_FA <- Dt_MUFAIn / Dt_FAIn * 100
Dt_PUFA_FA <- Dt_PUFAIn / Dt_FAIn * 100
Dt_SatFA_FA <- Dt_SatFAIn / Dt_FAIn * 100

#==============================================================#
#Macro Mineral Intakes from each ingredient, g/d;
f$Fd_CaIn = f$Fd_DMIn*f$Fd_Ca/100 * 1000
f$Fd_PIn = f$Fd_DMIn*f$Fd_P/100 * 1000
f$Fd_PinorgIn = f$Fd_PIn*f$Fd_Pinorg_P/100; #??Check Bill's text
f$Fd_PorgIn = f$Fd_PIn*f$Fd_Porg_P/100      #f$Fd_PphytIn = f$Fd_PIn*f$Fd_Pphyt_P/100 #Depracated by Bill.  Reduced to inorganic and organic.
f$Fd_NaIn = f$Fd_DMIn*f$Fd_Na/100 * 1000
f$Fd_MgIn = f$Fd_DMIn*f$Fd_Mg/100 * 1000
f$Fd_MgIn_min = ifelse(f$Fd_Category=="Vitamin/Mineral",f$Fd_DMIn*f$Fd_Mg/100*1000,0)  #Mg from vitamins and minerals only.
f$Fd_KIn = f$Fd_DMIn*f$Fd_K/100 * 1000
f$Fd_ClIn = f$Fd_DMIn*f$Fd_Cl/100 * 1000
f$Fd_SIn = f$Fd_DMIn*f$Fd_S/100 * 1000

#Micro Mineral Intakes from each ingredient, mg/d;
f$Fd_CoIn = f$Fd_DMIn*f$Fd_Co
f$Fd_CrIn = f$Fd_DMIn*f$Fd_Cr
f$Fd_CuIn = f$Fd_DMIn*f$Fd_Cu
f$Fd_FeIn = f$Fd_DMIn*f$Fd_Fe
f$Fd_IIn = f$Fd_DMIn*f$Fd_I
f$Fd_MnIn = f$Fd_DMIn*f$Fd_Mn
f$Fd_MoIn = f$Fd_DMIn*f$Fd_Mo
f$Fd_SeIn = f$Fd_DMIn*f$Fd_Se
f$Fd_ZnIn = f$Fd_DMIn*f$Fd_Zn

#Vitamin Intakes, IU/d;
f$Fd_VitAIn = f$Fd_DMIn*f$Fd_VitA
f$Fd_VitDIn = f$Fd_DMIn*f$Fd_VitD
f$Fd_VitEIn = f$Fd_DMIn*f$Fd_VitE
#Vitamin Intakes, mg/d;
f$Fd_CholineIn = f$Fd_DMIn*f$Fd_Choline
f$Fd_BiotinIn = f$Fd_DMIn*f$Fd_Biotin
f$Fd_NiacinIn = f$Fd_DMIn*f$Fd_Niacin
f$Fd_B_CaroteneIn = f$Fd_DMIn*f$Fd_B_Carotene

#Total Dietary Macro Mineral Intakes, g/d
Dt_CaIn <- sum(f$Fd_CaIn, na.rm=TRUE)
Dt_PIn <- sum(f$Fd_PIn, na.rm=TRUE)
Dt_PinorgIn <- sum(f$Fd_PinorgIn, na.rm=TRUE)
Dt_PorgIn <- sum(f$Fd_PorgIn, na.rm=TRUE)   #Dt_PphytIn <- sum(f$Fd_PphytIn, na.rm=TRUE)  #PphytIn depracatated
Dt_NaIn <- sum(f$Fd_NaIn, na.rm=TRUE)
Dt_MgIn <- sum(f$Fd_MgIn, na.rm=TRUE)
Dt_MgIn_min <- sum(f$Fd_MgIn_min, na.rm=TRUE)
Dt_KIn <- sum(f$Fd_KIn, na.rm=TRUE)
Dt_ClIn <- sum(f$Fd_ClIn, na.rm=TRUE)
Dt_SIn <- sum(f$Fd_SIn, na.rm=TRUE)

#Total Dietary Micro Mineral Intakes, mg/d
Dt_CoIn <- sum(f$Fd_CoIn, na.rm=TRUE)
Dt_CrIn <- sum(f$Fd_CrIn, na.rm=TRUE)
Dt_CuIn <- sum(f$Fd_CuIn, na.rm=TRUE)
Dt_FeIn <- sum(f$Fd_FeIn, na.rm=TRUE)
Dt_IIn <- sum(f$Fd_IIn, na.rm=TRUE)
Dt_MnIn <- sum(f$Fd_MnIn, na.rm=TRUE)
Dt_MoIn <- sum(f$Fd_MoIn, na.rm=TRUE)
Dt_SeIn <- sum(f$Fd_SeIn, na.rm=TRUE)
Dt_ZnIn <- sum(f$Fd_ZnIn, na.rm=TRUE)

#Total Dietary Vitamin Intakes
Dt_VitAIn <- sum(f$Fd_VitAIn, na.rm=TRUE);	#IU/d
Dt_VitDIn <- sum(f$Fd_VitDIn, na.rm=TRUE )
Dt_VitEIn <- sum(f$Fd_VitEIn, na.rm=TRUE)
Dt_CholineIn <- sum(f$Fd_CholineIn, na.rm=TRUE);	#mg/d
Dt_BiotinIn <- sum(f$Fd_BiotinIn, na.rm=TRUE)
Dt_NiacinIn <- sum(f$Fd_NiacinIn, na.rm=TRUE)
Dt_B_CaroteneIn <- sum(f$Fd_B_CaroteneIn, na.rm=TRUE)

#Calculate dietary Min/Vit concentrations
#Macro Minerals, % of DM
Dt_Ca <- Dt_CaIn / Dt_DMIn /1000 * 100
Dt_P <- Dt_PIn / Dt_DMIn /1000 * 100
Dt_Pinorg <- Dt_PinorgIn / Dt_DMIn /1000 * 100
Dt_Porg <- Dt_PorgIn / Dt_DMIn /1000 * 100
#Dt_Pphyt <- Dt_PphytIn / Dt_DMIn /1000 * 100
Dt_Na <- Dt_NaIn / Dt_DMIn /1000 * 100
Dt_Mg <- Dt_MgIn / Dt_DMIn /1000 * 100
Dt_K <- Dt_KIn / Dt_DMIn /1000 * 100
Dt_Cl <- Dt_ClIn / Dt_DMIn /1000 * 100
Dt_S <- Dt_SIn / Dt_DMIn /1000 * 100

#Total Dietary Micro Mineral Intakes, mg/kg
Dt_Co <- Dt_CoIn / Dt_DMIn
Dt_Cr <- Dt_CrIn / Dt_DMIn
Dt_Cu <- Dt_CuIn / Dt_DMIn
Dt_Fe <- Dt_FeIn / Dt_DMIn
Dt_I <- Dt_IIn / Dt_DMIn
Dt_Mn <- Dt_MnIn / Dt_DMIn
Dt_Mo <- Dt_MoIn / Dt_DMIn
Dt_Se <- Dt_SeIn / Dt_DMIn
Dt_Zn <- Dt_ZnIn / Dt_DMIn

#Total Dietary Vitamin Intakes, IU/kg
Dt_VitA <- Dt_VitAIn / Dt_DMIn
Dt_VitD <- Dt_VitDIn / Dt_DMIn
Dt_VitE <- Dt_VitEIn / Dt_DMIn
#mg/kg
Dt_Choline <- Dt_CholineIn / Dt_DMIn
Dt_Biotin <- Dt_BiotinIn / Dt_DMIn
Dt_Niacin <- Dt_NiacinIn / Dt_DMIn
Dt_B_Carotene <- Dt_B_CaroteneIn / Dt_DMIn

#===================Infused nutrient Calculations.  MDH, 9-29-17 ======================
#Used for simulations of infusions in research trials.  All infusions are specified as g/d, except for
#the nutrient subfractions, i.e. CPARum_CP which are % of the parent as for the feed library.
#The infusion site is used to direct the entire infusion to that site. Multi-site infusions are not
#explicitely supported unless the infusion amount at each site is the same which can be specified with 1 at each site.
#Spelling and case for infusion sites must match those coded in the model. Additional infused nutrients can be added to the model code.
#An IFN should be added to allow matching of ingredient composition from the feed table with infused ingredients.  
#This would allow a cleaner definition of the infusions and a more complete infusate profile to be developed 
#for ingredients other than pure nutrients, MDH.

#Convert infusion units to the units used in the model for each nutrient.
Inf_DMIn <- i$Inf_DM_g/1000
Inf_StIn <- i$Inf_St_g/1000
Inf_NDFIn <- i$Inf_NDF_g/1000
Inf_ADFIn <- i$Inf_ADF_g/1000
Inf_GlcIn <- i$Inf_Glc_g/1000
Inf_CPIn <- i$Inf_CP_g/1000
Inf_CPAIn <- i$Inf_CP_g/1000 * i$Inf_CPARum_CP/100
Inf_CPBIn <- i$Inf_CP_g/1000 * i$Inf_CPBRum_CP/100
Inf_CPCIn <- i$Inf_CP_g/1000 * i$Inf_CPCRum_CP/100
Inf_NPNCPIn <- i$Inf_NPNCP_g/1000 #Inf_NPNCP_g is expressed as g CP/d and should only be urea and Amm
Inf_TPIn <- Inf_CPIn - Inf_NPNCPIn
Inf_KdCPB <- i$Inf_KdCPB
Inf_dcRUP <- i$Inf_dcRUP
Inf_FAIn <- i$Inf_FA_g/1000
Inf_AshIn <- i$Inf_Ash_g/1000
Inf_OMIn <- Inf_DMIn - Inf_AshIn
Inf_VFAIn <- i$Inf_VFA_g/1000
Inf_AcetIn <- i$Inf_Acet_g/1000
Inf_PropIn <- i$Inf_Prop_g/1000
Inf_ButrIn <- i$Inf_Butr_g/1000

#Calculate infused nutrients as a % of total DM intake including infusions
Inf_DM <- Inf_DMIn/(Dt_DMIn+Inf_DMIn)*100
Inf_OM <- Inf_OMIn/(Dt_DMIn+Inf_DMIn)*100
Inf_St <- Inf_StIn/(Dt_DMIn+Inf_DMIn)*100
Inf_NDF <- Inf_NDFIn/(Dt_DMIn+Inf_DMIn)*100
Inf_ADF <- Inf_ADFIn/(Dt_DMIn+Inf_DMIn)*100
Inf_Glc <- Inf_GlcIn/(Dt_DMIn+Inf_DMIn)*100
Inf_CP <- Inf_CPIn/(Dt_DMIn+Inf_DMIn)*100
Inf_FA <- Inf_FAIn/(Dt_DMIn+Inf_DMIn)*100
Inf_VFA <- Inf_VFAIn/(Dt_DMIn+Inf_DMIn)*100
Inf_Acet <- Inf_AcetIn/(Dt_DMIn+Inf_DMIn)*100
Inf_Prop <- Inf_PropIn/(Dt_DMIn+Inf_DMIn)*100
Inf_Butr <- Inf_ButrIn/(Dt_DMIn+Inf_DMIn)*100

#Generate an infusion site ID matrix
i$Inf_Rum <- ifelse(i$Inf_Location == "Rumen", 1, 0)
i$Inf_SI <- ifelse(i$Inf_Location == "Abomasum" | i$Inf_Location == "Duodenum" | i$Inf_Location == "Duodenal", 1, 0)
i$Inf_Art <- ifelse(i$Inf_Location == "Jugular" | i$Inf_Location == "Arterial" | 
                       i$Inf_Location == "Iliac Artery" | i$Inf_Location == "Blood", 1, 0)

#Ruminally Infused nutrients, kg/d
InfRum_DMIn <- i$Inf_Rum*Inf_DMIn
InfRum_OMIn <- i$Inf_Rum*Inf_OMIn
InfRum_CPIn <- i$Inf_Rum*Inf_CPIn
InfRum_NPNCPIn <- i$Inf_Rum*Inf_NPNCPIn
InfRum_TPIn <- InfRum_CPIn - InfRum_NPNCPIn
InfRum_CPAIn <- i$Inf_Rum*Inf_CPAIn
InfRum_CPBIn <- i$Inf_Rum*Inf_CPBIn
InfRum_CPCIn <- i$Inf_Rum*Inf_CPCIn
InfRum_StIn <- i$Inf_Rum*Inf_StIn
InfRum_NDFIn <- i$Inf_Rum*Inf_NDFIn
InfRum_ADFIn <- i$Inf_Rum*Inf_ADFIn
InfRum_FAIn <- i$Inf_Rum*Inf_FAIn
InfRum_GlcIn <- i$Inf_Rum*Inf_GlcIn
InfRum_VFAIn <- i$Inf_Rum*Inf_VFAIn
InfRum_AcetIn <- i$Inf_Rum*Inf_AcetIn
InfRum_PropIn <- i$Inf_Rum*Inf_PropIn
InfRum_ButrIn <- i$Inf_Rum*Inf_ButrIn
InfRum_AshIn <- i$Inf_Rum*Inf_AshIn

#Intestinally infused nutrients, kg/d
InfSI_DMIn <- i$Inf_SI*Inf_DMIn
InfSI_OMIn <- i$Inf_SI*Inf_OMIn
InfSI_CPIn <- i$Inf_SI*Inf_CPIn
InfSI_NPNCPIn <- i$Inf_SI*Inf_NPNCPIn
InfSI_TPIn <- InfSI_CPIn - InfSI_NPNCPIn
InfSI_StIn <- i$Inf_SI*Inf_StIn
InfSI_GlcIn <- i$Inf_SI*Inf_GlcIn
InfSI_NDFIn <- i$Inf_SI*Inf_NDFIn
InfSI_ADFIn <- i$Inf_SI*Inf_ADFIn
InfSI_FAIn <- i$Inf_SI*Inf_FAIn
InfSI_VFAIn <- i$Inf_SI*Inf_VFAIn
InfSI_AcetIn <- i$Inf_SI*Inf_AcetIn
InfSI_PropIn <- i$Inf_SI*Inf_PropIn
InfSI_ButrIn <- i$Inf_SI*Inf_ButrIn
InfSI_AshIn <- i$Inf_SI*Inf_AshIn

#Systemically infused nutrients, kg/d
InfArt_DMIn <- i$Inf_Art*Inf_DMIn
InfArt_OMIn <- i$Inf_Art*Inf_OMIn
InfArt_CPIn <- i$Inf_Art*Inf_CPIn
InfArt_NPNCPIn <- i$Inf_Art*Inf_NPNCPIn
InfArt_TPIn <- i$Inf_Art*Inf_TPIn  #better by difference, but not sure of how it will behave.
InfArt_StIn <- i$Inf_Art*Inf_StIn
InfArt_GlcIn <- i$Inf_Art*Inf_GlcIn
InfArt_NDFIn <- i$Inf_Art*Inf_NDFIn
InfArt_ADFIn <- i$Inf_Art*Inf_ADFIn
InfArt_FAIn <- i$Inf_Art*Inf_FAIn
InfArt_VFAIn <- i$Inf_Art*Inf_VFAIn
InfArt_AcetIn <- i$Inf_Art*Inf_AcetIn
InfArt_PropIn <- i$Inf_Art*Inf_PropIn
InfArt_ButrIn <- i$Inf_Art*Inf_ButrIn
InfArt_AshIn <- i$Inf_Art*Inf_AshIn

#======= Total Nutrient Intakes including intestinal Infusions but excluding systemic infusions =====
An_DMIn <- Dt_DMIn + Inf_DMIn
An_DMIn_BW <- An_DMIn / An_BW
An_DMIn_MBW <- An_DMIn / An_MBW
An_StIn <- Dt_StIn + InfRum_StIn+InfSI_StIn
An_St <- An_StIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100
An_rOMIn <- Dt_rOMIn + InfRum_GlcIn + InfRum_AcetIn + InfRum_PropIn +
	InfRum_ButrIn + InfSI_AcetIn + InfSI_PropIn + InfSI_ButrIn
An_rOM <- An_rOMIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100
An_NDFIn <- (Dt_NDFIn+InfRum_NDFIn+InfSI_NDFIn)
An_NDFIn_BW <- An_NDFIn / An_BW * 100
An_NDF <- An_NDFIn / (Dt_DMIn+InfRum_DMIn+InfSI_DMIn)*100
An_ADFIn <- (Dt_ADFIn+InfRum_ADFIn+InfSI_ADFIn)
An_ADF <- An_ADFIn / (Dt_DMIn+InfRum_DMIn+InfSI_DMIn)*100
An_CPIn <- Dt_CPIn + Inf_CPIn
An_CPIn_g <- An_CPIn * 1000
An_CP <- An_CPIn / (Dt_DMIn+InfRum_DMIn+InfSI_DMIn) * 100
An_NIn_g <- An_CPIn * 0.16 * 1000
An_NPNCPIn <- Dt_NPNCPIn + Inf_NPNCPIn
An_TPIn <- Dt_TPIn + Inf_TPIn
An_FAIn <- Dt_FAIn + Inf_FAIn
An_FAhydrIn <- Dt_FAhydrIn + Inf_FAIn  #need to specify FA vs TAG in the infusion matrix to account for differences there. MDH
An_FA <- An_FAIn / (Dt_DMIn+InfRum_DMIn+InfSI_DMIn) * 100
An_AshIn <- (Dt_AshIn+InfRum_AshIn+InfSI_AshIn)
An_Ash <- An_AshIn / (Dt_DMIn+InfRum_DMIn+InfSI_DMIn)*100

######################### Predict voluntary water intake, kg/d ######################### 
#From Appuhamy et al., 2016.  Requires physiological state and mean daily ambient temp.
#Based on Diet DMI.  Should perhaps add infusions, but no minerals or DM specified for infusions?
#Lactating Cows
An_WaIn_Lact <- -91.1 + 2.93*Dt_DMIn + 0.61*Dt_DM + 0.062*(Dt_Na/0.023 + Dt_K/0.039)*10 +  #Low DMI, CP, and Na results in too low of WaIn of 10 kg/d.  
                  2.49*Dt_CP + 0.76*Env_TempCurr                                           #Consider trapping values below 22 which is the min from observed data. MDH from RM.
An_WaIn_Dry <- 1.16*Dt_DMIn + 0.23*Dt_DM + 0.44*Env_TempCurr + 0.061*(Env_TempCurr-16.4)^2
An_WaIn <- ifelse(An_StatePhys == "Lactating Cow", An_WaIn_Lact, An_WaIn_Dry)
An_WaIn <- ifelse(An_StatePhys == "Heifer", An_WaIn_Dry, An_WaIn)
An_WaIn <- ifelse(An_StatePhys=="Calf"|An_StatePhys == "Other", NA, An_WaIn)  #the above does not apply to calves/other, thus set to NA

#############################################################################################################
#                                Digested Nutrients
#############################################################################################################
#### Rumen Degraded NDF and Starch ####
#White et al (2016) rdNDF equation
Rum_dcNDF <- -31.9 + 0.721*(Dt_NDFIn+InfRum_NDFIn)/(Dt_DMIn+InfRum_DMIn)*100 - 
		0.247*(Dt_StIn + InfRum_StIn)/(Dt_DMIn+InfRum_DMIn)*100 + 
		6.63*(Dt_CPIn+InfRum_CPIn)/(Dt_DMIn+InfRum_DMIn)*100 - 
		0.211*((Dt_CPIn+InfRum_CPIn)/(Dt_DMIn+InfRum_DMIn)*100)^2 - 
		0.387*(Dt_ADFIn+InfRum_ADFIn)/(Dt_DMIn+InfRum_DMIn)/
                    ((Dt_NDFIn+InfRum_NDFIn)/(Dt_DMIn+InfRum_DMIn))*100 - 
		0.121*Dt_ForWet + 1.51*(Dt_DMIn+InfRum_DMIn)
		#% of NDF.  ADF/NDF needs to be multiplied by 100.  Not noted in manuscript. MDH.
Rum_dcNDF <- ifelse(Rum_dcNDF < 0.1 | is.na(Rum_dcNDF), 0.1, Rum_dcNDF)
Rum_dcNDF <- ifelse(is.na(Rum_dcNDF), 37.6, Rum_dcNDF)  #There should not be any missing values, but if so, use the mean.

#Roman Garcia et al (2016) rdSt equation
Rum_dcSt <- 70.6 - 1.45*(Dt_DMIn+InfRum_DMIn) + 0.424*Dt_ForNDF +     #This results in a few diets with predicted Fe_St output that exceed Du_StPas.  
	1.39*(Dt_StIn + InfRum_StIn)/(Dt_DMIn+InfRum_DMIn)*100 -         #TT predictions should be by summation from Rum and Intest St Digestion, and this
	0.0219*((Dt_StIn + InfRum_StIn)/(Dt_DMIn+InfRum_DMIn)*100)^2 -   #Ruminal eqn should be rechecked as it was derived before extensive data cleaning
	0.154*Dt_ForWet                                                  #including correction of many diets with no forage entered. MDH and RM
Rum_dcSt <- ifelse(Rum_dcSt < 0.1, 0.1, Rum_dcSt)                    #If Rum_dcSt is altered, all downstream elements (MiN, etc.) must be rechecked!!
Rum_dcSt <- ifelse(Rum_dcSt > 100, 100, Rum_dcSt)
Rum_dcSt <- ifelse(is.na(Rum_dcSt), 65.6, Rum_dcSt)  #There should not be any missing values, but if so, use the mean.

Rum_DigNDFIn <- Rum_dcNDF/100*(Dt_NDFIn + InfRum_NDFIn)
Rum_DigNDFnfIn <- Rum_dcNDF/100*Dt_NDFnfIn  #Not used.  IF used, should consider infusions
Rum_DigStIn <- Rum_dcSt/100*(Dt_StIn+InfRum_StIn)

Du_StPas <- Dt_StIn+InfRum_StIn-Rum_DigStIn
Du_StPas <- ifelse(Du_StPas < 0, 0, Du_StPas)  #All grass diets predicted to be very slightly negative
Du_NDFPas <- Dt_NDFIn + Inf_NDFIn - Rum_DigNDFIn

#### Total Tract Starch and rOM digestibility, From Tebbe et al., 2017 ####
Fe_rOMend_DMI <- 3.43  #3.43% of DMI
f$Fd_dcrOM <- 96				#this is a true digestbility.  There is a neg intercept of -3.43% of DM
Fe_rOMend <- Fe_rOMend_DMI/100 * Dt_DMIn;	#From Tebbe et al., 2017.  Negative interecept represents endogenous rOM
f$Fd_DigrOMt <- f$Fd_dcrOM/100*f$Fd_rOM                #Truly digested rOM in each feed, % of DM
f$Fd_DigrOMa <- f$Fd_DigrOMt - Fe_rOMend_DMI   #Apparently digested (% DM). Generates some negative values for minerals and other low rOM feeds.
f$Fd_DigrOMaIn <- f$Fd_DigrOMa/100 * f$Fd_DMIn		#kg/d
f$Fd_DigrOMtIn <- f$Fd_DigrOMt/100 * f$Fd_DMIn		#kg/d
f$Fd_DigWSC <- f$Fd_WSC				               #100% digestible
f$Fd_DigWSCIn <- f$Fd_DigWSC/100 * f$Fd_DMIn

f$Fd_DigSt <- f$Fd_St * f$Fd_dcSt/100
f$Fd_DigStIn_Base <- f$Fd_DigSt/100 * f$Fd_DMIn
Dt_DigStIn_Base <- sum(f$Fd_DigStIn_Base, na.rm=TRUE)
An_DigStIn_Base <- Dt_DigStIn_Base + Inf_StIn*i$Inf_ttdcSt/100	#Glc considered as WSC and thus with rOM

Dt_DigWSCIn <- sum(f$Fd_DigWSCIn, na.rm=TRUE)	#This is not used as it isn't additive with St, MDH.
Dt_DigrOMtIn <- sum(f$Fd_DigrOMtIn, na.rm=TRUE)
Dt_DigrOMaIn <- Dt_DigrOMtIn - Fe_rOMend
An_DigWSCIn <- Dt_DigWSCIn+InfRum_GlcIn+InfSI_GlcIn
An_DigrOMaIn <- Dt_DigrOMaIn+InfRum_GlcIn+InfRum_AcetIn+InfRum_PropIn+
	InfRum_ButrIn+InfSI_GlcIn+InfSI_AcetIn+InfSI_PropIn+InfSI_ButrIn
An_DigrOMtIn <- Dt_DigrOMtIn+InfRum_GlcIn+InfRum_AcetIn+InfRum_PropIn+
     InfRum_ButrIn+InfSI_GlcIn+InfSI_AcetIn+InfSI_PropIn+InfSI_ButrIn
#Possibly missing a small amount of rOM when ingredients are infused. Should infusions also drive endogenous rOM??

TT_dcSt_Base <- Dt_DigStIn_Base / Dt_StIn * 100
TT_dcSt_Base <- ifelse(is.na(TT_dcSt_Base),0, TT_dcSt_Base) 
TT_dcSt <- ifelse(TT_dcSt_Base == 0, 0, TT_dcSt_Base - (1.0 * (An_DMIn_BW - 0.035))*100)	#Adjust for DMI depression.
Dt_DigStIn <- Dt_StIn * TT_dcSt/100					#Digested Starch at Intake
An_DigStIn <- Dt_DigStIn + Inf_StIn*i$Inf_ttdcSt/100		#Glc considered as WSC and thus with rOM
TT_dcAnSt <- An_DigStIn / (Dt_StIn + Inf_StIn) * 100
TT_dcAnSt <- ifelse(is.na(TT_dcAnSt),0, TT_dcAnSt)
Dt_DigSt <- Dt_DigStIn / Dt_DMIn *100
An_DigSt <- An_DigStIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100
Dt_DigWSC <- Dt_DigWSCIn / Dt_DMIn * 100
An_DigWSC <- An_DigWSCIn / (Dt_DMIn+InfRum_DMIn+InfSI_DMIn) * 100
Dt_DigrOMa <- Dt_DigrOMaIn / Dt_DMIn * 100
Dt_DigrOMa.Dt <- Dt_rOM * 0.96 - Fe_rOMend_DMI;	#Crosscheck the feed level calculation and summation.
Dt_DigrOMt <- Dt_DigrOMtIn / Dt_DMIn * 100
An_DigrOMa <- An_DigrOMaIn / (Dt_DMIn+InfRum_DMIn+InfSI_DMIn) * 100
An_DigrOMt <- An_DigrOMtIn / (Dt_DMIn+InfRum_DMIn+InfSI_DMIn) * 100
Fe_rOM <- An_rOMIn - An_DigrOMaIn  #includes undigested rOM and fecal endogenous rOM
#Apparent and true TT digestibilty of rOM
TT_dcrOMa <- An_DigrOMaIn / (Dt_rOMIn+InfRum_GlcIn+InfRum_AcetIn+InfRum_PropIn+
               	InfRum_ButrIn+InfSI_GlcIn+InfSI_AcetIn+InfSI_PropIn+InfSI_ButrIn) * 100
TT_dcrOMt <- An_DigrOMtIn / (Dt_rOMIn+InfRum_GlcIn+InfRum_AcetIn+InfRum_PropIn+
                    InfRum_ButrIn+InfSI_GlcIn+InfSI_AcetIn+InfSI_PropIn+InfSI_ButrIn) * 100

Fe_St <- Dt_StIn + Inf_StIn - An_DigStIn
#### Total Tract Digested NDF ####
#Base digestible NDF 
TT_dcNDF_Base <- Dt_DigNDFIn_Base/Dt_NDFIn * 100
TT_dcNDF_Base <- ifelse(is.na(TT_dcNDF_Base),0, TT_dcNDF_Base) 
An_DigNDFIn_Base <- (Dt_NDFIn + InfRum_NDFIn) * TT_dcNDF_Base/100
#At Production Digested NDF, Vandehaar/Weiss equation
TT_dcNDF <- ifelse(TT_dcNDF_Base == 0, 0, 
                   (TT_dcNDF_Base/100 - 0.59*((Dt_StIn+InfRum_StIn+InfSI_StIn)/(Dt_DMIn+InfRum_DMIn+InfSI_DMIn)-0.26) - 
                              1.1*(An_DMIn_BW - 0.035))*100)
Dt_DigNDFIn <- TT_dcNDF/100 * Dt_NDFIn
An_DigNDFIn <- Dt_DigNDFIn + InfRum_NDFIn * TT_dcNDF/100  #should consider SI and LI infusions as well, but no predictions of LI NDF digestion available.
Dt_DigNDFnfIn <- TT_dcNDF/100 * Dt_NDFnfIn
Dt_DigNDF <- Dt_DigNDFIn / Dt_DMIn * 100
An_DigNDF <- An_DigNDFIn / (Dt_DMIn+InfRum_DMIn+InfSI_DMIn) * 100  #should add LI infusions
Dt_DigNDFnf <- Dt_DigNDFnfIn / Dt_DMIn * 100
Fe_NDF <- Dt_NDFIn - Dt_DigNDFIn
Fe_NDFnf <- Dt_NDFnfIn - Dt_DigNDFnfIn

#### Calculate digested RUP, kg/d ####
f$Fd_idRUPIn <- (f$Fd_dcRUP/100)*f$Fd_RUPIn  #dcRUP is the RUP DC by feed read in from the Feed Matrix.
f$Fd_idRUP <- ifelse(f$Fd_CPIn > 0, f$Fd_idRUPIn/f$Fd_DMIn*100, 0)
Dt_idRUPIn <- sum(f$Fd_idRUPIn, na.rm=TRUE)
Dt_idcRUP <- Dt_idRUPIn / Dt_RUPIn * 100  #Intestinal digestibility of RUP

#### Estimate fecal RUP output from feeds, kg/d
f$Fd_Fe_RUPout <- f$Fd_RUPIn*(1-f$Fd_dcRUP/100)


Dt_Fe_RUPout  <- sum(f$Fd_Fe_RUPout, na.rm=TRUE)

#RUP does not include CP infused into the SI
InfRum_RUPIn <- (InfRum_CPAIn-InfRum_NPNCPIn)*fCPAdu + InfRum_CPBIn * 
		KpConc/(Inf_KdCPB+KpConc) + InfRum_CPCIn
	#In general, CPB for infused proteins, which are generally soluble, has been set to 0.  
	#Abo/Duod infusions only considered at absorption.
InfRum_RUP_CP <- ifelse(InfRum_CPIn == 0, 0, InfRum_RUPIn / InfRum_CPIn * 100)
InfRum_idRUPIn <- InfRum_RUPIn * Inf_dcRUP/100;  #RUP
InfSI_idTPIn <- InfSI_TPIn * Inf_dcRUP/100;  #intestinally infused
dcNPNCP <- 100	       #urea and ammonium salt digestibility
InfSI_idCPIn <- InfSI_idTPIn + InfSI_NPNCPIn*dcNPNCP/100;  #SI infused idTP + urea or ammonia
Inf_idCPIn <- InfRum_idRUPIn + InfSI_idCPIn;  #RUP + intestinally infused
An_RDNPNCPIn <- Dt_NPNCPIn + InfRum_NPNCPIn
An_RUPIn <- Dt_RUPIn + InfRum_RUPIn  #SI infusions not considered
An_RUP <- An_RUPIn / (Dt_DMIn + InfRum_DMIn) * 100
An_RUP_CP <- An_RUPIn / (Dt_CPIn + InfRum_CPIn) * 100
An_idRUPIn <- Dt_idRUPIn + InfRum_idRUPIn + InfSI_idTPIn  #SI infusions considered here
An_idRUCPIn <- Dt_idRUPIn + InfRum_idRUPIn + InfSI_idCPIn;	#RUP + infused idCP
An_idRUP <- An_idRUPIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn)
Dt_RDPIn <- Dt_CPIn - Dt_RUPIn
Dt_RDTPIn <- Dt_RDPIn - (Dt_NPNCPIn * dcNPNCP/100)  #assumes all NPN is soluble.  Reflects only urea and ammonium salt NPN sources.
Dt_RDP <- Dt_RDPIn / Dt_DMIn *100
Dt_RDP_CP <- Dt_RDP / Dt_CP * 100
InfRum_RDPIn <- InfRum_CPIn - InfRum_RUPIn
An_RDPIn <- Dt_RDPIn + InfRum_RDPIn
An_RDTPIn <- Dt_RDTPIn + (InfRum_RDPIn - InfRum_NPNCPIn*dcNPNCP/100)
An_RDP <- An_RDPIn / (Dt_DMIn + InfRum_DMIn) *100
An_RDP_CP <- An_RDPIn / (Dt_CPIn + InfRum_CPIn) * 100
An_RDPIn_g <- An_RDPIn * 1000
######################################################################################
#                               Microbial N Growth                                   #
######################################################################################
#Parms from a Bayesian refit by Luis Moraes on Mar. 24, 2018, g N/d
#18% of the studies were from omasal sampling with a derived offset of 122 g/d
VmMiNInt <- 100.8
VmMiNRDPSlp <- 81.56
KmMiNRDNDF <- 0.0939
KmMiNRDSt <- 0.0274
fMiTP_MiCP <- 0.824;			#Fraction of MiCP that is True Protein; from Lapierre or Firkins
fIlEndTP_CP <- 0.73			#Fraction of EndCP that is True Protein, from Lapierre
SI_dcMiCP <- 80;				#Digestibility coefficient for Microbial Protein (%) from NRC 2001
RDPIn_MiNmax <- ifelse(An_RDP <= 12, An_RDPIn, (Dt_DMIn + InfRum_DMIn)*0.12)  #Capped at 12% of DM. From Firkins.
MiN_Vm <- VmMiNInt + VmMiNRDPSlp*RDPIn_MiNmax; #Vmax, g microbial N/d
Du_MiN_NRC2021_g <- MiN_Vm/(1 + KmMiNRDNDF/Rum_DigNDFIn + KmMiNRDSt/Rum_DigStIn); #g/d, NRC 2021 eqn.
#The above doesn't scale well to low DMI for heifers and dry cows.  Thus maximum RDP efficiency was capped at 100%.
#Isotope data suggest a cap of 114.6% (see Ch. 8), but even that is too high for low DMI as it allows neg Rum N balance at 
#17% CP diets for heifers.  Thus it was capped at 100% RDP efficiency to address heifer dry cow problems.  Need more work to scale Vm for DMI/BW, MDH
Du_MiN_NRC2021_g <- ifelse(Du_MiN_NRC2021_g > 1.0 * An_RDPIn_g/6.25,  1.0 * An_RDPIn_g/6.25, Du_MiN_NRC2021_g)

#MiN (g/d) Parms for eqn. 52 (linear) from Hanigan et al, RUP paper
#Derived using RUP with no KdAdjust
Int_MiN_VT <- 18.686  #Rederived estimates Aug 13, 2020, MDH
KrdSt_MiN_VT <- 10.214
KrdNDF_MiN_VT <- 28.976
KRDP_MiN_VT <- 43.405
KrOM_MiN_VT <- -11.731
KForNDF_MiN_VT <- 8.895
KrOM2_MiN_VT <- 2.861
KrdStxrOM_MiN_VT <- 5.637
KrdNDFxForNDF_MiN_VT <- -2.22

Du_MiN_VTln_g <- Int_MiN_VT + KrdSt_MiN_VT*Rum_DigStIn + KrdNDF_MiN_VT*Rum_DigNDFIn + 
     KRDP_MiN_VT*An_RDPIn + KrOM_MiN_VT*Dt_rOMIn + KForNDF_MiN_VT*Dt_ForNDFIn + KrOM2_MiN_VT *
     Dt_rOMIn^2 + KrdStxrOM_MiN_VT*Rum_DigStIn*Dt_rOMIn + KrdNDFxForNDF_MiN_VT*Rum_DigNDFIn*Dt_ForNDFIn
Du_MiN_VTnln_g <- 7.47 + 0.574*An_RDPIn*1000 / (1+ 3.60/Rum_DigNDFIn + 12.3/Rum_DigStIn)  #from White et al., 2017

###### Select the desired microbial N prediction for use in AA supply equations #######
#Should move the switch assignment to outside of the model to allow external control
#1=NRC 2021 (Moraes) nlin eqn, 2=Hanigan 2021 linear eqn, 3=White 2017 nonlin eqn
                  #The NRC2001 prediction can't be calculated here as it requires TDN which requires TT digCP 
                  #which relies on MiCP.  It is provided below for N flow comparisons only.
MiN_eqn <- ifelse(MiN_eqn < 1 | MiN_eqn > 3, 1, MiN_eqn) #Trap bad values and use default NRC eqn.
Du_MiN_g <- switch(MiN_eqn,
                  Du_MiN_NRC2021_g, #1, NRC 2021 
                  Du_MiN_VTln_g,  #2, Hanigan, 2021
                  Du_MiN_VTnln_g  #3, White, 2017
            )

############################################################################################
#         Ruminal N outflow, Ileal N Flow, Fecal N Flow, and Intestinal N Digestion        #
############################################################################################
Du_MiCP_g <- Du_MiN_g * 6.25
Du_MiCP_g <- ifelse(Du_MiCP_g<10, 10, Du_MiCP_g)	#Truncate to 10 to prevent negative values
Du_MiCP <- Du_MiCP_g / 1000
Du_MiTP_g <- fMiTP_MiCP*Du_MiCP_g;	#Convert MiCP to MiTP, g/day
Du_MiTP <- Du_MiTP_g / 1000
An_RDPbal_g <- An_RDPIn_g - Du_MiCP_g
#Duodenal endogenous flow of CP, g/d
Du_EndCP_g <- 96.1 + 7.54 * (Dt_DMIn+InfRum_DMIn)
Du_EndN_g <- 15.4 + 1.21 * (Dt_DMIn+InfRum_DMIn);	#g/d, recalc of the above eqn at 16% N in CP.
Du_EndCP <- Du_EndCP_g / 1000
Du_EndN <- Du_EndN_g / 1000

Du_NAN_g <- Du_MiN_g +  An_RUPIn*0.16*1000 + Du_EndN_g
Du_NANMN_g <- An_RUPIn*0.16*1000 + Du_EndN_g

#### Intestinally Digested Microbial Protein
#idRUP calculated at the ingredient level above
Du_idMiCP_g <- SI_dcMiCP/100 * Du_MiCP_g
Du_idMiCP <- Du_idMiCP_g/1000
Du_idMiTP_g <- fMiTP_MiCP * Du_idMiCP_g
Du_idMiTP <- Du_idMiTP_g / 1000

#Fecal N Flow;     Fecal Outputs should be renamed Fe_xxxOut to avoid confusion with conc, MDH
Fe_CPend_g <- (12 + 0.12*An_NDF) * (Dt_DMIn+InfRum_DMIn+InfSI_DMIn)  #g/d, endogen secretions plus urea capture in microbies in rumen and LI
K_FeCPend_ClfLiq <- ifelse(An_StatePhys=="Calf" & NonMilkCP_ClfLiq > 0, 34.4, 11.9)
Fe_CPend_g <- ifelse(An_StatePhys=="Calf", K_FeCPend_ClfLiq*Dt_DMIn_ClfLiq + 20.6*(An_DMIn-Dt_DMIn_ClfLiq), Fe_CPend_g)
Fe_CPend <- Fe_CPend_g / 1000
Fe_Nend <- Fe_CPend * 0.16	#kg/d
Fe_NPend <- Fe_CPend * 0.73			#73% TP from Lapierre, kg/d
Fe_NPend_g <- Fe_NPend * 1000
Fe_RDPend <- Fe_CPend*An_RDPIn/An_CPIn  #Arbitrary assignment of Fe_CPend to RDP and RUP based on CPI proportion
Fe_RUPend <- Fe_CPend*An_RUPIn/An_CPIn  #Only used for tabular reporting to DE from RDP and RUP.  No other function.
Fe_RumMiCP <- Du_MiCP - Du_idMiCP
Fe_MiTP <- Du_MiTP - Du_idMiTP
Fe_RUP <- An_RUPIn + InfSI_TPIn - An_idRUPIn
Fe_InfCP <- (InfRum_RUPIn + InfSI_CPIn) - (InfRum_idRUPIn + InfSI_idCPIn) #Included in An_RUP
Dt_dcCP_ClfDry <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq < 0.01, 0.70, 0.75)
Dt_dcCP_ClfLiq <- 0.95
Fe_CP <- Fe_RUP + Fe_RumMiCP + Fe_CPend  + InfSI_NPNCPIn*(1-dcNPNCP/100) #Double counting portion of RumMiCP derived from End CP. Needs to be fixed. MDH
Fe_CP <- ifelse(An_StatePhys == "Calf", (1-Dt_dcCP_ClfLiq)*Dt_CPIn_ClfLiq + (1-Dt_dcCP_ClfDry)*(An_CPIn-Dt_CPIn_ClfLiq) +
                   Fe_CPend, Fe_CP)  #CP based for calves. Ignores RDP, RUP, Fe_NPend, etc.  Needs refinement.
Fe_TP <- Fe_RUP + Fe_MiTP + Fe_NPend  #Doesn't apply for calves
Fe_N <- Fe_CP * 0.16
Fe_N_g <- Fe_N * 1000
#Total Tract Digested Protein.  Statements using RDP, RUP, and MiCP are not valid for the calf.
Dt_DigCPaIn <- Dt_CPIn - Fe_CP 		#kg CP/d, apparent total tract digested CP
Dt_DigCPtIn <- Dt_RDPIn + Dt_idRUPIn	#kg CP/d, true total tract digested CP
Dt_DigCPtIn <- ifelse(An_StatePhys == "Calf", Dt_DigCPaIn + Fe_CPend, Dt_DigCPtIn)
Dt_DigTPaIn <- Dt_RDTPIn - Fe_MiTP + Dt_idRUPIn - Fe_NPend  #Doesn't apply to calves
Dt_DigTPtIn <- Dt_RDTPIn + Dt_idRUPIn
Dt_DigCPa <- Dt_DigCPaIn / Dt_DMIn * 100; 	#Dietary Apparrent total tract % of DM
TT_dcDtCPa <- Dt_DigCPaIn/Dt_CPIn * 100		#% of CP
Dt_DigCPt <- Dt_DigCPtIn / Dt_DMIn * 100; 	#Dietary True total tract % of DM
Dt_DigTPt <- Dt_DigTPtIn / Dt_DMIn * 100; 	#True total tract % of DM
TT_dcDtCPt <- Dt_DigCPtIn/Dt_CPIn * 100		#% of CP
Dt_MPIn <- Dt_idRUPIn + Du_idMiTP
Dt_MPIn <- ifelse(An_StatePhys == "Calf", Dt_CPIn - Fe_CP + Fe_CPend, Dt_MPIn)  #ignores all ruminal activity.
Dt_MP <- Dt_MPIn / Dt_DMIn * 100			#% of DM
An_DigCPaIn <- An_CPIn - InfArt_CPIn - Fe_CP		#apparent total tract
An_DigCPa <- An_DigCPaIn / (An_DMIn - InfArt_DMIn) * 100	#% of DM
TT_dcAnCPa <- An_DigCPaIn/(An_CPIn - InfArt_CPIn)*100	#% of CP

An_DigCPtIn <- An_RDPIn + An_idRUPIn		#true CP total tract
An_DigCPtIn <- ifelse(An_StatePhys=="Calf",  Dt_DigCPtIn + Inf_idCPIn, An_DigCPtIn)  #This may need more work depending on infusion type and protein source
An_DigNtIn_g <- An_DigCPtIn / 6.25 * 1000   #some of the following are not valid for calves.
An_DigTPtIn <- An_RDTPIn - Fe_MiTP + An_idRUPIn - Fe_NPend
An_DigTPaIn <- An_TPIn - InfArt_CPIn - Fe_CP #Very messy. Some Fe_MiTP derived from NPN and some MiNPN from Dt_TP, thus Fe_CP
An_DigCPt <- An_DigCPtIn / (An_DMIn - InfArt_DMIn) * 100	#% of DMIn
An_DigTPt <- An_DigTPtIn / (An_DMIn - InfArt_DMIn) * 100	#% of DMIn
TT_dcAnCPt <- An_DigCPtIn/(An_CPIn - InfArt_CPIn)*100	#% of CP
TT_dcAnTPt <- An_DigTPtIn/(An_TPIn + InfArt_CPIn - InfRum_NPNCPIn - InfSI_NPNCPIn)*100	#% of TP
SI_dcAnRUP <- An_idRUPIn / An_RUPIn * 100
An_idCPIn <- An_idRUPIn + Du_idMiCP			 #not a true value as ignores recycled endCP
An_MPIn <- An_idRUPIn + Du_idMiTP + InfArt_TPIn	 #the above with correction for micr N
An_MPIn <- ifelse(An_StatePhys=="Calf",  An_DigCPtIn, An_MPIn)
An_MPIn_g <- An_MPIn * 1000
An_MP <- An_MPIn / (Dt_DMIn+InfRum_DMIn+InfSI_DMIn) * 100
An_MP_CP <- An_MPIn / An_CPIn * 100


############################################################################################
#                                          Digested Fat                                    #
############################################################################################
#dc (% of FA) from Daley et al., 2020
TT_dcFat_Base <- 68  #Default value
TT_dcFA_Base <- 73
TT_dcFA_ClfDryFd <- 81  #Used for all calf dry feed
TT_dcFA_ClfLiqFd <- 81  #Used for missing values in calf liquid feeds
f$TT_dcFdFA <- f$Fd_dcFA 
f$TT_dcFdFA <- ifelse(is.na(f$TT_dcFdFA) & f$Fd_Category == "Fatty Acid Supplement", TT_dcFA_Base, f$TT_dcFdFA)
f$TT_dcFdFA <- ifelse(is.na(f$TT_dcFdFA) & f$Fd_Category == "Fat Supplement", TT_dcFat_Base, f$TT_dcFdFA)
f$TT_dcFdFA <- ifelse(is.na(f$TT_dcFdFA), TT_dcFat_Base, f$TT_dcFdFA)  #Fill in any remaining missing values with fat dc
f$TT_dcFdFA <- ifelse(f$An_StatePhys == "Calf" & f$Fd_Category != "Calf Liquid Feed" & f$Fd_Type == "Concentrate", TT_dcFA_ClfDryFd, f$TT_dcFdFA) #likely an over estimate for forage
f$TT_dcFdFA <- ifelse(is.na(f$TT_dcFdFA) & f$An_StatePhys=="Calf" & f$Fd_Category=="Calf Liquid Feed", TT_dcFA_ClfLiqFd, f$TT_dcFdFA) #Default if dc is not entered.

#Ingredient Digestible FA Intake, kg/d
f$Fd_DigFAIn <- f$TT_dcFdFA/100 * f$Fd_FA/100 * f$Fd_DMIn
f$Fd_DigC120In <- f$TT_dcFdFA/100 * f$Fd_C120_FA/100 * f$Fd_FA/100 * f$Fd_DMIn
f$Fd_DigC140In <- f$TT_dcFdFA/100 * f$Fd_C140_FA/100 * f$Fd_FA/100 * f$Fd_DMIn
f$Fd_DigC160In <- f$TT_dcFdFA/100 * f$Fd_C160_FA/100 * f$Fd_FA/100 * f$Fd_DMIn
f$Fd_DigC161In <- f$TT_dcFdFA/100 * f$Fd_C161_FA/100 * f$Fd_FA/100 * f$Fd_DMIn
f$Fd_DigC180In <- f$TT_dcFdFA/100 * f$Fd_C180_FA/100 * f$Fd_FA/100 * f$Fd_DMIn
f$Fd_DigC181tIn <- f$TT_dcFdFA/100 * f$Fd_C181t_FA/100 * f$Fd_FA/100 * f$Fd_DMIn
f$Fd_DigC181cIn <- f$TT_dcFdFA/100 * f$Fd_C181c_FA/100 * f$Fd_FA/100 * f$Fd_DMIn
f$Fd_DigC182In <- f$TT_dcFdFA/100 * f$Fd_C182_FA/100 * f$Fd_FA/100 * f$Fd_DMIn
f$Fd_DigC183In <- f$TT_dcFdFA/100 * f$Fd_C183_FA/100 * f$Fd_FA/100 * f$Fd_DMIn
f$Fd_DigOtherFAIn <- f$TT_dcFdFA/100 * f$Fd_OtherFA_FA/100 * f$Fd_FA/100 * f$Fd_DMIn

Dt_DigFAIn <- sum(f$Fd_DigFAIn, na.rm=TRUE)
Dt_DigC120In <- sum(f$Fd_DigC120In, na.rm=TRUE)
Dt_DigC140In <- sum(f$Fd_DigC140In, na.rm=TRUE)
Dt_DigC160In <- sum(f$Fd_DigC160In, na.rm=TRUE)
Dt_DigC161In <- sum(f$Fd_DigC161In, na.rm=TRUE)
Dt_DigC180In <- sum(f$Fd_DigC180In, na.rm=TRUE)
Dt_DigC181tIn <- sum(f$Fd_DigC181tIn, na.rm=TRUE)
Dt_DigC181cIn <- sum(f$Fd_DigC181cIn, na.rm=TRUE)
Dt_DigC182In <- sum(f$Fd_DigC182In, na.rm=TRUE)
Dt_DigC183In <- sum(f$Fd_DigC183In, na.rm=TRUE)
Dt_DigOtherFAIn <- sum(f$Fd_DigOtherFAIn, na.rm=TRUE)
Dt_DigUFAIn <- Dt_DigC161In + Dt_DigC181tIn + Dt_DigC181cIn + Dt_DigC182In + Dt_DigC183In
Dt_DigMUFAIn <- Dt_DigC161In + Dt_DigC181tIn + Dt_DigC181cIn
Dt_DigPUFAIn <- Dt_DigC182In + Dt_DigC183In
Dt_DigSatFAIn <- Dt_DigFAIn - Dt_DigUFAIn

#Calculate Dietary DigFA as a % of FA
Dt_DigFA_FA <- Dt_DigFAIn / Dt_FAIn * 100
Dt_DigC120_FA <- Dt_DigC120In / Dt_FAIn * 100
Dt_DigC140_FA <- Dt_DigC140In / Dt_FAIn * 100
Dt_DigC160_FA <- Dt_DigC160In / Dt_FAIn * 100
Dt_DigC161_FA <- Dt_DigC161In / Dt_FAIn * 100
Dt_DigC180_FA <- Dt_DigC180In / Dt_FAIn * 100
Dt_DigC181t_FA <- Dt_DigC181tIn / Dt_FAIn * 100
Dt_DigC181c_FA <- Dt_DigC181cIn / Dt_FAIn * 100
Dt_DigC182_FA <- Dt_DigC182In / Dt_FAIn * 100
Dt_DigC183_FA <- Dt_DigC183In / Dt_FAIn * 100
Dt_DigUFA_FA <- Dt_DigUFAIn / Dt_FAIn * 100
Dt_DigMUFA_FA <- Dt_DigMUFAIn / Dt_FAIn * 100
Dt_DigPUFA_FA <- Dt_DigPUFAIn / Dt_FAIn * 100
Dt_DigSatFA_FA <- Dt_DigSatFAIn / Dt_FAIn * 100
Dt_DigOtherFA_FA <- Dt_DigOtherFAIn / Dt_FAIn * 100

#Infused FA
#Infused individual FA should be calculated here if they are to be considered.  Requires a change to the infusion table. MDH
Inf_DigFAIn <-  Inf_FAIn * TT_dcFA_Base	#used dcFA which is similar to oil, but should define for each infusate
#Infused digestible FA would be calculated here.
An_DigFAIn <- Dt_DigFAIn + Inf_DigFAIn
An_DigFA <- An_DigFAIn / (Dt_DMIn+InfRum_DMIn+InfSI_DMIn) * 100
Fe_FA <- Dt_FAIn + InfRum_FAIn + InfSI_FAIn - Dt_DigFAIn - Inf_DigFAIn
TT_dcDtFA <- Dt_DigFAIn / Dt_FAIn * 100
TT_dcAnFA <- (Dt_DigFAIn + Inf_DigFAIn)/(Dt_FAIn + Inf_FAIn) * 100  #this should be just gut infusions, but don't have those calculated as ruminal and SI DC will not  be the same.
Dt_DigFA <- Dt_DigFAIn / Dt_DMIn * 100
Fe_OM <- Fe_CP + Fe_NDF + Fe_St + Fe_rOM + Fe_FA; #kg/d
Fe_OM_end <- Fe_rOMend + Fe_CPend
Dt_OMIn <- Dt_DMIn - Dt_AshIn
An_OMIn <- Dt_OMIn + Inf_OMIn
An_DigOMaIn_Base <- An_DigNDFIn_Base + An_DigStIn_Base + An_DigFAIn + An_DigrOMaIn + An_DigCPaIn
An_DigOMtIn_Base <- An_DigNDFIn_Base + An_DigStIn_Base + An_DigFAIn + An_DigrOMtIn + An_DigCPtIn
Dt_DigOMaIn <- Dt_DigNDFIn + Dt_DigStIn + Dt_DigFAIn + Dt_DigrOMaIn + Dt_DigCPaIn
Dt_DigOMtIn <- Dt_DigNDFIn + Dt_DigStIn + Dt_DigFAIn + Dt_DigrOMtIn + Dt_DigCPtIn
An_DigOMaIn <- An_DigNDFIn + An_DigStIn + An_DigFAIn + An_DigrOMaIn + An_DigCPaIn
An_DigOMtIn <- An_DigNDFIn + An_DigStIn + An_DigFAIn + An_DigrOMtIn + An_DigCPtIn
TT_dcOMa <- An_DigOMaIn / An_OMIn * 100
TT_dcOMt <- An_DigOMtIn / An_OMIn * 100
TT_dcOMt_Base <- An_DigOMtIn_Base / An_OMIn * 100
Dt_DigOMa <- Dt_DigOMaIn/Dt_DMIn * 100
Dt_DigOMt <- Dt_DigOMtIn/Dt_DMIn * 100
An_DigOMa <- An_DigOMaIn/(Dt_DMIn+InfRum_DMIn+InfSI_DMIn) * 100
An_DigOMt <- An_DigOMtIn/(Dt_DMIn+InfRum_DMIn+InfSI_DMIn) * 100

############################################################################################
#                                Gross and Digestible Energy                               #
############################################################################################
#Gross Energy Concentrations and Intakes, MCal/kg diet or Mcal/d
#Dt_GEIn <-  Dt_NDFIn*En_NDF + Dt_StIn*En_St + Dt_rOMIn*En_rOM + Dt_FAIn*En_FA + 
#	Dt_TPIn*En_CP + Dt_NPNCPIn*En_NPNCP  #now summed by ingredient
An_GEIn <- Dt_GEIn + Inf_NDFIn*En_NDF + Inf_StIn*En_St + Inf_FAIn*En_FA + Inf_TPIn*En_CP + 
           Inf_NPNCPIn*En_NPNCP + Inf_AcetIn*En_Acet + Inf_PropIn*En_Prop + Inf_ButrIn*En_Butr
Dt_GE <- Dt_GEIn / Dt_DMIn
An_GE <- An_GEIn / An_DMIn  #included all infusions in DMIn
#Digestible Energy Intakes and Concentrations from Digested Nutrients, Mcal/kg diet or Mcal/d
Dt_DEStIn <- Dt_DigStIn*En_St
Dt_DErOMIn <- Dt_DigrOMaIn*En_rOM
Dt_DENDFIn <- Dt_DigNDFIn*En_NDF
Dt_DECPIn <- Dt_DigCPaIn*En_CP
Dt_DENPNCPIn <- Dt_NPNCPIn*dcNPNCP/100 * En_NPNCP
Dt_DETPIn <- Dt_DECPIn - Dt_DENPNCPIn/En_NPNCP*En_CP  #Caution! DigTPaIn not clean so subtracted DE for CP equiv of NPN to correct. Not a true DE_TP.
Dt_DEFAIn <- Dt_DigFAIn*En_FA
An_DEStIn <- An_DigStIn*En_St
An_DErOMIn <- An_DigrOMaIn*En_rOM
An_DENDFIn <- An_DigNDFIn*En_NDF
An_DECPIn <- An_DigCPaIn*En_CP
An_DENPNCPIn <- Dt_DENPNCPIn + Inf_NPNCPIn*dcNPNCP/100*En_NPNCP
An_DETPIn <- An_DECPIn - An_DENPNCPIn/En_NPNCP * En_CP  #Caution! DigTPaIn not clean so subtracted DE for CP equiv of NPN to correct. Not a true DE_TP.
Fe_DEMiCPend <- Fe_RumMiCP  * En_CP  #DE in undigested ruminal MiCP and RDP portion of Fe_EndCP.
Fe_DERDPend <- Fe_RDPend * En_CP  #Arbitrary DE assignment of Fe_CPend DE to RDP and RUP. Reporting use only.
Fe_DERUPend <- Fe_RUPend * En_CP
An_DERDTPIn <- An_RDTPIn*En_CP - Fe_DEMiCPend - Fe_DERDPend
An_DEidRUPIn <- An_idRUPIn*En_CP - Fe_DERUPend 
An_DEFAIn <- An_DigFAIn*En_FA
Inf_DEAcetIn <- Inf_AcetIn*En_Acet
Inf_DEPropIn <- Inf_PropIn*En_Prop
Inf_DEButrIn <- Inf_ButrIn*En_Butr
Dt_DEIn <-  Dt_DENDFIn + Dt_DEStIn + Dt_DErOMIn + Dt_DETPIn + Dt_DENPNCPIn + Dt_DEFAIn
An_DEIn <-  An_DENDFIn + An_DEStIn + An_DErOMIn + An_DETPIn + An_DENPNCPIn + An_DEFAIn + 
          Inf_DEAcetIn + Inf_DEPropIn + Inf_DEButrIn

#DE is calculated for calves in the software interface directly from ingredient nutrients rather than from digested nutrients. 
#This deviation from the scheme needs to be corrected in the next version of the NRC. MDH.
Dt_DEIn <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq >0, Dt_DEIn_base_ClfLiq + Dt_DEIn_base_ClfDry, Dt_DEIn)
An_DEIn <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq >0, Dt_DEIn, An_DEIn)  #Infusion DE not considered for milk-fed calves

Dt_DEIn <- ifelse(Monensin_eqn == 1, Dt_DEIn*1.02, Dt_DEIn)
An_DEIn <- ifelse(Monensin_eqn == 1, An_DEIn*1.02, An_DEIn)
En_OM <- An_DEIn / An_DigOMtIn
Dt_DE <- Dt_DEIn / Dt_DMIn
An_DE <- An_DEIn / An_DMIn
An_DE_GE <- An_DEIn / An_GEIn
Fe_DEout <- An_GEIn-An_DEIn
Fe_DE_GE <- Fe_DEout/An_GEIn
Fe_DE <- Fe_DEout/An_DMIn

#Create a nonprotein DEIn for milk protein predictions. 
An_DEInp <- An_DEIn - An_DETPIn - An_DENPNCPIn
An_DEnp <- An_DEInp / An_DMIn * 100     
Dt_TDN <- Dt_DigSt + Dt_DigNDF + Dt_DigrOMa + Dt_DigCPa + Dt_DigFA*2.25
Dt_TDNIn <- Dt_TDN/100*Dt_DMIn                         
Du_MiN_NRC2001_g <- ifelse(0.13*Dt_TDNIn > 0.85*An_RDPIn, 0.85*An_RDPIn, 0.13*Dt_TDNIn)*1000*0.16  #NRC 2001 eqn. for N flow comparison purposes

############## Gaseous energy loss mcal/d ###############################
Dt_GasE_IPCC2 <- 0.065 * Dt_GEIn	#for comparison purposes, 
An_GasE_IPCC2 <- 0.065 * An_GEIn	#but it reflects the whole farm not individual animal types

Dt_GasEOut_Lact <- 0.294*Dt_DMIn - 0.347*Dt_FA + 0.0409*Dt_DigNDF  #Lact Cows
Dt_GasEOut_Heif <- -0.038 + 0.051*Dt_GEIn - 0.0091*Dt_NDF          #Heifers/Buls
Dt_GasEOut_Dry <- -0.69 + 0.053*Dt_GEIn - 0.0789*Dt_FA             #Heifers/Bulls, convert from EE to FA assum 57% FA in EE, from BW
Dt_GasEOut_Clf <- 0   #No observations on calves.  Woudl not be 0 once the calf starts eating dry feed.

Dt_GasEOut <- ifelse(An_StatePhys == 'Dry Cow',Dt_GasEOut_Dry,Dt_GasEOut_Heif)
Dt_GasEOut <- ifelse(An_StatePhys == 'Calf',Dt_GasEOut_Clf,Dt_GasEOut)
Dt_GasEOut <- ifelse(An_StatePhys == 'Lactating Cow',Dt_GasEOut_Lact,Dt_GasEOut)
Dt_GasEOut <- ifelse(Monensin_eqn == 1, Dt_GasEOut * 0.95, Dt_GasEOut)
An_GasEOut_Lact <- 0.294*(Dt_DMIn+InfRum_DMIn) - 0.347*(Dt_FAIn+InfRum_FAIn)/(Dt_DMIn+InfRum_DMIn)*100 + 
     0.0409*An_DigNDF
An_GasEOut_Heif <- -0.038 + 0.051*An_GEIn + 0.0091*An_NDF                #Heifers/Bulls
An_GasEOut_Dry <- 0.69 + 0.053*An_GEIn - 0.07*(Dt_FAIn+InfRum_FAIn)/(Dt_DMIn+InfRum_DMIn)*100   #Dry Cows
An_GasEOut_Clf <- 0                  #Calves
An_GasEOut <- ifelse(An_StatePhys == 'Dry Cow',An_GasEOut_Dry,An_GasEOut_Heif)
An_GasEOut <- ifelse(An_StatePhys == 'Calf',An_GasEOut_Clf,An_GasEOut)
An_GasEOut <- ifelse(An_StatePhys == 'Lactating Cow',An_GasEOut_Lact,An_GasEOut)
An_GasEOut <- ifelse(Monensin_eqn == 1, An_GasEOut * 0.95, An_GasEOut)
GasE_DMIn <- An_GasEOut / An_DMIn
GasE_GEIn <- An_GasEOut / An_GEIn
GasE_DEIn <- An_GasEOut / An_DEIn

############################################################################################
#                      Amino Acid Supply                                                   #
############################################################################################
#AA profiles (g AA/100 g AA) for Microbial and Endogenous protein and hydration and recovery factors
#Also Digestible RUP AA values (dAA/dCP) from White and Firkins "Technical Note: Methodological 
#and feed factors affecting prediction of ruminal degradability and intestinal digestibility of 
#essential amino acids"
#All of the AA flows are in hydrated form regardless of whether they exist in a protien or in free form.
#Thus the flows within protein will be approximately 1.15 of the protein flow.
#Abbreviations: AA represents an apparent observed value not corrected for recovery during 24h hydrolysis
#			AAt = AA value corrected for hydrolysis recovery; hydr AAt = hydrated AAt in free form as measured 
#			after hydrolysis; dehydr AAt = dehydrated AAt in protein bound form

# Microbial protein AA profile (g hydrated AA / 100 g TP) corrected for 24h hydrolysis recovery. 
# Sok et al., 2017 JDS
MiTPArgProf <- 5.47
MiTPHisProf <- 2.21
MiTPIleProf <- 6.99
MiTPLeuProf <- 9.23
MiTPLysProf <- 9.44
MiTPMetProf <- 2.63
MiTPPheProf <- 6.30
MiTPThrProf <- 6.23
MiTPTrpProf <- 1.37
MiTPValProf <- 6.88

# Doudenal endogenous CP AA profile (g hydrated AA / 100 g CP) corrected for 24 h 
# hydrolysis recovery. Lapierre et al.from Orskov et al. 1986.  Br. J. Nutr. 56:241-248. 
# corrected for 24 h recovery by Lapierre
EndArgProf <- 4.61 
EndHisProf <- 2.90
EndIleProf <- 4.09
EndLeuProf <- 7.67
EndLysProf <- 6.23
EndMetProf <- 1.26
EndPheProf <- 3.98
EndThrProf <- 5.18
EndTrpProf <- 1.29
EndValProf <- 5.29

#AA recovery factors for recovery of each AA at maximum release in hydrolysis time over 24 h release (g true/g at 24 h)
#From Lapierre, H., et al., 2016. Pp 205-219. in Proc. Cornell Nutrition Conference for feed manufacturers. 
#	Key roles of amino acids in cow performance and metabolism ? considerations for 
#	defining amino acid requirement. 
#Inverted relative to that reported by Lapierre so they are true recovery factors, MDH
RecArg <- 1 / 1.061
RecHis <- 1 / 1.073
RecIle <- 1 / 1.12
RecLeu <- 1 / 1.065
RecLys <- 1 / 1.066
RecMet <- 1 / 1.05
RecPhe <- 1 / 1.061
RecThr <- 1 / 1.067
RecTrp <- 1 / 1.06
RecVal <- 1 / 1.102

#AA dehydration factors for mass change during peptide formation (g anhyd AAt / g hydrated AAt)
HydrArg <- 0.8967
HydrHis <- 0.8840
HydrIle <- 0.8628
HydrLeu <- 0.8628
HydrLys <- 0.8769
HydrMet <- 0.8794
HydrPhe <- 0.8910
HydrThr <- 0.8490
HydrTrp <- 0.9118
HydrVal <- 0.8464

#True feed AA (g hydrated AAt/100 g CP) corrected for reported 24 h recovered AA
#Consider moving the AA intakes to the Feed Section.
f$Fd_Argt_CP <- f$Fd_Arg_CP/RecArg
f$Fd_Hist_CP <- f$Fd_His_CP/RecHis
f$Fd_Ilet_CP <- f$Fd_Ile_CP/RecIle
f$Fd_Leut_CP <- f$Fd_Leu_CP/RecLeu
f$Fd_Lyst_CP <- f$Fd_Lys_CP/RecLys
f$Fd_Mett_CP <- f$Fd_Met_CP/RecMet
f$Fd_Phet_CP <- f$Fd_Phe_CP/RecPhe
f$Fd_Thrt_CP <- f$Fd_Thr_CP/RecThr
f$Fd_Trpt_CP <- f$Fd_Trp_CP/RecTrp
f$Fd_Valt_CP <- f$Fd_Val_CP/RecVal

#### Hydrated Amino Acid Intakes from each feed, g/d ####
#For code clarity, these should have been specified as Fd_AAIn_g.
f$Fd_ArgIn <- ifelse(f$Fd_CPIn > 0, (f$Fd_Argt_CP/100)*(f$Fd_CP/100)*f$Fd_DMIn*1000, 0)
f$Fd_HisIn <- ifelse(f$Fd_CPIn > 0, (f$Fd_Hist_CP/100)*(f$Fd_CP/100)*f$Fd_DMIn*1000, 0)
f$Fd_IleIn <- ifelse(f$Fd_CPIn > 0, (f$Fd_Ilet_CP/100)*(f$Fd_CP/100)*f$Fd_DMIn*1000, 0)
f$Fd_LeuIn <- ifelse(f$Fd_CPIn > 0, (f$Fd_Leut_CP/100)*(f$Fd_CP/100)*f$Fd_DMIn*1000, 0)
f$Fd_LysIn <- ifelse(f$Fd_CPIn > 0, (f$Fd_Lyst_CP/100)*(f$Fd_CP/100)*f$Fd_DMIn*1000, 0)
f$Fd_MetIn <- ifelse(f$Fd_CPIn > 0, (f$Fd_Mett_CP/100)*(f$Fd_CP/100)*f$Fd_DMIn*1000, 0)
f$Fd_PheIn <- ifelse(f$Fd_CPIn > 0, (f$Fd_Phet_CP/100)*(f$Fd_CP/100)*f$Fd_DMIn*1000, 0)
f$Fd_ThrIn <- ifelse(f$Fd_CPIn > 0, (f$Fd_Thrt_CP/100)*(f$Fd_CP/100)*f$Fd_DMIn*1000, 0)
f$Fd_TrpIn <- ifelse(f$Fd_CPIn > 0, (f$Fd_Trpt_CP/100)*(f$Fd_CP/100)*f$Fd_DMIn*1000, 0)
f$Fd_ValIn <- ifelse(f$Fd_CPIn > 0, (f$Fd_Valt_CP/100)*(f$Fd_CP/100)*f$Fd_DMIn*1000, 0)

#Sum across ingredients to yield true, hydrated dietary AA intakes, g/d
#Should change the abbreviation to Dt_AAIn_g for clarity.  Same for the rest of the AA system. MDH
Dt_ArgIn <- sum(f$Fd_ArgIn, na.rm=TRUE)
Dt_HisIn <- sum(f$Fd_HisIn, na.rm=TRUE)
Dt_IleIn <- sum(f$Fd_IleIn, na.rm=TRUE)
Dt_LeuIn <- sum(f$Fd_LeuIn, na.rm=TRUE)
Dt_LysIn <- sum(f$Fd_LysIn, na.rm=TRUE)
Dt_MetIn <- sum(f$Fd_MetIn, na.rm=TRUE)
Dt_PheIn <- sum(f$Fd_PheIn, na.rm=TRUE)
Dt_ThrIn <- sum(f$Fd_ThrIn, na.rm=TRUE)
Dt_TrpIn <- sum(f$Fd_TrpIn, na.rm=TRUE)
Dt_ValIn <- sum(f$Fd_ValIn, na.rm=TRUE)

############ Estimated RUP AAt outflow from each Feed, g hydrated AAt/d ############
f$Fd_ArgRUPIn <- ifelse(f$Fd_RUPIn > 0, (f$Fd_Argt_CP/100)*(f$Fd_RUPIn)*1000,  0)
f$Fd_HisRUPIn <- ifelse(f$Fd_RUPIn > 0, (f$Fd_Hist_CP/100)*(f$Fd_RUPIn)*1000,  0)
f$Fd_IleRUPIn <- ifelse(f$Fd_RUPIn > 0, (f$Fd_Ilet_CP/100)*(f$Fd_RUPIn)*1000,  0)
f$Fd_LeuRUPIn <- ifelse(f$Fd_RUPIn > 0, (f$Fd_Leut_CP/100)*(f$Fd_RUPIn)*1000,  0)
f$Fd_LysRUPIn <- ifelse(f$Fd_RUPIn > 0, (f$Fd_Lyst_CP/100)*(f$Fd_RUPIn)*1000,  0)
f$Fd_MetRUPIn <- ifelse(f$Fd_RUPIn > 0, (f$Fd_Mett_CP/100)*(f$Fd_RUPIn)*1000,  0)
f$Fd_PheRUPIn <- ifelse(f$Fd_RUPIn > 0, (f$Fd_Phet_CP/100)*(f$Fd_RUPIn)*1000,  0)
f$Fd_ThrRUPIn <- ifelse(f$Fd_RUPIn > 0, (f$Fd_Thrt_CP/100)*(f$Fd_RUPIn)*1000,  0)
f$Fd_TrpRUPIn <- ifelse(f$Fd_RUPIn > 0, (f$Fd_Trpt_CP/100)*(f$Fd_RUPIn)*1000,  0)
f$Fd_ValRUPIn <- ifelse(f$Fd_RUPIn > 0, (f$Fd_Valt_CP/100)*(f$Fd_RUPIn)*1000,  0)

#Sum across ingredients to yield duodenal RUP AA flows by diet, g hydrated AAt/d
Dt_ArgRUPIn <- sum(f$Fd_ArgRUPIn, na.rm=TRUE)
Dt_HisRUPIn <- sum(f$Fd_HisRUPIn, na.rm=TRUE)
Dt_IleRUPIn <- sum(f$Fd_IleRUPIn, na.rm=TRUE)
Dt_LeuRUPIn <- sum(f$Fd_LeuRUPIn, na.rm=TRUE)
Dt_LysRUPIn <- sum(f$Fd_LysRUPIn, na.rm=TRUE)
Dt_MetRUPIn <- sum(f$Fd_MetRUPIn, na.rm=TRUE)
Dt_PheRUPIn <- sum(f$Fd_PheRUPIn, na.rm=TRUE)
Dt_ThrRUPIn <- sum(f$Fd_ThrRUPIn, na.rm=TRUE)
Dt_TrpRUPIn <- sum(f$Fd_TrpRUPIn, na.rm=TRUE)
Dt_ValRUPIn <- sum(f$Fd_ValRUPIn, na.rm=TRUE)

#RUP AA expressed as a fraction of dietary AA
DtArgRUP_DtArg <- Dt_ArgRUPIn / Dt_ArgIn
DtHisRUP_DtHis <- Dt_HisRUPIn / Dt_HisIn
DtIleRUP_DtIle <- Dt_IleRUPIn / Dt_IleIn
DtLeuRUP_DtLeu <- Dt_LeuRUPIn / Dt_LeuIn
DtLysRUP_DtLys <- Dt_LysRUPIn / Dt_LysIn
DtMetRUP_DtMet <- Dt_MetRUPIn / Dt_MetIn
DtPheRUP_DtPhe <- Dt_PheRUPIn / Dt_PheIn
DtThrRUP_DtThr <- Dt_ThrRUPIn / Dt_ThrIn
DtTrpRUP_DtTrp <- Dt_TrpRUPIn / Dt_TrpIn
DtValRUP_DtVal <- Dt_ValRUPIn / Dt_ValIn

#Ruminally Inf_AA escaping the rumen
Inf_ArgRUPIn <- i$Inf_Rum * i$Inf_Arg_g * InfRum_RUP_CP/100
Inf_HisRUPIn <- i$Inf_Rum * i$Inf_His_g * InfRum_RUP_CP/100
Inf_IleRUPIn <- i$Inf_Rum * i$Inf_Ile_g * InfRum_RUP_CP/100
Inf_LeuRUPIn <- i$Inf_Rum * i$Inf_Leu_g * InfRum_RUP_CP/100
Inf_LysRUPIn <- i$Inf_Rum * i$Inf_Lys_g * InfRum_RUP_CP/100
Inf_MetRUPIn <- i$Inf_Rum * i$Inf_Met_g * InfRum_RUP_CP/100
Inf_PheRUPIn <- i$Inf_Rum * i$Inf_Phe_g * InfRum_RUP_CP/100
Inf_ThrRUPIn <- i$Inf_Rum * i$Inf_Thr_g * InfRum_RUP_CP/100
Inf_TrpRUPIn <- i$Inf_Rum * i$Inf_Trp_g * InfRum_RUP_CP/100
Inf_ValRUPIn <- i$Inf_Rum * i$Inf_Val_g * InfRum_RUP_CP/100

######## Microbial AA Flow, g hydrated true AA (AAt/d) ########
Du_ArgMic <- Du_MiTP_g * MiTPArgProf/100 #previously used Du_MiTP (kg/d) / 1000
Du_HisMic <- Du_MiTP_g * MiTPHisProf/100 #The LHS vars should all have _g in the names
Du_IleMic <- Du_MiTP_g * MiTPIleProf/100
Du_LeuMic <- Du_MiTP_g * MiTPLeuProf/100
Du_LysMic <- Du_MiTP_g * MiTPLysProf/100
Du_MetMic <- Du_MiTP_g * MiTPMetProf/100
Du_PheMic <- Du_MiTP_g * MiTPPheProf/100
Du_ThrMic <- Du_MiTP_g * MiTPThrProf/100
Du_TrpMic <- Du_MiTP_g * MiTPTrpProf/100
Du_ValMic <- Du_MiTP_g * MiTPValProf/100

# Duodenal EndPAA, g hydrated true AA/d 
Du_ArgEndP <- Du_EndCP_g * EndArgProf/100 
Du_HisEndP <- Du_EndCP_g * EndHisProf/100
Du_IleEndP <- Du_EndCP_g * EndIleProf/100
Du_LeuEndP <- Du_EndCP_g * EndLeuProf/100
Du_LysEndP <- Du_EndCP_g * EndLysProf/100
Du_MetEndP <- Du_EndCP_g * EndMetProf/100
Du_PheEndP <- Du_EndCP_g * EndPheProf/100
Du_ThrEndP <- Du_EndCP_g * EndThrProf/100
Du_TrpEndP <- Du_EndCP_g * EndTrpProf/100
Du_ValEndP <- Du_EndCP_g * EndValProf/100

#Total ruminal AA outflows, g hydr, fully recovered AA/d (true protein bound AA flows)
Du_Arg <- (Dt_ArgRUPIn + Inf_ArgRUPIn + Du_ArgMic + Du_ArgEndP) #These shoudl have _g at the end of each
Du_His <- (Dt_HisRUPIn + Inf_HisRUPIn + Du_HisMic + Du_HisEndP)
Du_Ile <- (Dt_IleRUPIn + Inf_IleRUPIn + Du_IleMic + Du_IleEndP)
Du_Leu <- (Dt_LeuRUPIn + Inf_LeuRUPIn + Du_LeuMic + Du_LeuEndP)
Du_Lys <- (Dt_LysRUPIn + Inf_LysRUPIn + Du_LysMic + Du_LysEndP)
Du_Met <- (Dt_MetRUPIn + Inf_MetRUPIn + Du_MetMic + Du_MetEndP)
Du_Phe <- (Dt_PheRUPIn + Inf_PheRUPIn + Du_PheMic + Du_PheEndP)
Du_Thr <- (Dt_ThrRUPIn + Inf_ThrRUPIn + Du_ThrMic + Du_ThrEndP)
Du_Trp <- (Dt_TrpRUPIn + Inf_TrpRUPIn + Du_TrpMic + Du_TrpEndP)
Du_Val <- (Dt_ValRUPIn + Inf_ValRUPIn + Du_ValMic + Du_ValEndP)
Du_EAA_g <- Du_Arg + Du_His + Du_Ile + Du_Leu + Du_Lys + Du_Met + Du_Phe + Du_Thr + Du_Trp + Du_Val

#Duodenal AA flow expressed as a fraction of dietary AA, ruminally infused included in Du but not Dt
DuArg_DtArg <- Du_Arg / Dt_ArgIn
DuHis_DtHis <- Du_His / Dt_HisIn
DuIle_DtIle <- Du_Ile / Dt_IleIn
DuLeu_DtLeu <- Du_Leu / Dt_LeuIn
DuLys_DtLys <- Du_Lys / Dt_LysIn
DuMet_DtMet <- Du_Met / Dt_MetIn
DuPhe_DtPhe <- Du_Phe / Dt_PheIn
DuThr_DtThr <- Du_Thr / Dt_ThrIn
DuTrp_DtTrp <- Du_Trp / Dt_TrpIn
DuVal_DtVal <- Du_Val / Dt_ValIn

#The following predicted AA flows are for comparison to observed Duod AA flows, g hydrat 24h recovered AA/d
Du_Arg24h <- Du_Arg * RecArg 
Du_His24h <- Du_His * RecHis 
Du_Ile24h <- Du_Ile * RecIle
Du_Leu24h <- Du_Leu * RecLeu
Du_Lys24h <- Du_Lys * RecLys
Du_Met24h <- Du_Met * RecMet
Du_Phe24h <- Du_Phe * RecPhe
Du_Thr24h <- Du_Thr * RecThr
Du_Trp24h <- Du_Trp * RecTrp
Du_Val24h <- Du_Val * RecVal




############################################################################################
#                             Digested AA (g/d)                                            #
############################################################################################
#Digested endogenous protein is ignored as it is a recycle of previously absorbed AA.
#SI Digestibility of AA relative to RUP digestibility ([g dAA / g AA] / [g dRUP / g RUP])
#All set to 1 due to lack of clear evidence for deviations.
SIDigArgRUPf <- 1
SIDigHisRUPf <- 1
SIDigIleRUPf <- 1
SIDigLeuRUPf <- 1
SIDigLysRUPf <- 1
SIDigMetRUPf <- 1
SIDigPheRUPf <- 1
SIDigThrRUPf <- 1
SIDigTrpRUPf <- 1
SIDigValRUPf <- 1

#Intestinally Digested (Id) RUP Animo Acid flow from each feed, g hydrated AAt/d. Base on other intest dig abbrev, this should be id not Id.
f$Fd_IdArgRUPIn <- ifelse(f$Fd_ArgRUPIn > 0,  f$Fd_dcRUP/100*f$Fd_ArgRUPIn*SIDigArgRUPf,  0)
f$Fd_IdHisRUPIn <- ifelse(f$Fd_HisRUPIn > 0,  f$Fd_dcRUP/100*f$Fd_HisRUPIn*SIDigHisRUPf,  0)
f$Fd_IdIleRUPIn <- ifelse(f$Fd_IleRUPIn > 0,  f$Fd_dcRUP/100*f$Fd_IleRUPIn*SIDigIleRUPf,  0)
f$Fd_IdLeuRUPIn <- ifelse(f$Fd_LeuRUPIn > 0,  f$Fd_dcRUP/100*f$Fd_LeuRUPIn*SIDigLeuRUPf,  0)
f$Fd_IdLysRUPIn <- ifelse(f$Fd_LysRUPIn > 0,  f$Fd_dcRUP/100*f$Fd_LysRUPIn*SIDigLysRUPf,  0)
f$Fd_IdMetRUPIn <- ifelse(f$Fd_MetRUPIn > 0,  f$Fd_dcRUP/100*f$Fd_MetRUPIn*SIDigMetRUPf,  0)
f$Fd_IdPheRUPIn <- ifelse(f$Fd_PheRUPIn > 0,  f$Fd_dcRUP/100*f$Fd_PheRUPIn*SIDigPheRUPf,  0)
f$Fd_IdThrRUPIn <- ifelse(f$Fd_ThrRUPIn > 0,  f$Fd_dcRUP/100*f$Fd_ThrRUPIn*SIDigThrRUPf,  0)
f$Fd_IdTrpRUPIn <- ifelse(f$Fd_TrpRUPIn > 0,  f$Fd_dcRUP/100*f$Fd_TrpRUPIn*SIDigTrpRUPf,  0)
f$Fd_IdValRUPIn <- ifelse(f$Fd_ValRUPIn > 0,  f$Fd_dcRUP/100*f$Fd_ValRUPIn*SIDigValRUPf,  0)

#### Intestinally digested RUP AA flow from each diet, g hydrated AA/d
Dt_IdArgRUPIn <- sum(f$Fd_IdArgRUPIn, na.rm=TRUE)
Dt_IdHisRUPIn <- sum(f$Fd_IdHisRUPIn, na.rm=TRUE)
Dt_IdIleRUPIn <- sum(f$Fd_IdIleRUPIn, na.rm=TRUE)
Dt_IdLeuRUPIn <- sum(f$Fd_IdLeuRUPIn, na.rm=TRUE)
Dt_IdLysRUPIn <- sum(f$Fd_IdLysRUPIn, na.rm=TRUE)
Dt_IdMetRUPIn <- sum(f$Fd_IdMetRUPIn, na.rm=TRUE)
Dt_IdPheRUPIn <- sum(f$Fd_IdPheRUPIn, na.rm=TRUE)
Dt_IdThrRUPIn <- sum(f$Fd_IdThrRUPIn, na.rm=TRUE)
Dt_IdTrpRUPIn <- sum(f$Fd_IdTrpRUPIn, na.rm=TRUE)
Dt_IdValRUPIn <- sum(f$Fd_IdValRUPIn, na.rm=TRUE)

### Intestinally digested AA from Infused RUP AA plus SI infused AA
Inf_IdArgIn <- (i$Inf_Arg_g*i$Inf_SI + Inf_ArgRUPIn) * i$Inf_dcRUP/100 
Inf_IdHisIn <- (i$Inf_His_g*i$Inf_SI + Inf_HisRUPIn) * i$Inf_dcRUP/100
Inf_IdIleIn <- (i$Inf_Ile_g*i$Inf_SI + Inf_IleRUPIn) * i$Inf_dcRUP/100
Inf_IdLeuIn <- (i$Inf_Leu_g*i$Inf_SI + Inf_LeuRUPIn) * i$Inf_dcRUP/100
Inf_IdLysIn <- (i$Inf_Lys_g*i$Inf_SI + Inf_LysRUPIn) * i$Inf_dcRUP/100
Inf_IdMetIn <- (i$Inf_Met_g*i$Inf_SI + Inf_MetRUPIn) * i$Inf_dcRUP/100
Inf_IdPheIn <- (i$Inf_Phe_g*i$Inf_SI + Inf_PheRUPIn) * i$Inf_dcRUP/100
Inf_IdThrIn <- (i$Inf_Thr_g*i$Inf_SI + Inf_ThrRUPIn) * i$Inf_dcRUP/100
Inf_IdTrpIn <- (i$Inf_Trp_g*i$Inf_SI + Inf_TrpRUPIn) * i$Inf_dcRUP/100
Inf_IdValIn <- (i$Inf_Val_g*i$Inf_SI + Inf_ValRUPIn) * i$Inf_dcRUP/100


######## Digested MicAA Flows, g hydrated true AA (IdAAt/d) #################
Du_IdArgMic <- Du_ArgMic * SI_dcMiCP/100
Du_IdHisMic <- Du_HisMic * SI_dcMiCP/100
Du_IdIleMic <- Du_IleMic * SI_dcMiCP/100
Du_IdLeuMic <- Du_LeuMic * SI_dcMiCP/100
Du_IdLysMic <- Du_LysMic * SI_dcMiCP/100
Du_IdMetMic <- Du_MetMic * SI_dcMiCP/100
Du_IdPheMic <- Du_PheMic * SI_dcMiCP/100
Du_IdThrMic <- Du_ThrMic * SI_dcMiCP/100
Du_IdTrpMic <- Du_TrpMic * SI_dcMiCP/100
Du_IdValMic <- Du_ValMic * SI_dcMiCP/100 

####### Total Digestible AA including ruminal and intestinal infusions #######
Dt_IdArgIn <- Du_IdArgMic + Dt_IdArgRUPIn
Dt_IdHisIn <- Du_IdHisMic + Dt_IdHisRUPIn
Dt_IdIleIn <- Du_IdIleMic + Dt_IdIleRUPIn
Dt_IdLeuIn <- Du_IdLeuMic + Dt_IdLeuRUPIn
Dt_IdLysIn <- Du_IdLysMic + Dt_IdLysRUPIn
Dt_IdMetIn <- Du_IdMetMic + Dt_IdMetRUPIn
Dt_IdPheIn <- Du_IdPheMic + Dt_IdPheRUPIn
Dt_IdThrIn <- Du_IdThrMic + Dt_IdThrRUPIn
Dt_IdTrpIn <- Du_IdTrpMic + Dt_IdTrpRUPIn
Dt_IdValIn <- Du_IdValMic + Dt_IdValRUPIn

An_IdArgIn <- Dt_IdArgIn + Inf_IdArgIn
An_IdHisIn <- Dt_IdHisIn + Inf_IdHisIn
An_IdIleIn <- Dt_IdIleIn + Inf_IdIleIn
An_IdLeuIn <- Dt_IdLeuIn + Inf_IdLeuIn
An_IdLysIn <- Dt_IdLysIn + Inf_IdLysIn
An_IdMetIn <- Dt_IdMetIn + Inf_IdMetIn
An_IdPheIn <- Dt_IdPheIn + Inf_IdPheIn
An_IdThrIn <- Dt_IdThrIn + Inf_IdThrIn
An_IdTrpIn <- Dt_IdTrpIn + Inf_IdTrpIn
An_IdValIn <- Dt_IdValIn + Inf_IdValIn


#Intestinally Digested AA flow expressed as a fraction of dietary AA
#ruminally and intesntinally infused included in id but not Dt
IdArg_DtArg <- An_IdArgIn / Dt_ArgIn
IdHis_DtHis <- An_IdHisIn / Dt_HisIn
IdIle_DtIle <- An_IdIleIn / Dt_IleIn
IdLeu_DtLeu <- An_IdLeuIn / Dt_LeuIn
IdLys_DtLys <- An_IdLysIn / Dt_LysIn
IdMet_DtMet <- An_IdMetIn / Dt_MetIn
IdPhe_DtPhe <- An_IdPheIn / Dt_PheIn
IdThr_DtThr <- An_IdThrIn / Dt_ThrIn
IdTrp_DtTrp <- An_IdTrpIn / Dt_TrpIn
IdVal_DtVal <- An_IdValIn / Dt_ValIn


############################################################################################
#                            Absorbed AA, g/d and mol/d                                    #
############################################################################################
#Includes blood infusions but ignores endogenous AA absorption
MWArg <- 174.2
MWHis <- 155.2
MWIle <- 131.2
MWLeu <- 131.2
MWLys <- 146.2
MWMet <- 149.2
MWPhe <- 165.2
MWThr <- 119.1
MWTrp <- 204.2
MWVal <- 117.2

#Net Absorbed hydrated AA (g/d) from diet, microbes, and infusions.  
#EndAA not considered as it is recycled.
Abs_Arg_g <- An_IdArgIn + i$Inf_Arg_g * i$Inf_Art
Abs_His_g <- An_IdHisIn + i$Inf_His_g * i$Inf_Art
Abs_Ile_g <- An_IdIleIn + i$Inf_Ile_g * i$Inf_Art
Abs_Leu_g <- An_IdLeuIn + i$Inf_Leu_g * i$Inf_Art
Abs_Lys_g <- An_IdLysIn + i$Inf_Lys_g * i$Inf_Art
Abs_Met_g <- An_IdMetIn + i$Inf_Met_g * i$Inf_Art
Abs_Phe_g <- An_IdPheIn + i$Inf_Phe_g * i$Inf_Art
Abs_Thr_g <- An_IdThrIn + i$Inf_Thr_g * i$Inf_Art
Abs_Trp_g <- An_IdTrpIn + i$Inf_Trp_g * i$Inf_Art
Abs_Val_g <- An_IdValIn + i$Inf_Val_g * i$Inf_Art

#sum of EAA
Abs_EAA_g <- Abs_Arg_g + Abs_His_g + Abs_Ile_g + Abs_Leu_g + Abs_Lys_g +
		Abs_Met_g + Abs_Phe_g + Abs_Thr_g + Abs_Trp_g + Abs_Val_g
Abs_neAA_g <- An_MPIn_g * 1.15 - Abs_EAA_g                          #Absorbed NEAA

#Sum of squared EAA for use in the Milk Protein eqn; correct one is selected in the milk protein section.
#All
Abs_EAA2_g <- Abs_Arg_g^2 + Abs_His_g^2 + Abs_Ile_g^2 + Abs_Leu_g^2 + Abs_Lys_g^2 +
		Abs_Met_g^2 + Abs_Phe_g^2 + Abs_Thr_g^2 + Abs_Trp_g^2 + Abs_Val_g^2
#NRC 2020 (no Arg, Phe, Thr, Trp, or Val)
Abs_EAA2_HILKM_g <- Abs_His_g^2 + Abs_Ile_g^2 + Abs_Leu_g^2 + Abs_Lys_g^2 + Abs_Met_g^2
#Virginia Tech 1 (no Phe, Thr, Trp, or Val)
Abs_EAA2_RHILKM_g <- Abs_Arg_g^2 + Abs_His_g^2 + Abs_Ile_g^2 + Abs_Leu_g^2 + Abs_Lys_g^2 +
		Abs_Met_g^2
#Virginia Tech 2 (no Arg, Phe, Trp, or Val)
Abs_EAA2_HILKMT_g <- Abs_His_g^2 + Abs_Ile_g^2 + Abs_Leu_g^2 + Abs_Lys_g^2 +
     Abs_Met_g^2 + Abs_Thr_g^2

############ AA as a percent of MP - JP ###############
Abs_Arg_MPp<-(Abs_Arg_g/An_MPIn_g)*100
Abs_His_MPp<-(Abs_His_g/An_MPIn_g)*100
Abs_Ile_MPp<-(Abs_Ile_g/An_MPIn_g)*100
Abs_Leu_MPp<-(Abs_Leu_g/An_MPIn_g)*100
Abs_Lys_MPp<-(Abs_Lys_g/An_MPIn_g)*100
Abs_Met_MPp<-(Abs_Met_g/An_MPIn_g)*100
Abs_Phe_MPp<-(Abs_Phe_g/An_MPIn_g)*100
Abs_Thr_MPp<-(Abs_Thr_g/An_MPIn_g)*100
Abs_Trp_MPp<-(Abs_Trp_g/An_MPIn_g)*100
Abs_Val_MPp<-(Abs_Val_g/An_MPIn_g)*100

############ Abs AA as a % of total Abs EAA ###################
Abs_Arg_p <- Abs_Arg_g / Abs_EAA_g * 100
Abs_His_p <- Abs_His_g / Abs_EAA_g * 100
Abs_Ile_p <- Abs_Ile_g / Abs_EAA_g * 100
Abs_Leu_p <- Abs_Leu_g / Abs_EAA_g * 100
Abs_Lys_p <- Abs_Lys_g / Abs_EAA_g * 100
Abs_Met_p <- Abs_Met_g / Abs_EAA_g * 100
Abs_Phe_p <- Abs_Phe_g / Abs_EAA_g * 100
Abs_Thr_p <- Abs_Thr_g / Abs_EAA_g * 100
Abs_Trp_p <- Abs_Trp_g / Abs_EAA_g * 100
Abs_Val_p <- Abs_Val_g / Abs_EAA_g * 100

###################### Abs AA / DEIn ##########################
Abs_Arg_DEI <- Abs_Arg_g / An_DEIn
Abs_His_DEI <- Abs_His_g / An_DEIn
Abs_Ile_DEI <- Abs_Ile_g / An_DEIn
Abs_Leu_DEI <- Abs_Leu_g / An_DEIn
Abs_Lys_DEI <- Abs_Lys_g / An_DEIn
Abs_Met_DEI <- Abs_Met_g / An_DEIn
Abs_Phe_DEI <- Abs_Phe_g / An_DEIn
Abs_Thr_DEI <- Abs_Thr_g / An_DEIn
Abs_Trp_DEI <- Abs_Trp_g / An_DEIn
Abs_Val_DEI <- Abs_Val_g / An_DEIn

#Convert absorbed g of AA to moles of AA/d
Abs_Arg_mol <- Abs_Arg_g / MWArg
Abs_His_mol <- Abs_His_g / MWHis
Abs_Ile_mol <- Abs_Ile_g / MWIle
Abs_Leu_mol <- Abs_Leu_g / MWLeu
Abs_Lys_mol <- Abs_Lys_g / MWLys
Abs_Met_mol <- Abs_Met_g / MWMet
Abs_Phe_mol <- Abs_Phe_g / MWPhe
Abs_Thr_mol <- Abs_Thr_g / MWThr
Abs_Trp_mol <- Abs_Trp_g / MWTrp
Abs_Val_mol <- Abs_Val_g / MWVal


############################################################################################
#                                Absorbed Minerals                                         #
############################################################################################
#Macro Minerals from each ingredient, g/d
f$Fd_acCa <- ifelse(f$An_StatePhys == "Calf" & f$Dt_DMIn_ClfLiq > 0, 1, f$Fd_acCa)      #scalars for An_StatePhys and Dt_DMIn_ClfLiq don't vectorize,
f$Fd_acCa <- ifelse(f$An_StatePhys == "Calf" & f$Dt_DMIn_ClfLiq == 0, 0.60, f$Fd_acCa) #so forced by adding them to the f DF above.
f$Fd_acPtot <- ifelse(f$Fd_Category=="Vitamin/Mineral", f$Fd_acPtot, f$Fd_Pinorg_P*0.0084 + f$Fd_Porg_P*0.0068)
f$Fd_acPtot <- ifelse(f$An_StatePhys == "Calf" & f$Dt_DMIn_ClfLiq > 0, 1, f$Fd_acPtot)
f$Fd_acPtot <- ifelse(f$An_StatePhys == "Calf" & f$Dt_DMIn_ClfLiq == 0, 0.75, f$Fd_acPtot)
f$Fd_acMg <- ifelse(f$An_StatePhys == "Calf" & f$Dt_DMIn_ClfLiq > 0, 1, f$Fd_acMg)
f$Fd_acMg <- ifelse(f$An_StatePhys == "Calf" & f$Dt_DMIn_ClfLiq == 0, 0.26, f$Fd_acMg)
f$Fd_acNa <- ifelse(f$An_StatePhys == "Calf", 1.0, f$Fd_acNa)
f$Fd_acK <- ifelse(f$An_StatePhys == "Calf", 1.0, f$Fd_acK)
f$Fd_acCl <- ifelse(f$An_StatePhys == "Calf" & f$Dt_DMIn_ClfLiq > 0, 1, f$Fd_acCl)
f$Fd_acCl <- ifelse(f$An_StatePhys == "Calf" & f$Dt_DMIn_ClfLiq == 0, 0.92, f$Fd_acCl)

f$Fd_absCaIn <- f$Fd_CaIn*f$Fd_acCa
f$Fd_absPIn <- f$Fd_PIn*f$Fd_acPtot
f$Fd_absMgIn_base <- f$Fd_MgIn*f$Fd_acMg
f$Fd_absNaIn <- f$Fd_NaIn*f$Fd_acNa
f$Fd_absKIn <- f$Fd_KIn*f$Fd_acK
f$Fd_absClIn <- f$Fd_ClIn*f$Fd_acCl

#Micro Minerals from each ingredient, mg/d
#micro requirements for calves are based on dietary concentrations, thus set their absorption coefficient to 1
f$Fd_acCo <- ifelse(f$An_StatePhys == "Calf", 0, 1.0)  #absorption of Co is 0 for calves and 1 for all others.
f$Fd_acCu <- ifelse(f$An_StatePhys == "Calf", 1.0, f$Fd_acCu)
f$Fd_acCu <- ifelse(f$An_StatePhys == "Calf" & f$Dt_DMIn_ClfLiq == 0, 0.10, f$Fd_acCu)
f$Fd_acFe <- ifelse(f$An_StatePhys == "Calf", 1.0, f$Fd_acFe)
f$Fd_acFe <- ifelse(f$An_StatePhys == "Calf" & f$Dt_DMIn_ClfLiq == 0, 0.10, f$Fd_acFe)
f$Fd_acMn <- ifelse(f$An_StatePhys == "Calf", 1.0, f$Fd_acMn)
f$Fd_acMn <- ifelse(f$An_StatePhys == "Calf" & f$Dt_DMIn_ClfLiq == 0, 0.005, f$Fd_acMn)
f$Fd_acZn <- ifelse(f$An_StatePhys == "Calf", 1.0, f$Fd_acZn)
f$Fd_acZn <- ifelse(f$An_StatePhys == "Calf" & f$Dt_DMIn_ClfLiq == 0, 0.20, f$Fd_acZn)

f$Fd_absCoIn <- f$Fd_CoIn*f$Fd_acCo
f$Fd_absCuIn <- f$Fd_CuIn*f$Fd_acCu
f$Fd_absFeIn <- f$Fd_FeIn*f$Fd_acFe
f$Fd_absMnIn <- f$Fd_MnIn*f$Fd_acMn
f$Fd_absZnIn <- f$Fd_ZnIn*f$Fd_acZn

#Total Dietary Absorbed Mineral Intakes, g/d
Abs_CaIn <- sum(f$Fd_absCaIn, na.rm=TRUE)
Abs_PIn <- sum(f$Fd_absPIn, na.rm=TRUE)
Abs_NaIn <- sum(f$Fd_absNaIn, na.rm=TRUE)
Dt_acMg <- ifelse(An_StatePhys=="Calf", 1, (44.1-5.42*log(Dt_K*10)-0.08*Dt_MgIn_min/Dt_MgIn*100)/100)
Abs_MgIn <- Dt_acMg * Dt_MgIn  #Mg absorption is inhibited by K
Abs_KIn <- sum(f$Fd_absKIn, na.rm=TRUE)
Abs_ClIn <- sum(f$Fd_absClIn, na.rm=TRUE)
Abs_CoIn <- sum(f$Fd_absCoIn, na.rm=TRUE)
Abs_CuIn <- sum(f$Fd_absCuIn, na.rm=TRUE)
Abs_FeIn <- sum(f$Fd_absFeIn, na.rm=TRUE)
Abs_MnIn <- sum(f$Fd_absMnIn, na.rm=TRUE)
Abs_ZnIn <- sum(f$Fd_absZnIn, na.rm=TRUE)


########################################################################################################
#                                  Nutrient Utilization                                                #
########################################################################################################
#### AA Composition of Proteins, g hydrated AA/100 g of TP ####
# all were corrected for incomplete recovery during a 24h acid hydrolysis

# Milk Protein AA Composition, g/100 g of TP
Mlk_Arg_TP <- 3.74
Mlk_His_TP <- 2.92
Mlk_Ile_TP <- 6.18
Mlk_Leu_TP <- 10.56
Mlk_Lys_TP <- 8.82
Mlk_Met_TP <- 3.03
Mlk_Phe_TP <- 5.26
Mlk_Thr_TP <- 4.62
Mlk_Trp_TP <- 1.65
Mlk_Val_TP <- 6.90

#Body Protein AA Composition, g/100 g of TP
Body_Arg_TP <- 8.20
Body_His_TP <- 3.04
Body_Ile_TP <- 3.69
Body_Leu_TP <- 8.27
Body_Lys_TP <- 7.90
Body_Met_TP <- 2.37
Body_Phe_TP <- 4.41
Body_Thr_TP <- 4.84
Body_Trp_TP <- 1.05
Body_Val_TP <- 5.15

#Endogenous Urinary Protein AA Composition, g/100 g of TP; these are set equal to body protein AA comp
Ur_ArgEnd_TP <- 8.20
Ur_HisEnd_TP <- 3.04
Ur_IleEnd_TP <- 3.69
Ur_LeuEnd_TP <- 8.27
Ur_LysEnd_TP <- 7.90
Ur_MetEnd_TP <- 2.37
Ur_PheEnd_TP <- 4.41
Ur_ThrEnd_TP <- 4.84
Ur_TrpEnd_TP <- 1.05
Ur_ValEnd_TP <- 5.15

#Metabolic Fecal Protein AA Composition, g/100 g of TP
Fe_ArgMetab_TP <- 5.90
Fe_HisMetab_TP <- 3.54
Fe_IleMetab_TP <- 5.39
Fe_LeuMetab_TP <- 9.19
Fe_LysMetab_TP <- 7.61
Fe_MetMetab_TP <- 1.73
Fe_PheMetab_TP <- 5.28
Fe_ThrMetab_TP <- 7.36
Fe_TrpMetab_TP <- 1.79
Fe_ValMetab_TP <- 7.01

#Scurf Protein AA Composition, g/100 g of TP
Scrf_Arg_TP <- 9.60
Scrf_His_TP <- 1.75
Scrf_Ile_TP <- 2.96
Scrf_Leu_TP <- 6.93
Scrf_Lys_TP <- 5.64
Scrf_Met_TP <- 1.40
Scrf_Phe_TP <- 3.61
Scrf_Thr_TP <- 4.01
Scrf_Trp_TP <- 0.73
Scrf_Val_TP <- 4.66


############################################################################################
#                             Maintenance Export Proteins                                  #
############################################################################################

############## Scurf Protein and AA#
Body_NP_CP <- 0.86    #NP content of all body proteins, g NP/g CP
Scrf_CP_g <- 0.20 * An_BW^0.60
Scrf_CP_g <- ifelse(An_StatePhys == "Calf", 0.219*An_BW^0.60, Scrf_CP_g)
Scrf_NP_g <- Scrf_CP_g * Body_NP_CP
Scrf_NP <- Scrf_NP_g * 0.001
Scrf_N_g <- Scrf_CP_g * 0.16
Scrf_Arg_g <- Scrf_NP_g * Scrf_Arg_TP / 100
Scrf_His_g <- Scrf_NP_g * Scrf_His_TP / 100
Scrf_Ile_g <- Scrf_NP_g * Scrf_Ile_TP / 100
Scrf_Leu_g <- Scrf_NP_g * Scrf_Leu_TP / 100
Scrf_Lys_g <- Scrf_NP_g * Scrf_Lys_TP / 100
Scrf_Met_g <- Scrf_NP_g * Scrf_Met_TP / 100
Scrf_Phe_g <- Scrf_NP_g * Scrf_Phe_TP / 100
Scrf_Thr_g <- Scrf_NP_g * Scrf_Thr_TP / 100
Scrf_Trp_g <- Scrf_NP_g * Scrf_Trp_TP / 100
Scrf_Val_g <- Scrf_NP_g * Scrf_Val_TP / 100

# As a fraction of absorbed
ScrfArg_AbsArg <- Scrf_Arg_g / Abs_Arg_g 
ScrfHis_AbsHis <- Scrf_His_g / Abs_His_g 
ScrfIle_AbsIle <- Scrf_Ile_g / Abs_Ile_g 
ScrfLeu_AbsLeu <- Scrf_Leu_g / Abs_Leu_g 
ScrfLys_AbsLys <- Scrf_Lys_g / Abs_Lys_g 
ScrfMet_AbsMet <- Scrf_Met_g / Abs_Met_g 
ScrfPhe_AbsPhe <- Scrf_Phe_g / Abs_Phe_g 
ScrfThr_AbsThr <- Scrf_Thr_g / Abs_Thr_g 
ScrfTrp_AbsTrp <- Scrf_Trp_g / Abs_Trp_g 
ScrfVal_AbsVal <- Scrf_Val_g / Abs_Val_g 


#### Metabolic Fecal AA (g/d) Predictions ####
Fe_ArgMet_g <- Fe_NPend_g * Fe_ArgMetab_TP / 100
Fe_HisMet_g <- Fe_NPend_g * Fe_HisMetab_TP / 100
Fe_IleMet_g <- Fe_NPend_g * Fe_IleMetab_TP / 100
Fe_LeuMet_g <- Fe_NPend_g * Fe_LeuMetab_TP / 100
Fe_LysMet_g <- Fe_NPend_g * Fe_LysMetab_TP / 100
Fe_MetMet_g <- Fe_NPend_g * Fe_MetMetab_TP / 100
Fe_PheMet_g <- Fe_NPend_g * Fe_PheMetab_TP / 100
Fe_ThrMet_g <- Fe_NPend_g * Fe_ThrMetab_TP / 100
Fe_TrpMet_g <- Fe_NPend_g * Fe_TrpMetab_TP / 100
Fe_ValMet_g <- Fe_NPend_g * Fe_ValMetab_TP / 100

# As a fraction of absorbed
Fe_ArgMet_AbsArg <- Fe_ArgMet_g / Abs_Arg_g 
Fe_HisMet_AbsHis <- Fe_HisMet_g / Abs_His_g 
Fe_IleMet_AbsIle <- Fe_IleMet_g / Abs_Ile_g 
Fe_LeuMet_AbsLeu <- Fe_LeuMet_g / Abs_Leu_g 
Fe_LysMet_AbsLys <- Fe_LysMet_g / Abs_Lys_g 
Fe_MetMet_AbsMet <- Fe_MetMet_g / Abs_Met_g 
Fe_PheMet_AbsPhe <- Fe_PheMet_g / Abs_Phe_g 
Fe_ThrMet_AbsThr <- Fe_ThrMet_g / Abs_Thr_g 
Fe_TrpMet_AbsTrp <- Fe_TrpMet_g / Abs_Trp_g 
Fe_ValMet_AbsVal <- Fe_ValMet_g / Abs_Val_g 

#### Urinary Endogenous N, CP, and AA (g/d) Predictions ####
Ur_Nend_Urea_g <- 0.010 * An_BW              #endogenous urea N, g/d
Ur_Nend_Creatn_g <- 0.00946 * An_BW          #endogenous creatinine N, g/d
Ur_Nend_Creat_g <- Ur_Nend_Creatn_g * 0.37   #endogenous creatine N, g/d
Ur_Nend_PD_g <- 0.0271 * An_BW^0.75          #endogenous purine derivative N, g/d
fN_3MH = (3*14)/169
Ur_NPend_3MH_g <- (7.84+0.55*An_BW)/1000      #endogenous 3-methyl-histidine NP, g/d
Ur_Nend_3MH_g <- Ur_NPend_3MH_g * fN_3MH 
Ur_Nend_sum_g <- (Ur_Nend_Urea_g + Ur_Nend_Creatn_g + Ur_Nend_Creat_g +Ur_Nend_PD_g + 
                         Ur_Nend_3MH_g)/(1-0.46)
Ur_Nend_Hipp_g <- Ur_Nend_sum_g * 0.46             #46% of the total end is hippuric acid

Ur_Nend_g <- 0.053 * An_BW                    #approximates Ur_Nend_sum
Ur_NPend_g <- Ur_Nend_g * 6.25
Ur_NPend_g <- ifelse(An_StatePhys == "Calf", 2.75*An_BW^0.50, Ur_NPend_g )  #Calf
Ur_NPend <- Ur_NPend_g * 0.001
Ur_MPend <- Ur_NPend
Ur_EAAend_g <- 0.010 * 6.25 * An_BW  #includes only the MP-EAA used for urea and 3-MHis.

Ur_ArgEnd_g <- Ur_EAAend_g * Ur_ArgEnd_TP / 100
Ur_HisEnd_g <- Ur_EAAend_g * Ur_HisEnd_TP / 100 + Ur_NPend_3MH_g #Urea plus 3-MHis
Ur_IleEnd_g <- Ur_EAAend_g * Ur_IleEnd_TP / 100
Ur_LeuEnd_g <- Ur_EAAend_g * Ur_LeuEnd_TP / 100
Ur_LysEnd_g <- Ur_EAAend_g * Ur_LysEnd_TP / 100
Ur_MetEnd_g <- Ur_EAAend_g * Ur_MetEnd_TP / 100
Ur_PheEnd_g <- Ur_EAAend_g * Ur_PheEnd_TP / 100
Ur_ThrEnd_g <- Ur_EAAend_g * Ur_ThrEnd_TP / 100
Ur_TrpEnd_g <- Ur_EAAend_g * Ur_TrpEnd_TP / 100
Ur_ValEnd_g <- Ur_EAAend_g * Ur_ValEnd_TP / 100

# As a fraction of absorbed
Ur_ArgEnd_AbsArg <- Ur_ArgEnd_g / Abs_Arg_g 
Ur_HisEnd_AbsHis <- Ur_HisEnd_g / Abs_His_g 
Ur_IleEnd_AbsIle <- Ur_IleEnd_g / Abs_Ile_g 
Ur_LeuEnd_AbsLeu <- Ur_LeuEnd_g / Abs_Leu_g 
Ur_LysEnd_AbsLys <- Ur_LysEnd_g / Abs_Lys_g 
Ur_MetEnd_AbsMet <- Ur_MetEnd_g / Abs_Met_g 
Ur_PheEnd_AbsPhe <- Ur_PheEnd_g / Abs_Phe_g 
Ur_ThrEnd_AbsThr <- Ur_ThrEnd_g / Abs_Thr_g 
Ur_TrpEnd_AbsTrp <- Ur_TrpEnd_g / Abs_Trp_g 
Ur_ValEnd_AbsVal <- Ur_ValEnd_g / Abs_Val_g 

Ur_EAAEnd_g <- Ur_ArgEnd_g + Ur_HisEnd_g + Ur_IleEnd_g + Ur_LeuEnd_g + 
	Ur_LysEnd_g + Ur_MetEnd_g + Ur_PheEnd_g + Ur_ThrEnd_g + Ur_TrpEnd_g + 
	Ur_ValEnd_g 

An_NPm_Use <- Scrf_NP_g + Fe_NPend_g + Ur_NPend_g
An_CPm_Use <- Scrf_CP_g + Fe_CPend_g + Ur_NPend_g

############################################################################################
#                    Milk protein and AA output                                            #
############################################################################################
#mPrt_eqn <- 2 #0 for target milk protein, 1 for NRC 2020 prediction, 2 for VT prediction
mPrt_parmset <- mPrt_eqn
if(mPrt_parmset == 0) {mPrt_parmset <- 1} #Trap 0 choice as used to select from the parameters vector

#NRC derived Coefficients from Dec. 20, 2020 solutions. AIC=10,631
#VT1 derived Coefficients from Dec. 20, 2020 solutions. AIC=10,629
#VT2 derived Coefficients from April, 2022 solutions after further data cleaning, AIC=10,405. In publication.
#Source copies of the mPrt equation coefficients (NRC, VT1, VT2)
#                       NRC,   VT1,     VT2
mPrt_Int_src <-      c(-97.0, -141,     -73.7) 
mPrt_k_BW_src <-     c(-0.4201,-0.4146, -.3663)
mPrt_k_DEInp_src <-  c(10.79,  10.65,   0)
mPrt_k_DigNDF_src <- c(-4.595, -4.62,   0)
mPrt_k_DEIn_StFA_src <-  c(0,  0,       10.87)         #DEStIn + DErOMIn + DEFAIn
mPrt_k_DEIn_NDF_src <-  c(0,   0,       5.43)          #DENDFIn
mPrt_k_Arg_src <-    c(0,      0.8175,  0)
mPrt_k_His_src <-    c(1.675,  1.641,   1.19)	
mPrt_k_Ile_src <-    c(0.885,  0.837,   1.08)
mPrt_k_Leu_src <-    c(0.466,  0.623,   0.238)
mPrt_k_Lys_src <-    c(1.153,  1.235,   1.08)	
mPrt_k_Met_src <-    c(1.839,  1.846,   1.91)
mPrt_k_Phe_src <-    c(0,      0,       0)
mPrt_k_Thr_src <-    c(0,      0,       1.36)
mPrt_k_Trp_src <-    c(0.0,    0,       0)
mPrt_k_Val_src <-    c(0,      0,       0)
mPrt_k_NEAA_src <-   c(0,      0.0925,  0.075)         #NEAA.  Phe, Thr, Trp, and Val not considered.
mPrt_k_OthAA_src <-  c(0.0773, 0,       0)             #NEAA + unused EAA.  Added for NRC eqn without Arg as slightly superior.
mPrt_k_EAA2_src <- c(-0.00215, -0.002451, -0.00175)    #for utilized EAA only
mPrt_Int <- mPrt_Int_src[mPrt_parmset]  #Use mPrt_eqn to select the desired parameters
mPrt_k_BW <- mPrt_k_BW_src[mPrt_parmset]
mPrt_k_DEInp <- mPrt_k_DEInp_src[mPrt_parmset]         #NRC 2021 and VT 2020 Equations
mPrt_k_DigNDF <- mPrt_k_DigNDF_src[mPrt_parmset]
mPrt_k_DEIn_StFA <- mPrt_k_DEIn_StFA_src[mPrt_parmset] #VT 2022 Equation
mPrt_k_DEIn_NDF <- mPrt_k_DEIn_NDF_src[mPrt_parmset]
mPrt_k_NEAA <- mPrt_k_NEAA_src[mPrt_parmset]
mPrt_k_OthAA <- mPrt_k_OthAA_src[mPrt_parmset]
#Select the correct sum of square EAA term
Abs_EAA2b_g <- Abs_EAA2_HILKM_g  #NRC eqn.
if(mPrt_eqn == 2){Abs_EAA2b_g <- Abs_EAA2_RHILKM_g}  #VT1 eqn.
if(mPrt_eqn == 3){Abs_EAA2b_g <- Abs_EAA2_HILKMT_g}  #VT2 eqn.
#following is specific to NRC 2021 eqn
Abs_OthAA_g <- Abs_neAA_g + Abs_Arg_g + Abs_Phe_g + Abs_Thr_g + Abs_Trp_g + Abs_Val_g #NRC eqn only.

################### Calculations to Allow Scaling of the Milk Protein Quadratics ###################
#Scale the maximum EAA responses to accommodate high genetic merit herds.  See description of qn by Hanigan et al. 
#An_305RHA_MlkNP is 305 mlk NP value passed to the model (280 kg/305d = no adjustment). Doubling,  doubles max mPrt output.
K_305RHA_MlkTP = 1.0 #A scalar to adjust the slope if needed.  Assumed to be 1. MDH
f_mPrt_max <- 1.0 + K_305RHA_MlkTP * (An_305RHA_MlkTP/280 - 1)  #280kg RHA ~ 930 g mlk NP/d herd average
mPrtmx_Arg <- -mPrt_k_Arg_src[mPrt_parmset]^2/(4*mPrt_k_EAA2_src[mPrt_parmset])	#maximum milk protein responses from each AA
mPrtmx_His <- -mPrt_k_His_src[mPrt_parmset]^2/(4*mPrt_k_EAA2_src[mPrt_parmset])
mPrtmx_Ile <- -mPrt_k_Ile_src[mPrt_parmset]^2/(4*mPrt_k_EAA2_src[mPrt_parmset])
mPrtmx_Leu <- -mPrt_k_Leu_src[mPrt_parmset]^2/(4*mPrt_k_EAA2_src[mPrt_parmset])
mPrtmx_Lys <- -mPrt_k_Lys_src[mPrt_parmset]^2/(4*mPrt_k_EAA2_src[mPrt_parmset])
mPrtmx_Met <- -mPrt_k_Met_src[mPrt_parmset]^2/(4*mPrt_k_EAA2_src[mPrt_parmset])
mPrtmx_Phe <- -mPrt_k_Phe_src[mPrt_parmset]^2/(4*mPrt_k_EAA2_src[mPrt_parmset])
mPrtmx_Thr <- -mPrt_k_Thr_src[mPrt_parmset]^2/(4*mPrt_k_EAA2_src[mPrt_parmset])
mPrtmx_Trp <- -mPrt_k_Trp_src[mPrt_parmset]^2/(4*mPrt_k_EAA2_src[mPrt_parmset])
mPrtmx_Val <- -mPrt_k_Val_src[mPrt_parmset]^2/(4*mPrt_k_EAA2_src[mPrt_parmset])
Arg_mPrtmx <- -mPrt_k_Arg_src[mPrt_parmset]/(2*mPrt_k_EAA2_src[mPrt_parmset])	#AA input at maximum milk protein response for each AA
His_mPrtmx <- -mPrt_k_His_src[mPrt_parmset]/(2*mPrt_k_EAA2_src[mPrt_parmset])
Ile_mPrtmx <- -mPrt_k_Ile_src[mPrt_parmset]/(2*mPrt_k_EAA2_src[mPrt_parmset])
Leu_mPrtmx <- -mPrt_k_Leu_src[mPrt_parmset]/(2*mPrt_k_EAA2_src[mPrt_parmset])
Lys_mPrtmx <- -mPrt_k_Lys_src[mPrt_parmset]/(2*mPrt_k_EAA2_src[mPrt_parmset])
Met_mPrtmx <- -mPrt_k_Met_src[mPrt_parmset]/(2*mPrt_k_EAA2_src[mPrt_parmset])
Phe_mPrtmx <- -mPrt_k_Phe_src[mPrt_parmset]/(2*mPrt_k_EAA2_src[mPrt_parmset])
Thr_mPrtmx <- -mPrt_k_Thr_src[mPrt_parmset]/(2*mPrt_k_EAA2_src[mPrt_parmset])
Trp_mPrtmx <- -mPrt_k_Trp_src[mPrt_parmset]/(2*mPrt_k_EAA2_src[mPrt_parmset])
Val_mPrtmx <- -mPrt_k_Val_src[mPrt_parmset]/(2*mPrt_k_EAA2_src[mPrt_parmset])

mPrt_Arg_0.1 <- Arg_mPrtmx*0.1*mPrt_k_Arg_src[mPrt_parmset] + (Arg_mPrtmx*0.1)^2*mPrt_k_EAA2_src[mPrt_parmset]	#Milk prt from each EAA
mPrt_His_0.1 <- His_mPrtmx*0.1*mPrt_k_His_src[mPrt_parmset] + (His_mPrtmx*0.1)^2*mPrt_k_EAA2_src[mPrt_parmset]	#at 10% of Max response
mPrt_Ile_0.1 <- Ile_mPrtmx*0.1*mPrt_k_Ile_src[mPrt_parmset] + (Ile_mPrtmx*0.1)^2*mPrt_k_EAA2_src[mPrt_parmset]
mPrt_Leu_0.1 <- Leu_mPrtmx*0.1*mPrt_k_Leu_src[mPrt_parmset] + (Leu_mPrtmx*0.1)^2*mPrt_k_EAA2_src[mPrt_parmset]
mPrt_Lys_0.1 <- Lys_mPrtmx*0.1*mPrt_k_Lys_src[mPrt_parmset] + (Lys_mPrtmx*0.1)^2*mPrt_k_EAA2_src[mPrt_parmset]
mPrt_Met_0.1 <- Met_mPrtmx*0.1*mPrt_k_Met_src[mPrt_parmset] + (Met_mPrtmx*0.1)^2*mPrt_k_EAA2_src[mPrt_parmset]
mPrt_Phe_0.1 <- Phe_mPrtmx*0.1*mPrt_k_Phe_src[mPrt_parmset] + (Phe_mPrtmx*0.1)^2*mPrt_k_EAA2_src[mPrt_parmset]
mPrt_Thr_0.1 <- Thr_mPrtmx*0.1*mPrt_k_Thr_src[mPrt_parmset] + (Thr_mPrtmx*0.1)^2*mPrt_k_EAA2_src[mPrt_parmset]
mPrt_Trp_0.1 <- Trp_mPrtmx*0.1*mPrt_k_Trp_src[mPrt_parmset] + (Trp_mPrtmx*0.1)^2*mPrt_k_EAA2_src[mPrt_parmset]
mPrt_Val_0.1 <- Val_mPrtmx*0.1*mPrt_k_Val_src[mPrt_parmset] + (Val_mPrtmx*0.1)^2*mPrt_k_EAA2_src[mPrt_parmset]

mPrtmx_Arg2 <- mPrtmx_Arg*f_mPrt_max
mPrtmx_His2 <- mPrtmx_His*f_mPrt_max
mPrtmx_Ile2 <- mPrtmx_Ile*f_mPrt_max
mPrtmx_Leu2 <- mPrtmx_Leu*f_mPrt_max
mPrtmx_Lys2 <- mPrtmx_Lys*f_mPrt_max
mPrtmx_Met2 <- mPrtmx_Met*f_mPrt_max
mPrtmx_Phe2 <- mPrtmx_Phe*f_mPrt_max
mPrtmx_Thr2 <- mPrtmx_Thr*f_mPrt_max
mPrtmx_Trp2 <- mPrtmx_Trp*f_mPrt_max
mPrtmx_Val2 <- mPrtmx_Val*f_mPrt_max

#Calculate new scaled linear EAA coeff and a common squared coefficient
mPrt_k_Arg <- -(2*sqrt(mPrtmx_Arg2^2-mPrt_Arg_0.1*mPrtmx_Arg2)-2*mPrtmx_Arg2)/(Arg_mPrtmx*0.1)
mPrt_k_His <- -(2*sqrt(mPrtmx_His2^2-mPrt_His_0.1*mPrtmx_His2)-2*mPrtmx_His2)/(His_mPrtmx*0.1)
mPrt_k_Ile <- -(2*sqrt(mPrtmx_Ile2^2-mPrt_Ile_0.1*mPrtmx_Ile2)-2*mPrtmx_Ile2)/(Ile_mPrtmx*0.1)
mPrt_k_Leu <- -(2*sqrt(mPrtmx_Leu2^2-mPrt_Leu_0.1*mPrtmx_Leu2)-2*mPrtmx_Leu2)/(Leu_mPrtmx*0.1)
mPrt_k_Lys <- -(2*sqrt(mPrtmx_Lys2^2-mPrt_Lys_0.1*mPrtmx_Lys2)-2*mPrtmx_Lys2)/(Lys_mPrtmx*0.1)
mPrt_k_Met <- -(2*sqrt(mPrtmx_Met2^2-mPrt_Met_0.1*mPrtmx_Met2)-2*mPrtmx_Met2)/(Met_mPrtmx*0.1)
mPrt_k_Phe <- -(2*sqrt(mPrtmx_Phe2^2-mPrt_Phe_0.1*mPrtmx_Phe2)-2*mPrtmx_Phe2)/(Phe_mPrtmx*0.1)
mPrt_k_Thr <- -(2*sqrt(mPrtmx_Thr2^2-mPrt_Thr_0.1*mPrtmx_Thr2)-2*mPrtmx_Thr2)/(Thr_mPrtmx*0.1)
mPrt_k_Trp <- -(2*sqrt(mPrtmx_Trp2^2-mPrt_Trp_0.1*mPrtmx_Trp2)-2*mPrtmx_Trp2)/(Trp_mPrtmx*0.1)
mPrt_k_Val <- -(2*sqrt(mPrtmx_Val2^2-mPrt_Val_0.1*mPrtmx_Val2)-2*mPrtmx_Val2)/(Val_mPrtmx*0.1)
#Convert NA to 0
mPrt_k_Arg <- ifelse(is.na(mPrt_k_Arg),0,mPrt_k_Arg)
mPrt_k_His <- ifelse(is.na(mPrt_k_His),0,mPrt_k_His)
mPrt_k_Ile <- ifelse(is.na(mPrt_k_Ile),0,mPrt_k_Ile)
mPrt_k_Leu <- ifelse(is.na(mPrt_k_Leu),0,mPrt_k_Leu)
mPrt_k_Lys <- ifelse(is.na(mPrt_k_Lys),0,mPrt_k_Lys)
mPrt_k_Met <- ifelse(is.na(mPrt_k_Met),0,mPrt_k_Met)
mPrt_k_Phe <- ifelse(is.na(mPrt_k_Phe),0,mPrt_k_Phe)
mPrt_k_Thr <- ifelse(is.na(mPrt_k_Thr),0,mPrt_k_Thr)
mPrt_k_Trp <- ifelse(is.na(mPrt_k_Trp),0,mPrt_k_Trp)
mPrt_k_Val <- ifelse(is.na(mPrt_k_Val),0,mPrt_k_Val)

#Scale the quadratic; can be calculated from any of the AA included in the squared term. All give the same answer
mPrt_k_EAA2 <- (2*sqrt(mPrtmx_Met2^2-mPrt_Met_0.1*mPrtmx_Met2)-2*mPrtmx_Met2+mPrt_Met_0.1)/(Met_mPrtmx*0.1)^2

#Predict net protein output in milk
Mlk_NP_g <- mPrt_Int + Abs_Arg_g*mPrt_k_Arg + Abs_His_g*mPrt_k_His + Abs_Ile_g*mPrt_k_Ile + 
	Abs_Leu_g*mPrt_k_Leu + Abs_Lys_g*mPrt_k_Lys + Abs_Met_g*mPrt_k_Met + Abs_Phe_g*mPrt_k_Phe +
	Abs_Thr_g*mPrt_k_Thr + Abs_Trp_g*mPrt_k_Trp + Abs_Val_g*mPrt_k_Val + Abs_neAA_g*mPrt_k_NEAA +
     Abs_OthAA_g*mPrt_k_OthAA + Abs_EAA2b_g*mPrt_k_EAA2 + An_DEInp*mPrt_k_DEInp + (An_DigNDF-17.06)*mPrt_k_DigNDF + 
     (An_DEStIn+An_DEFAIn+An_DErOMIn)*mPrt_k_DEIn_StFA + An_DENDFIn*mPrt_k_DEIn_NDF + (An_BW-612)*mPrt_k_BW 
     #BW and DigNDF were centered for the regression
    							 
#Calculate the maximal milk protein output at the entered DE, DigNDF, and BW.
Mlk_NPmx <- mPrt_Int + mPrtmx_Arg2 + mPrtmx_His2 + mPrtmx_Ile2 + mPrtmx_Leu2 + mPrtmx_Lys2 + 
     mPrtmx_Met2 + mPrtmx_Thr2 + mPrtmx_Val2 + An_DEInp*mPrt_k_DEInp + (An_DigNDF-17.06)*mPrt_k_DigNDF + 
     (An_BW-612)*mPrt_k_BW + Abs_neAA_g*mPrt_k_NEAA + Abs_OthAA_g*mPrt_k_OthAA

#Calculate predicted Mlk_NP as proportion of max mPrt for reporting purposes.
#This value should not exceed ~0.8 for an 18% CP diet with ~60% MP for peak production. (0.8 needs refinement)
#If it does, this is an indication that the genetic potential scalar, f_mPrt_max, is set too low.
MlkNP_MlkNPmx <- Mlk_NP_g / Mlk_NPmx

Mlk_NP_g <- ifelse(An_StatePhys == "Lactating Cow", Mlk_NP_g, 0)
Trg_Mlk_NP_g <- Trg_MilkProd*1000 * Trg_MilkTPp/100
Trg_Mlk_NP <- Trg_Mlk_NP_g/1000

if(mPrt_eqn==0) {Mlk_NP_g <- Trg_Mlk_NP_g} #Select Trg_MilkTP or predicted Mlk_NP for remaining calcs.
An_SWlact <- ifelse(Mlk_NP_g > 0, 1, 0)	#Detect lactation and set a switch for use with other eqns.
Mlk_NP <- Mlk_NP_g /1000 #kg NP/d

Mlk_CP_g <- Mlk_NP_g / 0.95
Mlk_CP <- Mlk_CP_g / 1000

#Calculate AA outputs in milk protein
Mlk_Arg_g <- Mlk_NP_g * Mlk_Arg_TP / 100
Mlk_His_g <- Mlk_NP_g * Mlk_His_TP / 100
Mlk_Ile_g <- Mlk_NP_g * Mlk_Ile_TP / 100
Mlk_Leu_g <- Mlk_NP_g * Mlk_Leu_TP / 100
Mlk_Lys_g <- Mlk_NP_g * Mlk_Lys_TP / 100
Mlk_Met_g <- Mlk_NP_g * Mlk_Met_TP / 100
Mlk_Phe_g <- Mlk_NP_g * Mlk_Phe_TP / 100
Mlk_Thr_g <- Mlk_NP_g * Mlk_Thr_TP / 100
Mlk_Trp_g <- Mlk_NP_g * Mlk_Trp_TP / 100
Mlk_Val_g <- Mlk_NP_g * Mlk_Val_TP / 100
Mlk_EAA_g <- Mlk_Arg_g + Mlk_His_g + Mlk_Ile_g + Mlk_Leu_g + Mlk_Lys_g + Mlk_Met_g + Mlk_Phe_g + Mlk_Thr_g + Mlk_Trp_g + Mlk_Val_g
### Calculate Predicted Gross efficiencies of Use of AA for Milk Protein ###
#Milk Protein Efficiency,  as a fraction of Absorbed
MlkNP_AnMP <- Mlk_NP_g / An_MPIn_g 
MlkArg_AbsArg <- Mlk_Arg_g / Abs_Arg_g 
MlkHis_AbsHis <- Mlk_His_g / Abs_His_g 
MlkIle_AbsIle <- Mlk_Ile_g / Abs_Ile_g 
MlkLeu_AbsLeu <- Mlk_Leu_g / Abs_Leu_g 
MlkLys_AbsLys <- Mlk_Lys_g / Abs_Lys_g 
MlkMet_AbsMet <- Mlk_Met_g / Abs_Met_g 
MlkPhe_AbsPhe <- Mlk_Phe_g / Abs_Phe_g 
MlkThr_AbsThr <- Mlk_Thr_g / Abs_Thr_g 
MlkTrp_AbsTrp <- Mlk_Trp_g / Abs_Trp_g 
MlkVal_AbsVal <- Mlk_Val_g / Abs_Val_g 
MlkEAA_AbsEAA <- Mlk_EAA_g / Abs_EAA_g
#Predicted Gross Milk Protein Efficiency, g/g in the diet
MlkNP_AnCP <- Mlk_NP_g / (An_CPIn*1000)
MlkArg_DtArg <- Mlk_Arg_g / Dt_ArgIn 
MlkHis_DtHis <- Mlk_His_g / Dt_HisIn 
MlkIle_DtIle <- Mlk_Ile_g / Dt_IleIn 
MlkLeu_DtLeu <- Mlk_Leu_g / Dt_LeuIn 
MlkLys_DtLys <- Mlk_Lys_g / Dt_LysIn 
MlkMet_DtMet <- Mlk_Met_g / Dt_MetIn 
MlkPhe_DtPhe <- Mlk_Phe_g / Dt_PheIn 
MlkThr_DtThr <- Mlk_Thr_g / Dt_ThrIn 
MlkTrp_DtTrp <- Mlk_Trp_g / Dt_TrpIn 
MlkVal_DtVal <- Mlk_Val_g / Dt_ValIn 


############################################################################################
#                            Milk Fat Predictions from Daley et al.                        #
############################################################################################
An_LactDay_MlkPred <- ifelse(An_LactDay <= 375, An_LactDay, 375)  #Cap DIM at 375 d to prevent the polynomial from getting out of range.
Mlk_Fatemp_g <- 453 - 1.42*An_LactDay_MlkPred + 24.52*(Dt_DMIn-Dt_FAIn) + 0.41*Dt_DigC160In*1000 + 
	1.80*Dt_DigC183In*1000 + 1.45 * Abs_Ile_g + 1.34*Abs_Met_g
Mlk_Fatemp_g <- ifelse(An_StatePhys == "Lactating Cow", Mlk_Fatemp_g, 0)
Trg_Mlk_Fat <- Trg_MilkProd * Trg_MilkFatp/100
Trg_Mlk_Fat_g <- Trg_Mlk_Fat * 1000

#Select Trg_MilkFat or predicted Mlk_Fat for remaining calcs.
Mlk_Fat_g <- ifelse(mFat_eqn==0, Trg_Mlk_Fat_g, Mlk_Fatemp_g)
Mlk_Fat <- Mlk_Fat_g / 1000	

#need to add calculations of milk fat output of each FA and the efficiency of conversion

################################################################################################
# Milk volume predictions from target or predicted milk protein, milk fat, BW, DIM, and Parity #
################################################################################################
#Component based milk production prediction; derived by regression from predicted milk protein and milk fat.
Mlk_Prod_comp <- 4.541 + 11.13*Mlk_NP + 2.648*Mlk_Fat + 0.1829 * An_DEIn - 0.06257*(An_LactDay_MlkPred-137.1) + 
	     2.766e-4*(An_LactDay_MlkPred-137.1)^2 + 1.603e-6*(An_LactDay_MlkPred-137.1)^3 - 7.397e-9*(An_LactDay_MlkPred-137.1)^4 + 
     1.567*(An_Parity_rl-1)  #Holstein equation
Mlk_Prod_comp <- ifelse(An_Breed == "Jersey", Mlk_Prod_comp - 3.400, Mlk_Prod_comp)
Mlk_Prod_comp <- ifelse(An_Breed != "Jersey" & An_Breed != "Holstein", Mlk_Prod_comp - 1.526, Mlk_Prod_comp)

#Milk production from component predictions or as entered by the user
Mlk_Prod <- ifelse(An_StatePhys == "Lactating Cow" & mProd_eqn==1, Mlk_Prod_comp, Trg_MilkProd)


############################################################################################
#                        Gestation Energy, NP, and AA Use                                  #
############################################################################################
#Gravid Uterus Composition from the predicted composition at d283 of gestation after the model of Koong et. 1975
#was fit to the composition data of Bell, 1995 and House and Bell, 1993. See Hanigan et al., 2009 for
#a description of the general approach as applied in the Molly model.

#Create a pregnancy switch for use in calculations.
An_Preg <- ifelse(An_GestDay > 0 & An_GestDay <= An_GestLength, 1, 0)

GrUterWt_FetBWbrth <- 1.816	#kg of Gravid Uterus/kg of calf birth weight based on 280 d gestation and Bell solutions.
UterWt_FetBWbrth <- 0.2311;	#kg Maternal Tissue/kg calf weight at parturition from fits to Bell 1995 data
#*# NE_GrUtWt <- 0.950;		#mcal/kg fresh Gravid Uterus weight at birth which represents the accumulated values
CP_GrUtWt <- 0.123;		#kg CP/kg fresh Gr Uterus weight

#Gravid uterine, fetal, and uterine (+cotyledons) growth rate constants derived from Bell data
#An_GestDay=0 shuts this section off.
GrUter_Ksyn <- 2.43e-2
GrUter_KsynDecay <- 2.45e-5
Fet_Ksyn <- 5.16e-2
Fet_KsynDecay <- 7.59e-5
Uter_Ksyn <- 2.42e-2		#Derived from Maternal Tissue data by Hanigan et al., 2009
Uter_KsynDecay <- 3.53e-5
Uter_Kdeg <- 0.20			#Estimate from Hanigan et al, 2009

#Estimate Maternal Tisue weight (uterus plus caruncles) at any time
Uter_Wtpart <- Fet_BWbrth * UterWt_FetBWbrth
Uter_Wt <- 0.204  #Nonpregnant uterine base weight; ideally would be scaled to BW/BWmature, but a small error for young animals
Uter_Wt <- ifelse(An_AgeDay < 240, 0, Uter_Wt)  #Set Uter_Wt to 0 for young animals
Uter_Wt <- ifelse(An_GestDay > 0 & An_GestDay <= An_GestLength,  #gestating animal
          Uter_Wtpart * exp(-(Uter_Ksyn-Uter_KsynDecay*An_GestDay)*(An_GestLength-An_GestDay)), Uter_Wt)
Uter_Wt <- ifelse(An_GestDay <= 0 & An_LactDay > 0 & An_LactDay < 100, #uterine involution after calving
          ((Uter_Wtpart-0.204)*exp(-Uter_Kdeg*An_LactDay))+0.204, Uter_Wt)	#LactDay should start at 1, not 0
Uter_Wt <- ifelse(An_Parity_rl > 0 & Uter_Wt < 0.204, 0.204, Uter_Wt)  #Set the min to 0.204.  Should be scaled to BW, but no data.
#The above needs to be looked at again.  It doesn't converge back to 0.204 as it should when using the Bell et al. birth weights.  Close but not exact.  Perhaps rounding error, but not sure. MDH

#Estimate Gravid Uterine weight at any time
GrUter_Wtpart <- Fet_BWbrth * GrUterWt_FetBWbrth
GrUter_Wt <- Uter_Wt                                               #non-pregnant animal
GrUter_Wt <- ifelse(An_GestDay > 0 & An_GestDay <= An_GestLength,  #gestating animal
          GrUter_Wtpart * exp(-(GrUter_Ksyn-GrUter_KsynDecay*An_GestDay)*(An_GestLength-An_GestDay)),
          GrUter_Wt)
GrUter_Wt <- ifelse(GrUter_Wt < Uter_Wt, Uter_Wt, GrUter_Wt)  #Shouldn't need this, but just in case, trap bad values

#Estimate Fetal weight at any time
Fet_Wt <- 0                                                     #open animal
Fet_Wt <- ifelse(An_GestDay > 0 & An_GestDay <= An_GestLength,  #gestating animal
                 Fet_BWbrth * exp(-(Fet_Ksyn-Fet_KsynDecay*An_GestDay)*(An_GestLength-An_GestDay)), Fet_Wt)

#Estimate rates of fresh tissue growth for the Gravid Uterus, Maternal Repro Tissue, and the Fetus
Uter_BWgain <- 0  #Open and nonregressing animal
Uter_BWgain <- ifelse(An_GestDay > 0 & An_GestDay <= An_GestLength,  #gestating animal
                      (Uter_Ksyn - Uter_KsynDecay * An_GestDay) * Uter_Wt, Uter_BWgain)
Uter_BWgain <- ifelse(An_GestDay <= 0 & An_LactDay > 0 & An_LactDay < 100, #uterine involution after calving
                      -Uter_Kdeg*Uter_Wt, Uter_BWgain)	#kg/d

GrUter_BWgain <- 0       #open animal and nonregressing, kg fresh wt/d
GrUter_BWgain <- ifelse(An_GestDay > 0 & An_GestDay <= An_GestLength,  #gestating animal
                     (GrUter_Ksyn-GrUter_KsynDecay*An_GestDay)*GrUter_Wt, GrUter_BWgain)
GrUter_BWgain <- ifelse(An_GestDay <= 0 & An_LactDay > 0 & An_LactDay < 100, #uterine involution after calving
                    Uter_BWgain, GrUter_BWgain)
Fet_BWgain <- 0	#open animal, kg/d
Fet_BWgain <- ifelse(An_GestDay > 0 & An_GestDay <= An_GestLength, #gestating animal
                    (Fet_Ksyn-Fet_KsynDecay*An_GestDay)*Fet_Wt, Fet_BWgain)
Conc_BWgain <- GrUter_BWgain - Uter_BWgain

#Net protein gain in other maternal tissues during late gestation: mammary, intestine, liver, and blood
#this should be replaced with a growth funncton such as Dijkstra's mammary growth equation. MDH.
Gest_NPother_g <- 0
#Gest_CPother_g <- ifelse(An_GestDay>=260, 0.135*6.25*An_MBW,0) #Causes a big jump when it turns on at 260 days pregnant.  Not used.
#0.135 g/kg is the mean of values from McNeill et al. 1997 and Putnam and Varga, 1998.
#Gest_NPother_g <- Gest_CPother_g * Body_NP_CP
	#Body_NP_CP is the conversion of CP to TP.

#### Gestation Energy ####
#*# Gest_REgain <- GrUter_BWgain * NE_GrUtWt;	#This will slightly underestimate release of NE from the regressing uterus

#### Estimate net rates of NP (g/d), and AA (g/d) deposition in the Gravid uterus ####
Gest_NCPgain_g <- GrUter_BWgain * CP_GrUtWt * 1000
Gest_NPgain_g <- Gest_NCPgain_g * Body_NP_CP;	#Will slightly underestimate release of NP from the regressing uterus
Gest_NPuse_g <- Gest_NPgain_g + Gest_NPother_g
Gest_CPuse_g <- Gest_NPuse_g/Body_NP_CP
Gest_Arg_g <- Gest_NPuse_g * Body_Arg_TP / 100
Gest_His_g <- Gest_NPuse_g * Body_His_TP / 100
Gest_Ile_g <- Gest_NPuse_g * Body_Ile_TP / 100
Gest_Leu_g <- Gest_NPuse_g * Body_Leu_TP / 100
Gest_Lys_g <- Gest_NPuse_g * Body_Lys_TP / 100
Gest_Met_g <- Gest_NPuse_g * Body_Met_TP / 100
Gest_Phe_g <- Gest_NPuse_g * Body_Phe_TP / 100
Gest_Thr_g <- Gest_NPuse_g * Body_Thr_TP / 100
Gest_Trp_g <- Gest_NPuse_g * Body_Trp_TP / 100
Gest_Val_g <- Gest_NPuse_g * Body_Val_TP / 100
Gest_EAA_g <- Gest_Arg_g + Gest_His_g + Gest_Ile_g + Gest_Leu_g + Gest_Lys_g + Gest_Met_g + Gest_Phe_g +
     Gest_Thr_g + Gest_Trp_g + Gest_Val_g

#Gest net deposition, g/g absorbed
GestArg_AbsArg <- Gest_Arg_g / Abs_Arg_g 
GestHis_AbsHis <- Gest_His_g / Abs_His_g 
GestIle_AbsIle <- Gest_Ile_g / Abs_Ile_g 
GestLeu_AbsLeu <- Gest_Leu_g / Abs_Leu_g 
GestLys_AbsLys <- Gest_Lys_g / Abs_Lys_g 
GestMet_AbsMet <- Gest_Met_g / Abs_Met_g 
GestPhe_AbsPhe <- Gest_Phe_g / Abs_Phe_g 
GestThr_AbsThr <- Gest_Thr_g / Abs_Thr_g 
GestTrp_AbsTrp <- Gest_Trp_g / Abs_Trp_g 
GestVal_AbsVal <- Gest_Val_g / Abs_Val_g 

############################################################################################
#                           Body Weight, Body Comp, and BW gain                            #
############################################################################################
BW_BCS <- 0.094 * An_BW  #Each BCS represents 94 g of weight per kg of BW
An_BWnp <- An_BW - GrUter_Wt  #Non-pregnant BW
An_BWnp3 <- An_BWnp / (1 + 0.094*(An_BCS - 3)) #BWnp standardized to BCS of 3 using 9.4% of BW/unit of BCS

#### Calculate Gut Fill and EBW so the latter is available for other eqns ####
An_GutFill_BWmature <- 0.18                                                                    #mature animals

An_GutFill_BW <- 0.06		                     								     #Milk fed calf, kg/kg BW
An_GutFill_BW <- ifelse(An_StatePhys=="Calf" & Dt_DMIn_ClfLiq>0.01 & Dt_DMIn_ClfStrt<=0.01 &   #Heavy milk fed veal calf 
                             An_BW>0.16*An_BW_mature, 0.09, An_GutFill_BW)	                           
An_GutFill_BW <- ifelse(An_StatePhys=="Calf" & Dt_DMIn_ClfLiq > 0.01 & Dt_DMIn_ClfStrt > 0.01, #Milk plus starter fed calf
                        0.07, An_GutFill_BW)
An_GutFill_BW <- ifelse(An_StatePhys=="Calf" & Dt_DMIn_ClfLiq < 0.01,                          #Weaned calf
                        0.15, An_GutFill_BW)
An_GutFill_BW <- ifelse(An_StatePhys=="Heifer", 0.15, An_GutFill_BW)                           #heifer
An_GutFill_BW <- ifelse((An_StatePhys=="Dry Cow" |An_StatePhys=="Lactating Cow") & An_Parity_rl > 0, An_GutFill_BWmature, An_GutFill_BW)	 #cow
An_GutFill_Wt_Erdman <- 5.9*(Dt_DMIn+InfRum_DMIn+InfSI_DMIn)	#cows only, from Erdman et al. 2017; not used

An_GutFill_Wt <- An_GutFill_BW * An_BWnp
An_BW_empty <- An_BW - An_GutFill_Wt 	
An_BWmature_empty <- An_BW_mature*(1-An_GutFill_BWmature)
An_BWnp_empty <- An_BWnp - An_GutFill_Wt 	#BCS3 Std EBW
An_BWnp3_empty <- An_BWnp3 - An_GutFill_Wt 	#BCS3 Std EBWnp

#Body Composition, g/g EBW
Body_Fat_EBW <- 0.067+0.188*An_BW/An_BW_mature #Equation 11-4a
Body_NonFat_EBW <- 1 - Body_Fat_EBW
Body_CP_EBW <- 0.215*Body_NonFat_EBW
Body_Ash_EBW <- 0.056 * Body_NonFat_EBW
Body_Wat_EBW <- 0.729 * Body_NonFat_EBW

Body_Fat <- An_BWnp_empty * Body_Fat_EBW  #Using a non-pregnant BW
Body_NonFat <- An_BWnp_empty * Body_NonFat_EBW
Body_CP <- An_BWnp_empty * Body_NonFat_EBW
Body_Ash <- An_BWnp_empty * Body_Ash_EBW
Body_Wat <- An_BWnp_empty * Body_Wat_EBW

#### Body gain and Composition of the Gain ####
#Gain
Frm_Gain <- Trg_FrmGain		#kg/d.  Add any predictions of ADG and select Trg or Pred ADG here
Rsrv_Gain <- Trg_RsrvGain
Body_Gain <- Frm_Gain + Rsrv_Gain
An_BodConcgain <- Body_Gain + Conc_BWgain #Minus fetal fluid.

Frm_Gain_empty <- Frm_Gain*(1-An_GutFill_BW)	    #Assume the same gut fill for frame gain
Frm_Gain_empty <- ifelse(Dt_DMIn_ClfLiq>0 & Dt_DMIn_ClfStrt>0, Frm_Gain*0.91, Frm_Gain_empty) #slightly different for grain & milk fed
Rsrv_Gain_empty <- Rsrv_Gain                     #Assume no gut fill associated with reserves gain
Body_Gain_empty <- Frm_Gain_empty + Rsrv_Gain_empty

#Fat Gain
An_REgain_Calf <- Body_Gain_empty^1.10*An_BW_empty^0.205    #calf RE gain needed here for fat gain, mcal/d
FatGain_FrmGain  <- ifelse(An_StatePhys == "Calf", 
                         0.0786+0.0370*An_REgain_Calf,   # Calves, ..., g/g EBW
                         (0.067+0.375*An_BW/An_BW_mature)) # Heifers and cows, g/g EBW p. 258
FatGain_FrmGain  <- ifelse(is.na(FatGain_FrmGain),0,FatGain_FrmGain)                 #trap NA when no Body_Gain
NonFatGain_FrmGain <- 1 - FatGain_FrmGain
FatGain_RsrvGain <- 0.622
Frm_Fatgain <- FatGain_FrmGain*Frm_Gain_empty
Rsrv_Fatgain <- FatGain_RsrvGain*Rsrv_Gain_empty
Body_Fatgain <- Frm_Fatgain + Rsrv_Fatgain
Body_NonFatGain <- Body_Gain_empty - Body_Fatgain

#Protein Gain
CPGain_FrmGain <- 0.201-0.081*An_BW/An_BW_mature  #CP gain / gain for heifers
NPGain_FrmGain <- CPGain_FrmGain * Body_NP_CP   #Convert to CP to TP gain / gain
Frm_NPgain <- NPGain_FrmGain * Frm_Gain_empty   #TP gain
Frm_NPgain <- ifelse(An_StatePhys == "Calf", (166.22*Body_Gain_empty + 6.13*An_REgain_Calf/Body_Gain_empty)/1000, Frm_NPgain)
Frm_NPgain_g <- Frm_NPgain * 1000
Frm_CPgain <- Frm_NPgain /  Body_NP_CP   #CP gain
Frm_CPgain_g <- Frm_CPgain * 1000

CPGain_RsrvGain <- 0.068
NPGain_RsrvGain <- CPGain_RsrvGain * Body_NP_CP 
Rsrv_NPgain <- NPGain_RsrvGain * Rsrv_Gain_empty
Rsrv_NPgain_g <- Rsrv_NPgain * 1000
Rsrv_CPgain <- CPGain_FrmGain * Rsrv_Gain_empty
Rsrv_CPgain_g <- Rsrv_CPgain * 1000

Body_NPgain <- Frm_NPgain + Rsrv_NPgain
Body_CPgain <- Body_NPgain / Body_NP_CP  #CP gain
Body_NPgain_g <- Body_NPgain * 1000
Body_CPgain_g <- Body_CPgain * 1000

#Ash Gain
#AshGain_FrmGain <- ?? #should be defined and added in the future.  No values at this time.
AshGain_RsrvGain <- 0.02
#Frm_AshGain <- AshGain_FrmGain * Frm_Gain_empty
Rsrv_AshGain <- AshGain_RsrvGain * Rsrv_Gain_empty
#Body_AshGain <- Frm_AshGain + Rsrv_AshGain
Body_AshGain <- 0.056*Body_NonFatGain  #Alternative method of estimation Body and Frm Ash
Frm_AshGain <- Body_AshGain

#Water Gain
#WatGain_FrmGain <- 100 - FatGain_FrmGain - NPGain_FrmGain - AshGain_FrmGain
WatGain_RsrvGain <- 100 - FatGain_RsrvGain - NPGain_RsrvGain - AshGain_RsrvGain
#Frm_WatGain <- WatGain_FrmGain * Frm_Gain_empty
Rsrv_WatGain <- WatGain_RsrvGain * Rsrv_Gain_empty
#Body_WatGain <- Frm_WatGain + Rsrv_WatGain
Body_WatGain <- 0.729*Body_NonFatGain #Alternative method of estimation
Frm_WatGain <- Body_WatGain - Rsrv_WatGain

#AA Gain
Body_ArgGain_g <- Body_NPgain_g * Body_Arg_TP / 100
Body_HisGain_g <- Body_NPgain_g * Body_His_TP / 100
Body_IleGain_g <- Body_NPgain_g * Body_Ile_TP / 100
Body_LeuGain_g <- Body_NPgain_g * Body_Leu_TP / 100
Body_LysGain_g <- Body_NPgain_g * Body_Lys_TP / 100
Body_MetGain_g <- Body_NPgain_g * Body_Met_TP / 100
Body_PheGain_g <- Body_NPgain_g * Body_Phe_TP / 100
Body_ThrGain_g <- Body_NPgain_g * Body_Thr_TP / 100
Body_TrpGain_g <- Body_NPgain_g * Body_Trp_TP / 100
Body_ValGain_g <- Body_NPgain_g * Body_Val_TP / 100
Body_EAAGain_g <- Body_ArgGain_g + Body_HisGain_g + Body_IleGain_g + Body_LeuGain_g + Body_LysGain_g +
     Body_MetGain_g + Body_PheGain_g + Body_ThrGain_g + Body_TrpGain_g + Body_ValGain_g
# As a fraction of absorbed
BodyArg_AbsArg <- Body_ArgGain_g / Abs_Arg_g 
BodyHis_AbsHis <- Body_HisGain_g / Abs_His_g 
BodyIle_AbsIle <- Body_IleGain_g / Abs_Ile_g 
BodyLeu_AbsLeu <- Body_LeuGain_g / Abs_Leu_g 
BodyLys_AbsLys <- Body_LysGain_g / Abs_Lys_g 
BodyMet_AbsMet <- Body_MetGain_g / Abs_Met_g 
BodyPhe_AbsPhe <- Body_PheGain_g / Abs_Phe_g 
BodyThr_AbsThr <- Body_ThrGain_g / Abs_Thr_g 
BodyTrp_AbsTrp <- Body_TrpGain_g / Abs_Trp_g 
BodyVal_AbsVal <- Body_ValGain_g / Abs_Val_g 

############################################################################################
#              Total NP, N, and AA Use and Postabsorptive Efficiency                       #
############################################################################################
#NP use for export protein (maintenance, milk, and body gain)
An_CPxprt_g <- Scrf_CP_g + Fe_CPend_g + Mlk_CP_g + Body_CPgain_g  #Initially defined only as true export protein, but it has migrated to include other prod proteins.
An_NPxprt_g <- Scrf_NP_g + Fe_NPend_g + Mlk_NP_g + Body_NPgain_g  #Should have changed the name.
Trg_NPxprt_g <- Scrf_NP_g + Fe_NPend_g + Trg_Mlk_NP_g + Body_NPgain_g  #Shouldn't these also include Gest??

An_CPprod_g <- Mlk_CP_g + Gest_NCPgain_g + Body_CPgain_g #CP use for production.  Be careful not to double count Gain.
An_NPprod_g <- Mlk_NP_g + Gest_NPgain_g + Body_NPgain_g #NP use for production
Trg_NPprod_g <- Trg_Mlk_NP_g + Gest_NPgain_g + Body_NPgain_g #NP needed for production target
An_NPprod_MPIn <- An_NPprod_g / An_MPIn_g

#Total protein and N use, g/d
Trg_NPuse_g <- Scrf_NP_g + Fe_NPend_g + Ur_NPend_g + Trg_Mlk_NP_g + Body_NPgain_g + Gest_NPgain_g
An_NPuse_g <- Scrf_NP_g + Fe_NPend_g + Ur_NPend_g + Mlk_NP_g + Body_NPgain_g + Gest_NPgain_g  #includes only net use of true protein.  Excludes non-protein maintenance use.
An_NCPuse_g <- Scrf_CP_g + Fe_CPend_g + Ur_NPend_g + Mlk_CP_g + Body_CPgain_g + Gest_NCPgain_g  #Net CP use
#An_Nuse_g <- An_CPuse_g * 0.16   #considers NPN fraction of the tissues and export fractions.  Not used as the abbreviation is misleading.
An_Nprod_g <- (Gest_NCPgain_g + Body_CPgain_g)/6.25 + Mlk_CP_g/6.34
An_Nprod_NIn <- An_Nprod_g / An_NIn_g
An_Nprod_DigNIn <- An_Nprod_g / An_DigNtIn_g

#Total Net AA use (Nutrient Allowable), g/d
An_ArgUse_g <- Gest_Arg_g + Mlk_Arg_g + Body_ArgGain_g + Scrf_Arg_g + Fe_ArgMet_g + Ur_ArgEnd_g
An_HisUse_g <- Gest_His_g + Mlk_His_g + Body_HisGain_g + Scrf_His_g + Fe_HisMet_g + Ur_HisEnd_g
An_IleUse_g <- Gest_Ile_g + Mlk_Ile_g + Body_IleGain_g + Scrf_Ile_g + Fe_IleMet_g + Ur_IleEnd_g
An_LeuUse_g <- Gest_Leu_g + Mlk_Leu_g + Body_LeuGain_g + Scrf_Leu_g + Fe_LeuMet_g + Ur_LeuEnd_g
An_LysUse_g <- Gest_Lys_g + Mlk_Lys_g + Body_LysGain_g + Scrf_Lys_g + Fe_LysMet_g + Ur_LysEnd_g
An_MetUse_g <- Gest_Met_g + Mlk_Met_g + Body_MetGain_g + Scrf_Met_g + Fe_MetMet_g + Ur_MetEnd_g
An_PheUse_g <- Gest_Phe_g + Mlk_Phe_g + Body_PheGain_g + Scrf_Phe_g + Fe_PheMet_g + Ur_PheEnd_g
An_ThrUse_g <- Gest_Thr_g + Mlk_Thr_g + Body_ThrGain_g + Scrf_Thr_g + Fe_ThrMet_g + Ur_ThrEnd_g
An_TrpUse_g <- Gest_Trp_g + Mlk_Trp_g + Body_TrpGain_g + Scrf_Trp_g + Fe_TrpMet_g + Ur_TrpEnd_g
An_ValUse_g <- Gest_Val_g + Mlk_Val_g + Body_ValGain_g + Scrf_Val_g + Fe_ValMet_g + Ur_ValEnd_g
An_EAAUse_g <- An_ArgUse_g + An_HisUse_g + An_IleUse_g + An_LeuUse_g + An_LysUse_g + An_MetUse_g + 
               An_PheUse_g + An_ThrUse_g + An_TrpUse_g + An_ValUse_g 

# Total Net AA efficiency, g/g absorbed
AnArgUse_AbsArg <- An_ArgUse_g / Abs_Arg_g 
AnHisUse_AbsHis <- An_HisUse_g / Abs_His_g 
AnIleUse_AbsIle <- An_IleUse_g / Abs_Ile_g 
AnLeuUse_AbsLeu <- An_LeuUse_g / Abs_Leu_g 
AnLysUse_AbsLys <- An_LysUse_g / Abs_Lys_g 
AnMetUse_AbsMet <- An_MetUse_g / Abs_Met_g 
AnPheUse_AbsPhe <- An_PheUse_g / Abs_Phe_g 
AnThrUse_AbsThr <- An_ThrUse_g / Abs_Thr_g 
AnTrpUse_AbsTrp <- An_TrpUse_g / Abs_Trp_g 
AnValUse_AbsVal <- An_ValUse_g / Abs_Val_g 
AnEAAUse_AbsEAA <- An_EAAUse_g / Abs_EAA_g 

# Total Net AA Balance, g/d
An_ArgBal_g <- Abs_Arg_g - An_ArgUse_g
An_HisBal_g <- Abs_His_g - An_HisUse_g
An_IleBal_g <- Abs_Ile_g - An_IleUse_g
An_LeuBal_g <- Abs_Leu_g - An_LeuUse_g
An_LysBal_g <- Abs_Lys_g - An_LysUse_g
An_MetBal_g <- Abs_Met_g - An_MetUse_g
An_PheBal_g <- Abs_Phe_g - An_PheUse_g
An_ThrBal_g <- Abs_Thr_g - An_ThrUse_g
An_TrpBal_g <- Abs_Trp_g - An_TrpUse_g
An_ValBal_g <- Abs_Val_g - An_ValUse_g
An_EAABal_g <- Abs_EAA_g - An_EAAUse_g

#Target postabsorptive efficiencies based on maximum observed efficiencies from Martineau and LaPiere as listed in NRC, Ch. 6.
Trg_AbsHis_NPxprtHis <- Eff$Trg_AbsHis_NPHis  
Trg_AbsIle_NPxprtIle <- Eff$Trg_AbsIle_NPIle
Trg_AbsLeu_NPxprtLeu <- Eff$Trg_AbsLeu_NPLeu
Trg_AbsLys_NPxprtLys <- Eff$Trg_AbsLys_NPLys
Trg_AbsMet_NPxprtMet <- Eff$Trg_AbsMet_NPMet
Trg_AbsPhe_NPxprtPhe <- Eff$Trg_AbsPhe_NPPhe
Trg_AbsThr_NPxprtThr <- Eff$Trg_AbsThr_NPThr
Trg_AbsTrp_NPxprtTrp <- Eff$Trg_AbsTrp_NPTrp
Trg_AbsVal_NPxprtVal <- Eff$Trg_AbsVal_NPVal
Trg_AbsEAA_NPxprtEAA <- (Trg_AbsHis_NPxprtHis + Trg_AbsIle_NPxprtIle + Trg_AbsLeu_NPxprtLeu + Trg_AbsLys_NPxprtLys + Trg_AbsMet_NPxprtMet +   #Should be weighted or derived 
                 Trg_AbsPhe_NPxprtPhe +Trg_AbsThr_NPxprtThr + Trg_AbsTrp_NPxprtTrp + Trg_AbsVal_NPxprtVal) / 9            #directly from total EAA
Trg_AbsArg_NPxprtArg <- Trg_AbsEAA_NPxprtEAA  #none provided thus assumed to be the same as for EAA
Trg_MP_NPxprt <- Eff$Trg_MP_NP

#Estimate the degree of AA imbalance within the EAA as ratios of each Eff to the total EAA Eff.
#These "Target" ratios are calculated as efficiency target (NRC 2021 Ch. 6) / total EAA eff.
#Thus they are scaled to Ch. 6 targets.  Ch. 6 values should not be used directly here. Ratio first.
#The target eff from Ch. 6 are likely not true maximum efficiencies.
Trg_ArgEff_EAAEff <- Trg_AbsArg_NPxprtArg / Trg_AbsEAA_NPxprtEAA  
Trg_HisEff_EAAEff <- Trg_AbsHis_NPxprtHis / Trg_AbsEAA_NPxprtEAA  #ratio to the mean Trg for each EAA / total EAA Trg of 70.6%
Trg_IleEff_EAAEff <- Trg_AbsIle_NPxprtIle / Trg_AbsEAA_NPxprtEAA  #e.g. Ile Trg is 97.3% of 70.6%
Trg_LeuEff_EAAEff <- Trg_AbsLeu_NPxprtLeu / Trg_AbsEAA_NPxprtEAA
Trg_LysEff_EAAEff <- Trg_AbsLys_NPxprtLys / Trg_AbsEAA_NPxprtEAA
Trg_MetEff_EAAEff <- Trg_AbsMet_NPxprtMet / Trg_AbsEAA_NPxprtEAA
Trg_PheEff_EAAEff <- Trg_AbsPhe_NPxprtPhe / Trg_AbsEAA_NPxprtEAA
Trg_ThrEff_EAAEff <- Trg_AbsThr_NPxprtThr / Trg_AbsEAA_NPxprtEAA
Trg_TrpEff_EAAEff <- Trg_AbsTrp_NPxprtTrp / Trg_AbsEAA_NPxprtEAA
Trg_ValEff_EAAEff <- Trg_AbsVal_NPxprtVal / Trg_AbsEAA_NPxprtEAA

#Calculate the current ratios for the diet.  This centers the ratio to the prevailing EAA Efficiency   
An_ArgEff_EAAEff <- AnArgUse_AbsArg / AnEAAUse_AbsEAA
An_HisEff_EAAEff <- AnHisUse_AbsHis / AnEAAUse_AbsEAA
An_IleEff_EAAEff <- AnIleUse_AbsIle / AnEAAUse_AbsEAA
An_LeuEff_EAAEff <- AnLeuUse_AbsLeu / AnEAAUse_AbsEAA
An_LysEff_EAAEff <- AnLysUse_AbsLys / AnEAAUse_AbsEAA
An_MetEff_EAAEff <- AnMetUse_AbsMet / AnEAAUse_AbsEAA
An_PheEff_EAAEff <- AnPheUse_AbsPhe / AnEAAUse_AbsEAA
An_ThrEff_EAAEff <- AnThrUse_AbsThr / AnEAAUse_AbsEAA
An_TrpEff_EAAEff <- AnTrpUse_AbsTrp / AnEAAUse_AbsEAA
An_ValEff_EAAEff <- AnValUse_AbsVal / AnEAAUse_AbsEAA

#Calculate a relative penalty for each EAA to reflect the degree of imbalance for each.
#if the diet eff = Trg_eff then no penalty. f_Imb is a vector of penalty costs for each EAA.
#f_Imb should be passed to the model fn rather than handled as a global variable.
Imb_Arg <- ((An_ArgEff_EAAEff - Trg_ArgEff_EAAEff) * f_Imb["Arg"])^2
Imb_His <- ((An_HisEff_EAAEff - Trg_HisEff_EAAEff) * f_Imb["His"])^2
Imb_Ile <- ((An_IleEff_EAAEff - Trg_IleEff_EAAEff) * f_Imb["Ile"])^2
Imb_Leu <- ((An_LeuEff_EAAEff - Trg_LeuEff_EAAEff) * f_Imb["Leu"])^2
Imb_Lys <- ((An_LysEff_EAAEff - Trg_LysEff_EAAEff) * f_Imb["Lys"])^2
Imb_Met <- ((An_MetEff_EAAEff - Trg_MetEff_EAAEff) * f_Imb["Met"])^2
Imb_Phe <- ((An_PheEff_EAAEff - Trg_PheEff_EAAEff) * f_Imb["Phe"])^2
Imb_Thr <- ((An_ThrEff_EAAEff - Trg_ThrEff_EAAEff) * f_Imb["Thr"])^2
Imb_Trp <- ((An_TrpEff_EAAEff - Trg_TrpEff_EAAEff) * f_Imb["Trp"])^2
Imb_Val <- ((An_ValEff_EAAEff - Trg_ValEff_EAAEff) * f_Imb["Val"])^2

#Sum the penalty to get a relative imbalance value for the optimizer
Imb_EAA <- Imb_Arg + Imb_His + Imb_Ile + Imb_Leu + Imb_Lys + Imb_Met + 
            Imb_Phe + Imb_Thr + Imb_Trp + Imb_Val


############################################################################################
#                     Total MP use and MP Allowable Production                             #
############################################################################################
#Fixed assumed efficiencies of conversion of MP to NP.  These do not consider AA balance or energy effects, 
     #and thus may not be true max values. Greater efficiencies are likely possible given that max observed
     #does not guarantee that a perfect mix of AA and DE was achieved.  Thus they are current Targets subject to revision.
#These should really be abbreviated as _NP_MP to donote the ratio.
Kx_MP_NP_Trg  <- Trg_MP_NPxprt   #Target observed Export plus Gain Protein efficiency from NRC 2021, Table 6-6 
Km_MP_NP_Trg <- Kx_MP_NP_Trg #Maintenance assumed to be equal to target efficiency for export plus gain protein
Km_MP_NP_Trg <- ifelse(An_StatePhys == "Calf" | An_StatePhys == "Heifer", 0.66, Km_MP_NP_Trg)
Kl_MP_NP_Trg <- Kx_MP_NP_Trg #Lactation assumed to be equal to target efficiency for export plus gain protein

Ky_MP_NP_Trg <- 0.33         #Gestation MP to NP efficiency from NRC GrUter Growth, 2001 NRC.
Ky_NP_MP_Trg <- 1.0          #Getation NP to MP efficiency when tissue NP deposition is negative after calving

Kg_MP_NP_Trg <- 0.60 * Body_NP_CP  #Default value for Growth MP to TP.  Shouldn't be used for any.
Kg_MP_NP_Trg <- ifelse(An_Parity_rl == 0 & An_BW_empty/An_BWmature_empty > 0.12,
                       (0.64 - 0.3*An_BW_empty/An_BWmature_empty) * Body_NP_CP,  #for heifers from 12% until 83% of BW_mature
                       Kg_MP_NP_Trg)
Kg_MP_NP_Trg <- ifelse(Kg_MP_NP_Trg < 0.394*Body_NP_CP, 0.394*Body_NP_CP*Body_NP_CP, Kg_MP_NP_Trg)  #Trap heifer values less than 0.39 MP to CP
Kg_MP_NP_Trg <- ifelse(An_StatePhys=="Calf", (0.70 - 0.532*(An_BW/An_BW_mature))*Body_NP_CP, Kg_MP_NP_Trg) #calves
Kg_MP_NP_Trg <- ifelse(An_Parity_rl > 0,  Eff$Trg_MP_NP, Kg_MP_NP_Trg)  #Cows

######## Estimate MP Allowable Production using Target Production and Target Fixed efficiencies - biased as efficiencies are not fixed
Fe_MPendUse_g_Trg <- Fe_NPend_g / Km_MP_NP_Trg
Fe_MPendUse_g_Trg <- ifelse(An_StatePhys == "Calf" | An_StatePhys == "Heifer", Fe_CPend_g/Km_MP_NP_Trg, Fe_MPendUse_g_Trg) #calves and heifers are CP based.
Scrf_MPUse_g_Trg <- Scrf_NP_g / Km_MP_NP_Trg
Scrf_MPUse_g_Trg <- ifelse(An_StatePhys == "Calf" | An_StatePhys == "Heifer", Scrf_CP_g/Km_MP_NP_Trg, Scrf_MPUse_g_Trg) #calves and heifers are CP based.
Ur_MPendUse_g <- Ur_NPend_g
Rsrv_MPUse_g_Trg <- Rsrv_NPgain_g / Kg_MP_NP_Trg  #kg MP/d for Reserves NP gain
Frm_MPUse_g_Trg <- Frm_NPgain_g / Kg_MP_NP_Trg  #kg MP/d for Frame NP gain
Body_MPUse_g_Trg <- Body_NPgain_g / Kg_MP_NP_Trg  #kg MP/d for NP gain
Gest_MPUse_g_Trg <- ifelse(Gest_NPuse_g >= 0, Gest_NPuse_g/Ky_MP_NP_Trg, Gest_NPuse_g*Ky_NP_MP_Trg)
Mlk_MPUse_g_Trg <- Trg_Mlk_NP_g/ Kl_MP_NP_Trg  #kg MP/d for target milk protein lactation

An_MPm_g_Trg <- Fe_MPendUse_g_Trg + Scrf_MPUse_g_Trg + Ur_MPendUse_g 
An_MPuse_g_Trg <- An_MPm_g_Trg + Body_MPUse_g_Trg + Gest_MPUse_g_Trg + Mlk_MPUse_g_Trg

#Adjust heifer MPuse target if the MP:ME ratio is below optimum for development.
#Can't calculate ME before MP, thus estimated ME in the MP:ME ratio using the target NPgain.  Will be incorrect
#if the animal is lactating or gestating.
An_MEIn_approx <- An_DEInp + An_DENPNCPIn + (An_DigTPaIn-Body_NPgain)*4.0 + Body_NPgain*En_CP - An_GasEOut
Min_MPuse_g <- ifelse(An_StatePhys == "Heifer" & An_MPuse_g_Trg < (53-25*An_BW/An_BW_mature) * An_MEIn_approx,
                      (53-25*An_BW/An_BW_mature)*An_MEIn_approx, An_MPuse_g_Trg)
Diff_MPuse_g <- Min_MPuse_g - An_MPuse_g_Trg

#Adjust MPuse based on Min_MPuse
Frm_MPUse_g_Trg <- ifelse(An_StatePhys == "Heifer" & Diff_MPuse_g > 0, Frm_MPUse_g_Trg + Diff_MPuse_g, Frm_MPUse_g_Trg) 
#Recalculate Kg_MP_NP
Kg_MP_NP_Trg <- ifelse(An_StatePhys == "Heifer" & Diff_MPuse_g > 0, Frm_NPgain_g/Frm_MPUse_g_Trg, Kg_MP_NP_Trg)
#Recalculate Rsrv and Body_MPUse
Rsrv_MPUse_g_Trg <- ifelse(An_StatePhys == "Heifer" & Diff_MPuse_g > 0, Rsrv_NPgain_g / Kg_MP_NP_Trg, Rsrv_MPUse_g_Trg) 
Body_MPUse_g_Trg <- ifelse(An_StatePhys == "Heifer" & Diff_MPuse_g > 0, Body_NPgain_g / Kg_MP_NP_Trg, Body_MPUse_g_Trg) 
An_MPuse_g_Trg <- An_MPm_g_Trg + Frm_MPUse_g_Trg + Rsrv_MPUse_g_Trg + Gest_MPUse_g_Trg + Mlk_MPUse_g_Trg


An_MPBal_g_Trg <- An_MPIn_g - An_MPuse_g_Trg
Xprt_NP_MP_Trg <- (Scrf_NP_g + Fe_NPend_g + Trg_Mlk_NP_g + Body_NPgain_g) / (An_MPIn_g -  Ur_NPend_g - Gest_MPUse_g_Trg) #Predicted An_NP_MP using Target Milk NP, g/g
     #The above excludes Ur_NPend and Gest_NPgain from the denominator and the numerator as that is how Helene and Roger derived target efficiencies. 
     #Seems incorrect unless one does not consider Urinary endogenous as NP which is inconsistent with the definition.  Not a true, total MP efficiency

#Calculate MP allowable milk and gain using fixed apparent maximal target efficiencies
An_MPavail_Milk_Trg <- An_MPIn - An_MPuse_g_Trg/1000 + Mlk_MPUse_g_Trg/1000
Mlk_NP_MPalow_Trg_g <- An_MPavail_Milk_Trg * Kx_MP_NP_Trg * 1000   #g milk NP/d
Mlk_Prod_MPalow <- Mlk_NP_MPalow_Trg_g / (Trg_MilkTPp/100)/1000 #kg milk/d using Trg milk protein % to predict volume
Mlk_Prod <- ifelse(An_StatePhys == "Lactating Cow" & mProd_eqn==3, Mlk_Prod_MPalow, Mlk_Prod)  #Use MP Allowable based predictions
Trg_MPIn_req <- Fe_MPendUse_g_Trg+Scrf_MPUse_g_Trg+Ur_MPendUse_g+Body_MPUse_g_Trg+Gest_MPUse_g_Trg+Trg_Mlk_NP_g/Kl_MP_NP_Trg

An_MPavail_Gain_Trg <- An_MPIn - An_MPuse_g_Trg/1000 + Body_MPUse_g_Trg/1000
Body_NPgain_MPalowTrg_g <- An_MPavail_Gain_Trg  * Kg_MP_NP_Trg * 1000   #g NP gain/d
Body_CPgain_MPalowTrg_g <- Body_NPgain_MPalowTrg_g / Body_NP_CP   #g CP gain/d
Body_Gain_MPalowTrg_g <- Body_NPgain_MPalowTrg_g / NPGain_FrmGain  #g/d, Assume all is frame gain
Body_Gain_MPalowTrg <- Body_Gain_MPalowTrg_g / 1000


###### Calculate MP efficiency for Export and Total NP for comparison to the ideal efficiency
Xprt_NP_MP <- (Scrf_NP_g + Fe_NPend_g + Mlk_NP_g + Body_NPgain_g) / (An_MPIn_g - Ur_NPend_g - Gest_MPUse_g_Trg)  
#MP to NP conversion efficiency assuming 100% efficiency of Ur_NPend.  Should not be named as a K as it is not a constant.  This is apparent efficiency.
Km_MP_NP <- ifelse(An_StatePhys == "Heifer", 0.69, Xprt_NP_MP) #Assumed equal to efficiency for total proteins except for heifers.
Kl_MP_NP <- Xprt_NP_MP

######## Estimate MP Use for Milk NP and Maintenance NP
Fe_MPendUse_g <- Fe_NPend_g / Km_MP_NP
Scrf_MPUse_g <- Scrf_NP_g / Km_MP_NP
Mlk_MPUse_g <- Mlk_NP_g / Kl_MP_NP  #kg MP/d for lactation
An_MPuse_g <- Fe_MPendUse_g + Scrf_MPUse_g + Ur_MPendUse_g + Body_MPUse_g_Trg + Gest_MPUse_g_Trg + Mlk_MPUse_g
An_MPuse <- An_MPuse_g / 1000
An_MPBal_g <- An_MPIn_g - An_MPuse_g  #This will always be 0 given how the efficiencies are calculated. Not informative
     #Compare Kl_MP_NP_Trg with Kl_MP_NP to determine diet effectiveness

An_MP_NP <- An_NPuse_g / An_MPuse_g  #Total MP Efficiency, g/g
An_NPxprt_MP <- (An_NPuse_g-Ur_NPend_g-Gest_NPuse_g) / (An_MPIn_g-Ur_NPend_g-Gest_MPUse_g_Trg)  #g/g. For comparison to target efficiency, but a duplicate of Xprt_NP_MP.
An_CP_NP <- An_NPuse_g / (An_CPIn*1000)  #Total CP efficiency, g/g

An_NPBal_g <- An_MPIn_g*An_MP_NP - An_NPuse_g  #Also always 0, thus non-informative
An_NPBal <- An_NPBal_g / 1000

######################## Urinary N and Energy Losses ########################
Ur_Nout_g <- (An_CPIn*1000 - Fe_CP*1000 - Scrf_CP_g - Fe_CPend_g - Mlk_CP_g - 
                   Body_CPgain_g - Gest_CPuse_g) / 6.25
Ur_Nout_DigNIn <- Ur_Nout_g/(An_DigCPtIn*1000/6.25)*100
Ur_Nout_CPcatab <- Ur_Nout_g - Ur_Nend_g  #primarily AA catab, but also absorbed non-MP N such as PD

Ur_DEout <- 0.0143 * Ur_Nout_g
UrDE_DMIn <- Ur_DEout / An_DMIn
UrDE_GEIn <- Ur_DEout / An_GEIn
UrDE_DEIn <- Ur_DEout / An_DEIn

###################### Estimated ME and NE Intakes ####################
An_MEIn <- An_DEIn - An_GasEOut - Ur_DEout
K_DE_ME_ClfDry <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq > 0.015*An_BW & RumDevDisc_Clf > 0, 
                         0.93 * 0.9, 0.93)
An_MEIn <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq >0, 
          Dt_DEIn_base_ClfLiq*0.96 + Dt_DEIn_base_ClfDry*K_DE_ME_ClfDry, An_MEIn) #no consideration of infusions for calves.
An_ME <- An_MEIn / An_DMIn
An_ME_GE <- An_MEIn / An_GEIn
An_ME_DE <- An_MEIn / An_DEIn
An_NEIn <- An_MEIn * 0.66
An_NE <- An_NEIn / An_DMIn
An_NE_GE <- An_NEIn / An_GEIn
An_NE_DE <- An_NEIn / An_DEIn
An_NE_ME <- An_NEIn / An_MEIn
An_MPIn_MEIn <- An_MPIn_g / An_MEIn    #g/Mcal


##############################################################################################
#                      Estimated ME and NE Use                                               #
##############################################################################################

#### Net Energy of Maintenance Requirements (NEm, mcal/d) ####
#Unstressed (NS) Maintenance costs NEm, mcal/d
#*##Heifers
#*#An_NEmUse_NS <- 0.10 * An_BW^0.75  #Back calculated from MEm of 0.15 and Km_NE_ME = 0.66
#*##Calves
#*#An_NEmUse_NS <- ifelse(An_StatePhys == "Calf", 0.0769*An_BW_empty^0.75, An_NEmUse_NS)  #milk or mixed diet
#*#An_NEmUse_NS <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq == 0, 0.097*An_BW_empty^0.75, An_NEmUse_NS)  #weaned calf
#*##Cows
#*#An_NEmUse_NS <- ifelse(An_Parity_rl>0, 0.10*An_BW^0.75,  An_NEmUse_NS)


#Environmental stress cost (NEm_Env), mcal/d ##
#*#An_NEmUse_Env <- 0
#*#An_NEmUse_Env <- ifelse(Env_TempCurr<LCT & An_BW<100, 0.00201*(LCT-Env_TempCurr)*
#*#                        An_MBW,An_NEmUse_Env)							#calves - cold stress
#*#An_NEmUse_Env <- ifelse(Env_TempCurr>UCT & An_BW<100, 0.00201*(Env_TempCurr-UCT)*
#*#                        An_MBW,An_NEmUse_Env)							#calves - heat stress
#*#
#*##Locomotion costs (NEm_Act), mcal/d ##
#*#An_Grazing <- ifelse(Dt_PastIn/Dt_DMIn < 0.005, 0, 1)
#*#An_NEm_Act_Graze <- ifelse(Dt_PastIn/Dt_DMIn < 0.005, 0, 
#*#                    0.0075*An_MBW*(600-12*Dt_PastSupplIn)/600)
#*#An_NEm_Act_Parlor <-  (0.00035*Env_DistParlor/1000) * Env_TripsParlor * An_BW
#*#An_NEm_Act_Topo <- 0.0067*Env_Topo/1000 * An_BW
#*#An_NEmUse_Act <- An_NEm_Act_Graze + An_NEm_Act_Parlor + An_NEm_Act_Topo
#*#
#*#
#*##Total Maintenance cost (NEm), mcal/d ##
#*#An_NEmUse <- An_NEmUse_NS + An_NEmUse_Env + An_NEmUse_Act


############ efficiencies of Energy Use (Kxxx), Mcal NE/Mcal ME ######################
An_MEIn_ClfDry <- An_MEIn - Dt_MEIn_ClfLiq
An_ME_ClfDry <- An_MEIn_ClfDry / (An_DMIn - Dt_DMIn_ClfLiq)
An_NE_ClfDry <- 1.1104*An_ME_ClfDry - 0.0946*An_ME_ClfDry^2 + 0.0065*An_ME_ClfDry^3 - 0.7783

## Maintenance ##
Km_ME_NE_Clf <- ifelse(An_StatePhys == "Calf" & An_ME_ClfDry > 0 & An_NE_ClfDry >0 & Dt_DMIn_ClfLiq == 0, 
                       An_NE_ClfDry/An_ME_ClfDry,   #Dry feed only
                        0.69)                       #mixed dry and liquid feed
Km_ME_NE_Clf <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfStrt == 0 & Dt_DMIn_ClfLiq > 0, 0.723, Km_ME_NE_Clf) #Liquid feed only
Km_ME_NE_Heif <- 0.63
Km_ME_NE_Cow <- 0.66 #Dry and lactating
Km_ME_NE <- ifelse(An_StatePhys == "Calf", Km_ME_NE_Clf, Km_ME_NE_Heif)  #calves, Heifer is default
Km_ME_NE <- ifelse(An_StatePhys=="Lactating Cow" | An_StatePhys=="Dry Cow", Km_ME_NE_Cow, Km_ME_NE)  #Dry and Lactating Cows

#Activity
#Km_ME_NEact <- 0.66

## Lactation ##
Kl_ME_NE <- 0.66

## Frame (f) Gain (excludes Reserves Gain or Loss) ##
#Calf frame gain
Kf_ME_RE_ClfLiq <- 0.56
Kf_ME_RE_ClfDry <- (1.1376*An_DE*0.93 -0.1198*(An_DE*0.93)^2+0.0076*(An_DE*0.93)^3-1.2979)/(An_DE*0.93)
Kf_ME_RE_Clf <- Kf_ME_RE_ClfLiq*Dt_DMIn_ClfLiq/Dt_DMIn + Kf_ME_RE_ClfDry*(Dt_DMIn-Dt_DMIn_ClfLiq)/Dt_DMIn

Kf_ME_RE <- ifelse(An_StatePhys == "Calf", Kf_ME_RE_Clf, 0.4)    #Default frame gain is 0.4 for heifers and cows

#Reserves Gain and Loss
#*#Kr_ME_RE <- 0.60                    #Efficiency of ME to RE for reserves gain, Heifers and dry cows
#*#Kr_ME_RE <- ifelse(Trg_MilkProd > 0 & Trg_RsrvGain > 0, 0.75, Kr_ME_RE) #Efficiency of ME to Rsrv RE for lactating cows gaining Rsrv
#*#Kr_ME_RE <- ifelse(Trg_RsrvGain <= 0, 0.89, Kr_ME_RE)                #Efficiency of ME generated for cows losing Rsrv

##Gestation ##
#*# Ky_ME_NE <- ifelse(Gest_REgain >= 0, 0.14, 0.89) #Gain from Ferrell et al, 1976, and loss assumed = Rsrv loss
   


############## ME Maintenance Requirements (MEm, mcal/d) ################
#*#An_MEmUse <- An_NEmUse / Km_ME_NE
An_MEmUse_NS <- An_NEmUse_NS / Km_ME_NE
An_MEmUse_Act <- An_NEmUse_Act / Km_ME_NE
An_MEmUse_Env <- An_NEmUse_Env / Km_ME_NE
An_NEm_ME <- An_NEmUse / An_MEIn #proportion of MEIn used for maintenance
An_NEm_DE <- An_NEmUse / An_DEIn #proportion of DEIn used for maintenance
An_NEmNS_DE <- An_NEmUse_NS / An_DEIn
An_NEmAct_DE <- An_NEmUse_Act / An_DEIn
An_NEmEnv_DE <- An_NEmUse_Env / An_DEIn

################ Energy Available for Production, Mcal/d ######################
An_NEprod_Avail <- An_NEIn - An_NEmUse  
An_MEprod_Avail <- An_MEIn - An_MEmUse

############################# Gestation ###########################################
#*# Gest_MEuse <- Gest_REgain / Ky_ME_NE
Gest_NELuse <- Gest_MEuse * Kl_ME_NE  #mcal/d ME required. ??This should not be used, delete.
Gest_NE_ME <- Gest_MEuse / An_MEIn #proportion of MEIn used for Gestation
Gest_NE_DE <- Gest_REgain / An_DEIn #proportion of DEIn retained in gravid uterus tissue

######################## Frame and Reserves Gain ########################
An_REgain <- 9.4*Body_Fatgain+5.55*Body_CPgain	     #Retained Energy, mcal/d. Does not apply to calves
#*#Rsrv_NEgain <- 9.4*Rsrv_Fatgain + 5.55*Rsrv_CPgain     #These are really REgain.  Abbreviations on NEgain need to be sorted out. MDH
Frm_NEgain <- 9.4*Frm_Fatgain + 5.55*Frm_CPgain
Rsrv_NE_DE <- Rsrv_NEgain / An_DEIn #proportion of DEIn used for Reserves gain
Frm_NE_DE <- Frm_NEgain / An_DEIn #proportion of DEIn used for Frame gain
Body_NEgain_BWgain <- An_REgain / Body_Gain #mcal NE/kg BW gain
#*# Rsrv_MEgain <- Rsrv_NEgain / Kr_ME_RE
#*# Frm_MEgain <- Frm_NEgain / Kf_ME_RE
An_MEgain <- Rsrv_MEgain + Frm_MEgain
An_ME_NEg <- An_REgain / An_MEgain  #A weighted average efficiency based on user entered or prediction frame and reserves gains. Cows only at this time.

Rsrv_NELgain <- Rsrv_MEgain * Kl_ME_NE  #express body energy required in NEL terms
Frm_NELgain <- Frm_MEgain * Kl_ME_NE
An_NELgain <- An_MEgain * Kl_ME_NE

An_NEgain_DE <- An_REgain / An_DEIn
An_NEgain_ME <- An_REgain / An_MEIn

######################## Lactation Energy ########################
Trg_MilkLacp <- ifelse(is.na(Trg_MilkLacp),4.78,Trg_MilkLacp)	#use the median if missing
Trg_MilkLac <- Trg_MilkLacp/100 * Trg_MilkProd
Trg_NEmilk_Milk <- 9.29*Trg_MilkFatp/100 + 5.85*Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100
Trg_NEmilk_Milk <- ifelse(is.na(Trg_NEmilk_Milk), 0.36+9.69*Trg_MilkFatp/100, Trg_NEmilk_Milk) #If milk protein and lactose are not provided, use the Tyrrell and Reid (1965) eqn.
Trg_Mlk_NEout <- Trg_MilkProd * Trg_NEmilk_Milk
Trg_Mlk_MEout <- Trg_Mlk_NEout / Kl_ME_NE
Trg_NEmilk_DEIn <- Trg_Mlk_NEout / An_DEIn
Trg_MilkProd_EPcor <- 0.327*Trg_MilkProd + (12.97*Trg_MilkFatp/100*Trg_MilkProd) + 
     (7.65*Trg_MilkTPp/100*Trg_MilkProd)  #energy and protein corrected milk

## Energy Allowable Milk - biased estimates as assumption of all added energy to 1 target is wrong ##
#An_NEavail_Milk <- An_NEIn - An_NEgain - An_NEmUse - Gest_NELuse ??Don't calculate directly.  Calculate from ME available.
An_MEavail_Milk <- An_MEIn - An_MEgain - An_MEmUse - Gest_MEuse
Mlk_Prod_NEalow <- An_MEavail_Milk * Kl_ME_NE / Trg_NEmilk_Milk 	#Energy allowable Milk Production, kg/d
Mlk_Prod <- ifelse(An_StatePhys == "Lactating Cow" & mProd_eqn==2, Mlk_Prod_NEalow, Mlk_Prod)  #use NE Allowable Milk prediction
Mlk_Prod <- ifelse(mProd_eqn==4, min(Mlk_Prod_NEalow,Mlk_Prod_MPalow), Mlk_Prod)  #Use min of NE and MP Allowable
Mlk_Prod_NEalow_EPcor <- 0.327*Mlk_Prod_NEalow + (12.97*Trg_MilkFatp/100*Mlk_Prod_NEalow) + 
                         (7.65*Trg_MilkTPp/100*Mlk_Prod_NEalow)  #energy and protein corrected milk
Mlk_EPcorNEalow_DMIn <- Mlk_Prod_NEalow_EPcor / An_DMIn

#Milk Composition
#g/g
MlkNP_Milk <- Mlk_NP_g/1000/Mlk_Prod;	#Milk true protein, g/g
MlkNP_Milk <- ifelse(An_StatePhys == "Lactating Cow", MlkNP_Milk, 0)
MlkFat_Milk <- Mlk_Fat / Mlk_Prod  #Milk Fat, g/g
MlkFat_Milk <- ifelse(An_StatePhys == "Lactating Cow", MlkFat_Milk, 0)

#Percentages
MlkNP_Milk_p <- MlkNP_Milk*100
MlkFat_Milk_p <- MlkFat_Milk*100


MlkNE_Milk <- 9.29*MlkFat_Milk + 5.85*MlkNP_Milk + 3.95*Trg_MilkLacp/100
Mlk_NEout <- MlkNE_Milk * Mlk_Prod
Mlk_MEout <- Mlk_NEout / Kl_ME_NE
Mlk_NE_DE <- Mlk_NEout / An_DEIn #proportion of DEIn used for milk

## Total Energy Use, Mcal/d ##
An_MEuse <- An_MEmUse + An_MEgain + Gest_MEuse + Mlk_MEout
Trg_MEuse <- An_MEmUse + An_MEgain + Gest_MEuse + Trg_Mlk_MEout
An_NEuse <- An_NEmUse + An_REgain + Gest_REgain + Mlk_NEout
Trg_NEuse <- An_NEmUse + An_REgain + Gest_REgain + Trg_Mlk_NEout
An_NELuse <- An_MEuse * Kl_ME_NE
Trg_NELuse <- Trg_MEuse * Kl_ME_NE

An_NEprod_GE <- (An_NEuse-An_NEmUse) / An_GEIn  #Total efficiency of GE use
Trg_NEprod_GE <- (Trg_NEuse-An_NEmUse) / An_GEIn  #Total efficiency of GE use
An_NEmlk_GE <- Mlk_NEout / An_GEIn  #Efficiency of GE use for milk NE
Trg_NEmlk_GE <- Trg_Mlk_NEout / An_GEIn  #Efficiency of GE use for milk NE

An_MEbal <- An_MEIn - An_MEuse
An_NELbal <- An_MEbal * Kl_ME_NE
An_NEbal <- An_NEIn - An_NEuse

Trg_MEbal <- An_MEIn - Trg_MEuse
Trg_NELbal <- Trg_MEbal * Kl_ME_NE
Trg_NEbal <- An_NEIn - Trg_NEuse

An_MPuse_MEuse <- An_MPuse_g / An_MEuse     #g/mcal
Trg_MPuse_MEuse <- An_MPuse_g_Trg / An_MEuse

## Energy Allowable Gain at the user specified mix of Frame and Reserves ##
An_MEavail_Grw <- An_MEIn - An_MEmUse - Gest_MEuse - Mlk_MEout
#Use a weighted average of Kf and Kr to predict allowable gain at that mix of Frm and Rsrv gain.
Kg_ME_NE <- Kf_ME_RE*Frm_NEgain/(Frm_NEgain+Rsrv_NEgain) + Kr_ME_RE*Rsrv_NEgain/(Frm_NEgain+Rsrv_NEgain)
Body_Gain_NEalow <- An_MEavail_Grw * Kg_ME_NE / Body_NEgain_BWgain


#Make NEallow have the same comp as the mix of Trg Rsrv and Frm
An_BodConcgain_NEalow <- Body_Gain_NEalow + Conc_BWgain
Body_Fatgain_NEalow <- 0.85*(Body_Gain_NEalow/0.85-1.19)/8.21
Body_NPgain_NEalow <- 0.85 * (1-Body_Fatgain_NEalow/0.85) * 0.215

An_Days_BCSdelta1 <- BW_BCS / Body_Gain_NEalow   #days to gain or lose 1 BCS (9.4% of BW), 5 pt scale.


################## Macro Mineral Requirements ###########################
### Calcium, g/d ###
Ca_Mlk <- ifelse(An_Breed == "Jersey" | !is.na(An_Breed), 1.17, 1.03) #Calcium content of milk, g/L
Fe_Ca_m <- 0.9 * An_DMIn								#maintenance
An_Ca_g <- (9.83 * An_BW_mature^0.22 * An_BW^-.22) * Body_Gain;	#growth
An_Ca_y <- (0.0245*exp((0.05581-0.00007*An_GestDay)*An_GestDay)-0.0245*
                  exp((0.05581-0.00007*(An_GestDay-1))*(An_GestDay-1)))*An_BW/715;  #gestation
An_Ca_l <- ifelse(is.na(Mlk_NP_g), Ca_Mlk * Trg_MilkProd, (0.295+0.239*Trg_MilkTPp) * Trg_MilkProd);	#lactation
An_Ca_l <- ifelse(is.na(An_Ca_l),0,An_Ca_l)
An_Ca_Clf <- (0.0127*An_BW_empty + (14.4*(An_BW_empty^-0.139)*Body_Gain_empty)) / 0.73
An_Ca_req <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq > 0, 
                    An_Ca_Clf, Fe_Ca_m + An_Ca_g + An_Ca_y + An_Ca_l)
An_Ca_bal <- Abs_CaIn - An_Ca_req
An_Ca_prod <- An_Ca_y + An_Ca_l + An_Ca_g

### Phosphorus, g/d ###
Ur_P_m <- 0.0006 * An_BW
Fe_P_m <- ifelse(An_Parity_rl == 0, 0.8 * An_DMIn, 1.0 * An_DMIn)
An_P_m <- Ur_P_m + Fe_P_m
An_P_g <- (1.2+(4.635*An_BW_mature^.22 * An_BW^-0.22))*Body_Gain
An_P_y <- (0.02743*exp((0.05527-0.000075*An_GestDay)*An_GestDay)-0.02743*
                  exp((0.05527-0.000075*(An_GestDay-1))*(An_GestDay-1)))*An_BW/715
An_P_l <- ifelse(is.na(Trg_MilkProd), 0, (0.48+0.13*MlkNP_Milk*100)*Trg_MilkProd)
	#If MTP not known then 0.9*Milk
An_P_Clf <- (0.0118*An_BW_empty + (5.85*(An_BW_empty^-0.027)*Body_Gain_empty)) / 0.65
An_P_req <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq > 0, 
                   An_P_Clf, An_P_m + An_P_g + An_P_y + An_P_l)
An_P_bal <- Abs_PIn - An_P_req
#Infused P not currently considered as an input, but should be.
Fe_P_g <- Dt_PIn - An_P_l - An_P_y - An_P_g - Ur_P_m
      #urinary losses will be underestimated at very high dietary P. Ordinarily 99% by feces.
An_P_prod <- An_P_y + An_P_l + An_P_g

### Mg, g/d ###
An_Mg_Clf <- (0.0035*An_BW_empty + (0.60*(An_BW_empty^-0.036)*Body_Gain_empty)) / 0.30
Ur_Mg_m <- 0.0007 * An_BW
Fe_Mg_m <- 0.3 * An_DMIn
An_Mg_m <- Ur_Mg_m + Fe_Mg_m
An_Mg_g <- 0.45 * Body_Gain
An_Mg_y <- ifelse(An_GestDay > 190, 0.3 * (An_BW/715), 0)
An_Mg_l <- ifelse(is.na(Trg_MilkProd), 0, 0.11 * Trg_MilkProd)
An_Mg_req <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq > 0, 
                    An_Mg_Clf, An_Mg_m + An_Mg_g + An_Mg_y + An_Mg_l)
An_Mg_bal <- Abs_MgIn - An_Mg_req
An_Mg_prod <- An_Mg_y + An_Mg_l + An_Mg_g

### Na, g/d ###
An_Na_Clf <- (0.00637*An_BW_empty + (1.508*(An_BW_empty^-0.045)*Body_Gain_empty)) / 0.24
Fe_Na_m <- 1.45 * An_DMIn
An_Na_g <- 1.4 * Body_Gain
An_Na_y <- ifelse(An_GestDay > 190, 1.4 * An_BW/715, 0)
An_Na_l <- ifelse(is.na(Trg_MilkProd), 0, 0.4 * Trg_MilkProd)
An_Na_req <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq > 0, 
                    An_Na_Clf, Fe_Na_m + An_Na_g + An_Na_y + An_Na_l)
An_Na_bal <- Abs_NaIn - An_Na_req
An_Na_prod <- An_Na_y + An_Na_l + An_Na_g
### Cl, g/d ###
An_Cl_Clf <- 0.8*(0.00637*An_BW_empty + (1.508*(An_BW_empty^-0.045)*Body_Gain_empty)) / 0.24
Fe_Cl_m <- 1.11 * An_DMIn
An_Cl_g <- 1.0 * Body_Gain
An_Cl_y <- ifelse(An_GestDay > 190, 1.0 * An_BW/715, 0)
An_Cl_l <- ifelse(is.na(Trg_MilkProd), 0, 1.0 * Trg_MilkProd)
An_Cl_req <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq > 0, 
                    An_Cl_Clf, Fe_Cl_m + An_Cl_g + An_Cl_y + An_Cl_l)
An_Cl_bal <- Abs_ClIn - An_Cl_req
An_Cl_prod <- An_Cl_y + An_Cl_l + An_Cl_g
### K, g/d ###
An_K_Clf <- (0.0203*An_BW_empty + (1.14*(An_BW_empty^-0.048)*Body_Gain_empty)) / 0.13
Ur_K_m <- ifelse(Trg_MilkProd > 0, 0.2 * An_BW, 0.07 * An_BW) 
Fe_K_m <- 2.5 * An_DMIn
An_K_m <- Ur_K_m + Fe_K_m
An_K_g <- 2.5 * Body_Gain
An_K_y <- ifelse(An_GestDay > 190, 1.03 * (An_BW/715), 0)
An_K_l <- ifelse(is.na(Trg_MilkProd),0,1.5 * Trg_MilkProd)
An_K_req <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq > 0, 
                   An_K_Clf, An_K_m + An_K_g + An_K_y + An_K_l)
An_K_bal <- Abs_KIn - An_K_req
An_K_prod <- An_K_y + An_K_l + An_K_g
### S, g/d ###
An_S_req <- 2 * An_DMIn
An_S_bal <- Dt_SIn - An_S_req


################## Micro Mineral Requirements ###########################
### Co, mg/d ###
An_Co_req <- 0.2 * An_DMIn  #Based on dietary intake assuming no absorption for a calf
An_Co_bal <- Abs_CoIn - An_Co_req #calf absorption set to 0 and other StatePhys to 1 above

### Cu, mg/d ###
An_Cu_Clf <- (0.0145*An_BW + 2.5*Body_Gain_empty) / 0.5
An_Cu_m <- 0.0145 * An_BW
An_Cu_g <- 2.0 * Body_Gain
An_Cu_y <- ifelse(An_GestDay < 90, 0, ifelse(An_GestDay > 190, 0.0023 * An_BW, 0.0003 * An_BW))
An_Cu_l <- ifelse(is.na(Trg_MilkProd), 0, 0.04 * Trg_MilkProd)
An_Cu_req <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq > 0, 
                    An_Cu_Clf, An_Cu_m + An_Cu_g + An_Cu_y + An_Cu_l)
An_Cu_bal <- Abs_CuIn - An_Cu_req
An_Cu_prod <- An_Cu_y + An_Cu_l + An_Cu_g
### I, mg/d ###
An_I_req <- ifelse(An_StatePhys=="Calf", 0.8*An_DMIn, 0.216*An_BW^0.528+0.1*Trg_MilkProd)
An_I_bal <- Dt_IIn - An_I_req

### Fe, mg/d ###
An_Fe_Clf <- 34*Body_Gain / 0.25
An_Fe_g <- 34 * Body_Gain
An_Fe_y <- ifelse(An_GestDay > 190, 0.025 * An_BW, 0)
An_Fe_l <- ifelse(is.na(Trg_MilkProd), 0, 1.0 * Trg_MilkProd)
An_Fe_req <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq > 0, 
                    An_Fe_Clf, An_Fe_g + An_Fe_y + An_Fe_l) #add An_Fe_m when I move the eqn up here.
An_Fe_bal <- Abs_FeIn - An_Fe_req
An_Fe_prod <- An_Fe_y + An_Fe_l + An_Fe_g
### Mn, mg/d ###
An_Mn_Clf <- (0.0026*An_BW + 0.7*Body_Gain) / 0.01
An_Mn_m <- 0.0026 * An_BW
An_Mn_g <- 0.7 * Body_Gain
An_Mn_y <- ifelse(An_GestDay > 190, 0.00042 * An_BW, 0)
An_Mn_l <- ifelse(is.na(Trg_MilkProd), 0, 0.03 * Trg_MilkProd)
An_Mn_req <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq > 0, 
                    An_Mn_Clf, An_Mn_m + An_Mn_g + An_Mn_y + An_Mn_l)
An_Mn_bal <- Abs_MnIn - An_Mn_req
An_Mn_prod <- An_Mn_y + An_Mn_l + An_Mn_g
### Se, mg/d ###
An_Se_req <- 0.3 * An_DMIn
An_Se_bal <- Dt_SeIn - An_Se_req

### Zn, mg
An_Zn_Clf <- (2.0*An_DMIn + 24*Body_Gain) / 0.25
An_Zn_m <- 5.0 * An_DMIn
An_Zn_g <- 24 * Body_Gain
An_Zn_y <- ifelse(An_GestDay > 190, 0.017 * An_BW, 0)
An_Zn_l <- ifelse(is.na(Trg_MilkProd), 0, 4.0 * Trg_MilkProd)
An_Zn_req <- ifelse(An_StatePhys == "Calf" & Dt_DMIn_ClfLiq > 0, 
                    An_Zn_Clf, An_Zn_m + An_Zn_g + An_Zn_y + An_Zn_l)
An_Zn_bal <- Abs_ZnIn - An_Zn_req
An_Zn_prod <- An_Zn_y + An_Zn_l + An_Zn_g
An_DCADmeq <- (Dt_K/0.039 + Dt_Na/0.023 - Dt_Cl/0.0355 - Dt_S/0.016) * 10 #DCAD in meg/kg

################## Vitamin Requirements ###########################
### Vit A, IU/d ###
An_VitA_req <- ifelse(Trg_MilkProd > 35, 110*An_BW + 1000*(Trg_MilkProd-35), 110*An_BW)
An_VitA_bal <- Dt_VitAIn - An_VitA_req

### Vit D, IU/d ###
An_VitD_req <- ifelse(Trg_MilkProd > 0, 40*An_BW, 32*An_BW)
An_VitD_bal <- Dt_VitDIn - An_VitD_req

### Vitamin E, IU/d ###
An_VitE_req <- ifelse(Trg_MilkProd == 0 & An_Parity_rl >= 1, 2.0 * An_BW, 0.8 * An_BW)
An_VitE_req <- ifelse(An_StatePhys == "Calf", 2.0 * An_BW, An_VitE_req)
An_VitE_req <- ifelse(An_GestDay >= 259 & An_Preg ==1, 3.0 * An_BW, An_VitE_req)
An_VitE_req <- An_VitE_req - Dt_PastIn * 50  #50 IU provided per kg of pasture DM
An_VitE_req <- ifelse(An_VitE_req < 0, 0, An_VitE_req)
An_VitE_bal <- Dt_VitEIn - An_VitE_req


################################ End of Model Calculations ################################


################### Additional Code added at the end of the project. ######################
#   Distribute this to the appropriate sections after Abbas has completed the C# code     #
#Efficiencies
Rum_MiCP_DigCHO <- Du_MiCP / (Rum_DigNDFIn + Rum_DigStIn)
An_MP_CP <- An_MPIn / An_CPIn

#EAA flows
An_IdEAAIn <- An_IdArgIn + An_IdHisIn + An_IdIleIn + An_IdLeuIn + An_IdLysIn + An_IdMetIn +
               An_IdPheIn + An_IdThrIn + An_IdTrpIn + An_IdValIn
Du_IdEAAMic <- Du_IdArgMic + Du_IdHisMic + Du_IdIleMic + Du_IdLeuMic + Du_IdLysMic + Du_IdMetMic +
          Du_IdPheMic + Du_IdThrMic + Du_IdTrpMic + Du_IdValMic
Dt_IdEAARUPIn <- Dt_IdArgRUPIn + Dt_IdHisRUPIn + Dt_IdIleRUPIn + Dt_IdLeuRUPIn + Dt_IdLysRUPIn + Dt_IdMetRUPIn +
     Dt_IdPheRUPIn + Dt_IdThrRUPIn + Dt_IdTrpRUPIn + Dt_IdValRUPIn
An_RUPIn_g <- An_RUPIn * 1000


#Target Milk EAA Outputs, g/d
Trg_Mlk_Arg_g <- Trg_Mlk_NP_g * Mlk_Arg_TP / 100
Trg_Mlk_His_g <- Trg_Mlk_NP_g * Mlk_His_TP / 100
Trg_Mlk_Ile_g <- Trg_Mlk_NP_g * Mlk_Ile_TP / 100
Trg_Mlk_Leu_g <- Trg_Mlk_NP_g * Mlk_Leu_TP / 100
Trg_Mlk_Lys_g <- Trg_Mlk_NP_g * Mlk_Lys_TP / 100
Trg_Mlk_Met_g <- Trg_Mlk_NP_g * Mlk_Met_TP / 100
Trg_Mlk_Phe_g <- Trg_Mlk_NP_g * Mlk_Phe_TP / 100
Trg_Mlk_Thr_g <- Trg_Mlk_NP_g * Mlk_Thr_TP / 100
Trg_Mlk_Trp_g <- Trg_Mlk_NP_g * Mlk_Trp_TP / 100
Trg_Mlk_Val_g <- Trg_Mlk_NP_g * Mlk_Val_TP / 100
Trg_Mlk_EAA_g <- Trg_Mlk_Arg_g + Trg_Mlk_His_g + Trg_Mlk_Ile_g + Trg_Mlk_Leu_g + Trg_Mlk_Lys_g + 
     Trg_Mlk_Met_g + Trg_Mlk_Phe_g + Trg_Mlk_Thr_g + Trg_Mlk_Trp_g + Trg_Mlk_Val_g
#Trg_DEInp_MlkNP <-Trg_Mlk_NP_g /  mPrt_k_DEInp #Need to subtract partials contrib from AA and NDF first.

#Net EAA Use at User Entered Production, g/d
Trg_ArgUse_g <- Trg_Mlk_Arg_g+Scrf_Arg_g+Fe_ArgMet_g + Ur_ArgEnd_g + Gest_Arg_g + Body_ArgGain_g
Trg_HisUse_g <- Trg_Mlk_His_g+Scrf_His_g+Fe_HisMet_g + Ur_HisEnd_g + Gest_His_g + Body_HisGain_g
Trg_IleUse_g <- Trg_Mlk_Ile_g+Scrf_Ile_g+Fe_IleMet_g + Ur_IleEnd_g + Gest_Ile_g + Body_IleGain_g
Trg_LeuUse_g <- Trg_Mlk_Leu_g+Scrf_Leu_g+Fe_LeuMet_g + Ur_LeuEnd_g + Gest_Leu_g + Body_LeuGain_g
Trg_LysUse_g <- Trg_Mlk_Lys_g+Scrf_Lys_g+Fe_LysMet_g + Ur_LysEnd_g + Gest_Lys_g + Body_LysGain_g
Trg_MetUse_g <- Trg_Mlk_Met_g+Scrf_Met_g+Fe_MetMet_g + Ur_MetEnd_g + Gest_Met_g + Body_MetGain_g
Trg_PheUse_g <- Trg_Mlk_Phe_g+Scrf_Phe_g+Fe_PheMet_g + Ur_PheEnd_g + Gest_Phe_g + Body_PheGain_g
Trg_ThrUse_g <- Trg_Mlk_Thr_g+Scrf_Thr_g+Fe_ThrMet_g + Ur_ThrEnd_g + Gest_Thr_g + Body_ThrGain_g
Trg_TrpUse_g <- Trg_Mlk_Trp_g+Scrf_Trp_g+Fe_TrpMet_g + Ur_TrpEnd_g + Gest_Trp_g + Body_TrpGain_g
Trg_ValUse_g <- Trg_Mlk_Val_g+Scrf_Val_g+Fe_ValMet_g + Ur_ValEnd_g + Gest_Val_g + Body_ValGain_g
Trg_EAAUse_g <- Trg_ArgUse_g + Trg_HisUse_g + Trg_IleUse_g + Trg_LeuUse_g + Trg_LysUse_g + Trg_MetUse_g + Trg_PheUse_g + 
                Trg_ThrUse_g + Trg_TrpUse_g + Trg_ValUse_g

#Abs EAA Use at User Entered Production, g/d
Trg_AbsHis_g <- (Trg_Mlk_His_g+Scrf_His_g+Fe_HisMet_g)/Trg_AbsHis_NPxprtHis + Ur_HisEnd_g + Gest_His_g/Ky_MP_NP_Trg + Body_HisGain_g/Kg_MP_NP_Trg
Trg_AbsIle_g <- (Trg_Mlk_Ile_g+Scrf_Ile_g+Fe_IleMet_g)/Trg_AbsIle_NPxprtIle + Ur_IleEnd_g + Gest_Ile_g/Ky_MP_NP_Trg + Body_IleGain_g/Kg_MP_NP_Trg
Trg_AbsLeu_g <- (Trg_Mlk_Leu_g+Scrf_Leu_g+Fe_LeuMet_g)/Trg_AbsLeu_NPxprtLeu + Ur_LeuEnd_g + Gest_Leu_g/Ky_MP_NP_Trg + Body_LeuGain_g/Kg_MP_NP_Trg
Trg_AbsLys_g <- (Trg_Mlk_Lys_g+Scrf_Lys_g+Fe_LysMet_g)/Trg_AbsLys_NPxprtLys + Ur_LysEnd_g + Gest_Lys_g/Ky_MP_NP_Trg + Body_LysGain_g/Kg_MP_NP_Trg
Trg_AbsMet_g <- (Trg_Mlk_Met_g+Scrf_Met_g+Fe_MetMet_g)/Trg_AbsMet_NPxprtMet + Ur_MetEnd_g + Gest_Met_g/Ky_MP_NP_Trg + Body_MetGain_g/Kg_MP_NP_Trg
Trg_AbsPhe_g <- (Trg_Mlk_Phe_g+Scrf_Phe_g+Fe_PheMet_g)/Trg_AbsPhe_NPxprtPhe + Ur_PheEnd_g + Gest_Phe_g/Ky_MP_NP_Trg + Body_PheGain_g/Kg_MP_NP_Trg
Trg_AbsThr_g <- (Trg_Mlk_Thr_g+Scrf_Thr_g+Fe_ThrMet_g)/Trg_AbsThr_NPxprtThr + Ur_ThrEnd_g + Gest_Thr_g/Ky_MP_NP_Trg + Body_ThrGain_g/Kg_MP_NP_Trg
Trg_AbsTrp_g <- (Trg_Mlk_Trp_g+Scrf_Trp_g+Fe_TrpMet_g)/Trg_AbsTrp_NPxprtTrp + Ur_TrpEnd_g + Gest_Trp_g/Ky_MP_NP_Trg + Body_TrpGain_g/Kg_MP_NP_Trg
Trg_AbsVal_g <- (Trg_Mlk_Val_g+Scrf_Val_g+Fe_ValMet_g)/Trg_AbsVal_NPxprtVal + Ur_ValEnd_g + Gest_Val_g/Ky_MP_NP_Trg + Body_ValGain_g/Kg_MP_NP_Trg
Trg_AbsEAA_g <- Trg_AbsHis_g + Trg_AbsIle_g + Trg_AbsLeu_g + Trg_AbsLys_g + Trg_AbsMet_g + Trg_AbsPhe_g + 
                    Trg_AbsThr_g + Trg_AbsTrp_g + Trg_AbsVal_g  #Arg not considered as partially synthesized
Trg_MlkEAA_AbsEAA <- (Mlk_EAA_g - Mlk_Arg_g) / Trg_AbsEAA_g

#Partial Milk Protein Outputs - These should be moved to the Milk Protein Prediction section and summed for Mlk_NP
MlkNP_Int <- mPrt_Int + (An_BW-612)*mPrt_k_BW
MlkNP_DEInp <- An_DEInp*mPrt_k_DEInp
MlkNP_NDF <- (An_DigNDF-17.06)*mPrt_k_DigNDF
MlkNP_AbsArg <- Abs_Arg_g*mPrt_k_Arg 
MlkNP_AbsHis <- Abs_His_g*mPrt_k_His
MlkNP_AbsIle <- Abs_Ile_g*mPrt_k_Ile 
MlkNP_AbsLeu <- Abs_Leu_g*mPrt_k_Leu
MlkNP_AbsLys <- Abs_Lys_g*mPrt_k_Lys
MlkNP_AbsMet <- Abs_Met_g*mPrt_k_Met
MlkNP_AbsPhe <- Abs_Phe_g*mPrt_k_Phe
MlkNP_AbsThr <- Abs_Thr_g*mPrt_k_Thr
MlkNP_AbsTrp <- Abs_Trp_g*mPrt_k_Trp
MlkNP_AbsVal <- Abs_Val_g*mPrt_k_Val
MlkNP_AbsEAA <- Abs_EAA2b_g*mPrt_k_EAA2 
MlkNP_AbsNEAA <- Abs_neAA_g*mPrt_k_NEAA
MlkNP_AbsOthAA <- Abs_OthAA_g*mPrt_k_OthAA

#Predicted Efficiency of AbsAA to export and gain NPAA using Nutrient Allowable milk protein, g NPAA/g absorbed AA (Ur_AAend use set to an efficiency of 1). These are for comparison to Trg AA Eff.
AnNPxArg_AbsArg <- (An_ArgUse_g - Gest_Arg_g - Ur_ArgEnd_g) / (Abs_Arg_g - Ur_ArgEnd_g - Gest_Arg_g/Ky_MP_NP_Trg) #Subtract Gest_AA and UrEnd for use and supply
AnNPxHis_AbsHis <- (An_HisUse_g - Gest_His_g - Ur_HisEnd_g) / (Abs_His_g - Ur_HisEnd_g - Gest_His_g/Ky_MP_NP_Trg)
AnNPxIle_AbsIle <- (An_IleUse_g - Gest_Ile_g - Ur_IleEnd_g) / (Abs_Ile_g - Ur_IleEnd_g - Gest_Ile_g/Ky_MP_NP_Trg)
AnNPxLeu_AbsLeu <- (An_LeuUse_g - Gest_Leu_g - Ur_LeuEnd_g) / (Abs_Leu_g - Ur_LeuEnd_g - Gest_Leu_g/Ky_MP_NP_Trg)
AnNPxLys_AbsLys <- (An_LysUse_g - Gest_Lys_g - Ur_LysEnd_g) / (Abs_Lys_g - Ur_LysEnd_g - Gest_Lys_g/Ky_MP_NP_Trg)
AnNPxMet_AbsMet <- (An_MetUse_g - Gest_Met_g - Ur_MetEnd_g) / (Abs_Met_g - Ur_MetEnd_g - Gest_Met_g/Ky_MP_NP_Trg)
AnNPxPhe_AbsPhe <- (An_PheUse_g - Gest_Phe_g - Ur_PheEnd_g) / (Abs_Phe_g - Ur_PheEnd_g - Gest_Phe_g/Ky_MP_NP_Trg)
AnNPxThr_AbsThr <- (An_ThrUse_g - Gest_Thr_g - Ur_ThrEnd_g) / (Abs_Thr_g - Ur_ThrEnd_g - Gest_Thr_g/Ky_MP_NP_Trg)
AnNPxTrp_AbsTrp <- (An_TrpUse_g - Gest_Trp_g - Ur_TrpEnd_g) / (Abs_Trp_g - Ur_TrpEnd_g - Gest_Trp_g/Ky_MP_NP_Trg)
AnNPxVal_AbsVal <- (An_ValUse_g - Gest_Val_g - Ur_ValEnd_g) / (Abs_Val_g - Ur_ValEnd_g - Gest_Val_g/Ky_MP_NP_Trg)
AnNPxEAA_AbsEAA <- (An_EAAUse_g - Gest_EAA_g - Ur_EAAEnd_g) / (Abs_EAA_g - Ur_EAAEnd_g - Gest_EAA_g/Ky_MP_NP_Trg)

#Efficiency of AbsAA to export and gain NPAA at User Entered milk protein, g NPAA/g absorbed AA (Ur_AAend use set to an efficiency of 1).
AnNPxArgUser_AbsArg <- (Trg_ArgUse_g - Gest_Arg_g - Ur_ArgEnd_g) / (Abs_Arg_g - Ur_ArgEnd_g - Gest_Arg_g/Ky_MP_NP_Trg) #Subtract Gest_AA and UrEnd for use and supply
AnNPxHisUser_AbsHis <- (Trg_HisUse_g - Gest_His_g - Ur_HisEnd_g) / (Abs_His_g - Ur_HisEnd_g - Gest_His_g/Ky_MP_NP_Trg)
AnNPxIleUser_AbsIle <- (Trg_IleUse_g - Gest_Ile_g - Ur_IleEnd_g) / (Abs_Ile_g - Ur_IleEnd_g - Gest_Ile_g/Ky_MP_NP_Trg)
AnNPxLeuUser_AbsLeu <- (Trg_LeuUse_g - Gest_Leu_g - Ur_LeuEnd_g) / (Abs_Leu_g - Ur_LeuEnd_g - Gest_Leu_g/Ky_MP_NP_Trg)
AnNPxLysUser_AbsLys <- (Trg_LysUse_g - Gest_Lys_g - Ur_LysEnd_g) / (Abs_Lys_g - Ur_LysEnd_g - Gest_Lys_g/Ky_MP_NP_Trg)
AnNPxMetUser_AbsMet <- (Trg_MetUse_g - Gest_Met_g - Ur_MetEnd_g) / (Abs_Met_g - Ur_MetEnd_g - Gest_Met_g/Ky_MP_NP_Trg)
AnNPxPheUser_AbsPhe <- (Trg_PheUse_g - Gest_Phe_g - Ur_PheEnd_g) / (Abs_Phe_g - Ur_PheEnd_g - Gest_Phe_g/Ky_MP_NP_Trg)
AnNPxThrUser_AbsThr <- (Trg_ThrUse_g - Gest_Thr_g - Ur_ThrEnd_g) / (Abs_Thr_g - Ur_ThrEnd_g - Gest_Thr_g/Ky_MP_NP_Trg)
AnNPxTrpUser_AbsTrp <- (Trg_TrpUse_g - Gest_Trp_g - Ur_TrpEnd_g) / (Abs_Trp_g - Ur_TrpEnd_g - Gest_Trp_g/Ky_MP_NP_Trg)
AnNPxValUser_AbsVal <- (Trg_ValUse_g - Gest_Val_g - Ur_ValEnd_g) / (Abs_Val_g - Ur_ValEnd_g - Gest_Val_g/Ky_MP_NP_Trg)
AnNPxEAAUser_AbsEAA <- (Trg_EAAUse_g - Gest_EAA_g - Ur_EAAEnd_g) / (Abs_EAA_g - Ur_EAAEnd_g - Gest_EAA_g/Ky_MP_NP_Trg)

#Calculate Diet level absorption coefficients for minerals, g/g
Dt_acCa <- Abs_CaIn / Dt_CaIn
Dt_acP <- Abs_PIn / Dt_PIn
Dt_acNa <- Abs_NaIn / Dt_NaIn
Dt_acMg <- Abs_MgIn / Dt_MgIn
Dt_acK <- Abs_KIn / Dt_KIn
Dt_acCl <- Abs_ClIn / Dt_ClIn

Dt_acCo <- Abs_CoIn / Dt_CoIn
Dt_acCu <- Abs_CuIn / Dt_CuIn
Dt_acFe <- Abs_FeIn / Dt_FeIn
Dt_acMn <- Abs_MnIn / Dt_MnIn
Dt_acZn <- Abs_ZnIn / Dt_ZnIn

#Nutrient Excretion
#Methane
CH4vol_kg <- 1497 #liters/kg
En_CH4 <- 55.5 / 4.184                     #mcal/kg methane; 890 kJ/mol / 16 g/mol = 55.6 MJ/kg from Rossini, 1930
CH4out_g <- An_GasEOut / En_CH4 * 1000     #g methane/d
CH4out_L <- CH4out_g / 1000 * CH4vol_kg    #L/d
CH4g_Milk <- CH4out_g / Mlk_Prod           #g/kg
CH4L_Milk <- CH4out_L / Mlk_Prod           #L/kg

#Manure Volume
Man_out <- -28.3 +3.6*An_DMIn + 12.4*Dt_K   #kg wet manure/d
Man_out <- ifelse(An_StatePhys == "Calf", NA, Man_out)
Man_Milk <- Man_out / Mlk_Prod #kg wet manure/kg milk

#Volatile Solids
Man_VolSld <- 0.364*(Dt_DMIn+InfRum_DMIn+InfSI_DMIn) + 0.026*An_NDF - 0.078*An_CP  #Empirical prediction from Ch 14 of NRC. NDF and CP should exclude arterial Infusions.
Man_VolSld2 <- Fe_OM - Dt_LgIn + Ur_Nout_g/0.16/1000  #Mass balance based volatile solids output in manure; Ur slightly overestimated by CP
VolSlds_Milk <- Man_VolSld / Mlk_Prod #kg/kg
VolSlds2_Milk <- Man_VolSld2 / Mlk_Prod #kg/kg;  mass balance derived

#Manure (urine + feces) Nitrogen
Man_Nout_g <- Ur_Nout_g + Fe_N_g + Scrf_N_g      #g/d; direct by summation of fecal, urinary, and scurf predictions
Man_Nout2_g <- An_NIn_g - An_Nprod_g             #g/d; by difference from intake and productive NP use
ManN_Milk <- Man_Nout_g / Mlk_Prod               #g N / kg of milk

#Manure macro minerals, g/d
Man_Ca_out <- Dt_CaIn - An_Ca_prod
Man_P_out <- Dt_PIn - An_P_prod
Man_Mg_out <- Dt_MgIn - An_Mg_prod
Man_K_out <- Dt_KIn - An_K_prod
Man_Na_out <- Dt_NaIn - An_Na_prod
Man_Cl_out <- Dt_ClIn - An_Cl_prod
Man_MacMin_out <- Man_Ca_out + Man_P_out + Man_Mg_out + Man_K_out + Man_Na_out + Man_Cl_out


#Manure micro minerals, mg/d
Man_Cu_out <- Dt_CuIn - An_Cu_prod
Man_Fe_out <- Dt_FeIn - An_Fe_prod
Man_Mn_out <- Dt_MnIn - An_Mn_prod
Man_Zn_out <- Dt_ZnIn - An_Zn_prod
Man_MicMin_out <- Man_Cu_out + Man_Fe_out + Man_Mn_out + Man_Zn_out #Not a complete accounting.  Many other micros also present

Man_Min_out_g <- Man_MacMin_out + Man_MicMin_out/1000  #also an incomplete summation as many micros are not represented.

#Efficiency of Dietary Mineral Use
#Macro minerals, g/g
CaProd_CaIn <- An_Ca_prod / Dt_CaIn
PProd_PIn <- An_P_prod / Dt_PIn
MgProd_MgIn <- An_Mg_prod / Dt_MgIn
KProd_KIn <- An_K_prod / Dt_KIn
NaProd_NaIn <- An_Na_prod / Dt_NaIn
ClProd_ClIn <- An_Cl_prod / Dt_ClIn

#Micro mineral, mg/mg
An_Fe_m <- 0  #no Fe maintenance requirement
CuProd_CuIn <- An_Cu_prod / Dt_CuIn
FeProd_FeIn <- An_Fe_prod / Dt_FeIn
MnProd_MnIn <- An_Mn_prod / Dt_MnIn
ZnProd_ZnIn <- An_Zn_prod / Dt_ZnIn


#Efficiency of Absorbed Mineral Use
#Macro, g/g
CaProd_CaAbs <- An_Ca_prod / Abs_CaIn
PProd_PAbs <- An_P_prod / Abs_PIn
MgProd_MgAbs <- An_Mg_prod / Abs_MgIn
KProd_KAbs <- An_K_prod / Abs_KIn
NaProd_NaAbs <- An_Na_prod / Abs_NaIn
ClProd_ClAbs <- An_Cl_prod / Abs_ClIn

#Micro, mg/mg
CuProd_CuAbs <- An_Cu_prod / Abs_CuIn
FeProd_FeAbs <- An_Fe_prod / Abs_FeIn
MnProd_MnAbs <- An_Mn_prod / Abs_MnIn
ZnProd_ZnAbs <- An_Zn_prod / Abs_ZnIn

#Required dietary mineral and vitamin densities to meet requirements
Dt_CaReq_DMI <- An_Ca_req / Dt_acCa / An_DMIn / 10
Dt_PReq_DMI <- An_P_req / Dt_acP / An_DMIn / 10
Dt_MgReq_DMI <- An_Mg_req / Dt_acMg / An_DMIn / 10
Dt_KReq_DMI <- An_K_req / Dt_acK / An_DMIn / 10
Dt_NaReq_DMI <- An_Na_req / Dt_acNa / An_DMIn / 10
Dt_ClReq_DMI <- An_Cl_req / Dt_acCl / An_DMIn / 10
Dt_SReq_DMI <- An_S_req / An_DMIn / 10
Dt_CoReq_DMI <- An_Co_req / An_DMIn
Dt_CuReq_DMI <- An_Cu_req / Dt_acCu / An_DMIn
Dt_FeReq_DMI <- An_Fe_req / Dt_acFe / An_DMIn
Dt_IReq_DMI <- An_I_req / An_DMIn
Dt_MnReq_DMI <- An_Mn_req / Dt_acMn / An_DMIn
Dt_SeReq_DMI <- An_Se_req / An_DMIn
Dt_ZnReq_DMI <- An_Zn_req / Dt_acZn / An_DMIn
Dt_VitAReq_DMI <- An_VitA_req / An_DMIn
Dt_VitDReq_DMI <- An_VitD_req / An_DMIn
Dt_VitEReq_DMI <- An_VitE_req / An_DMIn

#Water Use Efficiency
Man_Wa_out <- Man_out - Fe_OM - Ur_Nout_g/0.45/1000 - Man_Min_out_g/1000    #Manure Water estimate,  L/d
An_Wa_Insens <- An_WaIn - Mlk_Prod - Man_Wa_out                      #L/d;  by difference
WaIn_Milk <- An_WaIn / Mlk_Prod  #L/kg
ManWa_Milk <- Man_Wa_out / Mlk_Prod  #L/kg
Man_Wa_out <- ifelse(An_StatePhys=="Calf", 0, Man_Wa_out)

######################################################################################################
#   Aggregate nutrients, digestible nutrients, animal performance, and excretion into vectors        #
######################################################################################################
#Always generated.
an <- data.frame(DietID, An_Breed, An_StatePhys, An_AgeDay, An_Parity_rl, An_LactDay, An_GestDay, 
                 Env_TempCurr,Env_DistParlor,Env_TripsParlor,Env_Topo, Trg_FrmGain, Trg_RsrvGain,Trg_BWgain, 
                 Trg_MilkProd,Trg_NEmilk_Milk,Trg_NEmilkOut,Trg_MilkLacp,Trg_MilkTPp,Trg_Mlk_NP_g, Trg_MilkFatp,Trg_Mlk_Fat_g)

dmi <- data.frame(DietID,DMIn_eqn,Trg_Dt_DMIn, An_WaIn, An_DMIn, An_DMIn_BW, An_DMIn_MBW, Dt_DMInSum,
                  Dt_DMIn_Calf1,Dt_DMIn_ClfLiq,Dt_DMIn_ClfStrt,Dt_DMIn_ClfFor,
                  Dt_DMIn_Heif_H1,Dt_DMIn_Heif_H2,Dt_DMIn_Heif_HJ1,Dt_DMIn_Heif_HJ2,
                  Dt_DMIn_DryCow1, Dt_DMIn_DryCow2, Dt_DMIn_DryCow1_FarOff,Dt_DMIn_DryCow1_Close, 
                  Dt_DMIn_Lact1,Dt_DMIn_Lact2, An_NDFIn_BW,Fd_DMInp_Sum)

mlk <- data.frame(DietID,mProd_eqn, mLac_eqn, mPrt_eqn, An_305RHA_MlkTP, f_mPrt_max, Mlk_NPmx, MlkNP_MlkNPmx, mFat_eqn, 
                  Mlk_Prod, Mlk_Prod_NEalow,Mlk_Prod_MPalow, Mlk_NP_g, MlkNP_Milk,Mlk_NP_MPalow_Trg_g, 
                  Mlk_Arg_g,Mlk_His_g,Mlk_Ile_g,Mlk_Leu_g,Mlk_Lys_g,Mlk_Met_g,Mlk_Phe_g,Mlk_Thr_g,Mlk_Trp_g,Mlk_Val_g,
                  Mlk_Fat_g,MlkFat_Milk)

excr <- data.frame(DietID,Dt_GasE_IPCC2, GasE_DEIn, CH4out_L, CH4L_Milk,
                   Man_out, Man_Wa_out, An_Wa_Insens, WaIn_Milk, ManWa_Milk,
                   Man_VolSld, VolSlds_Milk, Man_Nout_g, ManN_Milk,
                   Man_Ca_out,Man_P_out,Man_Mg_out,Man_K_out,Man_Na_out,Man_Cl_out, Man_MacMin_out,
                   Man_Cu_out, Man_Fe_out, Man_Mn_out, Man_Zn_out, Man_MicMin_out, Man_Min_out_g,
                   Fe_N_g, Ur_Nout_g, Ur_Nout_CPcatab, Ur_Nend_g,Ur_Nend_sum_g)


#verbose is used to control output: 0=no output, 1=output required for an optimizer, 2+=full output
if(exists("verbose")==0) {verbose <- 3}  #use full output if argument not provided


if(verbose == 0) { out <- NA  #output an empty scalar

} else if(verbose == 1 & exists("Nutr_constr_active")) { 
     #output only vectors required by the optimizer
     imb <- data.frame(DietID,Imb_EAA,Imb_Arg,Imb_His,Imb_Ile,Imb_Leu,Imb_Lys,Imb_Met,Imb_Phe,Imb_Thr,Imb_Trp,Imb_Val)
     
     #Grab anything listed in the Nutrient Constraint table defined for the optimizer and add to a dataframe to be output
     nutr_tab <- subset(Nutr_constr, Nutr_constr$inclCon==1)
     nutr_nam <- paste(nutr_tab$Nutr)  #extract variable names from the df to a string vector
     nutr <- as.data.frame(`row.names<-`(do.call(cbind,mget(nutr_nam)), NULL))  #use do.call, cbind, and mget to build 
                                                                                #a matrix of the values.
     out <- list(dmi=dmi, excr=excr, imb=imb, mlk=mlk, nutr=nutr)

     
} else { #output the full NRC 2021 list of variables
dt <- data.frame(DietID,Dt_ForWet,Dt_ForDry,Dt_For,Dt_Conc,Dt_OM,Dt_Ash,
		Dt_NDF,Dt_NDFnf,Dt_ForNDF,Dt_ForNDF_NDF,Dt_ADF,Dt_Lg,Dt_Lg_NDF, Dt_NDFIn_BW,
		Dt_ForNDFIn_BW,Dt_NFC,Dt_St,Dt_WSC,Dt_rOM,
		Dt_CP,Dt_TP,Dt_NPNCP,Dt_NPN,Dt_CPA,Dt_CPB,Dt_CPC,
		Dt_CPA_CP,Dt_CPB_CP,Dt_CPC_CP,Dt_CFat,Dt_FA,
		Dt_C120,Dt_C140,Dt_C160,Dt_C161,Dt_C180, Dt_C181t,
		Dt_C181c,Dt_C182,Dt_C183,Dt_OtherFA,
		Dt_DMIn, Dt_AFIn,Dt_ForWetIn,Dt_ForDryIn,Dt_ForIn,Dt_PastIn,Dt_PastSupplIn,
		Dt_ConcIn,Dt_OMIn,Dt_AshIn,Dt_NDFIn,Dt_NDFnfIn,Dt_ForNDFIn,Dt_ADFIn,Dt_LgIn, 
		Dt_NFCIn,Dt_StIn,Dt_WSCIn,Dt_rOMIn,
		Dt_CPIn,Dt_TPIn,Dt_NPNCPIn,Dt_NPNIn,Dt_NPNDMIn,Dt_CPAIn,Dt_CPBIn,Dt_CPCIn,
		Dt_CFatIn,Dt_FAIn,Dt_FAhydrIn,Dt_FAhydr,
		Dt_ArgIn, Dt_HisIn, Dt_IleIn, Dt_LeuIn, Dt_LysIn, Dt_MetIn, Dt_PheIn, 
		Dt_ThrIn, Dt_TrpIn, Dt_ValIn,
		Dt_C120In,Dt_C140In,Dt_C160In,Dt_C161In,Dt_C180In, Dt_C181tIn,
		Dt_C181cIn,Dt_C182In,Dt_C183In,Dt_OtherFAIn,Dt_SatFAIn, Dt_UFAIn,Dt_MUFAIn,Dt_PUFAIn)

dig <- data.frame(DietID,Rum_dcNDF, Rum_DigNDFIn,Rum_DigNDFnfIn,Du_NDFPas,TT_dcNDF_Base, TT_dcNDF,Dt_DigNDFIn,An_DigNDFIn,Dt_DigNDFnfIn,Dt_DigNDF,An_DigNDF,
          Rum_dcSt,Rum_DigStIn,Du_StPas,Use_DNDF_IV,Dt_DigStIn_Base,TT_dcSt_Base,TT_dcSt,Dt_DigStIn,An_DigStIn,An_DigSt,
          Dt_DigrOMtIn,Dt_DigrOMaIn,Dt_DigrOMt,Dt_DigrOMa,
          An_DigrOMtIn,An_DigrOMaIn,TT_dcrOMa,TT_dcrOMt,An_DigrOMt,An_DigrOMa,Dt_DigWSCIn,
          RUP_eqn,Dt_RUPBIn,An_RUPIn,Dt_RUPIn,Dt_RUPIn.dt, An_RUP, Dt_RUP, Dt_RUP_CP,An_RDPIn,Dt_RDPIn, An_RDP, Dt_RDP, Dt_RDP_CP, Dt_idRUPIn,
		Du_EndCP_g,Du_EndN_g,
		Du_NAN_g,Du_NANMN_g,Dt_DigCPaIn,Dt_DigCPtIn,Dt_DigTPaIn,Dt_DigTPtIn,
		Dt_DigCPt,An_DigCPaIn,An_DigCPtIn,An_DigTPaIn,An_DigTPtIn,TT_dcAnTPt,TT_dcAnCPa,
		TT_dcDtFA,Dt_DigFAIn,An_DigFAIn,An_DigFA,
		Dt_DigOMtIn, Dt_DigOMaIn, Dt_DigOMt, Dt_DigOMa,
		An_DigOMtIn,An_DigOMaIn, TT_dcOMa,TT_dcOMt,An_DigOMt,An_DigOMa,
		Dt_DigC120In,Dt_DigC140In,Dt_DigC160In,Dt_DigC161In,Dt_DigC180In,Dt_DigC181tIn,
		Dt_DigC181cIn,Dt_DigC182In,Dt_DigC183In,Dt_DigOtherFAIn,Dt_DigSatFAIn,Dt_DigUFAIn,Dt_DigMUFAIn,Dt_DigPUFAIn,
		Dt_ArgRUPIn,Dt_HisRUPIn,Dt_IleRUPIn,Dt_LeuRUPIn,Dt_LysRUPIn,Dt_MetRUPIn,Dt_PheRUPIn,Dt_ThrRUPIn,Dt_TrpRUPIn,Dt_ValRUPIn,
		Du_ArgEndP,Du_HisEndP,Du_IleEndP,Du_LeuEndP,Du_LysEndP,Du_MetEndP,Du_PheEndP,Du_ThrEndP,Du_TrpEndP,Du_ValEndP,
		Du_Arg,Du_His,Du_Ile,Du_Leu,Du_Lys,Du_Met,Du_Phe,Du_Thr,Du_Trp,Du_Val,
		Du_Arg24h,Du_His24h,Du_Ile24h,Du_Leu24h,Du_Lys24h,Du_Met24h,Du_Phe24h,Du_Thr24h,Du_Trp24h,Du_Val24h,
		Dt_IdArgRUPIn,Dt_IdHisRUPIn,Dt_IdIleRUPIn,Dt_IdLeuRUPIn,Dt_IdLysRUPIn,Dt_IdMetRUPIn,Dt_IdPheRUPIn,Dt_IdThrRUPIn,Dt_IdTrpRUPIn,Dt_IdValRUPIn,
		Dt_IdArgIn,Dt_IdHisIn,Dt_IdIleIn,Dt_IdLeuIn,Dt_IdLysIn,Dt_IdMetIn,Dt_IdPheIn,Dt_IdThrIn,Dt_IdTrpIn,Dt_IdValIn,
		Fe_OM,Fe_St,Fe_NDF,Fe_NDFnf,Fe_CP,Fe_N,Fe_RumMiCP,Fe_MiTP,Fe_RUP, Fe_FA,Fe_rOM,Fe_rOMend,
		Dt_Fe_RUPout,Fe_CPend,Fe_Nend)

enrg <- data.frame(DietID,Dt_GEIn,Dt_DEIn,An_DEIn,An_DEInp,Dt_DE,An_DE,Dt_TDN,Dt_TDNIn,
		Dt_DEStIn,Dt_DErOMIn,Dt_DENDFIn,Dt_DECPIn,Dt_DETPIn,Dt_DENPNCPIn,Fe_DEMiCPend,Fe_DERDPend,Fe_DERUPend,Dt_DEFAIn,
		An_DEStIn,An_DErOMIn,An_DENDFIn,An_DECPIn,An_DETPIn,An_DERDTPIn,An_DEidRUPIn,An_DENPNCPIn,
		An_DEFAIn,Dt_DEIn_ClfLiq,Dt_DEIn_base_ClfLiq,Dt_DEIn_base_ClfDry,An_GasEOut,Ur_DEout,
		An_MEIn,An_ME,Dt_MEIn_ClfLiq,An_MEIn_ClfDry,An_MEprod_Avail,An_MEbal,
		An_NEIn,An_NE,An_NEprod_Avail,An_MEavail_Milk,An_NEbal, Mlk_MEout, Mlk_NEout, MlkNE_Milk)

micr <- data.frame(DietID,MiN_eqn,Du_MiN_g,Du_MiN_NRC2021_g,Du_MiN_VTln_g,Du_MiN_VTnln_g,Du_MiN_NRC2001_g,
          Du_MiCP_g,Du_MiTP_g,Du_idMiCP_g,Du_idMiTP_g,RDPIn_MiNmax,
          Du_ArgMic,Du_HisMic,Du_IleMic,Du_LeuMic,Du_LysMic,Du_MetMic,Du_PheMic,Du_ThrMic,Du_TrpMic,Du_ValMic,
          Du_IdArgMic,Du_IdHisMic,Du_IdIleMic,Du_IdLeuMic,Du_IdLysMic,Du_IdMetMic,Du_IdPheMic,Du_IdThrMic,Du_IdTrpMic,Du_IdValMic)

abs <- data.frame(DietID,Abs_Arg_g,Abs_His_g,Abs_Ile_g,Abs_Leu_g,Abs_Lys_g,Abs_Met_g,Abs_Phe_g, Abs_Thr_g, Abs_Trp_g, Abs_Val_g, 
          Abs_EAA_g, Abs_EAA2_g, Abs_EAA2b_g, Abs_EAA2_HILKM_g, Abs_EAA2_RHILKM_g, Abs_neAA_g, Abs_OthAA_g, 
          Abs_Arg_MPp,Abs_His_MPp,Abs_Ile_MPp,Abs_Leu_MPp,Abs_Lys_MPp,Abs_Met_MPp,Abs_Phe_MPp,Abs_Thr_MPp,Abs_Trp_MPp,Abs_Val_MPp,
          Abs_Arg_DEI,Abs_His_DEI,Abs_Ile_DEI,Abs_Leu_DEI,Abs_Lys_DEI,Abs_Met_DEI,Abs_Phe_DEI,Abs_Thr_DEI,Abs_Trp_DEI,Abs_Val_DEI)

inf <- data.frame(DietID,Inf_DMIn,Inf_StIn, Inf_GlcIn,Inf_NDFIn,Inf_ADFIn,Inf_FAIn,Inf_AshIn,
      Inf_VFAIn,Inf_AcetIn,Inf_PropIn,Inf_ButrIn,Inf_CPIn, Inf_NPNCPIn,
      Inf_ArgRUPIn,Inf_HisRUPIn,Inf_IleRUPIn,Inf_LeuRUPIn,Inf_LysRUPIn,Inf_MetRUPIn,Inf_PheRUPIn,Inf_ThrRUPIn,Inf_TrpRUPIn,Inf_ValRUPIn,
      Inf_IdArgIn,Inf_IdHisIn,Inf_IdIleIn,Inf_IdLeuIn,Inf_IdLysIn,Inf_IdMetIn,Inf_IdPheIn,Inf_IdThrIn,Inf_IdTrpIn,Inf_IdValIn,
      Inf_DEAcetIn,Inf_DEPropIn,Inf_DEButrIn,InfRum_RUPIn,InfRum_RDPIn,InfRum_CPIn,InfSI_CPIn,InfSI_idCPIn,InfArt_TPIn,Fe_InfCP)

mp <- data.frame(DietID,An_CPIn_g, An_MPIn_g,An_MPIn,An_MP,Dt_MPIn, Dt_MP, An_NPuse_g, An_NPxprt_g, 
          Fe_MPendUse_g, Scrf_MPUse_g, Ur_MPendUse_g, Body_MPUse_g_Trg, Gest_MPUse_g_Trg, Mlk_MPUse_g, 
          An_MPuse_g,An_MPuse_g_Trg,An_NPBal_g,An_MPBal_g, An_MPIn_MEIn, An_MPuse_MEuse)
main <- data.frame(DietID,An_MEmUse,An_NEmUse,An_NEmUse_NS,An_NEmUse_Act,An_NEm_Act_Graze,
         An_NEm_Act_Parlor,An_NEmUse_Env,Fe_NPend_g,Scrf_NP_g,Ur_NPend_g, An_NPm_Use,
         Fe_ArgMet_g,Fe_HisMet_g,Fe_IleMet_g,Fe_LeuMet_g,Fe_LysMet_g,Fe_MetMet_g,
         Fe_PheMet_g,Fe_ThrMet_g,Fe_TrpMet_g,Fe_ValMet_g,
         Scrf_Arg_g,Scrf_His_g,Scrf_Ile_g,
         Scrf_Leu_g,Scrf_Lys_g,Scrf_Met_g,Scrf_Phe_g,Scrf_Thr_g,Scrf_Trp_g,Scrf_Val_g,
         Ur_EAAEnd_g,Ur_ArgEnd_g,Ur_HisEnd_g,Ur_IleEnd_g,Ur_LeuEnd_g,
         Ur_LysEnd_g,Ur_MetEnd_g,Ur_PheEnd_g,Ur_ThrEnd_g,Ur_TrpEnd_g,Ur_ValEnd_g,
         An_ArgUse_g,An_HisUse_g,An_IleUse_g,An_LeuUse_g,An_LysUse_g,An_MetUse_g,
         An_PheUse_g,An_ThrUse_g,An_TrpUse_g,An_ValUse_g,
         An_ArgBal_g,An_HisBal_g,An_IleBal_g,An_LeuBal_g,An_LysBal_g,An_MetBal_g,
         An_PheBal_g,An_ThrBal_g,An_TrpBal_g,An_ValBal_g)

gest <- data.frame(DietID,An_Preg,An_PostPartDay, An_PrePartDay,An_PrePartWkDurat,Fet_BWbrth,  
          GrUter_Wt, Uter_Wt, Fet_Wt,GrUter_BWgain, Uter_BWgain, Fet_BWgain, Conc_BWgain, Gest_MEuse, Gest_NPuse_g,
          Gest_Arg_g,Gest_His_g,Gest_Ile_g,Gest_Leu_g,Gest_Lys_g,Gest_Met_g,Gest_Phe_g,Gest_Thr_g,Gest_Trp_g,Gest_Val_g)


bod <- data.frame(DietID, FrmGain_eqn,RsrvGain_eqn,
          An_BW,An_MBW,An_BCS,An_BW_empty,An_BWnp,An_BWnp3,An_BWnp3_empty,Frm_Gain,Frm_Gain_empty, Rsrv_Gain,
         Rsrv_Gain_empty,Body_Gain,Body_Gain_empty,An_GutFill_BW, An_BodConcgain,
         Frm_Fatgain, Rsrv_Fatgain, Body_Fatgain,Body_NonFatGain,Body_AshGain,Body_WatGain,
         An_Days_BCSdelta1,An_REgain,Frm_NEgain, Rsrv_NEgain, 
         Body_NPgain, Body_NPgain_g, Frm_NPgain, Rsrv_NPgain,
         Body_ArgGain_g,Body_HisGain_g,Body_IleGain_g,Body_LeuGain_g,Body_LysGain_g,Body_MetGain_g,
         Body_PheGain_g,Body_ThrGain_g,Body_TrpGain_g,Body_ValGain_g,
         Body_Gain_NEalow, An_MPavail_Gain_Trg,Body_NPgain_MPalowTrg_g, Body_Gain_MPalowTrg)

MV <- data.frame(DietID, Dt_CaIn, Dt_PIn, Dt_PinorgIn, Dt_PorgIn, 
   	Dt_NaIn, Dt_MgIn, Dt_KIn, Dt_ClIn, Dt_SIn, Dt_CoIn, Dt_CuIn, Dt_CrIn, Dt_FeIn, 
	   Dt_IIn, Dt_MnIn, Dt_MoIn, Dt_SeIn, Dt_ZnIn, Dt_VitAIn, Dt_VitDIn, 
	   Dt_VitEIn, Dt_CholineIn, Dt_BiotinIn, Dt_NiacinIn, Dt_B_CaroteneIn,
	   Dt_Ca, Dt_P, Dt_Pinorg, Dt_Porg,  
	   Dt_Na, Dt_Mg, Dt_K, Dt_Cl, Dt_S, Dt_Co, Dt_Cu, Dt_Cr, Dt_Fe, 
	   Dt_I, Dt_Mn, Dt_Mo, Dt_Se, Dt_Zn,An_DCADmeq, Dt_VitA, Dt_VitD, 
	   Dt_VitE, Dt_Choline, Dt_Biotin, Dt_Niacin, Dt_B_Carotene,
	   Abs_CaIn,Abs_PIn,Abs_NaIn,Abs_MgIn,Abs_KIn,Abs_ClIn,
	   Abs_CuIn,Abs_FeIn,Abs_MnIn,Abs_ZnIn,
	   An_Ca_req, An_P_req, An_Mg_req, An_Na_req, An_Cl_req, An_K_req, An_S_req, 
	   An_Co_req,An_Cu_req,An_I_req,An_Fe_req, An_Mn_req, An_Se_req, An_Zn_req, 
	   An_VitA_req, An_VitD_req, An_VitE_req,
	   An_Ca_bal,An_P_bal,An_Mg_bal,An_Na_bal,An_Cl_bal,An_K_bal,An_S_bal, 
	   An_Co_bal,An_Cu_bal,An_I_bal,An_Fe_bal, An_Mn_bal, An_Se_bal, An_Zn_bal, 
	   An_VitA_bal, An_VitD_bal, An_VitE_bal,
	   Fe_P_m, Ur_P_m, Fe_Mg_m, Ur_Mg_m, Fe_K_m, Ur_K_m)

eff <- data.frame(DietID,An_DE_GE,An_ME_DE,An_NE_DE,An_NE_ME,An_NEprod_GE,An_NEmlk_GE,Km_ME_NE,Kg_ME_NE,Km_ME_NE_Clf,
        An_MP_CP, MlkNP_AnCP, MlkNP_AnMP, An_MP_NP,Xprt_NP_MP_Trg, Kl_MP_NP, Kl_MP_NP_Trg,
	   An_NPprod_MPIn, An_MPIn_MEIn, An_MPuse_MEuse,
  	   DtArgRUP_DtArg,DtHisRUP_DtHis,DtIleRUP_DtIle,DtLeuRUP_DtLeu,DtLysRUP_DtLys,DtMetRUP_DtMet,
	   DtPheRUP_DtPhe,DtThrRUP_DtThr,DtTrpRUP_DtTrp,DtValRUP_DtVal,
	   DuArg_DtArg,DuHis_DtHis,DuIle_DtIle,DuLeu_DtLeu,DuLys_DtLys,DuMet_DtMet,DuPhe_DtPhe,DuThr_DtThr,
	   DuTrp_DtTrp,DuVal_DtVal,
	   IdArg_DtArg,IdHis_DtHis,IdIle_DtIle,IdLeu_DtLeu,IdLys_DtLys,IdMet_DtMet,IdPhe_DtPhe,IdThr_DtThr,
	   IdTrp_DtTrp,IdVal_DtVal,
	   MlkArg_AbsArg,MlkHis_AbsHis,MlkIle_AbsIle,MlkLeu_AbsLeu,MlkLys_AbsLys,MlkMet_AbsMet,
	   MlkPhe_AbsPhe,MlkThr_AbsThr,MlkTrp_AbsTrp,MlkVal_AbsVal,MlkArg_DtArg,MlkHis_DtHis,MlkIle_DtIle,MlkLeu_DtLeu,
	   MlkLys_DtLys,MlkMet_DtMet,MlkPhe_DtPhe,MlkThr_DtThr,MlkTrp_DtTrp,MlkVal_DtVal,
	   AnArgUse_AbsArg,AnHisUse_AbsHis,AnIleUse_AbsIle,AnLeuUse_AbsLeu,AnLysUse_AbsLys,
	   AnMetUse_AbsMet,AnPheUse_AbsPhe,AnThrUse_AbsThr,AnTrpUse_AbsTrp,AnValUse_AbsVal,AnEAAUse_AbsEAA)

imb <- data.frame(DietID,Imb_EAA,Imb_Arg,Imb_His,Imb_Ile,Imb_Leu,Imb_Lys,Imb_Met,Imb_Phe,Imb_Thr,Imb_Trp,Imb_Val)

oth <- data.frame(DietID, Env_TempCurr,
      Dt_MEIn_ClfLiq,Dt_ME_ClfLiq,An_MEIn_ClfDry,An_ME_ClfDry,Km_ME_NE_Clf)

#The following tables are recreations of some of the NRC software tables.  They do not need to be translated into C sharp
if("Fd_Name" %in% names(f)==FALSE) f$Fd_Name <- f$Feed  #Fd_Name from NRC software but Feed from NANP database.
f$Fd_DEIn_base <- f$Fd_DE_base * f$Fd_DMIn       #need to test for DE_base first as it won't always be present.
Dt_DEIn_base <- sum(f$Fd_DEIn_base, na.rm=TRUE)
f$Fd_RDPIn <- f$Fd_RDP/100*f$Fd_DMIn

Tbl1_1 <- data.frame("Animal Type" = An_StatePhys,
                   "Animal Breed" = An_Breed,
                   "Body Weight, kg" = An_BW,
                   "Empty BW, kg" = An_BW_empty,
                   "Birth Weight, kg" = Fet_BWbrth,
                   "Mature Weight, kg" = An_BW_mature,
                   "Mature Empty BW, kg" = An_BWmature_empty,
                   "Age, d" = An_AgeDay,
                   "Condition Score, 1 to 5" = An_BCS,
                   "Percent First Parity" = (2-An_Parity_rl)*100,
                   "Days in Milk" = An_LactDay,
                   "Age At First Calving, d)" = An_AgeConcept1st + 280,
                   "Days Pregnant" = An_GestDay,
                   "Temperature, C)" = Env_TempCurr,
                   "Use In vitro NDF digest" = Use_DNDF_IV,
                   "Feeding Monensin, 0=No, 1=Yes" = Monensin_eqn,
                   "Grazing" = An_Grazing,
                   "Topography" = Env_Topo,
                   "Dist. (Pasture to Parlor, m)" = Env_DistParlor,
                   "One-Way Trips to the Parlor, m)" = Env_TripsParlor)
Tbl1_1 <- t(Tbl1_1)
colnames(Tbl1_1) <- "Values"

Tbl1_2 <- t(data.frame(Trg_MilkProd,
                     Trg_MilkProd_EPcor,
                     Trg_MilkFatp,
                     Trg_MilkTPp,
                     Trg_MilkLacp,
                     Trg_Mlk_Fat,
                     Trg_Mlk_NP,
                     Trg_MilkProd * Trg_MilkLacp/100,
                     Trg_FrmGain,
                     Trg_RsrvGain,
                     GrUter_BWgain,
                     An_BodConcgain))
rownames(Tbl1_2) <- c("Milk Production", "Energy/Protein Corrected Milk, kg/d", 
                   "Milk Fat, %", "Milk True Protein", "Milk Lactose,%", "Milk Fat, kg/d", 
                   "Milk True Protein, kg/d", "Milk Lactose, kg/d", "Frame Gain, kg/d", 
                   "Body Reserves Gain, kg/d", "Gravid Uterine Gain, kg/d", 
                   "Total Gain, kg/d")
colnames(Tbl1_2) <- "Target Performance:"

Tbl1_3_NameList <- c("Allowable Performance","Dry Matter Intake Eqn Used")
Tbl1_3_VarVals <- c(NA,DMIn_eqn)
if(An_StatePhys == "Calf") {
     Tbl1_3_NameList <- c(Tbl1_3_NameList, "Liquid DMI, kg/d",
                         "Predicted Starter DMI, kg/d", "Forage DMI (Anim Factors), kg/d")
     Tbl1_3_VarVals <- c(Tbl1_3_VarVals, Dt_DMIn_ClfLiq, Dt_DMIn_ClfStrt, Dt_DMIn_ClfFor)}
if(An_StatePhys == "Heifer" & An_PrePartWk < An_PrePartWkDurat) {
     Tbl1_3_NameList <- c(Tbl1_3_NameList, "Predicted DMI (Anim Factors), kg/d", "Predicted DMI (Feed Factors), kg/d")
     Tbl1_3_VarVals <- c(Tbl1_3_VarVals, Dt_DMIn_Heif_NRCai, Dt_DMIn_Heif_NRCadi)} 
if(An_StatePhys == "Heifer" & An_PrePartWk > An_PrePartWkDurat) {
     Tbl1_3_NameList <- c(Tbl1_3_NameList, "Predicted Ind. DMI (Anim Factors), kg/d", "Predicted Ind. DMI (Feed Factors), kg/d", 
                          "Predicted Pen DMI (Anim Factors), kg/d", "Predicted Pen DMI (Feed Factors), kg/d")
     Tbl1_3_VarVals <- c(Tbl1_3_VarVals, Dt_DMIn_Heif_NRCai, Dt_DMIn_Heif_NRCadi, Dt_DMIn_Heif_NRCap, Dt_DMIn_Heif_NRCadp)} 
if(An_StatePhys == "Lactating Cow") {
     Tbl1_3_NameList <- c(Tbl1_3_NameList,"Predicted DMI (Anim Factors), kg/d","Predicted DMI (Feed Factors), kg/d")
     Tbl1_3_VarVals <- c(Tbl1_3_VarVals, Dt_DMIn_Lact1, Dt_DMIn_Lact2)}
if(An_StatePhys == "Dry Cow") {
     Tbl1_3_NameList <- c(Tbl1_3_NameList, "Predicted DMI (Anim Factors), kg/d")
     Tbl1_3_VarVals <- c(Tbl1_3_VarVals, Dt_DMIn_DryCow1)}
Tbl1_3 = data.frame(Tbl1_3_VarVals)
rownames(Tbl1_3) <- Tbl1_3_NameList
colnames(Tbl1_3) <- "Values"

Tbl1_3b <- data.frame(An_DMIn, An_DMIn_BW*100, An_MPIn_MEIn, An_MPuse_MEuse, Body_Gain_NEalow, Body_Gain_MPalowTrg,
                     Mlk_Prod_NEalow, Mlk_Prod_MPalow, Mlk_Prod_NEalow_EPcor, Mlk_EPcorNEalow_DMIn, An_Days_BCSdelta1, NA, Mlk_Prod,
                     Mlk_Fat,Mlk_NP,An_305RHA_MlkTP, MlkNP_MlkNPmx)
Tbl1_3b <- t(Tbl1_3b)
rownames(Tbl1_3b) <- c("DMI Used, kg/d", "DMI, % BW", "MP Supply / ME Supply, g/mcal","MP Use / ME Use, g/mcal",
                       "NE Allow Body Gain, kg/d","MP Allow Body Gain, kg/d","NEL Allow Milk, kg/d","MP Allow Milk, kg/d",
                         "Energy/Protein Corrected Milk, kg/d","EPCM/DMI, kg/kg","Days to change 1 BCS","Nutrient Predicted Performance:",
                         "Milk Production, kg/d","Milk Fat, kg/d","Milk True Protein, kg/d","Current Milk True Protein RHA, kg/305d", 
                         "Predicted Milk Protein/Milk NP 305d Maximum")
colnames(Tbl1_3b) <- "Values"
Tbl1_3 <- rbind(Tbl1_3, Tbl1_3b)

Tbl2_1 <- data.frame(DM=Dt_DM, Forage=Dt_For, ME=An_ME, NEL=An_NE, CP=An_CP,
                     RUP=An_RUP, RDP=An_RDP, "DigRUP"=An_idRUP*100, MP=An_MP, ADF=An_ADF, NDF=An_NDF, ADF_NDF=An_ADF/An_NDF,
                     "ForNDF"=Dt_ForNDF,Starch=An_St,rOM=An_rOM, WSC=Dt_WSC, Ash=An_Ash,"TotalFA"=An_FA,
                    Ca=Dt_Ca,P=Dt_P,Mg=Dt_Mg, K=Dt_K, Na=Dt_Na, Cl=Dt_Cl, S=Dt_S, "DCAD meq"=An_DCADmeq,
                    "Micro Min, mg/kg"=NA, Co=Dt_Co, Cu=Dt_Cu, Fe=Dt_Fe, I=Dt_I, Mn=Dt_Mn, Se=Dt_Se, Zn=Dt_Zn)
Tbl2_1 <- t(Tbl2_1)
colnames(Tbl2_1) <- "Values"

Tbl2_2 <- as.data.frame(f[,c("Fd_Name","Fd_AFIn","Fd_AFInp","Fd_DMIn","Fd_DMInp")])
Total <- c("Total", Dt_AFIn, sum(Tbl2_2$Fd_AFInp,na.rm=TRUE), Dt_DMInSum, sum(Tbl2_2$Fd_DMInp, na.rm=TRUE))
Tbl2_2 <- rbind(Tbl2_2, Total)

Tbl3_1 <- f[, c("Fd_Name","Fd_DM","Fd_DEIn_base","Fd_CPIn","Fd_RDPIn","Fd_RUPIn","Fd_idRUPIn","Fd_NDFIn","Fd_StIn","Fd_FAIn")]
Total <- data.frame(Fd_Name="Total", Dt_DMIn, Dt_DEIn_base, Dt_CPIn, Dt_RDPIn, Dt_RUPIn, Dt_idRUPIn, Dt_NDFIn, Dt_StIn, Dt_FAIn)
colnames(Total) <- colnames(Tbl3_1)
Tbl3_1 <- rbind(Tbl3_1, Total)
Tbl3_1t <- t(Tbl3_1)

Tbl4_1 <- data.frame(GE=c(An_GEIn, An_GE, 100,"", ""),
                     FE=c(Fe_DEout, Fe_DE, Fe_DE_GE*100, "", ""),
                     DE=c(An_DEIn, An_DE, An_DE_GE*100, An_DEIn/An_DEIn*100, ""),	
                     "Urinary E"=c(Ur_DEout, UrDE_DMIn, UrDE_GEIn*100, UrDE_DEIn*100, ""),	
                     "Gaseous E"=c(An_GasEOut, GasE_DMIn, GasE_GEIn*100, GasE_DEIn*100, ""),	
                     ME=c(An_MEIn, An_ME, An_ME_GE*100, An_ME_DE*100, An_MEIn/An_MEIn*100),
                     NEL=c(An_NEIn, An_NE, An_NE_GE*100, An_NE_DE*100, An_NE_ME*100))
rownames(Tbl4_1) <- c("Mcal/d", "Mcal/kg", "% of GE", "% of DE", "% of ME")
Tbl4_1 <- t(Tbl4_1)

Tbl4_2 <- data.frame(Maintenance=c(An_MEmUse_NS, An_NEmUse_NS, An_NEmNS_DE, Km_ME_NE),  
                    "Entered Milk"=c(Trg_Mlk_MEout, Trg_Mlk_NEout, Trg_NEmilk_DEIn, Kl_ME_NE),
                    "Nutr Allow Milk"=c(Mlk_MEout, Mlk_NEout, Mlk_NE_DE, Kl_ME_NE),
                    Pregnancy=c(Gest_MEuse, Gest_NELuse, Gest_NE_DE, Ky_ME_NE),
                    "Grazing Activity"=c(An_MEmUse_Act, An_NEmUse_Act, An_NEmAct_DE, Km_ME_NE),  
                    "Thermal Stress"=c(An_MEmUse_Env, An_NEmUse_Env, An_NEmEnv_DE, Km_ME_NE),  
                    "Frame Gain"=c(Frm_MEgain, Frm_NELgain, Frm_NE_DE, Kf_ME_RE),
                    "Reserves Gain"=c(Rsrv_MEgain, Rsrv_NELgain, Rsrv_NE_DE, Kr_ME_RE),
                    "Empty Body Gain"=c(An_MEgain, An_NELgain, An_NEgain_DE, Kg_ME_NE),
                    "Total Req for Nutr Allow"=c(An_MEuse, An_NELuse, " ", " "),
                    "Total Req for Entered Production"=c(Trg_MEuse, Trg_NELuse, " ", " "),
                    "Supply - Entered Req."=c(Trg_MEbal,Trg_NELbal, " "," "),
                    "Supply - Nutr Allow Req."=c(An_MEbal,An_NELbal, " "," "))
rownames(Tbl4_2) <- c("ME, mcal/d", "NEL, mcal/d", "NE:DE", "NE:ME")
Tbl4_2 <- t(Tbl4_2)

Tbl4_3 <- data.frame(NDF=c(An_NDFIn,   TT_dcNDF_Base,TT_dcNDF,  An_DigNDFIn,  NA,         An_DigNDFIn,  TT_dcNDF,   En_NDF, An_DENDFIn),
                     Starch=c(An_StIn, TT_dcSt_Base, TT_dcSt,   An_DigStIn,   NA,         An_DigStIn,   TT_dcSt,    En_St,  An_DEStIn),
                     FA=c(An_FAIn,     TT_dcAnFA,    TT_dcAnFA, An_DigFAIn,   NA,         An_DigFAIn,   TT_dcAnFA,  En_FA,  An_DEFAIn),
                    rOM=c(An_rOMIn,    TT_dcrOMt,    TT_dcrOMt, An_DigrOMtIn, Fe_rOMend,  An_DigrOMaIn, TT_dcrOMa,  En_rOM, An_DErOMIn),
                    CP=c(An_CPIn,      TT_dcDtCPt,   TT_dcDtCPt,An_DigCPtIn,  Fe_CPend,   An_DigCPaIn,  TT_dcDtCPa, En_CP,  An_DECPIn),
                    RDPNPN=c(An_RDNPNCPIn, 100,      NA,        An_RDNPNCPIn, NA,         An_RDNPNCPIn, 100,        En_NPNCP,An_DENPNCPIn),
                    RDTP=c(An_RDTPIn, 100, NA,    An_RDTPIn,    Fe_RDPend, An_RDPIn-Fe_RDPend,(An_RDPIn-Fe_RDPend)/An_RDPIn, En_CP, An_DERDTPIn),
                    RUP=c(An_RUPIn,   SI_dcAnRUP, NA,An_idRUPIn,Fe_RUPend, An_idRUPIn-Fe_RUPend,(An_idRUPIn-Fe_RUPend)/An_idRUPIn, En_CP, An_DEidRUPIn),
                    OM=c(An_OMIn,      TT_dcOMt_Base,TT_dcOMt,  An_DigOMtIn,  Fe_OM_end,  An_DigOMaIn,  TT_dcOMa,   En_OM,  An_DEIn))
rownames(Tbl4_3) <- c("Intake","Base DC","Adj DC","True Digest","End_Fec","App Digest","App DC","Hc","DE")
Tbl4_3 <- t(Tbl4_3) #Transposed to match NRC software table.

Tbl5_1 <- data.frame(C120=c(Dt_C120_FA, Dt_C120, Dt_C120In*1000, NA),
                    C140=c(Dt_C140_FA, Dt_C140, Dt_C140In*1000, NA),
                    C160=c(Dt_C160_FA, Dt_C160, Dt_C160In*1000, NA),
                    C161=c(Dt_C161_FA, Dt_C161, Dt_C161In*1000, NA),
                    C180=c(Dt_C180_FA, Dt_C180, Dt_C180In*1000, NA),
                    C181t=c(Dt_C181t_FA, Dt_C181t, Dt_C181tIn*1000, NA),
                    C181c=c(Dt_C181c_FA, Dt_C181c, Dt_C181cIn*1000, NA),
                    C182=c(Dt_C182_FA, Dt_C182, Dt_C182In*1000, NA),
                    C183=c(Dt_C183_FA, Dt_C183, Dt_C183In*1000, NA),
                    "Other FA"=c(Dt_OtherFA_FA, Dt_OtherFA, Dt_OtherFAIn*1000, NA),
                    "Total FA"=c("100", Dt_FA, Dt_FAIn*1000, Dt_DigFAIn*1000),
                    "Saturated FA"=c(Dt_SatFA_FA, Dt_SatFA, Dt_SatFAIn*1000, NA),
                    "Total UFA"=c(Dt_UFA_FA, Dt_UFA, Dt_UFAIn*1000, NA),
                    "Total MUFA"=c(Dt_MUFA_FA, Dt_MUFA, Dt_MUFAIn*1000, NA),
                    "Total PUFA"=c(Dt_PUFA_FA, Dt_PUFA, Dt_PUFAIn*1000, NA))
Tbl5_1 <- t(Tbl5_1)  #Converting to text on Transpose for some reason.  Need to sort out.
colnames(Tbl5_1) <- c("% of Total FA", "% Of DM", "Intake, g/d", "Digested, g/d")
rownames(Tbl5_1) <- c("C12:0","C14:0","C16:0","C16:1","C18:0","C18:1t","C18:1c","C18:2","C18:3","Other FA","Total FA",
                    "Saturated FA","Total UFA","Total MUFA","Total PUFA")

Tbl6_1 <- data.frame("Animal Inputs:"="",
                    "DE-Non Protein"=An_DEInp,
                    "Ruminal Digestion and Outflow:"="",
                    "___Ruminally Digested Starch"=Rum_DigStIn,
                    "___Ruminally Digested NDF"=Rum_DigNDFIn,
                    "___Microbial Protein"=Du_MiCP,
                    "___RDP minus MiCP, kg/d" = An_RDPbal_g/1000,
                    "___Rumen Undegrad Protein"=An_RUPIn,
                    "Metabolized Protein Supply"=An_MPIn,
                    "___MP from Microbes"=Du_idMiTP,
                    "___MP from RUP"=An_idRUPIn,
                    "___MP from Body Wt Change"= ifelse(Body_MPUse_g_Trg < 0, -Body_MPUse_g_Trg/1000, 0))
Tbl6_1 <- t(Tbl6_1)

#MP, CP, and NP Supply and Use, g/d.  CP is required for calves and heifers.
Tbl6_2 <- data.frame("Scurf" = c(Scrf_NP_g, Scrf_CP_g, Scrf_MPUse_g_Trg),  #Don't really need the vector names here as respecified below
                    "EndogUrinary" = c(Ur_NPend_g, NA, Ur_MPendUse_g),  #so that punctuation is properly captured.
                    "MetabFecal" = c(Fe_NPend_g, Fe_CPend_g, Fe_MPendUse_g_Trg),
                    "FrameGrowth"= c(Frm_NPgain_g, Frm_CPgain_g, Frm_MPUse_g_Trg),
                    "BodyReserves" = c(Rsrv_NPgain_g, Rsrv_CPgain_g, Rsrv_MPUse_g_Trg),
                    "Pregnancy" = c(Gest_NPgain_g, Gest_NCPgain_g, Gest_MPUse_g_Trg),
                    "Lactation_User" = c(Trg_Mlk_NP_g, NA, Mlk_MPUse_g_Trg),
                    "__________________________" = c(NA, NA,NA),
                    "Total_User" = c(Trg_NPuse_g, NA, An_MPuse_g_Trg),
                    "Supply" = c(NA, An_CPIn_g, An_MPIn_g),
                    "Balance_User" = c(NA, NA, An_MPBal_g_Trg),
                    "Eff_User" = c(NA, NA, Xprt_NP_MP_Trg),
                    "__________________________" = c(NA, NA,NA),
                    "Lactation_NutrAllow" = c(Mlk_NP_g, NA, Mlk_MPUse_g),
                    "Total_NutrAllow" = c(An_NPuse_g, An_NCPuse_g, An_MPuse_g),
                    "Balance_User" = c(NA, NA, An_MPBal_g),
                    "Eff_NutrAllow" = c(NA, NA, Xprt_NP_MP),
                    "__________________________" = c(NA, NA,NA),
                    "MPSupply_MESupply" = c(NA, NA, An_MPIn_MEIn),
                    "MPUse_MEUse" = c(NA, NA, An_MPuse_MEuse))
Tbl6_2 <- t(Tbl6_2) #Transpose
colnames(Tbl6_2) <- c("Net TP", "Net CP", "MP (a)")
rownames(Tbl6_2) <- c("Scurf", "Endogenous Urinary (a)", "Metabolic Fecal", "Frame Growth", "Body Reserves",
                      "Pregnancy (a)", "Lactation, User Entered", "__________________________", "Total Use, at User Entered",
                      "Supply", "Supply - Use at User Entered", "Required Eff at User Entered, g/g",
                      "__________________________", "Lactation, Nutrient Allowable", "Total Use, at Nutrient Allowable",
                      "Supply - Use at Nutrient Allowable", "Predicted Eff at Nutr Allowable, g/g (b",  
                      "__________________________", "MP Supply / ME Supply, g/mcal",
                      "MP Use / ME Use, g/mcal")  #Names specified here to preserve formatting.
#Footnotes
Tbl6_2_Footnote <- data.frame(a="MP efficiency 0.69 except for endogenous urinary and pregnancy which are 1 and 0.33, respectively",
                             b="Calculated using predicted MP efficiency for nutrient allowable milk protein production")
Tbl6_2_Footnote <- t(Tbl6_2_Footnote)

Tbl6_3 <- data.frame(Inter=c(NA, NA, mPrt_Int),
                     BW=c(An_BW-612, mPrt_k_BW, (An_BW-612)*mPrt_k_BW),
                     DigNDF=c(An_DigNDF-17.06, mPrt_k_DigNDF, MlkNP_NDF),
                     DEInp=c(An_DEInp, mPrt_k_DEInp, MlkNP_DEInp),
                      Arg=c(Abs_Arg_g, mPrt_k_Arg, MlkNP_AbsArg),
                      His=c(Abs_His_g, mPrt_k_His,  MlkNP_AbsHis),
                      Ile=c(Abs_Ile_g, mPrt_k_Ile, MlkNP_AbsIle),
                      Leu=c(Abs_Leu_g, mPrt_k_Leu, MlkNP_AbsLeu),
                      Lys=c(Abs_Lys_g, mPrt_k_Lys, MlkNP_AbsLys),
                      Met=c(Abs_Met_g, mPrt_k_Met, MlkNP_AbsMet),
                      Phe=c(Abs_Phe_g, mPrt_k_Phe, MlkNP_AbsPhe),
                      Thr=c(Abs_Thr_g, mPrt_k_Thr, MlkNP_AbsThr),
                      Trp=c(Abs_Trp_g, mPrt_k_Trp, MlkNP_AbsTrp),
                      Val=c(Abs_Val_g, mPrt_k_Val, MlkNP_AbsVal),
                      Squared_EAA=c(Abs_EAA2b_g, mPrt_k_EAA2, MlkNP_AbsEAA),
                      Other_AA=c(Abs_OthAA_g, mPrt_k_OthAA, MlkNP_AbsOthAA),
                      "Nutr Allow MilkNP"=c(NA,       NA,        Mlk_NP_g),
                     "Nutr Allow MilkNP_305d Max"=c(NA,NA,MlkNP_MlkNPmx))
rownames(Tbl6_3) <- c("Independent Var","Coeff (a)","Predicted Milk NP")
Tbl6_3 <- t(Tbl6_3) #Transpose to match NRC software table
rownames(Tbl6_3) <- c("Intercept","(BW - 612), kg (b)","(Digested NDF - 17.06), % DM (c)","Non-protein DEIn, mcal/d", "Absorbed Arg, g/d", 
                      "Absorbed His, g/d", "Absorbed Ile, g/d", "Absorbed Leu, g/d", "Absorbed Lys, g/d", "Absorbed Met, g/d", 
                      "Absorbed Phe, g/d", "Absorbed Thr, g/d", "Absorbed Trp, g/d", "Absorbed Val, g/d", "Squared EAA, g^2/d (d)", 
                      "Absorbed Other AA, g/d (e)", "Nutr Allow Milk NP, g/d", "Nutr Allow Milk NP / User Enter Max NP (305d RHA) (f)")

Tbl6_3_Footnote <- data.frame(a="Regression coefficient from Eqn. 6.6 adjusted based on user entered Rolling Herd Average Protein",
                      b="centered to 612 kg",
                      c="centered to 17.06% of DM",
                      d="the sum of the squared supplies of each EAA with non-zero coefficients",
                      e="includes all AA other than the EAA with non-zero coefficients",
                      f="nutrient allowable NP production as a proportion of the maximum calculated from the user entered 305d RHA milk protein.  This ratio should not be greater than 0.80 under normal feeding conditions.")
Tbl6_3_Footnote <- t(Tbl6_3_Footnote)             

#AA Flows, g/d
Tbl6_4 <- data.frame(Arg=c(Dt_ArgIn, Dt_ArgRUPIn, Du_ArgMic, Du_ArgEndP, Du_Arg, Du_Arg24h, Dt_IdArgRUPIn, Du_IdArgMic, Abs_Arg_g, NA),
                     His=c(Dt_HisIn, Dt_HisRUPIn, Du_HisMic, Du_HisEndP, Du_His, Du_His24h, Dt_IdHisRUPIn, Du_IdHisMic, Abs_His_g, Trg_AbsHis_g),
                     Ile=c(Dt_IleIn, Dt_IleRUPIn, Du_IleMic, Du_IleEndP, Du_Ile, Du_Ile24h, Dt_IdIleRUPIn, Du_IdIleMic, Abs_Ile_g, Trg_AbsIle_g),
                     Leu=c(Dt_LeuIn, Dt_LeuRUPIn, Du_LeuMic, Du_LeuEndP, Du_Leu, Du_Leu24h, Dt_IdLeuRUPIn, Du_IdLeuMic, Abs_Leu_g, Trg_AbsLeu_g),
                     Lys=c(Dt_LysIn, Dt_LysRUPIn, Du_LysMic, Du_LysEndP, Du_Lys, Du_Lys24h, Dt_IdLysRUPIn, Du_IdLysMic, Abs_Lys_g, Trg_AbsLys_g),
                     Met=c(Dt_MetIn, Dt_MetRUPIn, Du_MetMic, Du_MetEndP, Du_Met, Du_Met24h, Dt_IdMetRUPIn, Du_IdMetMic, Abs_Met_g, Trg_AbsMet_g),
                     Phe=c(Dt_PheIn, Dt_PheRUPIn, Du_PheMic, Du_PheEndP, Du_Phe, Du_Phe24h, Dt_IdPheRUPIn, Du_IdPheMic, Abs_Phe_g, Trg_AbsPhe_g),
                     Thr=c(Dt_ThrIn, Dt_ThrRUPIn, Du_ThrMic, Du_ThrEndP, Du_Thr, Du_Thr24h, Dt_IdThrRUPIn, Du_IdThrMic, Abs_Thr_g, Trg_AbsThr_g),
                     Trp=c(Dt_TrpIn, Dt_TrpRUPIn, Du_TrpMic, Du_TrpEndP, Du_Trp, Du_Trp24h, Dt_IdTrpRUPIn, Du_IdTrpMic, Abs_Trp_g, Trg_AbsTrp_g),
                     Val=c(Dt_ValIn, Dt_ValRUPIn, Du_ValMic, Du_ValEndP, Du_Val, Du_Val24h, Dt_IdValRUPIn, Du_IdValMic, Abs_Val_g, Trg_AbsVal_g))
rownames(Tbl6_4) <- c("Diet (a)","Duod RUP (b)","Duod Micr (b)","Duod Endog (b)","Duod Tot, True (b)", "Duod Tot, 24h Hydr (a)",
                      "Met RUP (b,c)","Met Micr (b,c)","Met Total (b,c)", "Targ Supp at User Enter (b,d)") 
Tbl6_4 <- t(Tbl6_4) #Transpose to match NRC software table
Tbl6_4_Footnote <- data.frame(a=c("not corrected for incomplete recovery of AA during a 24-h acid hydrolysis"),
                              b=c("corrected for incomplete recovery of AA during a 24-h acid hydrolysis."),
                              c=c("mEAA: metabolized EAA."),
                              d=c("Calculated using target efficiencies and net use pre Table 6.5 and user entered milk protein production"))
Tbl6_4_Footnote <- t(Tbl6_4_Footnote)

#EAA partitioning using Predicted Milk NP, g/d
Tbl6_5 <- data.frame(Arg=c(Ur_ArgEnd_g, Fe_ArgMet_g, Scrf_Arg_g, Gest_Arg_g, Body_ArgGain_g, Mlk_Arg_g, Trg_Mlk_Arg_g, An_ArgUse_g, Trg_ArgUse_g, NA, AnNPxArg_AbsArg, AnNPxArgUser_AbsArg),
                     His=c(Ur_HisEnd_g, Fe_HisMet_g, Scrf_His_g, Gest_His_g, Body_HisGain_g, Mlk_His_g, Trg_Mlk_His_g, An_HisUse_g, Trg_HisUse_g, Trg_AbsHis_NPxprtHis, AnNPxHis_AbsHis, AnNPxHisUser_AbsHis),
                     Ile=c(Ur_IleEnd_g, Fe_IleMet_g, Scrf_Ile_g, Gest_Ile_g, Body_IleGain_g, Mlk_Ile_g, Trg_Mlk_Ile_g, An_IleUse_g, Trg_IleUse_g, Trg_AbsIle_NPxprtIle, AnNPxIle_AbsIle, AnNPxIleUser_AbsIle),
                     Leu=c(Ur_LeuEnd_g, Fe_LeuMet_g, Scrf_Leu_g, Gest_Leu_g, Body_LeuGain_g, Mlk_Leu_g, Trg_Mlk_Leu_g, An_LeuUse_g, Trg_LeuUse_g, Trg_AbsLeu_NPxprtLeu, AnNPxLeu_AbsLeu, AnNPxLeuUser_AbsLeu),
                     Lys=c(Ur_LysEnd_g, Fe_LysMet_g, Scrf_Lys_g, Gest_Lys_g, Body_LysGain_g, Mlk_Lys_g, Trg_Mlk_Lys_g, An_LysUse_g, Trg_LysUse_g, Trg_AbsLys_NPxprtLys, AnNPxLys_AbsLys, AnNPxLysUser_AbsLys),
                     Met=c(Ur_MetEnd_g, Fe_MetMet_g, Scrf_Met_g, Gest_Met_g, Body_MetGain_g, Mlk_Met_g, Trg_Mlk_Met_g, An_MetUse_g, Trg_MetUse_g, Trg_AbsMet_NPxprtMet, AnNPxMet_AbsMet, AnNPxMetUser_AbsMet),
                     Phe=c(Ur_PheEnd_g, Fe_PheMet_g, Scrf_Phe_g, Gest_Phe_g, Body_PheGain_g, Mlk_Phe_g, Trg_Mlk_Phe_g, An_PheUse_g, Trg_PheUse_g, Trg_AbsPhe_NPxprtPhe, AnNPxPhe_AbsPhe, AnNPxPheUser_AbsPhe),
                     Thr=c(Ur_ThrEnd_g, Fe_ThrMet_g, Scrf_Thr_g, Gest_Thr_g, Body_ThrGain_g, Mlk_Thr_g, Trg_Mlk_Thr_g, An_ThrUse_g, Trg_ThrUse_g, Trg_AbsThr_NPxprtThr, AnNPxThr_AbsThr, AnNPxThrUser_AbsThr),
                     Trp=c(Ur_TrpEnd_g, Fe_TrpMet_g, Scrf_Trp_g, Gest_Trp_g, Body_TrpGain_g, Mlk_Trp_g, Trg_Mlk_Trp_g, An_TrpUse_g, Trg_TrpUse_g, Trg_AbsTrp_NPxprtTrp, AnNPxTrp_AbsTrp, AnNPxTrpUser_AbsTrp),
                     Val=c(Ur_ValEnd_g, Fe_ValMet_g, Scrf_Val_g, Gest_Val_g, Body_ValGain_g, Mlk_Val_g, Trg_Mlk_Val_g, An_ValUse_g, Trg_ValUse_g, Trg_AbsVal_NPxprtVal, AnNPxVal_AbsVal, AnNPxValUser_AbsVal))
rownames(Tbl6_5) <- c("Uri. Endo.","Metab. Fecal","Scurf","Gestation","Body Gain","Milk, Nutr. Allow.","Milk, User Enter.","Total, Nutr. Allow.","Total, User Enter.", 
                      "Target Eff (b)","Nutr Allow Eff (b)","User Enter Eff (b)")
Tbl6_5 <- t(Tbl6_5) #Transpose to match NRC software table
Tbl6_5_Footnote <- data.frame(a=c("Corrected for incomplete recovery of AA during a 24-h hydrolysis."),
                              b=c("Efficiencies for Uri. Endo. and gestation are 1 and 0.33. Combined efficiencies calculated from MP supply for other functions.
A target efficiency was not estimated for Arg due to semi-essentiality."))
Tbl6_5_Footnote <- t(Tbl6_5_Footnote)

Tbl7_1 <- data.frame(Ca=c(Dt_Ca, Dt_CaReq_DMI, Dt_acCa*100, An_Ca_req, Dt_CaIn, Abs_CaIn, An_Ca_bal, Fe_Ca_m, NA, An_Ca_y, An_Ca_l, An_Ca_g),
                     P=c(Dt_P, Dt_PReq_DMI, Dt_acP*100, An_P_req, Dt_PIn, Abs_PIn, An_P_bal, Fe_P_m, Ur_P_m, An_P_y, An_P_l, An_P_g),
                     Mg=c(Dt_Mg,Dt_MgReq_DMI, Dt_acMg*100,An_Mg_req,Dt_MgIn,Abs_MgIn,An_Mg_bal,Fe_Mg_m,Ur_Mg_m,An_Mg_y,An_Mg_l,An_Mg_g),
                     Cl=c(Dt_Cl,Dt_ClReq_DMI, Dt_acCl*100,An_Cl_req,Dt_ClIn,Abs_ClIn,An_Cl_bal,Fe_Cl_m, NA, An_Cl_y,An_Cl_l,An_Cl_g),
                     K=c(Dt_K,Dt_KReq_DMI, Dt_acK*100,An_K_req,Dt_KIn,Abs_KIn,An_K_bal,Fe_K_m,Ur_K_m, An_K_y,An_K_l,An_K_g),
                     Na=c(Dt_Na, Dt_NaReq_DMI, Dt_acNa*100, An_Na_req, Dt_NaIn, Abs_NaIn, An_Na_bal, Fe_Na_m, NA, An_Na_y, An_Na_l, An_Na_g),
                     S=c(Dt_S, Dt_SReq_DMI, NA, An_S_req, Dt_SIn, NA, An_S_bal, NA, NA, NA, NA, NA))
rownames(Tbl7_1) <- c("Diet, % DM", "Diet Required, % of DM", "AC, g/100 g", "Absorb Requir, g/d", "Intake, g/d", "Absorbed, g/d", "Balance, g/d", 
                      "Met. Fecal, g/d", "End. Urin. g/d", "Pregn. Req., g/d", "Lact. Req., g/d", "Growth Req, g/d")
Tbl7_1t <- t(Tbl7_1)

Tbl7_2 <- data.frame(Co=c(Dt_Co,Dt_CoReq_DMI,Dt_acCo*100,An_Co_req,Dt_CoIn,Abs_CoIn,An_Co_bal,NA,NA,NA,NA),	
                     Cr=c(Dt_Cr,NA,NA,NA,Dt_CrIn,NA,NA,NA,NA,NA,NA),
                     Cu=c(Dt_Cu,Dt_CuReq_DMI,Dt_acCu*100,An_Cu_req,Dt_CuIn,Abs_CuIn,An_Cu_bal,An_Cu_m,An_Cu_y,An_Cu_l,An_Cu_g),
                    Fe=c(Dt_Fe,Dt_FeReq_DMI,Dt_acFe*100,An_Fe_req,Dt_FeIn,Abs_FeIn,An_Fe_bal,An_Fe_m,	An_Fe_y,An_Fe_l,An_Fe_g),
                    I=c(Dt_I,Dt_IReq_DMI,NA,An_I_req,Dt_IIn,NA,An_I_bal,NA,NA,NA,NA),
                    Mn=c(Dt_Mn,Dt_MnReq_DMI,Dt_acMn*100,An_Mn_req,Dt_MnIn,Abs_MnIn,An_Mn_bal,An_Mn_m,	An_Mn_y,An_Mn_l,An_Mn_g),
                    Se=c(Dt_Se,Dt_SeReq_DMI,NA,An_Se_req,Dt_SeIn,NA,An_Se_bal,NA,NA,NA,NA),
                    Zn=c(Dt_Zn,Dt_ZnReq_DMI,Dt_acZn*100,An_Zn_req,Dt_ZnIn,Abs_ZnIn,An_Zn_bal,An_Zn_m,	An_Zn_y,An_Zn_l,An_Zn_g))
rownames(Tbl7_2) <- c("Diet, mg/kg", "Diet Required, mg/kg","AC","Absorb Requir., mg/d","Intake, mg/d","Absorbed, mg/d","Balance, mg/d",
                      "Maintenance, mg/d","Pregn. Req., mg/d","Lact. Req., mg/d","Growth Req., mg/d")
Tbl7_2t <- t(Tbl7_2)

Tbl7_3 <- data.frame(A=c(Dt_VitA,Dt_VitAReq_DMI,An_VitA_req,Dt_VitAIn,An_VitA_bal),
                    D=c(Dt_VitD,Dt_VitDReq_DMI,An_VitD_req,Dt_VitDIn,An_VitD_bal),
                    E=c(Dt_VitE,Dt_VitEReq_DMI,An_VitE_req,Dt_VitEIn,An_VitE_bal),
                    Biotin=c(Dt_Biotin,NA,NA,Dt_BiotinIn,NA),
                    B_Carotene=c(Dt_B_Carotene,NA,NA,Dt_B_CaroteneIn,NA),
                    Choline=c(Dt_Choline,NA,NA,Dt_CholineIn,NA),
                    Niacin=c(Dt_Niacin,NA,NA,Dt_NiacinIn,NA))
rownames(Tbl7_3) <- c("Diet, IU/kg","Diet Requir., IU/kg","Diet Requir., IU/d","Intake, IU/d","Balance, mg/d")
Tbl7_3t <- t(Tbl7_3)

Tbl8_1 <- data.frame("Water Intake (kg)" = c(An_WaIn, WaIn_Milk),
                    "Wet Manure Output (kg)" = c(Man_out, Man_Milk),
                    "Manure Water Output (kg)" = c(Man_Wa_out, ManWa_Milk),
                    "Manure Volatile Solids (kg)" = c(Man_VolSld, VolSlds_Milk),
                    "Enteric Methane Production (g)" = c(CH4out_g, CH4g_Milk),
                    "Enteric Methane Production (L)"=c(CH4out_L, CH4L_Milk))
Tbl8_1 <- t(Tbl8_1)
colnames(Tbl8_1)=c("per day", "per L Milk")
                     
Tbl8_2 <- data.frame("Nitrogen and Macro-minerals"=c("g/d", "g/d","g/d","g/g"),
                     "Nitrogen"=c(An_NIn_g,An_Nprod_g,Man_Nout2_g,An_Nprod_NIn),
                     "Ca"=c(Dt_CaIn,An_Ca_prod,Man_Ca_out,CaProd_CaAbs),
                     "P"=c( Dt_PIn, An_P_prod, Man_P_out, PProd_PAbs),
                     "Mg"=c(Dt_MgIn,An_Mg_prod,Man_Mg_out,MgProd_MgAbs),
                     "Cl"=c(Dt_ClIn,An_Cl_prod,Man_Cl_out,ClProd_ClAbs),
                     "K"=c( Dt_KIn, An_K_prod, Man_K_out, KProd_KAbs),
                     "Na"=c(Dt_NaIn,An_Na_prod,Man_Na_out,NaProd_NaAbs),
                     "Micro-minerals"=c("mg/d","mg/d","mg/d","mg/mg"),
                     "Cu"=c(Dt_CuIn,An_Cu_prod,Man_Cu_out,CuProd_CuAbs),
                     "Fe"=c(Dt_FeIn,An_Fe_prod,Man_Fe_out,FeProd_FeAbs),
                     "Mn"=c(Dt_MnIn,An_Mn_prod,Man_Mn_out,MnProd_MnAbs),
                     "Zn"=c(Dt_ZnIn,An_Zn_prod,Man_Zn_out,ZnProd_ZnAbs))
Tbl8_2 <- t(Tbl8_2)
colnames(Tbl8_2) <- c("Intake", "Retained in Product","Manure","Product/Intake")
# Add these two statements, just before the out <-
# message ("You are in the browser mode to inspect variables and debug the model. Type c to exit the browser mode and continue with the execution of the program")
# browser()
#return output variables in a list. Each is an element in out, i.e. out [1] = dmi table or out$dmi; out$dmi$An_DMIn for DMI.
out <- list(an=an, dmi=dmi, dt=dt, dig=dig, enrg=enrg, micr=micr, abs=abs, inf=inf, mp=mp, main=main, 
            gest=gest, bod=bod, mlk=mlk, MV=MV, excr=excr, eff=eff, imb=imb, 
            f=f,
            Tbl1_1=Tbl1_1, Tbl1_2=Tbl1_2, Tbl1_3=Tbl1_3,
            Tbl2_1=Tbl2_1,
            Tbl2_2=Tbl2_2,
            Tbl3_1=Tbl3_1, 
            Tbl4_1=Tbl4_1, Tbl4_2=Tbl4_2, Tbl4_3=Tbl4_3, 
            Tbl5_1=Tbl5_1,
            Tbl6_1=Tbl6_1, Tbl6_2=Tbl6_2, Tbl6_2_Footnote=Tbl6_2_Footnote,
            Tbl6_3=Tbl6_3, Tbl6_3_Footnote=Tbl6_3_Footnote,
            Tbl6_4=Tbl6_4, Tbl6_4_Footnote=Tbl6_4_Footnote,
            Tbl6_5=Tbl6_5, Tbl6_5_Footnote=Tbl6_5_Footnote,
            Tbl7_1=Tbl7_1,Tbl7_2=Tbl7_2,Tbl7_3=Tbl7_3,
            Tbl8_1=Tbl8_1,Tbl8_2=Tbl8_2
)
            #f=f and dmip=Fd_DMInp can be added to return for cross-checking
}

return(out)
}
############################################# End of the NRC2020 Model Function ##############################################




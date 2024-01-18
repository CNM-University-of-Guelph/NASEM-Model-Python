#Version 2021_06_28: Load simulation from an NRC 2021 Program xml file 
# First naavigate to the script subfolder and then run this file from there.
require(XML)
require("plyr")
require("ggplot2")
require("gridExtra")
require(openxlsx)

#setwd("C:/NASEM/NASEM-Dairy-8/script") #if running from R directly, wd may not be the script directory
wd_script <- getwd()   # get the working directory, which by default is the script directory
wd_root = substr(wd_script,1, nchar(wd_script)-7) # strip the \script from the end of the path
wd_simulation = paste(wd_root, "simulations", sep="/")
wd_research = paste(wd_root, "research", sep="/")


##########################################################################
#Animal Inputs
fullpath <- paste(wd_simulation, "DataTable_Input.sys",sep="/" )
if (file.exists(fullpath)){message("OK1")} else
{
  message("Error! File does not exist:", fullpath)
}
an1 <- xmlParse(fullpath) 
class(an1)
an1top <- xmlRoot(an1) #gives content of root
#Turning XML into a dataframe
an <- xmlToDataFrame(an1)
an$No <- NULL
rownames(an) <- an$Name
an$Name <- NULL
an$Unit <- NULL
an <- as.data.frame(t(an))
an

############################################################################
#Ingredient matrix
fullpath <- paste(wd_simulation, "DataTable_Feeds.sys",sep="/" )
if (file.exists(fullpath)){message("OK2")} else
{
  message("Error! File does not exist:", fullpath)
}
feed1 <- xmlParse(fullpath) #feed grid read
class(feed1)
fd1top <- xmlRoot(feed1) #gives content of root
#class(fd1top)#"XMLInternalElementNode" "XMLInternalNode" "XMLAbstractNode"
#xmlName(fd1top) #give name of node, GridFeeds_Con
#xmlSize(fd1top) #how many children in node, 12
#xmlName(fd1top[[1]]) #name of root's children
#xmlName(fd1top[[2]]) #name of root's children
#Convert to a dataframe
fd <- xmlToDataFrame(feed1)
attributes(fd)
cols <- ncol(fd)
is.character(fd$Fd_NDF)
fd[,7:cols] <- sapply(fd[,7:cols],as.numeric)
is.numeric(fd$Fd_NDF)
fd
dim(fd)
head(fd)

############################################################################
#Diet 
fullpath <- paste(wd_simulation, "DataTable_Ration.sys",sep="/" )
if (file.exists(fullpath)){message("OK3")} else
{
  message("Error! File does not exist:", fullpath)
}
dt1 <- xmlParse(fullpath) #xml feed grid read
class(dt1)
dt1top <- xmlRoot(dt1) #gives content of root
#Turning XML into a dataframe
dt <- xmlToDataFrame(dt1)
dt

############################################################################
# Read Amino Acid Efficiencies vector
# check if file exit
fullpath <- paste(wd_research, "DataTable_Efficiency.xml",sep="/" )
if (file.exists(fullpath)){message("OK4")} else
{
  message("Error! File does not exist:", fullpath)
}

# the contents of DataTable_Efficiency.xml are parsed
Effl<- xmlParse(fullpath)
# get the root
class(Effl)
#Convert to a dataframe
Eff <- xmlToDataFrame(Effl)
# Delete NO and Tip columns
Eff$NO <- NULL
Eff$Tip <-NULL
# Use Nae column as the name of rows
rownames(Eff) <- Eff$Name
# Delete the Name column
Eff$Name <- NULL
#conver values from string to numeric
Eff$Value <- as.numeric(Eff$Value)
# transpose
Eff <- as.data.frame(t(Eff))
Eff
#####################################################################
#Read infusion vectors
# check if file exit
fullpath <- paste(wd_research, "DataTable_Infusion.xml", sep="/" )
if (file.exists(fullpath)){message("OK5")} else
{
  message("Error! File does not exist:", fullpath)
}

inf1 <- xmlParse(fullpath)
class(inf1)
#Convert to a dataframe
inf <- xmlToDataFrame(inf1)
inf$NO <- NULL
inf$Tip <-NULL
rownames(inf) <- inf$Name
inf$Name <- NULL
inf$Value <- as.numeric(inf$Value)
inf <- as.data.frame(t(inf))
if("Inf_Location" %in% names(inf)==FALSE) inf$Inf_Location <- "Rumen"   #if infusion location not passed, set to rumen.
inf$temp <- inf$Inf_Location
inf$Inf_Location <- ifelse(inf$temp == 2, "Duodenum", "Rumen")  #Decode numeric location to text for model
inf$Inf_Location <- ifelse(inf$temp == 3, "Arterial", inf$Inf_Location)
dim(inf)
inf
######################################################################

setwd(wd_simulation)

#Extract Individual Variables from the imported data frames
DietID <- as.numeric(an$DietID)  #need to maintain TrtID as an input for the function to work with meta data.
An_StatePhys <- an$An_StatePhys
An_Breed <- an$An_Breed
An_305RHA_MlkTP <- as.numeric(an$An_305RHA_MlkTP)
An_BW_mature <- as.numeric(an$An_BW_Mature)  #note case is wrong for M in mature
An_AgeDay <- as.numeric(an$An_AgeDay)
An_BW <- as.numeric(an$An_BW)
An_BCS <- as.numeric(an$An_BCS)
An_Parity_rl <- as.numeric(an$An_Parity_rl) 
An_LactDay <- as.numeric(an$An_LactDay)

An_GestLength <- as.numeric(an$An_GestLength)
# An_AgeCalv1st <- as.numeric(an$An_AgeCalv1st) # Deleted from version 2020-02-15

Monensin_eqn  <- as.numeric(an$Monensin_eqn) # added to version 2020-02-15

An_AgeConcept1st <- as.numeric(an$An_AgeConcept1st) 
An_GestDay <- as.numeric(an$An_GestDay)
An_DIMConcept <- as.numeric(an$An_DIMConcept)

Env_Topo <- as.numeric(an$Env_TopoParlor)
Env_DistParlor <- as.numeric(an$Env_DistParlor) 
Env_DistParlor <- ifelse(is.na(Env_DistParlor), 0, Env_DistParlor)  #Abbas needs to provide a default value for this
Env_TripsParlor <- as.numeric(an$Env_TripsParlor)
Env_TripsParlor <- ifelse(is.na(Env_TripsParlor), 4, Env_TripsParlor)  #Abbas needs to provide a default value for this
Env_TempCurr <- as.numeric(an$Env_TempCurr)
Env_TempCurr <- ifelse(is.na(Env_TempCurr), 24, Env_TempCurr)  #Abbas needs to provide a default value for this

Fet_BWbrth <- as.numeric(an$Fet_BWbrth)
Trg_RsrvGain <- as.numeric(an$Trg_RsrvGain)
Trg_FrmGain <- as.numeric(an$Trg_FrmGain)
Trg_MilkProd <- as.numeric(an$Trg_MilkProd)
Trg_MilkFatp <- as.numeric(an$Trg_MilkFatp)
Trg_MilkTPp <- as.numeric(an$Trg_MilkTPp)
Trg_MilkLacp <- as.numeric(an$Trg_MilkLacp)

Trg_Dt_DMIn <- as.numeric(an$Trg_Dt_DMIn)
Fd_DMInp <- as.numeric(dt$Fd_Percent_DM) / 100
An_AgeDryFdStart <- as.numeric(an$An_AgeDryFdStart)

DMIn_eqn <- as.numeric(an$DMIn_eqn)
FrmGain_eqn <- as.numeric(an$FrmGain_eqn)
RsrvGain_eqn <- as.numeric(an$RsrvGain_eqn)
RUP_eqn <- as.numeric(an$RUP_eqn)
mFat_eqn <- as.numeric(an$mFat_eqn)
MiN_eqn <- as.numeric(an$MiN_eqn)
mLac_eqn <- as.numeric(an$mLac_eqn)
mProd_eqn <- as.numeric(an$mProd_eqn)
mPrt_eqn <- as.numeric(an$mPrt_eqn)
mPrt_eqn <- 1 #temp override
Use_DNDF_IV <- as.numeric(an$Use_DNDF_IV)
message("Use_DNDF_IV = ", Use_DNDF_IV)

# two new flags. Their names in R-Code are different than thier name in C-Sharp
RumDevDisc_Clf <- as.numeric(an$Discount_ME_eqn)
NonMilkCP_ClfLiq <- as.numeric(an$Milk_Replacer_eqn)


setwd(wd_script)   # set the working directory back to what it was

# if(exists("NRC2020") == 0) source("NRC Dairy 2020 Model Fn - 2022_09_02.R")  #Source the model function if not present
source("NRC Dairy 2020 Model Fn - 2022_09_02.R")  #Source the model function if not present
#Evaluate the diet using the model in R
out <- NRC2020(DietID, An_Breed, An_AgeDay, An_BW, An_BW_mature, Trg_FrmGain, Trg_RsrvGain, 
               An_Parity_rl, An_BCS, An_GestLength, An_AgeConcept1st, 
               An_DIMConcept, Fet_BWbrth, An_StatePhys, An_LactDay, An_GestDay, Env_TempCurr, Env_DistParlor, 
               Env_TripsParlor, Env_Topo, Trg_MilkProd, Trg_MilkLacp, Trg_MilkTPp, Trg_MilkFatp,
               Trg_Dt_DMIn, An_AgeDryFdStart, Fd_DMInp, f=fd,i=inf, DMIn_eqn, Use_DNDF_IV, RUP_eqn, 
               MiN_eqn, mProd_eqn, mLac_eqn, mPrt_eqn, An_305RHA_MlkTP, mFat_eqn, FrmGain_eqn, RsrvGain_eqn, 
               Monensin_eqn, RumDevDisc_Clf, NonMilkCP_ClfLiq, Eff)
out


#Write the simulation data to Excel
# Load workbook
wb <- createWorkbook()

#Get Sheet Names
#wsnames <- names(wb)
#Wsnames

# Rename a worksheet
#renameWorksheet(wb, wsnames[1], "All 3-19-2020")

#Delete a worksheet
#removeWorksheet(wb, wsnames[2])

#Add worksheets and fill with data
sheetnam <- "R_Sim_Results"
addWorksheet(wb, sheetnam)
writeData(wb,sheetnam, Sys.Date(),startCol=1,startRow=1)
writeData(wb,sheetnam, "R Model Output",startCol=3,startRow=1)
writeData(wb,sheetnam, "Animal Inputs",startCol=1,startRow=3)
writeData(wb, sheetnam, out$an, startCol=1, startRow=4, colNames=TRUE)

writeData(wb,sheetnam, "Intake",startCol=1,startRow=7)
writeData(wb, sheetnam, out$dmi, startCol=1, startRow=8, colNames=TRUE)

writeData(wb,sheetnam, "Dietary Nutrients",startCol=1,startRow=11)
writeData(wb, sheetnam, out$dt, startCol=1, startRow=12, colNames=TRUE)

writeData(wb,sheetnam, "Infused Nutrients",startCol=1,startRow=15)
writeData(wb, sheetnam, out$inf, startCol=1, startRow=16, colNames=TRUE)

writeData(wb,sheetnam, "Diet Digestion",startCol=1,startRow=19)
writeData(wb, sheetnam, out$dig, startCol=1, startRow=20, colNames=TRUE)

writeData(wb,sheetnam, "Energy",startCol=1,startRow=23)
writeData(wb, sheetnam, out$enrg, startCol=1, startRow=24, colNames=TRUE)

writeData(wb,sheetnam, "Microbial Growth",startCol=1,startRow=27)
writeData(wb, sheetnam, out$micr, startCol=1, startRow=28, colNames=TRUE)

writeData(wb,sheetnam, "Absorbed Amino Acids",startCol=1,startRow=31)
writeData(wb, sheetnam, out$abs, startCol=1, startRow=32, colNames=TRUE)

writeData(wb,sheetnam, "Metabolizable Protein",startCol=1,startRow=35)
writeData(wb, sheetnam, out$mp, startCol=1, startRow=36, colNames=TRUE)

writeData(wb,sheetnam, "Maintenance",startCol=1,startRow=39)
writeData(wb, sheetnam, out$main, startCol=1, startRow=40, colNames=TRUE)

writeData(wb,sheetnam, "Gestation",startCol=1,startRow=43)
writeData(wb, sheetnam, out$gest, startCol=1, startRow=44, colNames=TRUE)

writeData(wb,sheetnam, "Growth and Reserves",startCol=1,startRow=47)
writeData(wb, sheetnam, out$bod, startCol=1, startRow=48, colNames=TRUE)

writeData(wb,sheetnam, "Milk",startCol=1,startRow=51)
writeData(wb, sheetnam, out$mlk, startCol=1, startRow=52, colNames=TRUE)

writeData(wb,sheetnam, "Minerals and Vitamins",startCol=1,startRow=55)
writeData(wb, sheetnam, out$MV, startCol=1, startRow=56, colNames=TRUE)

writeData(wb,sheetnam, "Excreted Nutrients",startCol=1,startRow=59)
writeData(wb, sheetnam, out$excr, startCol=1, startRow=60, colNames=TRUE)

writeData(wb,sheetnam, "Efficiency",startCol=1,startRow=63)
writeData(wb, sheetnam, out$eff, startCol=1, startRow=64, colNames=TRUE)

writeData(wb,sheetnam, "Amino Acid Imbalance (Values near 0 are in balance EAA)",startCol=1,startRow=67)
writeData(wb, sheetnam, out$imb, startCol=1, startRow=68, colNames=TRUE)

writeData(wb,sheetnam, "Feed Composition",startCol=1,startRow=71)
writeData(wb,sheetnam, "Dt Prop, %",startCol=1,startRow=72)
writeData(wb, sheetnam, out$dmip*100, startCol=1, startRow=73, colNames=TRUE)
writeData(wb, sheetnam, out$f, startCol=2, startRow=72, colNames=TRUE)

# Save workbook to working directory (this actually writes the file to disk)
saveWorkbook(wb,"Dairy_Model_Output.xlsx", overwrite = TRUE)
writeLines("The Excel output file, Dairy_Model_Output.xlsx, is generated in the script subfolder")



import pandas as pd
from xlsxwriter import Workbook
import os, ntpath
from datetime import datetime
import numpy as np

#renaming fields (in order to match and to adapt kobo names removing double underscores
#if missing, add and populate adm0_name adm0_iso3 round
##reclass languages
##convert time string to datetime fields

####IRQ
table = r'C:\temp\IRQ_R5_step0.csv' # IRQ_R5_step0.csv NGA_R1_step0.csv
output_folder = r'C:\temp'
adm0_name = "Iraq"
adm0_iso3 = "IRQ"
round = 5
languages_country = {"ar":'Arabic'}   #Hausa {"ar":'Arabic'} {1:'English',2:"Hausa"}
qc_enumerator = "Kobo" #"Geopoll" or "Kobo"
qc_method = "CATI"
qc_step0_date = "01-07-2021"   ##NGA: "28-06-2021"  IRQ "01-07-2021"
qc_step1_username = "andrea.amparore"


# ####NGA
# table = r'C:\temp\NGA_R1_step0.csv' # IRQ_R5_step0.csv NGA_R1_step0.csv
# output_folder = r'C:\temp'
# adm0_name = "Nigeria"
# adm0_iso3 = "NGA"
# round = 1
# languages_country = {1:'English',2:"Hausa"}   #Hausa {"ar":'Arabic'} {1:'English',2:"Hausa"}
# qc_enumerator = "Geopoll" #"Geopoll" or "Kobo"
# qc_method = "CATI"
# qc_step0_date = "28-06-2021"   ##NGA: "28-06-2021"  IRQ "01-07-2021"
# qc_step1_username = "andrea.amparore"




filename = ntpath.basename(table).split(".")[0]
if "step0" in table:
    output_file = os.path.join(output_folder, filename.replace("step0","step1") + ".csv")
elif "step_0" in table:
    output_file = os.path.join(output_folder, filename.replace("step_0","step_1") + ".csv")
else:
    output_file = os.path.join(output_folder,filename +'_step1.csv')
df = pd.read_csv(open(table, 'rb'), encoding = "ISO-8859-1")

#replace double underscore  in case of Kobo dataset
df.columns = df.columns.str.replace("__", "_")

###rename specific fields

dict = {"_uuid":"survey_id","enumerator":"operator_id","start":"survey_date_time",'language2' : 'language',
        "covid_policy_otherspecified":"covid_otherspecify", "crp_salesdif_otherspecify": "crp_saledif_otherspecify",
        "fish_salesdif_otherspecify": "fish_saledif_otherspecify","shock_otherspecified":"shock_otherspecify","cs_begging":"cs_emergency_begged","cs_borrowmoney":"cs_stress_borrowed_money","cs_eatplantingseeds":"cs_crisis_consumed_seed_stocks","cs_purchasedfoodcredit":"cs_stress_credit",
       "cs_soldfemanimals":"cs_emergency_sold_last_female","cs_soldhhassetsgoods":"cs_stress_hh_assets",
       "cs_soldlandhouse":"cs_emergency_sold_house","cs_soldprodassets":"cs_crisis_sold_prod_assets",
       "cs_spentsavings":"cs_stress_spent_savings","cs_withdrewchild":"cs_crisis_no_school","ls_main_other":"ls_main_otherspecify","crp_irrigation_other":"crp_irrigation_otherspecify",
        "ls_food_supply_commngpastureland":"ls_food_supply_commonpasture","ls_food_supply_purchasefeedorfodderonmarkets":"ls_food_supply_purchased",
        "fish_salesdif_1":"fish_salesdif","cs_crisis_sold_prod_assets":"cs_crisis_sold_prod_assets","cs_crisis_sold_productive_assets":"cs_crisis_sold_prod_assets",
        "crp_seed_supply_otherspecify":"crp_seed_otherspecify","cs_crisis_sold_productive_asset":"cs_crisis_sold_prod_assets","opt_in_date":"survey_date_time",
        "adm0_ISO3":"adm0_iso3"}


df.rename(columns=dict, inplace=True)
###if missing (in kobo) add adm0_name adm-_iso3 round
if 'adm0_name' in df.columns:
    print ("field %s exists already" % 'adm0_name')
else:
    df["adm0_name"] = adm0_name
if 'adm0_iso3' in df.columns:
    print ("field %s exists already" % 'adm0_iso3')
else:
    df["adm0_iso3"] = adm0_iso3
if 'round' in df.columns:
    print ("field %s exists already" % 'round')
else:
    df["round"] = round


##convert time from string to datetime format
if "T" in df['survey_date_time'].iloc[0]:
    df['survey_date'] = df['survey_date_time'].str.split("T").str[0] #this works for geopoll 2021-06-23T16:27:48.892+03:00
    df['survey_date_dateformat'] = pd.to_datetime(df.survey_date)
    df['survey_date'] = df['survey_date_dateformat'].dt.strftime('%d-%m-%Y')
else:
    df['survey_date'] = df['survey_date_time'].str.split(" ").str[0]  # this works for kobo
    df['survey_date_dateformat'] = pd.to_datetime(df.survey_date)
    df['survey_date'] = df['survey_date_dateformat'].dt.strftime('%d-%m-%Y')




if 'survey_created_date' in df.columns:
    del df['survey_created_date']
if 'survey_date_dateformat' in df.columns:
    del df['survey_date_dateformat']

##removing personal info
if 'phone_number' in df.columns:
    del df['phone_number']

##reclassify languages
domains_table = r'C:\temp\coded_values_20210708151543.xlsx'
domains_dict = pd.read_excel(domains_table, sheet_name=None)
if 'language' in domains_dict:
    reference_languages_df = domains_dict['language']

for countr_language_code, countr_language_name in languages_country.items():
    general_code_for_that_language = reference_languages_df.loc[reference_languages_df['label'] == countr_language_name]['code'].iloc[0]
    df.loc[df.language == countr_language_code, 'language_rec'] = general_code_for_that_language

df['language'] = df['language_rec']
del df['language_rec']
if 'resp_language' in df.columns:
    del df['resp_language']

##add QC fields:

df['qc_enumerator'] = qc_enumerator
df['qc_method'] = qc_method
df['qc_step0_date'] = qc_step0_date
df['qc_step1_date'] = datetime.now().strftime("%d-%m-%Y")
df['qc_step1_username'] = qc_step1_username
df['qc_step2_date'] = np.nan
df['qc_step2_username'] = np.nan



print("Saving processed dataset: %s" % output_file)
df.to_csv(output_file)
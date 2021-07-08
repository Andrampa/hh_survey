import pandas as pd
from xlsxwriter import Workbook
import os, ntpath
import numpy as np

#renaming fields (in order to match and to adapt kobo names removing double underscores
#if missing, add and populate adm0_name adm0_iso3 round
##reclass languages
##convert time string to datetime fields

table = r'C:\temp\IRQ_5.csv' # IRQ_5.csv NGA_R2.csv
output_folder = r'C:\temp'
adm0_name = "Iraq"
adm0_ISO3 = "IRQ"
round = 7
languages_country = {'ar':'Arabic',2:'Spanish'}


filename = ntpath.basename(table).split(".")[0]
output_file = os.path.join(output_folder,filename +'_renamed.csv')
df = pd.read_csv(open(table, 'rb'), encoding = "ISO-8859-1")

###rename specific fields

dict = {"_uuid":"survey_id","enumerator":"operator_id","start":"opt_in_date",'language2' : 'language',
        "covid_policy_otherspecified":"covid_otherspecify", "crp_salesdif_otherspecify": "crp_saledif_otherspecify",
        "fish_salesdif_otherspecify": "fish_saledif_otherspecify","shock_otherspecified":"shock_otherspecify","cs_begging":"cs_emergency_begged","cs_borrowmoney":"cs_stress_borrowed_money","cs_eatplantingseeds":"cs_crisis_consumed_seed_stocks","cs_purchasedfoodcredit":"cs_stress_credit",
       "cs_soldfemanimals":"cs_emergency_sold_last_female","cs_soldhhassetsgoods":"cs_stress_hh_assets",
       "cs_soldlandhouse":"cs_emergency_sold_house","cs_soldprodassets":"cs_crisis_sold_productive_asset",
       "cs_spentsavings":"cs_stress_spent_savings","cs_withdrewchild":"cs_crisis_no_school","ls_main_other":"ls_main_otherspecify","crp_irrigation_other":"crp_irrigation_otherspecify"}

 #       "ls_food_supply_commngpastureland":"ls_food_supply_commngpasturelan","ls_food_supply_purchasefeedorfodderonmarkets":"ls_food_supply_purchasefeedorfodderonmarkets"}


df.rename(columns=dict, inplace=True)
###if missing (in kobo) add adm0_name adm-_iso3 round
if 'adm0_name' in df.columns:
    print ("field %s exists already" % 'adm0_name')
else:
    df["adm0_name"] = adm0_name
if 'adm0_ISO3' in df.columns:
    print ("field %s exists already" % 'adm0_ISO3')
else:
    df["adm0_ISO3"] = adm0_ISO3
if 'round' in df.columns:
    print ("field %s exists already" % 'round')
else:
    df["round"] = round


#replace double underscore  in case of Kobo dataset
df.columns = df.columns.str.replace("__", "_")

##convert time from string to datetime format
df['opt_in_date_dateformat'] = pd.to_datetime(df['opt_in_date'])
df['opt_in_date'] = df['opt_in_date_dateformat']
del df['opt_in_date_dateformat']

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

print("Saving processed dataset: %s" % output_file)
df.to_csv(output_file)
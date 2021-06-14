import pandas as pd
from xlsxwriter import Workbook
import os


table = r'C:\temp\geopoll_test_for_ibrahim.csv' #include the word 'kobo' or 'geopoll' inside the filename

output_folder = r'C:/temp'
output_file = os.path.join(output_folder,'renamed_table.csv')

df = pd.read_csv(open(table, 'rb'), encoding = "ISO-8859-1")

dict = {"cs_begging":"cs_emergency_begged","cs_borrowmoney":"cs_stress_borrowed_money","cs_eatplantingseeds":"cs_crisis_consumed_seed_stocks","cs_purchasedfoodcredit":"cs_stress_credit",
       "cs_soldfemanimals":"cs_emergency_sold_last_female","cs_soldhhassetsgoods":"cs_stress_hh_assets",
       "cs_soldlandhouse":"cs_emergency_sold_house","cs_soldprodassets":"cs_crisis_sold_productive_asset",
       "cs_spentsavings":"cs_stress_spent_savings","cs_withdrewchild":"cs_crisis_no_school"}

df.rename(columns=dict, inplace=True)
print("Saving processed dataset: %s" % output_file)
df.to_csv(output_file)
import pandas as pd
from xlsxwriter import Workbook
from two_lists_similarity import Calculate_Similarity as cs
import os


hh_data = r'C:\temp\renamed_table.csv' #include the word 'kobo' or 'geopoll' inside the filename
master_table_template = r'C:\temp\hh_master_table.csv'
output_folder = r'C:/temp'

geopoll_or_kobo = "geopoll"


country_df = pd.read_csv(open(hh_data, 'rb'))
if geopoll_or_kobo == "kobo":
    country_df.columns = country_df.columns.str.replace("[/]", "")
    print("Opening kobo questionnaire")
elif geopoll_or_kobo == "geopoll":
    print("Opening geopoll questionnaire")
else:
    print("Please include Geopoll or Kobo inside the filename: %s " % hh_data)
    exit()

print("Opening master table")
global_df = pd.read_csv(open(master_table_template, 'rb'))

country_cols = country_df.columns
global_cols = global_df.columns


common_cols = list(country_cols.intersection(global_cols))
country_not_global = list(country_cols.difference(global_cols))
global_not_country = list(global_cols.difference(country_cols))


Column1 = country_not_global
Column2 = global_not_country

from xlsxwriter import Workbook
output_file = os.path.join(output_folder,'table_structure_comparison.xlsx')
workbook = Workbook(output_file)

stats_Sheet=workbook.add_worksheet()

stats_Sheet.write(0, 0, 'Columns matching: %s' % len(common_cols))
stats_Sheet.write(1, 0, 'columns in geopoll/kobo template and not in master: %s' % len(country_not_global))
stats_Sheet.write(2, 0, 'columns in in master and not in geopoll/kobo template: %s' % len(global_not_country))

Report_Sheet=workbook.add_worksheet()

Report_Sheet.write(0, 0, 'common_cols')
Report_Sheet.write(0, 1, 'columns in geopoll/kobo template and not in master')
Report_Sheet.write(0, 2, 'columns in in master and not in geopoll/kobo template')


Report_Sheet.write_column(1, 0, common_cols)
Report_Sheet.write_column(1, 1, country_not_global)
Report_Sheet.write_column(1, 2, global_not_country)
workbook.close()
print("Check output table with structure comparison: ", output_file)



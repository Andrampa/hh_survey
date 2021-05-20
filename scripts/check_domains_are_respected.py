import pandas as pd
from xlsxwriter import Workbook
import os


domains_table = r'C:\temp\coded_values.xlsx'
data_table = r"C:\temp\renamed_table.csv"

output_folder = r'C:/temp'
output_file = os.path.join(output_folder,'output.csv')

domains_dict = pd.read_excel(domains_table, sheet_name=None)
derived_fields = list(domains_dict["derived_fields"][0])

data = pd.read_csv(data_table)

for column in data:
       try:
              column_name = data[column].name
              column_entries = list(set(data[column]))
              if column_name in domains_dict:
                     domain_df = domains_dict[data[column].name]
                     allowed_entries = list(set(domain_df.code))
                     for entry in column_entries:
                            if entry not in allowed_entries and not pd.isnull(entry):
                                   print ("Value %s in column %s is not accepted. Valid entries: %s" % (entry, column_name, allowed_entries))
                                   pass
              elif column_name in derived_fields:
                     allowed_entries = [0,1]
                     for entry in column_entries:
                            if entry not in allowed_entries and not pd.isnull(entry): #remove second condition soon
                                   print ("Value %s in derived column %s in not accepted. Valid entries: %s" % (entry, column_name, allowed_entries))
                                   pass
              else:
                     print("There is no domain specified for field %s" % column_name)
                     pass

       except:
              print ("Failed for field %s" % column_name)


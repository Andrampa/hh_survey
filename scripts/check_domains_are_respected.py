import pandas as pd
from xlsxwriter import Workbook
import os


domains_table = r'C:\temp\data_processing_exports\coded_values_20210802172812.xlsx'
data_table = r"C:\temp\LEB_R1_step1_20210804.csv" # NGA_R1_step2_20210805  LEB_R1_step1_20210804
output_folder = r'C:\temp'
output_file = os.path.join(output_folder,'output.csv')

domains_dict = pd.read_excel(domains_table, sheet_name=None)
derived_fields = list(domains_dict["derived_fields"][0])

data = pd.read_csv(data_table)

for column in data:
       if (column[-13:] != "_otherspecify") and ("admin" not in column) and (column not in ("survey_id","operator_id","adm0_name","adm0_ISO3","adm1_pcode","adm2_pcode","survey_created_date","opt_in_date",
                                                              "total_case_duration","resp_age","adm1_name","adm2_name","","","","","","")):
              try:
                     column_name = data[column].name
                     column_entries = list(set(data[column]))

                     if column_name in domains_dict:
                            domain_df = domains_dict[data[column].name]
                            allowed_entries = list(set(domain_df.code))
                            if column_name == 'crp_main':
                                   try:
                                          allowed_entries = [float(i.replace(",",".")) for i in allowed_entries] # it may happend that it is needed to convert string like "1,24" to floating number 1.24
                                   except:
                                          pass
                                   #check if we are dealing with data before or after reclassification of crp values (performed by amandine for step 2)
                                   column_entries = [x for x in column_entries if pd.notnull(x)] # removing nan values
                                   try: #if data is step0 or step1, needs to be converted to float
                                          column_entries = [float(i.replace(",",".")) for i in column_entries]
                                   except: # if data is in step 2, this is alredy done and the replace function will fail. no problem
                                          pass
                                   if all(i < 1000 for i in column_entries): # for step0 and step 1, reclassification is needed (multiply by 1000
                                          column_entries = [x * 1000 for x in column_entries]


                            for entry in column_entries:
                                   # if column_name == 'crp_main':
                                   #        if entry == 777.0:
                                   #               entry = 777
                                   #        elif entry == 888.0:
                                   #               entry = 888
                                   wrong_data_type = False #when there is at least 1 string, all column entries are imported as string. therefore it may happen that we are just dealing with the wrong data type, and we just need to convert the value to integer
                                   if entry not in allowed_entries and not pd.isnull(entry):
                                          try:
                                                 if int(entry) in allowed_entries:
                                                        wrong_data_type = True
                                          except:
                                                 pass #string can be converted to integer only if it contains a number
                                          if not wrong_data_type: #if it's not a matter of integer vs string
                                                 print ("Value %s in column %s is not accepted. Valid entries: %s" % (entry, column_name, allowed_entries))

                     elif ((column_name in derived_fields) or (column_name[-6:] == "_other")):
                            allowed_entries = [0,1]
                            for entry in column_entries:
                                   wrong_data_type = False  # when there is at least 1 string, all column entries are imported as string. therefore it may happen that we are just dealing with the wrong data type, and we just need to convert the value to integer
                                   if entry not in allowed_entries and not pd.isnull(entry):
                                          try:
                                                 if int(entry) in allowed_entries:
                                                        wrong_data_type = True
                                          except:
                                                 pass #string can be converted to integer only if it contains a number
                                          if not wrong_data_type: #if it's not a matter of integer vs string
                                                 print ("Value %s in derived column %s in not accepted. Valid entries: %s" % (entry, column_name, allowed_entries))


                     else:
                            print("There is no domain specified for field %s. Values: %s" % (column_name, column_entries))
                            pass

              except:
                     print ("Failed for field %s" % column_name)


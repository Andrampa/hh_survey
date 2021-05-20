import pandas as pd
import xlrd
import arcpy
from pandas import ExcelWriter
from datetime import datetime
import os



now = datetime.now().strftime('%Y%m%d%H%M%S')
temp_path = r'C:\temp\data_processing_exports'
questionnaire_file = r'C:\git\hh_survey\GeoPoll_FAO Nigeria Covid-19 Needs Assessment_HH_CATI_V10_IL.xlsx'
coded_values_file = os.path.join(temp_path, "coded_values_%s.xlsx" % now)
writer = pd.ExcelWriter(coded_values_file, engine='xlsxwriter')

field_names_list = []

def importallsheets(in_excel, out_gdb):
    workbook = xlrd.open_workbook(in_excel)
    sheets = [sheet.name for sheet in workbook.sheets()]

    print('{} sheets found: {}'.format(len(sheets), ','.join(sheets)))
    for sheet in sheets:
        # The out_table is based on the input excel file name
        # a underscore (_) separator followed by the sheet name
        out_table = os.path.join(
            out_gdb,
            arcpy.ValidateTableName(
                "{0}".format(sheet),
                out_gdb))

        print('Converting {} to {}'.format(sheet, out_table))

        # Perform the conversion
        arcpy.ExcelToTable_conversion(in_excel, out_table, sheet)


print("Opening questionnaire DF")
quest_df = pd.read_excel(open(questionnaire_file, 'rb'), sheet_name='Questionnaire HH',skiprows=2)
#create a list of all possible numbering
numbering = ["%s)" % n for n in range(1,200)]
# initialize list of lists that will store the results
codes_and_labels = []
for index, row in quest_df.iterrows():
    try:
        codes_and_labels = []
        optional_answers = str(row['English']).replace("\t","")
        question_name = row['Suggested Qname']  #Q Name
        skip_pattern = row['Skip Pattern']
        question_type = row['Q Type']
        universe = row['UNIVERSE']
        print("\n\n----%s----" % question_name)
        #find all numbering present in the string
        numbering_in_text = [n for n in numbering if n in optional_answers]
        if len(numbering_in_text) > 0:
            field_names_list.append(question_name)
            print(numbering_in_text)
            for index in range(0,len(numbering_in_text)):
                start = optional_answers.find(numbering_in_text[index]) + len(numbering_in_text[index])
                try:
                    end = optional_answers.find(numbering_in_text[index + 1])
                    substring = optional_answers[start:end].strip()
                except:
                    # it fails during the last loop -> the last option is usually at the end of the string
                    substring = optional_answers[start:].strip()
                print(substring)
                codes_and_labels.append([index +1, substring])
            if question_type != "Open Ended-Select All That Apply":
                codes_and_labels_df = pd.DataFrame(codes_and_labels, columns=['code', 'label'])
                codes_and_labels_df.to_excel(writer, sheet_name=question_name)
            else:
                numbering_in_qname = [n for n in numbering if n in question_name]
                for index in range(0, len(numbering_in_qname)):
                    start = question_name.find(numbering_in_qname[index]) + len(numbering_in_qname[index])
                    try:
                        end = question_name.find(numbering_in_qname[index + 1])
                        derived_field_name = question_name[start:end].strip()
                    except:
                        # it fails during the last loop -> the last option is usually at the end of the string
                        derived_field_name = question_name[start:].strip()

                    field_names_list.append(derived_field_name)
                    codes_and_labels_df = pd.DataFrame(codes_and_labels, columns=['code', 'label'])
                    codes_and_labels_df.to_excel(writer, sheet_name=derived_field_name)
    except:
        pass


print("Saving codes and labels %s" % coded_values_file)
# Close the Pandas Excel writer and output the Excel file.
writer.save()
gdb_name = "fGDB_with_coded_values_%s.gdb" % now
output_gdb = os.path.join(temp_path, gdb_name)
arcpy.CreateFileGDB_management(temp_path,gdb_name)
importallsheets(coded_values_file, output_gdb)

survey_empty_table_df = pd.DataFrame(columns=[field_names_list])
survey_empty_table_xlsx = os.path.join(temp_path, "survey_empty_table_%s.xlsx" % now)
writer = pd.ExcelWriter(survey_empty_table_xlsx, engine='xlsxwriter')
survey_empty_table_df.to_excel(writer, sheet_name="survey_data")
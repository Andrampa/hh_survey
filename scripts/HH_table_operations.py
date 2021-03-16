import pandas as pd
import numpy as np
import os
from pandas import ExcelWriter

def SummarizeSurveys(surveys_df, surveys_admin_key_field, surveys_weight_field, surveys_summary_field, surveys_summary_field_universe):
    df = surveys_df
    universe_clause = ""
    if surveys_summary_field_universe is not None:
        surveys_summary_field_universe_array = surveys_summary_field_universe.split(';')
        for i, value in enumerate(surveys_summary_field_universe_array):
            if i == 0:
                temp_Arr = value.split(':')
                universe_clause += temp_Arr[0] + " == " + '"' + temp_Arr[1] + '"'
            else:
                temp_Arr = value.split(':')
                universe_clause += " & " + temp_Arr[0] + " == " + '"' + temp_Arr[1] + '"'

        df = df.query(f'{universe_clause}')

    df['temp_percent'] = 100 * df[f'{surveys_weight_field}'] / df.groupby(f'{surveys_admin_key_field}')[f'{surveys_weight_field}'].transform('sum')
    
    table = pd.pivot_table(df, values='temp_percent', index=[f'{surveys_admin_key_field}'], columns=[f'{surveys_summary_field}'], aggfunc=np.sum)
    return table

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

country_file_subset = os.path.join(__location__, 'input_table.xlsx')
label_mapping_table = os.path.join(__location__, 'label_mapping.xlsx')

boolean_mode = "Y/N"
#boolean_mode = "percent"

print("Opening country DF")
country_df = pd.read_excel(open(country_file_subset, 'rb'), sheet_name='Sheet1')
print("Opening operations sheet")
operations_df = pd.read_excel(open(label_mapping_table, 'rb'), sheet_name='operations')
print("Opening all label mapping sheets")
xls = pd.ExcelFile(label_mapping_table)
# to read all sheets to a map
label_mapping_dfs = {}
for sheet_name in xls.sheet_names:
    label_mapping_dfs[sheet_name] = xls.parse(sheet_name)

#the first operation should be the renaming of the columns, if expressly requested in the operations sheet
#check if in the operations sheet there is such operation
column_renaming_found = operations_df[operations_df['operation'].str.contains('columns_renaming')]
if not column_renaming_found.empty:
    print("Renaming columns")
    #converting column renaming dataframe into a dict with a suitable format
    column_renaming_df = label_mapping_dfs["columns_renaming"]
    column_renaming_df.set_index('ColumnName', inplace=True)
    renaming_dictionary = column_renaming_df.to_dict()['VariableLabel']
    country_df.rename(columns=renaming_dictionary, inplace=True)
else:
    print ("Columns renaming not needed")

#the second operation should be the replacing of values in order to match them with the approved options,
# if expressly requested inside the operations sheet
#so: let's check if in the operations sheet there is such operation
column_renaming_found = operations_df[operations_df['operation'].str.contains('values_replacing')]
if not column_renaming_found.empty:
    #converting replacing values dataframe into a dict with a suitable format
    values_replacing_df = label_mapping_dfs["values_replacing"]
    fields_needing_values_replacing = values_replacing_df['column'].unique()
    for field_needing_values_replacing in fields_needing_values_replacing:
        print("Replacing values in column %s" % field_needing_values_replacing)
        values_replacing_df_specific_column = values_replacing_df.loc[(values_replacing_df['column'] == field_needing_values_replacing)
                                                                      & (values_replacing_df['old_value'].notnull())
                                                                      & (values_replacing_df['new_value'].notnull())]
        del values_replacing_df_specific_column['column']
        values_replacing_df_specific_column.set_index('old_value', inplace=True)
        replacing_dictionary = values_replacing_df_specific_column.to_dict()['new_value']
        country_df = country_df.replace({field_needing_values_replacing: replacing_dictionary})

else:
    print ("Values replacing not needed")


#now, proceed column by column in the country sheet, and check if there is an associated task in the operations sheet
for column in country_df:
    column_series = country_df[column]
    #check if there is an associated sheet for this column in the label mapping excel file
    if column in label_mapping_dfs:
        print("\n------------")
        label_mapping_df = label_mapping_dfs[column]
        #now read  the operations sheet and understand the necessary operation to be performed with this column
        operation = operations_df.loc[operations_df['field1'] == column]['operation'].values[0]
        if operation == 'single_check':
            print("Performing single check on column %s to validate all values" % column)
            column_unique_values = country_df[column].unique().tolist()
            answer_options = label_mapping_df['AnswerOptions'].unique().tolist()
            unmatched_answers = [x for x in column_unique_values if x not in answer_options]
            if len(unmatched_answers) > 0:
                print ("The following values do not match the given options:")
                for number, answer in enumerate(unmatched_answers):
                    print(number, ": ",answer)
            else:
                print("All values match with the given options")

        elif operation == 'double_boolean':
            associated_column = operations_df.loc[operations_df['field1'] == column]['field2'].values[0]
            print("Performing double boolean transposing with field %s and %s" % (column, associated_column))

            #first, check values from main columns, to see if they match with the given options:
            column_unique_values = country_df[column].unique().tolist()
            answer_options = label_mapping_df['AnswerOptions'].unique().tolist()
            unmatched_answers = [x for x in column_unique_values if x not in answer_options]
            if len(unmatched_answers) > 0:
                print ("The following values from column %s do not match the given options:" % column)
                for number, answer in enumerate(unmatched_answers):
                    print(number, ": ",answer)
            else:
                print("All values match with the given options")

            #then, check values from second column, to see if they match with the given options
            column_unique_values = country_df[associated_column].unique().tolist()
            answer_options = label_mapping_df['AnswerOptions'].unique().tolist()
            unmatched_answers = [x for x in column_unique_values if x not in answer_options]
            if len(unmatched_answers) > 0:
                print ("The following values from column %s do not match the given options:" % associated_column)
                for number, answer in enumerate(unmatched_answers):
                    print(number, ": ",answer)
            else:
                print("All values match with the given options")

            print("Creating boolean fields and calculating them")
            list_of_boolean_fields_to_create = label_mapping_df['VariableLabel'].unique()
            n_of_boolean_fields = len(list_of_boolean_fields_to_create)
            #first, set the default negative value (0 or No)
            if boolean_mode == "Y/N":
                list_of_values = ["No"] * n_of_boolean_fields #alternatively, for setting null value by default: [np.nan] * n_of_boolean_fields
            elif boolean_mode == "percent":
                list_of_values = [0] * n_of_boolean_fields  # alternatively, for setting null value by default: [np.nan] * n_of_boolean_fields
            #insert the new boolean column with negative default values
            country_df[list_of_boolean_fields_to_create] = pd.DataFrame([list_of_values], index=country_df.index)
            #now, calculate every row and set the positive value in case at least one occurrence match the desired value
            #create a cursor in label mapping options DF and perform the calculation below at each option
            for index, row in label_mapping_df.iterrows():
                answer_option = row.AnswerOptions # i.e. Dryspell or drought
                variable_label = row.VariableLabel # i.e. crop_prod_diff_01
                if boolean_mode == "Y/N":
                    country_df.loc[country_df[column] == answer_option, variable_label] = "Yes"
                    country_df.loc[country_df[associated_column] == answer_option, variable_label] = "Yes"
                elif boolean_mode == "percent":
                    country_df.loc[country_df[column] == answer_option, variable_label] = country_df["percent"]
                    country_df.loc[country_df[associated_column] == answer_option, variable_label] = country_df["percent"]


print("\n------------")
output_excel_file = os.path.join(os.path.dirname(country_file_subset), "output_table.xlsx")
print("Saving processed dataset: %s" % output_excel_file)
writer = ExcelWriter(output_excel_file)
country_df.to_excel(writer, 'Sheet1')
writer.save()

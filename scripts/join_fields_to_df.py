import pandas as pd


main_table = r'C:\temp\IRQ_R5_step2_20210825.csv'
join_field_main_table = 'adm2_pcode'
additional_info = r'C:\temp\IRQ CO Admin Boundaries.xlsx'
join_field_additional_info = 'Admin 2 PCODE'
desired_new_fields = ["admin2Name","admin2Na_1","admin1Name"]
sheet_name = "Admin 2"

df1 = pd.read_csv(open(main_table, 'rb'))
df2 = pd.read_excel(open(additional_info, 'rb'), sheet_name=sheet_name)

desired_new_fields.append(join_field_additional_info)
df2 = df1.merge(df2[desired_new_fields], how = 'left',
                left_on = join_field_main_table, right_on = join_field_additional_info ).drop(columns= [join_field_additional_info])

output = main_table[:-4] + "_joined.csv"

df2.to_csv(output,encoding='utf8')

"""
CAMPAIGN FINANCE ANALYZER v3

CREATED BY DANIEL SIMMONS-RITCHIE

ABOUT: Analyzes campaign finance CSVs using Pandas.
This version differs from v2 in that it  is designed to handle the Dept of State's "full export" dataset.


"""

import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

def main():
    campaign_finance_analyzer()


def campaign_finance_analyzer():

    #################### SET COLUMN NAMES ########################

    contrib_columns = ['FILERID', 'EYEAR', 'CYCLE', 'SECTION', 'CONTRIBUTOR', 'ADDRESS1', 'ADDRESS2', 'CITY', 'STATE', 'ZIPCODE', 'OCCUPATION', 'ENAME', 'EADDRESS1', 'EADDRESS2', 'ECITY', 'ESTATE', 'EZIPCODE', 'CONTDATE1', 'CONTAMT1', 'CONTDATE2', 'CONTAMT2', 'CONTDATE3', 'CONTAMT3', 'CONTDESC']

    filer_columns = ['FILERID', 'EYEAR', 'CYCLE', 'AMMEND', 'TERMINATE', 'FILERTYPE', 'FILERNAME', 'OFFICE', 'DISTRICT', 'PARTY', 'ADDRESS1', 'ADDRESS2', 'CITY', 'STATE', 'ZIPCODE', 'COUNTY', 'PHONE', 'BEGINNING', 'MONETARY', 'INKIND']



    ##################### READ CSV AND SET COLUMN NAMES #######################

    print("Importing CSVs into pandas...")
    #Converting data to CSV and using dtype to ensure 'filerid' in contribs is object type, as it is in filer summary_pivot
    # some field names have lots of white space, hence the funny field name in dtype
    df_contribs = pd.read_csv("/Users/dsimmonsritchie/PycharmProjects/campaign_finance_analyzer_v3/contrib_2018.txt", header=None,error_bad_lines=False,
                              names=contrib_columns, dtype={'FILERID': 'object', 'ZIPCODE':'object','EZIPCODE':'object'}, low_memory=False)
    df_filer = pd.read_csv("/Users/dsimmonsritchie/PycharmProjects/campaign_finance_analyzer_v3/filer_2018.txt", header=None, error_bad_lines=False,
                           names=filer_columns, dtype={'ZIPCODE':'object'})


    ##################### PANDAS ANALYSIS #######################

    #Sets how many columns to display in console
    pd.set_option('display.max_columns', 5)
    pd.set_option('display.width', 1000)

    # Remove trailing white space from column names
    df_contribs.rename(columns=lambda x: x.strip(),inplace=True)
    df_filer.rename(columns=lambda x: x.strip(),inplace=True)

    # Drop all rows that duplicate filerids so that I have a nice clean list of all filers and I won't have
    # duplicates when data is merged
    df_filer_filtered = df_filer.drop_duplicates(subset='FILERID')

    #Join filer and contrib tables on 'filerid' field
    merged_table = pd.merge(df_contribs, df_filer_filtered, left_on = 'FILERID', right_on = 'FILERID')

    # Create new column that adds together amount donated in contamt1, 2 and 3 (somewhat unclear if these are contribs for cycle or what)
    merged_table['sum_of_cont123'] = merged_table['CONTAMT1'] + merged_table['CONTAMT2'] + merged_table['CONTAMT3']

    #Cut unneeded columns
    slimmed_down = merged_table.filter(['FILERID','FILERNAME','CYCLE_x','CONTRIBUTOR','CONTDATE1','CONTAMT1','ADDRESS1_x','ADDRESS2_x','CITY_x','STATE_x','ZIPCODE_x','OCCUPATION','ENAME','EADDRESS1','EADDRESS2','ECITY','ESTATE','EZIPCODE'], axis=1)

    #Renaming columns
    slimmed_down.rename(columns={'FILERNAME': 'RECIPIENT','CONTDATE1':'CONTRIB_DATE','CONTAMT1':'CONTRIB_AMT'}, inplace=True)

    #Splitting data into two separate dataframes for Wolf and Wagner
    df_wolf = slimmed_down[slimmed_down['RECIPIENT'].str.contains('wolf',case=False)]
    df_wagner = slimmed_down[slimmed_down['RECIPIENT'].str.contains('wagner',case=False)]

    #Sorting Wagner and Wolf data by contrib_amt, descending
    df_wolf = df_wolf.sort_values(by='CONTRIB_AMT', ascending=False)
    df_wagner = df_wagner.sort_values(by='CONTRIB_AMT', ascending=False)

    #################### PANDAS GROUPBY QUERIES #########################

    #Wolf - Group by contributor and sort by biggest donor
    wolf_grouped = df_wolf.groupby('CONTRIBUTOR').agg({'CONTRIBUTOR': np.size, 'CONTRIB_AMT':np.sum, 'ADDRESS1_x':'first', 'ADDRESS2_x':'first', 'CITY_x':'first','STATE_x':'first','ZIPCODE_x':'first','OCCUPATION':'first','ENAME':'first','EADDRESS1':'first','EADDRESS2':'first','ECITY':'first','ESTATE':'first','EZIPCODE':'first'}) #aggregate functions
    wolf_grouped.rename(columns={'CONTRIBUTOR': 'CONTRIB_CNT', 'CONTRIB_AMT': 'CONTRIB_TOTAL'}, inplace=True) #renaming contrib column so there's not two of them
    wolf_grouped = wolf_grouped.sort_values(by='CONTRIB_TOTAL', ascending=False).reset_index() #reset index turns it back into a normal dataframe

    #Wagner - Group by contributor and sort by biggest donor
    wagner_grouped = df_wagner.groupby('CONTRIBUTOR').agg({'CONTRIBUTOR': np.size, 'CONTRIB_AMT':np.sum, 'ADDRESS1_x':'first', 'ADDRESS2_x':'first', 'CITY_x':'first','STATE_x':'first','ZIPCODE_x':'first','OCCUPATION':'first','ENAME':'first','EADDRESS1':'first','EADDRESS2':'first','ECITY':'first','ESTATE':'first','EZIPCODE':'first'}) #aggregate functions
    wagner_grouped.rename(columns={'CONTRIBUTOR': 'CONTRIB_CNT', 'CONTRIB_AMT': 'CONTRIB_TOTAL'}, inplace=True) #renaming contrib column so there's not two of them
    wagner_grouped = wagner_grouped.sort_values(by='CONTRIB_TOTAL', ascending=False).reset_index() #reset index turns it back into a normal dataframe

    ############### PIVOT TABLE WITH SUMMARY DATA #################
    # Creating pivot table from full data and then getting aggregate values for certain fields. Index reset restores table to normal dataframe.
    summary_pivot = pd.pivot_table(slimmed_down, index=['RECIPIENT'],values=['CONTRIB_AMT','CONTRIBUTOR'],aggfunc={'CONTRIB_AMT':np.sum,'CONTRIBUTOR':lambda x: len(x.unique())}).reset_index()
    # Renaming field names so they're less confusing.
    summary_pivot.rename(columns={'CONTRIB_AMT':'TOTAL_DONATION_AMT_RECIEVED','CONTRIBUTOR':'NUM_OF_DONORS'},inplace=True)
    # Adding calculated field: working out average donated by each donor
    summary_pivot['AVG_DONATION_PER_DONOR'] = summary_pivot['TOTAL_DONATION_AMT_RECIEVED'] / summary_pivot['NUM_OF_DONORS']
    # Sort summary pivot by biggest donors
    summary_pivot = summary_pivot.sort_values(by="TOTAL_DONATION_AMT_RECIEVED",ascending=False)

    ############### PIVOT TABLE WOLF V WAGNER SUMMARY #################
    wolf_wagner_campaign_committees = ["WAGNER, SCOTT FOR GOVERNOR, INC","Tom Wolf for Governor"]
    wolf_v_wag_summary = summary_pivot[summary_pivot['RECIPIENT'].isin(wolf_wagner_campaign_committees)]

    #####################  EXPORT #######################
    print("Converting to excel file")

    #This exports the files to excel and makes sure that column width is reasonably sized for each column
    today = get_today_date()
    filename = "analyzed_data_{}.xlsx".format(today)
    dfs = {'total_donations':summary_pivot, 'Wolf_v_Wagner':wolf_v_wag_summary,'wolf_top_donors':wolf_grouped,'wagner_top_donors':wagner_grouped,'wolf_all_donations':df_wolf, 'wagner_all_donations': df_wagner, 'info_on_each_filer':df_filer_filtered}


    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    for sheetname, df in dfs.items():  # loop through `dict` of dataframes
        df.to_excel(writer, sheet_name=sheetname, index=False)  # send df to writer, no index
        worksheet = writer.sheets[sheetname]  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
            )) + 1  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)  # set column width

    make_chart(writer, 'Wolf_v_Wagner')

    writer.save()
    print("Conversion complete")


def make_chart(writer, sheetname):
    ####### EXPERIMENT WITH EXCEL CHART #########

    workbook = writer.book
    worksheet = writer.sheets[sheetname]

    # Create a chart object.
    chart = workbook.add_chart({'type': 'column'})

    # Configure the series of the chart from the dataframe data.
    chart.add_series({
        'categories': '=' + sheetname + '!$A$2:$A$3',
        'data_labels': {'value': True},
        'values': '=' + sheetname + '!$C$2:$C$3',
        'gap': 2,
       })

    chart.set_title({
        'name': 'Total donations',
        'name_font': {
            'name': 'Calibri',
            'color': 'black',
        },
    })

    # Configure the chart axes.
    chart.set_y_axis({'major_gridlines': {'visible': False}})

    # Turn off chart legend. It is on by default in Excel.
    chart.set_legend({'position': 'none'})

    # Insert the chart into the worksheet.
    worksheet.insert_chart('B7', chart)


def get_today_date():
    today = datetime.datetime.today()
    today = today.strftime("%b_%d_%Y_%I_%M_%p")
    return today


def merged_data():
    #Wolf = Join contrib info from wolf_grouped data
    wolf_grouped_merged = pd.merge(wolf_grouped, df_wolf[['CONTRIBUTOR','ADDRESS1_x','ADDRESS2_x']], left_on = 'CONTRIBUTOR', right_on = 'CONTRIBUTOR', how='left')
    wolf_grouped_merged = wolf_grouped_merged.drop_duplicates()

    print(wolf_grouped_merged)



    # #Analysis complete message
    print("Pandas analysis complete")

def old_export():
    # Saving this in case new code messes up in some way.

    ##################### EXPORT #######################

    #Turning Wolf and Wagner dataframes into separate sheets in same spreadsheet
    print("Generating excel file...")
    writer = pd.ExcelWriter('final.xlsx')
    df_wolf.to_excel(writer,"Wolf_fulldata",index=False)
    df_wagner.to_excel(writer,"Wagner_fulldata",index=False)
    wolf_grouped.to_excel(writer,"Wolf_top_donors",index=False)
    wagner_grouped.to_excel(writer,"Wagner_top_donors",index=False)
    writer.save()
    print("Files created")




if __name__ == '__main__':
    main()
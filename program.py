
"""
CAMPAIGN FINANCE CRUNCHER

CREATED BY DANIEL SIMMONS-RITCHIE

ABOUT: Analyzes Pa. campaign finance CSVs using Pandas. This new version concats 2017 data with freshly downloaded data and then analyzes both years together.

NOTE: For some reason, the total donations for Wagner and Wolf are slightly inconsistent with those reported on https://www.campaignfinanceonline.pa.gov/Pages/CFAnnualTotals.aspx?Filer=20130153

Data available here: https://www.dos.pa.gov/VotingElections/CandidatesCommittees/CampaignFinance/Resources/Pages/FullCampaignFinanceExport.aspx

UPDATES: This version is in BETA!!! Just trying to see how it works. Don't use this for real tests.

"""

import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import requests
import zipfile
import os
import shutil
import glob



def main():
    # Setting directory names
    base_folder_zipped = 'zipped' # Setting name of folder to stash zip file
    base_folder_unzipped = 'unzipped' # Setting name of folder to stash unzipped files
    base_folder_excel = 'excel' # Setting name of folder to stash excel files

    # Main program
    # delete_old_data(base_folder_zipped, base_folder_unzipped) # Deleting old files,
    # download_data(base_folder_zipped, base_folder_unzipped) # Downloading data
    path_to_excel_file = create_excel_filename_and_folder(base_folder_excel) # Creating excel filename
    campaign_finance_analyzer(base_folder_unzipped, path_to_excel_file) # Analyzing data


def delete_old_data(base_folder_zipped, base_folder_unzipped):
    print("Checking to see if old ZIPPED data exists...")
    if os.path.exists(base_folder_zipped):
        print("Detected existence of zip folder: {}".format(base_folder_zipped))
        try:
            shutil.rmtree(base_folder_zipped)
            print("Successfully deleted directory and all files inside")
        except OSError:
            print("Deletion of the directory %s failed for some reason" % base_folder_zipped)
    else:
        print("No old zipped data detected")

    print("Checking to see if old UNZIPPED data exists...")
    if os.path.exists(base_folder_unzipped):
        print("Detected existence of zip folder: {}".format(base_folder_unzipped))
        try:
            shutil.rmtree(base_folder_unzipped)
            print("Successfully deleted directory and all files inside")
        except OSError:
            print("Deletion of the directory %s failed for some reason" % base_folder_unzipped)
    else:
        print("No old unzipped data detected")


def download_data(base_folder_zipped, base_folder_unzipped):
    # Getting and setting important variables
    today = get_today_date()
    year = get_current_year()
    zip_filename = 'raw_file_{}.zip'.format(today)
    os.mkdir(base_folder_zipped) # Creating directory to stash zipped file
    zip_path = os.path.join(base_folder_zipped,zip_filename)
    unzipped_path = os.path.join(base_folder_unzipped)

    # Summarzing URL and year details
    print("Current year is: {}".format(year))
    download_url = "https://www.dos.pa.gov/VotingElections/CandidatesCommittees/CampaignFinance/Resources/Documents/{}.zip".format(year)
    print("URL for download is: {}".format(download_url))

    # Beginning download of zip file from Pa Dept of State website
    print("Downloading zip file for {} from Campaign Finance website...".format(year))
    try:
        r = requests.get(download_url, allow_redirects=True)
        open(zip_path, 'wb').write(r.content)
    except:
        print("Something went wrong when attempting to download")
        print("Exiting program")
        exit()
    print("...Data downloaded!")

    # Unzipping zip file
    print("Unzipping file...")
    try:
        zip_ref = zipfile.ZipFile(zip_path, 'r')
        zip_ref.extractall('unzipped')
        zip_ref.close()
    except:
        print("Something went wrong when attempting to unzip file")
        print("Exiting program")
        exit()
    print("File successfully unzipped")



def campaign_finance_analyzer(base_folder_unzipped, path_to_excel_file):

    #################### SET COLUMN NAMES AND TYPES ########################

    # Setting data types to reduce memory usage. Using category reduces usage significantly.
    # Note however that columns with 'category' type might cause problems if you attempt Numpy aggregation methods.
    # Change dtypes for those columns to 'object' if you encounter problems
    # Note that ZIPCODE, EZIPCODE and FILERID are set as categories/objects rather than integers.

    contrib_column_types = {
        'FILERID': 'category',
        'EYEAR': 'int64',
        'CYCLE': 'int64',
        'SECTION': 'category',
        'CONTRIBUTOR': 'object',
        'ADDRESS1': 'category',
        'ADDRESS2': 'category',
        'CITY': 'category',
        'STATE': 'category',
        'ZIPCODE': 'category',
        'OCCUPATION': 'category',
        'ENAME': 'category',
        'EADDRESS1':'category',
        'EADDRESS2':'category',
        'ECITY':'category',
        'ESTATE':'category',
        'EZIPCODE':'category',
        'CONTDATE1':'float64',
        'CONTAMT1':'float64',
        'CONTDATE2':'float64',
        'CONTAMT2':'float64',
        'CONTDATE3':'float64',
        'CONTAMT3':'float64',
        'CONTDESC':'category'
    }

    # Creating list of contrib column names from the above dictionary
    contrib_columns = []
    for key in contrib_column_types:
        contrib_columns.append(key)

    # Creating list of filer column names
    filer_columns = ['FILERID', 'EYEAR', 'CYCLE', 'AMMEND', 'TERMINATE', 'FILERTYPE', 'FILERNAME', 'OFFICE', 'DISTRICT', 'PARTY', 'ADDRESS1', 'ADDRESS2', 'CITY', 'STATE', 'ZIPCODE', 'COUNTY', 'PHONE', 'BEGINNING', 'MONETARY', 'INKIND']


    #################### GET PATHS OF TEXT FILES ########################

    # Getting current year so we have accurate file names
    year = get_current_year()

    # Generating paths with partial filenames
    contrib_path = os.path.join(base_folder_unzipped,"contrib*")
    filer_path = os.path.join(base_folder_unzipped,"filer*")

    # Generating full paths using glob (doing this because DoS seems to change names of unzipped files)
    contrib_path = glob.glob(contrib_path)[0]
    filer_path = glob.glob(filer_path)[0]

    ##################### READ CSV AND SET COLUMN NAMES #######################

    print("Importing CSVs into pandas...")
    #Converting data to CSV and using dtype to ensure 'filerid' in contribs is object type, as it is in filer summary_pivot
    # some field names have lots of white space, hence the funny field name in dtype
    df_contribs = pd.read_csv(contrib_path, header=None,error_bad_lines=False,
                              names=contrib_columns, dtype=contrib_column_types, low_memory=False, encoding="ISO-8859-1")
    df_filer = pd.read_csv(filer_path, header=None, error_bad_lines=False,
                           names=filer_columns, dtype={'ZIPCODE':'object'}, encoding="ISO-8859-1")
    print("CSVs sucessfully imported")


    ##################### APPEND DATA FROM PRIOR YEARS ##########################

    df_contribs, df_filer = append_prior_year_data(df_contribs, df_filer)

    ##################### PANDAS ANALYSIS #######################

    print("Beginning pandas analysis...")
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
    merged_table = merged_table.loc[:,['FILERID','FILERNAME','CYCLE_x','CONTRIBUTOR','CONTDATE1','CONTAMT1','ADDRESS1_x','ADDRESS2_x','CITY_x','STATE_x','ZIPCODE_x','OCCUPATION','ENAME','EADDRESS1','EADDRESS2','ECITY','ESTATE','EZIPCODE']]

    #Renaming columns
    merged_table.rename(columns={'FILERNAME': 'RECIPIENT','CONTDATE1':'CONTRIB_DATE','CONTAMT1':'CONTRIB_AMT'}, inplace=True)

    #Splitting data into two separate dataframes for Wolf and Wagner
    df_wolf = merged_table[merged_table['RECIPIENT'].str.contains('wolf',case=False)]
    df_wagner = merged_table[merged_table['RECIPIENT'].str.contains('wagner',case=False)]

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
    summary_pivot = pd.pivot_table(merged_table, index=['RECIPIENT'],values=['CONTRIB_AMT','CONTRIBUTOR'],aggfunc={'CONTRIB_AMT':np.sum,'CONTRIBUTOR':lambda x: len(x.unique())}).reset_index()
    # Renaming field names so they're less confusing.
    summary_pivot.rename(columns={'CONTRIB_AMT':'TOTAL_DONATION_AMT_RECIEVED','CONTRIBUTOR':'NUM_OF_DONORS'},inplace=True)
    # Adding calculated field: working out average donated by each donor
    summary_pivot['AVG_DONATION_PER_DONOR'] = summary_pivot['TOTAL_DONATION_AMT_RECIEVED'] / summary_pivot['NUM_OF_DONORS']
    # Sort summary pivot by biggest donors
    summary_pivot = summary_pivot.sort_values(by="TOTAL_DONATION_AMT_RECIEVED",ascending=False)

    ############### PIVOT TABLE WOLF V WAGNER SUMMARY #################

    wolf_wagner_campaign_committees = ["WAGNER, SCOTT FOR GOVERNOR, INC","Tom Wolf for Governor"]
    wolf_v_wag_summary = summary_pivot[summary_pivot['RECIPIENT'].isin(wolf_wagner_campaign_committees)]
    print("Pandas analysis complete")



    #####################  EXPORT TO EXCEL #######################
    print("Converting to excel file")

    #This exports the files to excel and makes sure that column width is reasonably sized for each column

    dfs = {'total_donations':summary_pivot, 'Wolf_v_Wagner':wolf_v_wag_summary,'wolf_top_donors':wolf_grouped,'wagner_top_donors':wagner_grouped,'wolf_all_donations':df_wolf, 'wagner_all_donations': df_wagner, 'info_on_each_filer':df_filer_filtered}

    writer = pd.ExcelWriter(path_to_excel_file, engine='xlsxwriter')
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
    ####### CREATES EXCEL CHART #########

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

def get_current_year():
    year = datetime.datetime.today()
    year = year.strftime("%Y")
    return year

def create_excel_filename_and_folder(base_folder_excel):
    #####################  CREATE FILENAME AND FOLDER FOR EXCEL EXPORT #######################

    print("Checking to see whether folder for storing excel files exists...")
    today = get_today_date()

    if os.path.exists(base_folder_excel):
        print("Folder already exists")
    else:
        print("Folder doesn't exist")
        os.mkdir(base_folder_excel)
        print("Folder created: {}".format(base_folder_excel))

    filename = "analyzed_data_{}.xlsx".format(today)
    path_to_excel_file = os.path.join(base_folder_excel,filename)
    print("Filename and path to excel file created")
    return path_to_excel_file


def append_prior_year_data(df_contribs, df_filer):



    contrib_column_types = {
        'FILERID': 'category',
        'EYEAR': 'int64',
        'CYCLE': 'int64',
        'SECTION': 'category',
        'CONTRIBUTOR': 'object',
        'ADDRESS1': 'category',
        'ADDRESS2': 'category',
        'CITY': 'category',
        'STATE': 'category',
        'ZIPCODE': 'category',
        'OCCUPATION': 'category',
        'ENAME': 'category',
        'EADDRESS1':'category',
        'EADDRESS2':'category',
        'ECITY':'category',
        'ESTATE':'category',
        'EZIPCODE':'category',
        'CONTDATE1':'float64',
        'CONTAMT1':'float64',
        'CONTDATE2':'float64',
        'CONTAMT2':'float64',
        'CONTDATE3':'float64',
        'CONTAMT3':'float64',
        'CONTDESC':'category'
    }

    # Creating list of contrib column names from the above dictionary
    contrib_columns = []
    for key in contrib_column_types:
        contrib_columns.append(key)

    # Creating list of filer column names
    filer_columns = ['FILERID', 'EYEAR', 'CYCLE', 'AMMEND', 'TERMINATE', 'FILERTYPE', 'FILERNAME', 'OFFICE', 'DISTRICT', 'PARTY', 'ADDRESS1', 'ADDRESS2', 'CITY', 'STATE', 'ZIPCODE', 'COUNTY', 'PHONE', 'BEGINNING', 'MONETARY', 'INKIND']





    ##################### READ OLD CSV DATA INTO PANDAS #######################

    contribs_2017_path = "prior_years/contrib_2017.txt"
    filer_2017_path = "prior_years/filer_2017.txt"

    print("Importing OLD CSVs into pandas...")
    #Converting data to CSV and using dtype to ensure 'filerid' in contribs is object type, as it is in filer summary_pivot
    # some field names have lots of white space, hence the funny field name in dtype
    df_contribs_2017 = pd.read_csv(contribs_2017_path, header=None,error_bad_lines=False,
                              names=contrib_columns, dtype=contrib_column_types, low_memory=False, encoding="ISO-8859-1")
    df_filer_2017 = pd.read_csv(filer_2017_path, header=None, error_bad_lines=False,
                           names=filer_columns, dtype={'ZIPCODE':'object'}, encoding="ISO-8859-1")
    print("OLD CSVs sucessfully imported")

    ##################### MERGE OLD CSV DATA WITH NEW #######################

    print("Concatenating OLD and NEW dataframes together...")
    df_contribs = pd.concat([df_contribs, df_contribs_2017],axis=0)
    df_filer = pd.concat([df_filer, df_filer_2017],axis=0)
    print("Concatenation complate")


    return df_contribs, df_filer


if __name__ == '__main__':
    main()
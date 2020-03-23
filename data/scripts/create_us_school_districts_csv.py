import os
import re
import pandas as pd
import xlrd #For pandas to read excel files
import us #US metadata for state names

"""
RAW_PATH (str): the path to the raw data directory. /data_raw contains .xls Sheets.
CLEAN_PATH (str): the desired location to save the final csv.
CLEAN_NAME (str): the desired file name.
SCHEMA (list of str): the desired column headers gathered from the raw data documentation.
"""
RAW_PATH = "../data_raw/"
CLEAN_PATH = "../data_clean/"
CLEAN_NAME = "us_school_districts.csv"

#Desired columns from original XLS - STATE and YRDATA are new columns
SCHEMA = ['STATE',
'ENROLL',
'NAME',
'YRDATA',
'TOTALREV',
'TFEDREV',
'TSTREV',
'TLOCREV',
'LOCRTAX',
'LOCRPROP',
'LOCREVPAR',
'PCTTOTAL',
'PCTFTOT',
'PCTSTOT',
'PCTLTOT',
'TOTALEXP',
'TCURSPND',
'TSALWAGE',
'TEMPBENE',
'TCURINST',
'TCURSSVC',
'PPCSTOT',
'PPITOTAL',
'PPSTOTAL']

def get_year_from_filename(filename):
    """Extract year abbreviations from filenames.

        Parameters:
            filename (str): name of file to be cleaned ex.(elsec00t.xls).
        Returns:
            year (str): a 4 character year ex.(2000).
    """

    #Extract numbers from filename
    regex = re.compile(r'\d+')
    year_tail = int(regex.findall(filename)[0])

    #Create a complete year string
    if year_tail < 10:
        year = '200' + str(year_tail)
    elif year_tail > 90:
        year = '19' + str(year_tail)
    else:
        year = '20' + str(year_tail)

    return year

def get_stateID_from_year(year):
    """
    Different years have different header names.
    Gets the appropriate state identifier column header to add to the SCHEMA.

    Parameters:
        year (str): the year, used to classify.
    Returns:
        state_id (list): a list with a column header.
    """

    if int(year) >= 2002:
        state_id = ['IDCENSUS']
    elif int(year) == 1992:
        state_id = ['ID']
    else:
        state_id = ['GOVSID']

    return state_id


def sort_by_state_year(df):
    """
    Sort the dataframe by state, then year.

    Returns:
        df (dataframe): a sorted dataframe.
    """

    df['STATE'] = df['STATE'].astype('str')
    df = df.sort_values(by=['STATE', 'YRDATA'])

    df = df.reset_index(drop=True)

    return df

#Handles start to finish conversion of a given XLS file to a csv
def xls_to_df(filename):
    """
    Given an xls file, create a dataframe.
    Map state id's to state names as STATE.
    Create YRDATA feature from file name.

    Returns:
        data (dataframe): a cleaned dataframe ready to be combined
    """

    year = get_year_from_filename(filename)
    state_id = get_stateID_from_year(year)

    #The state_id is a unique identifier, [01-51]
    schema = state_id + SCHEMA

    #Read in .xls as a string to retain leading 0's in state ids
    print('Reading ' + year + ': ' + filename + '...')
    data = pd.read_excel(RAW_PATH + filename, dtype=str)
    data = pd.DataFrame(data, columns=schema)

    #Map the state_id [01-51] to its state name using us
    print("Creating 'State' column...")
    data[state_id] = data[state_id].applymap(lambda x: x[:2]) #Extract the first 2 characters for state id
    data['STATE'] = data[state_id].applymap(lambda x: us.STATES[(int(x)-1)]) #Map on id - 1 to align with us

    data = data.drop(state_id, axis=1)

    print("Creating 'Year' column...")
    data['YRDATA'] = year

    return data

def main():
    """
    Driver function that reads in files one at a time from a specified directory.
    In this case, xls files are read in, cleaned, combined, sorted, and exported as
    a csv.
    """

    #A list(df) to store each cleaned sheet before concatinating
    df_list = []

    #Clean every file in the RAW_PATH directory
    for filename in os.listdir(RAW_PATH):
        df = xls_to_df(filename)
        df_list.append(df)


    #Concat all cleaned dataframes
    print('Concatinating Sheets...')
    df_concat = pd.concat(df_list, ignore_index=True)

    #Sort new dataframe by 'STATE', then 'YEAR'
    print('Sorting...')
    output = sort_by_state_year(df_concat)

    #Download csv at specified location/name
    print('Exporting...')
    output.to_csv(CLEAN_PATH + CLEAN_NAME, index=False, header=True)


if __name__ == "__main__":
    print('Beginning .XLS file conversion.')
    main()
    print('Completed!')

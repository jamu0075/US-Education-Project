import os
import re
import pandas as pd
import xlrd #For pandas to read excel files
import us #US metadata for state names

RAW_PATH = "../data_raw/"
CLEAN_PATH = "../data_clean/"
CLEAN_NAME = "us_school_districts"

#Desired columns from original XLS - STATE and YRDATA are new columns
SCHEMA = ['STATE',
'ENROLL',
'NAME',
'YRDATA',
'TOTALREV',
'TFEDREV',
'FEDRCOMP',
'FEDRSPEC',
'FEDRNUTR',
'FEDROTHR',
'TSTREV',
'STRFORM',
'STRSPEC',
'STRTRANS',
'STROTHER',
'TLOCREV',
'LOCRTAX',
'LOCRPROP',
'LOCREVPAR',
'LOCREVCICO',
'LOCREVOSCH',
'LOCRCHAR',
'LOCROTHR',
'TOTALEXP',
'TCURSPND',
'TSALWAGE',
'TEMPBENE',
'TCURINST',
'TCURSSVC',
'TCURONON',
'DEBTOUT',
'LONGISSU',
'LONGRET',
'PPITOTAL',
'PPISALWG',
'PPIEMBEN',
'PPSTOTAL']

#Extract the year digits from a filename
def get_year_from_filename(filename):

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

#Determine which column to use as state identifier. The census changed the column name for the state identifier in 2002. 1992 also has a unique column name
def get_stateID_from_year(year):
    if int(year) >= 2002:
        state_id = ['IDCENSUS']
    elif int(year) == 1992:
        state_id = ['ID']
    else:
        state_id = ['GOVSID']

    return state_id

#Handles start to finish conversion of a given XLS file to a csv
def xls_to_df(filename):

    year = get_year_from_filename(filename)
    state_id = get_stateID_from_year(year)

    schema = state_id + SCHEMA

    #Read in XLS as a string to retain leading 0's
    print('Reading ' + year + ': ' + filename + '...')
    data = pd.read_excel(RAW_PATH + filename, dtype=str)
    data = pd.DataFrame(data, columns=schema)

    #Convert state_id to state name based off leading 2 digits (1-51 for each state)
    #us.STATES[] contains the name of every state in alphabetic order
    print("Creating 'State' column...")
    data[state_id] = data[state_id].applymap(lambda x: x[:2])
    data['STATE'] = data[state_id].applymap(lambda x: us.STATES[(int(x)-1)])

    data = data.drop(state_id, axis=1)

    print("Creating 'Year' column...")
    data['YRDATA'] = year

    return data

#Sort a dataframe by year then state
def sort_by_state_year(df):
        df['STATE'] = df['STATE'].astype('str')
        df = df.sort_values(by=['STATE', 'YRDATA'])

        df = df.reset_index(drop=True)

        return df

def main():

    df_list = []

    for filename in os.listdir(RAW_PATH):
        df = xls_to_df(filename)
        df_list.append(df)


    #Concat each XLS sheet into a single dataframe
    print('Concatinating Sheets...')
    df_concat = pd.concat(df_list, ignore_index=True)

    print('Sorting...')
    output = sort_by_state_year(df_concat)
    print('Exporting...')
    output.to_csv(CLEAN_PATH + CLEAN_NAME, index=False)


if __name__ == "__main__":
    print('Beginning .XLS file conversion.')
    main()
    print('Completed!')

import pandas               as pd
import numpy                as np
from collections import deque
import io
from modules.csv_columns import *

#------------------------------------------------------------------------------------------------------
# Read csv data file
#df = pd.read_csv(
#    "/Users/bernhardklein/Library/Mobile Documents/com~apple~CloudDocs/FPV/POD_Racer/PODRacer/python/data/students.csv",
#    "/Users/bernhardklein/Library/Mobile Documents/com~apple~CloudDocs/FPV/POD_Racer/PODRacer/python/data/podrdata.csv",
#    "/Users/bernhardklein/Library/Mobile Documents/com~apple~CloudDocs/FPV/POD_Racer/PODRacerAnalyser/data/podrdata.csv",
    #dtype={'MS':int, 'TASK':str, 'GROUP':str},
#    delimiter=',',
#)

idx_time_min = 0
idx_time_max = 1000

help_df = None

def loadDataset(data, delimiter:str=',') -> pd.DataFrame:
    global idx_time_min, idx_time_max
    df = pd.read_csv(data,
        #dtype={'MS':int, 'TASK':str, 'GROUP':str},
        delimiter=delimiter,
    )

    # create an index with combination from TASK & GROUP
    df["GROUPING"] = df.TASK + "_" + df.GROUP
    df.set_index(["GROUPING"], inplace=True)

    # channels can't be negativ - bug in FW, 
    df[[df["CH_R"] < 0]] = 0
    df[[df["CH_P"] < 0]] = 0
    df[[df["CH_Y"] < 0]] = 0
    df[[df["CH_H"] < 0]] = 0
    df[[df["CH_T"] < 0]] = 0


    idx_time_min = df["TIME"].min()
    idx_time_max = df["TIME"].max()

    return df


def ImportHelpData(fname:str, delimiter:str='|'):
    global help_df
    help_df = pd.read_csv(fname, delimiter=delimiter)
    return help_df

def readContinously(df:pd.DataFrame, fname:str='livedata.csv', tail:int=200, initial:bool=False) -> pd.DataFrame:
    """
    read continously from dataframe the last tail(x) rows.
    the csv file should be in the same folder as app.py

    Used by page_dynamic to show real-time data

    if initial is set to true a index is created (this should only do once)

    Args:
        df (pd.DataFrame): _description_
        fname (str, optional): _description_. Defaults to livedata.csv.
        tail (int, optional): _description_. Defaults to 250.
        initial (bool, optional): _description_. Defaults to False.

    Returns:
        pd.DataFrame: _description_
    """
    # df_tmp = pd.read_csv("livedata.csv")
    #
    # read only last 'tail' rows from CSV and load them into dataframe
    with open (fname, 'r') as f:
        q = deque(f, tail)
    
    df_tmp = pd.read_csv(io.StringIO(''.join(q)),header=None)
    df_tmp.columns=columns
    df = pd.concat([df, df_tmp],)
    df.set_index(["GROUPING"], inplace=True)

    #df3 = df[['float0','float1']].tail(tail)
    return df
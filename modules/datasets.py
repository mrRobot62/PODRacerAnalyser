import pandas               as pd
import numpy                as np

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
    help_df.shape

    
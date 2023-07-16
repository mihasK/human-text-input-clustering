import pathlib
from icecream import ic
from loguru import logger
import pandas as pd

ic(__file__)
data_dir = pathlib.Path(__file__).parent / 'data'

data_list = ic(
    list(data_dir.iterdir())
)


 

def load_df(d_name):
    logger.info(f'{d_name} data selected')
    df = pd.read_csv(data_dir / d_name)
    
    
    # (re)write _RID
    df.drop(['_RID'], axis=1, errors='ignore', inplace=True)
    df.insert(0, '_RID', df.index)  
    
    return df

def write_df(df: pd.DataFrame, d_name):
    logger.info(f'{d_name} data overwriten')
    
    df.to_csv(data_dir / d_name, index=False)
    

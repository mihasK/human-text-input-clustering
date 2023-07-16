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
    return pd.read_csv(data_dir / d_name)


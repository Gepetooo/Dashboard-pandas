from functools import lru_cache
from pathlib import Path

import pandas as pd


DATASET_URL = 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv'
DATASET_REPOSITORY_URL = 'https://github.com/mwaskom/seaborn-data'
DATASET_PATH = Path(__file__).resolve().parents[1] / 'data' / 'titanic.csv'
DATASET_COLUMNS = [
    'survived',
    'pclass',
    'sex',
    'age',
    'sibsp',
    'parch',
    'fare',
    'embarked',
    'deck',
    'embark_town',
]
NUMERIC_COLUMNS = [
    'survived',
    'pclass',
    'age',
    'sibsp',
    'parch',
    'fare',
]


@lru_cache(maxsize=1)
def carregar_conjunto_dados():
    frame = pd.read_csv(DATASET_PATH, usecols=DATASET_COLUMNS)
    frame['sex'] = frame['sex'].astype('string').str.strip()
    frame['embark_town'] = frame['embark_town'].astype('string').str.strip()
    for column in NUMERIC_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors='coerce')
    frame['survived'] = frame['survived'].astype('Int64')
    frame['pclass'] = frame['pclass'].astype('Int64')
    return frame.reset_index(drop=True)
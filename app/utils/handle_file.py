import datetime
import re
import os
import pandas as pd
from pandas import DataFrame

from app.utils.logger import logger


async def save_tt(user_info:dict,file_data:bytes):
    logger.debug(user_info)
    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = f"{user_info['data'].get('department')}_{user_info['data'].get('div')}_{user_info['data'].get('year')}_date-{current_time}_att-{user_info.get("file_name_og")}"

    os.makedirs("attachments", exist_ok=True)
    filepath = os.path.join("attachments", file_name)
    with open(filepath, "wb") as f:
        f.write(file_data)
    logger.debug(f"Saved: {filepath}")
    return filepath


async def extract_data_from_xlsx(file_path: str,target_columns):
    logger.warning(f"Extracting data from {file_path}")
    if not file_path.endswith(".xlsx"):
        logger.error(f"File {file_path} is not a .xlsx file")
        raise Exception(f"File {file_path} is not a .xlsx file")
    tt = pd.read_excel(file_path, header=None)
    logger.debug(target_columns)
    header_row = tt[tt[0] == 'DAY'].index[0]
    expected_columns = ['DAY', 'TIME', 'SY A', 'SY B', 'SY C', 'SY D', 'TY A', 'TY B', 'TY C', 'TY D', 'Btech A', 'Btech B']
    actual_columns = tt.iloc[header_row].tolist()
    if not set(expected_columns).issubset(set(actual_columns)):
        logger.warning(f"Found columns {actual_columns}")
        raise Exception(f"Header row does not match expected columns {expected_columns}")
    tt.columns = tt.iloc[header_row]
    tt = tt.iloc[header_row + 1:].reset_index(drop=True)
    if target_columns not in tt.columns:
        logger.error(f"Column {target_columns} not found in the Excel file")
        raise Exception(f"Column {target_columns} not found in the Excel file")
    tt = tt[['DAY', 'TIME', target_columns]]
    tt["TIME"] = tt["TIME"].astype(str).apply(lambda x: re.sub(r'\s*to\s*', ' - ', x.strip()))
    tt['DAY'] = tt['DAY'].fillna(method='bfill', limit=1)
    tt['DAY'] = tt['DAY'].ffill()
    return tt




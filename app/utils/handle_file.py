import datetime
import re
import os
import pandas as pd
from pandas import DataFrame

from app.utils.logger import logger


async def save_tt(user_info:dict,file_data:bytes):
    logger.debug(user_info)
    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = f"{user_info.get('department')}_{user_info.get('div')}_{user_info.get('year')}_date-{current_time}_att-{user_info.get("file_name_og")}"

    os.makedirs("attachments", exist_ok=True)
    filepath = os.path.join("attachments", file_name)
    with open(filepath, "wb") as f:
        f.write(file_data)
    logger.debug(f"Saved: {filepath}")
    return filepath

def parse_time(time_str):
    time_str = time_str.strip()
    pattern = re.compile(r'(\d+\.\d{2}) ?(am|pm)', re.IGNORECASE)
    match = pattern.match(time_str)
    if match:
        time_part = match.group(1)
        meridian = match.group(2).lower()
        hour, minute = map(int, time_part.split('.'))
        if meridian == 'am':
            if hour == 12:
                hour = 0
        elif meridian == 'pm':
            if hour != 12:
                hour += 12
        return f"{hour:02d}:{minute:02d}"
    return time_str
def extract_day(day_row,day,target_columns):
    schedule_items = []
    id_counter=1
    for _, row in day_row.iterrows():
        time_range = row['TIME']
        time_range = str(time_range).strip()
        time_range = re.sub(r'\s*-\s*', '-', time_range)
        try:
            start_str, end_str = time_range.split('-')
            start_time = parse_time(start_str)
            end_time = parse_time(end_str)
        except ValueError:
            logger.error(f"Invalid time range: {time_range}")
            continue
        subject = row[target_columns]
        if pd.notna(subject) and subject.strip() != '' and subject.strip().lower() != 'lunch break':
            schedule_items.append({
                'id': id_counter,
                'start_time': start_time,
                'end_time': end_time,
                'name': subject.strip()
            })
            id_counter += 1
    return {day: schedule_items}

async def extract_data_from_xlsx(file_name: str, user_info: dict):
    target_columns = f"{user_info.get('year')} {user_info.get('div')}"

    if not file_name.endswith(".xlsx"):
        logger.error(f"File {file_name} is not a .xlsx file")
        raise Exception(f"File {file_name} is not a .xlsx file")
    tt = pd.read_excel(file_name, header=None)
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
    unique_days = tt['DAY'].dropna().unique()
    result = []
    tt.to_excel("test.xlsx", index=False)
    for day in unique_days:
        day_rows = tt[tt['DAY'] == day]
        day_tt= extract_day(day_rows, day, target_columns)
        # logger.debug(f"Found {len(day_tt)} rows for day {day_tt}")
        result.append(day_tt)
    return result





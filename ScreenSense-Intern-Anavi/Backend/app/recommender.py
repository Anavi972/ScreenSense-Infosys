# backend/app/recommender.py
import pandas as pd
import numpy as np
from typing import Tuple
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "Indian_Kids_Screen_Time_Cleaned.csv"

def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(str(path))
    # derived columns
    df['Educational_Avg_Screen_Time_hr'] = (df['Avg_Daily_Screen_Time_hr'] /
                                           (1 + df['Educational_to_Recreational_Ratio'])).round(2)
    df['Recreational_Avg_Screen_Time_hr'] = (df['Avg_Daily_Screen_Time_hr'] - 
                                            df['Educational_Avg_Screen_Time_hr']).round(2)

    # clean Health_Impacts into lists
    df['Health_Impacts'] = (
        df['Health_Impacts']
        .astype(str)
        .str.replace(r"[\[\]']", '', regex=True)
        .str.replace('"', '', regex=False)
        .str.strip()
        .str.split(',')
    )
    df_exploded = df.explode('Health_Impacts')
    df_exploded['Health_Impacts'] = df_exploded['Health_Impacts'].str.strip()
    return df, df_exploded

# load once
DF, DF_EXPLODED = load_data()

# Precompute aggregates
NON_EXCEEDED = DF[DF['Exceeded_Recommended_Limit'] == False]

AVG_SCREEN_TIME_BY_AGE = (
    NON_EXCEEDED.groupby('Age')['Avg_Daily_Screen_Time_hr']
    .mean()
    .reset_index()
    .rename(columns={'Avg_Daily_Screen_Time_hr': 'Avg_Screen_Time_By_Age'})
)

AVG_SCREEN_TIME_BY_DEVICE = (
    NON_EXCEEDED.groupby('Primary_Device')['Avg_Daily_Screen_Time_hr']
    .mean()
    .reset_index()
    .rename(columns={'Avg_Daily_Screen_Time_hr': 'Avg_Screen_Time_By_Device'})
)

AVG_SCREEN_TIME_BY_GENDER = (
    NON_EXCEEDED.groupby('Gender')['Avg_Daily_Screen_Time_hr']
    .mean()
    .reset_index()
    .rename(columns={'Avg_Daily_Screen_Time_hr': 'Avg_Screen_Time_By_Gender'})
)

age_to_limit = dict(zip(AVG_SCREEN_TIME_BY_AGE['Age'], AVG_SCREEN_TIME_BY_AGE['Avg_Screen_Time_By_Age']))
device_to_limit = dict(zip(AVG_SCREEN_TIME_BY_DEVICE['Primary_Device'], AVG_SCREEN_TIME_BY_DEVICE['Avg_Screen_Time_By_Device']))
gender_to_limit = dict(zip(AVG_SCREEN_TIME_BY_GENDER['Gender'], AVG_SCREEN_TIME_BY_GENDER['Avg_Screen_Time_By_Gender']))

GLOBAL_MEAN = DF['Avg_Daily_Screen_Time_hr'].mean()

# Helper functions (kept behavior from notebook)
def get_age_based_limit(age: int) -> float:
    return round(age_to_limit.get(age, GLOBAL_MEAN), 2)

def get_device_based_limit(device: str) -> float:
    return round(device_to_limit.get(device, GLOBAL_MEAN), 2)

def get_gender_based_limit(gender: str) -> float:
    return round(gender_to_limit.get(gender, GLOBAL_MEAN), 2)

def get_combined_recommended_limit(age: int, device: str, gender: str) -> float:
    combined_limit = (get_age_based_limit(age) + get_device_based_limit(device) + get_gender_based_limit(gender)) / 3
    return round(combined_limit, 2)

def exceeded_logic(age: int, device: str, gender: str, screen_time: float) -> Tuple[bool, bool, bool, bool]:
    age_limit = get_age_based_limit(age)
    device_limit = get_device_based_limit(device)
    gender_limit = get_gender_based_limit(gender)
    combined_limit = get_combined_recommended_limit(age, device, gender)
    return (
        screen_time > age_limit,
        screen_time > device_limit,
        screen_time > gender_limit,
        screen_time > combined_limit
    )

def recommendation_system(age: int, gender: str, device: str, screen_time: float) -> dict:
    users_behind = round((DF['Avg_Daily_Screen_Time_hr'] < screen_time).mean() * 100, 2)

    age_limit = get_age_based_limit(age)
    device_limit = get_device_based_limit(device)
    gender_limit = get_gender_based_limit(gender)
    combined_limit = get_combined_recommended_limit(age, device, gender)

    exceeded_age, exceeded_device, exceeded_gender, exceeded_combined = exceeded_logic(age, device, gender, screen_time)

    return {
        "Age": age,
        "Gender": gender,
        "Device": device,
        "Your Screen Time (hrs)": round(screen_time, 2),
        "Age-based Recommended Limit (hrs)": age_limit,
        "Device-based Recommended Limit (hrs)": device_limit,
        "Gender-based Recommended Limit (hrs)": gender_limit,
        "Combined Recommended Limit (hrs)": combined_limit,
        "Exceeded Age Limit": exceeded_age,
        "Exceeded Device Limit": exceeded_device,
        "Exceeded Gender Limit": exceeded_gender,
        "Exceeded Combined Limit": exceeded_combined,
        "Users having lower Screen Time (%)": users_behind
    }

# Educational / recreational analysis helpers
def get_edu_rec_limits():
    edu_limit = round(NON_EXCEEDED['Educational_Avg_Screen_Time_hr'].mean(), 2)
    rec_limit = round(NON_EXCEEDED['Recreational_Avg_Screen_Time_hr'].mean(), 2)
    return edu_limit, rec_limit

def find_health_impacts_near_time(time_hr: float) -> list:
    window = DF_EXPLODED[
        (DF_EXPLODED['Avg_Daily_Screen_Time_hr'] >= time_hr - 0.5) &
        (DF_EXPLODED['Avg_Daily_Screen_Time_hr'] <= time_hr + 0.5)
    ]
    impacts = window['Health_Impacts'].dropna().astype(str).str.strip().unique()
    impacts = sorted(set([i.title() for i in impacts if str(i).lower() != 'no impact']))
    return impacts

import pandas as pd
import numpy as np
import streamlit as st
import requests

# Title of the app
st.title("OBV Analysis")

# Function to load data (using the raw file from GitHub)
@st.cache_data
def load_data():
    file_url = "https://github.com/LeScott2406/StatsApp/raw/refs/heads/main/updated_player_stats.xlsx"
    response = requests.get(file_url)
    with open("/tmp/updated_player_stats.xlsx", "wb") as f:
        f.write(response.content)
    player_stats_df = pd.read_excel("/tmp/updated_player_stats.xlsx")
    return player_stats_df

# Load the data
player_stats_df = load_data()

# Filters in the sidebar
st.sidebar.header("Filters")

# Age slider (with both min and max set between 15 and 35)
age_min, age_max = st.sidebar.slider(
    "Age Range",
    min_value=15,
    max_value=35,
    value=(15, 35),
    step=1
)

# Usage slider (with both min and max from 0 to 140)
usage_min, usage_max = st.sidebar.slider(
    "Usage Range",
    min_value=0,
    max_value=140,
    value=(0, 140),
    step=1
)

# Primary Position multi-select dropdown with an "All" option
primary_positions = ['All'] + player_stats_df['Primary Position'].unique().tolist()
selected_primary_positions = st.sidebar.multiselect("Primary Position", primary_positions)

# Competition multi-select dropdown with an "All" option
competitions = ['All'] + player_stats_df['Competition'].unique().tolist()
selected_competitions = st.sidebar.multiselect("Competition", competitions)

# Team multi-select dropdown with an "All" option
if selected_competitions:
    if "All" in selected_competitions:
        teams = ['All'] + player_stats_df['Team'].unique().tolist()
    else:
        # Filter teams based on the selected competitions
        teams = ['All'] + player_stats_df[player_stats_df['Competition'].isin(selected_competitions)]['Team'].unique().tolist()
else:
    teams = ['All']

selected_teams = st.sidebar.multiselect("Team", teams)

# Round the 'Minutes Played' column to 0 decimal places
if 'Minutes Played' in player_stats_df.columns:
    player_stats_df['Minutes Played'] = player_stats_df['Minutes Played'].round(0)

# Define the conditions and their corresponding values (no need for these as we want all competitions)
# conditions = [
#     (player_stats_df["Competition"] == "1. Bundesliga"),
#     (player_stats_df["Competition"] == "1. HNL"),
#     # Add more conditions as needed...
# ]
# values = [
#     15, 18, # Add corresponding values...
# ]
# player_stats_df["Matches"] = np.select(conditions, values, default=np.nan)

# Calculate Available Minutes by multiplying Matches by 90 (if Matches is already present)
if 'Matches' in player_stats_df.columns:
    player_stats_df['Available Minutes'] = player_stats_df['Matches'] * 90

    # Calculate 'Usage' by dividing 'Minutes Played' by 'Available Minutes' and multiplying by 100
    if 'Minutes Played' in player_stats_df.columns and 'Available Minutes' in player_stats_df.columns:
        player_stats_df['Usage'] = ((player_stats_df['Minutes Played'] / player_stats_df['Available Minutes']) * 100).round(2)

# Filter based on user selections
filtered_df = player_stats_df[
    (player_stats_df['Age'] >= age_min) & (player_stats_df['Age'] <= age_max) &
    (player_stats_df['Usage'] >= usage_min) & (player_stats_df['Usage'] <= usage_max)
]

# Filter by Primary Position
if selected_primary_positions and "All" not in selected_primary_positions:
    filtered_df = filtered_df[filtered_df['Primary Position'].isin(selected_primary_positions)]

# Filter by Competition
if selected_competitions and "All" not in selected_competitions:
    filtered_df = filtered_df[filtered_df['Competition'].isin(selected_competitions)]

# Filter by Team
if selected_teams and "All" not in selected_teams:
    filtered_df = filtered_df[filtered_df['Team'].isin(selected_teams)]

# Define the exact columns you want to display in the specified order
display_columns = [
    'Name', 'Team', 'Age', 'Primary Position', 
    'Defensive Action OBV', 'Pass OBV', 
    'Dribble & Carry OBV', 'Shot OBV', 'OBV'
]

# Check if all columns are present in the DataFrame
available_columns = [col for col in display_columns if col in filtered_df.columns]
filtered_df = filtered_df[available_columns]

# Display the filtered DataFrame with the selected columns
st.write("Filtered Player Stats:")
st.dataframe(filtered_df)

# Option to download the filtered data as an Excel file
output_path = "/tmp/filtered_player_stats.xlsx"
filtered_df.to_excel(output_path, index=False)
st.download_button(
    label="Download Filtered Stats",
    data=open(output_path, "rb").read(),
    file_name="filtered_player_stats.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


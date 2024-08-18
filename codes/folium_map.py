import folium
from folium.plugins import HeatMap
import pandas as pd

# Define the years for which heat maps will be generated
years = [2020, 2021, 2022, 2023]

# Load the data from CSV file
df = pd.read_csv('data2.csv')

for year in years:
    # Filter the data for the specific year
    df_sorted2 = df[pd.to_datetime(df['DATE OCC']).dt.year == year]

    # Convert LAT and LON columns to numeric values
    df_sorted2['LAT'] = pd.to_numeric(df_sorted2['LAT'], errors='coerce')
    df_sorted2['LON'] = pd.to_numeric(df_sorted2['LON'], errors='coerce')

    # Drop rows with NaN values in LAT or LON columns
    df_sorted2 = df_sorted2.dropna(subset=['LAT', 'LON'])

    # Central coordinates of Los Angeles
    latitude = 34.0522
    longitude = -118.2437

    # Create a map centered around Los Angeles with CartoDB Dark Matter tiles
    la_map = folium.Map(location=[latitude, longitude], zoom_start=10, tiles='CartoDB dark_matter')

    # Generate heat map data
    heat_data = [[row['LAT'], row['LON']] for index, row in df_sorted2.iterrows()]

    # Configure heat map parameters
    heatmap = HeatMap(
        heat_data,
        radius=8,  # Radius of the points
        blur=9,    # Blur of the points
        max_zoom=13 # Maximum zoom level
    )

    # Add the heat map to the map
    heatmap.add_to(la_map)

    # Save the map as an HTML file
    file_name = f'la_heatmap{year}.html'
    la_map.save(file_name)
    print(f'{file_name} has been saved.')


import folium
import pandas as pd
import requests
import io
import os
import webbrowser

# Import folium MarkerCluster plugin
from folium.plugins import MarkerCluster
# Import folium MousePosition plugin
from folium.plugins import MousePosition
# Import folium DivIcon plugin
from folium.features import DivIcon

## Task 1: Mark all launch sites on a map

URL = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_geo.csv'

# Fetch the content using requests
response = requests.get(URL)

# Raise an error if the request failed
response.raise_for_status()

# Convert response content into a BytesIO stream and read it into pandas
spacex_csv_file = io.BytesIO(response.content)
spacex_df = pd.read_csv(spacex_csv_file)

# Display the first few rows
print(spacex_df.head())

# Select relevant sub-columns: `Launch Site`, `Lat(Latitude)`, `Long(Longitude)`, `class`
spacex_df = spacex_df[['Launch Site', 'Lat', 'Long', 'class']]
launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
launch_sites_df = launch_sites_df[['Launch Site', 'Lat', 'Long']]
launch_sites_df

# Start location is NASA Johnson Space Center
nasa_coordinate = [29.559684888503615, -95.0830971930759]
site_map = folium.Map(location=nasa_coordinate, zoom_start=10)

# Create a blue circle at NASA Johnson Space Center's coordinate with a popup label showing its name
circle = folium.Circle(nasa_coordinate, radius=1000, color='#d35400', fill=True).add_child(folium.Popup('NASA Johnson Space Center'))
# Create a blue circle at NASA Johnson Space Center's coordinate with a icon showing its name
marker = folium.map.Marker(
    nasa_coordinate,
    # Create an icon as a text label
    icon=DivIcon(
        icon_size=(20,20),
        icon_anchor=(0,0),
        html='<div style="font-size: 12; color:#d35400;"><b>%s</b></div>' % 'NASA JSC',
        )
    )
site_map.add_child(circle)
site_map.add_child(marker)


file_path = os.path.abspath("spacex_launch_sites_map.html")
site_map.save(file_path)
# print(f"Map saved at {file_path}")

# Open it in the default browser
# webbrowser.open(f"file://{file_path}")

for i in range(0,len(launch_sites_df)): 
    coordinate_i = [launch_sites_df['Lat'][i], launch_sites_df['Long'][i]]
    site_name_i = launch_sites_df['Launch Site'][i]
    
    circle = folium.Circle(coordinate_i, radius=1000, color='#d35400', fill=True).add_child(folium.Popup(site_name_i))
    # Create a blue circle at NASA Johnson Space Center's coordinate with a icon showing its name
    marker = folium.map.Marker(
        coordinate_i,
        # Create an icon as a text label
        icon=DivIcon(
            icon_size=(20,20),
            icon_anchor=(0,0),
            html=f'<div style="font-size: 12; color:#d35400;"><b>{site_name_i}</b></div>'
            )
        )
    site_map.add_child(circle)
    site_map.add_child(marker)
    
file_path = os.path.abspath("spacex_launch_sites_map.html")
# site_map.save(file_path)

# webbrowser.open(f"file://{file_path}")

# Task 2: Mark the success/failed launches for each site on the map

spacex_df.tail(10)

marker_cluster = MarkerCluster()

# Apply a function to check the value of `class` column
# If class=1, marker_color value will be green
# If class=0, marker_color value will be red
spacex_df['marker_color'] = spacex_df['class'].apply(lambda x: 'green' if x == 1 else 'red')
# Add marker_cluster to current site_map
site_map.add_child(marker_cluster)

# for each row in spacex_df data frame
# create a Marker object with its coordinate
# and customize the Marker's icon property to indicate if this launch was successed or failed, 
# e.g., icon=folium.Icon(color='white', icon_color=row['marker_color']
for index, row in spacex_df.iterrows():
    coordinate = [row['Lat'], row['Long']]
    site_name = row['Launch Site']
    launch_result = 'Success' if row['class'] == 1 else 'Failure'
    color = row['marker_color']
    
    # Create and add marker to the cluster
    marker = folium.Marker(location=coordinate,popup=f"{site_name} - {launch_result}",icon=folium.Icon(color=color))
    marker_cluster.add_child(marker)


site_map.save(file_path)

webbrowser.open(f"file://{file_path}")

# TASK 3: Calculate the distances between a launch site to its proximities

# Add Mouse Position to get the coordinate (Lat, Long) for a mouse over on the map
formatter = "function(num) {return L.Util.formatNum(num, 5);};"
mouse_position = MousePosition(
    position='topright',
    separator=' Long: ',
    empty_string='NaN',
    lng_first=False,
    num_digits=20,
    prefix='Lat:',
    lat_formatter=formatter,
    lng_formatter=formatter,
)

site_map.add_child(mouse_position)

from math import sin, cos, sqrt, atan2, radians

def calculate_distance(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

coastline_lat = 28.56260
coastline_lon = -80.56786

launch_site = 'CCAFS LC-40'
launch_row = launch_sites_df[launch_sites_df['Launch Site'] == launch_site].iloc[0]
launch_lat = launch_row['Lat']
launch_lon = launch_row['Long']

distance_km = calculate_distance(launch_lat, launch_lon, coastline_lat, coastline_lon)
print(f"Distance to coast: {distance_km:.2f} km")

# Add a marker on the coastline
folium.Marker(location=[coastline_lat, coastline_lon],popup='Coastline',icon=folium.Icon(color='blue', icon='info-sign')).add_to(site_map)

# Add a distance label (as a text icon on the map)
folium.Marker(location=[(launch_lat + coastline_lat)/2, (launch_lon + coastline_lon)/2], icon=DivIcon(icon_size=(250,36),icon_anchor=(0,0),
        html=f'<div style="font-size: 12px; color:#d35400;"><b>{distance_km:.2f} KM</b></div>',)).add_to(site_map)

# Optionally, draw a line between the two points
folium.PolyLine(
    locations=[[launch_lat, launch_lon], [coastline_lat, coastline_lon]],
    color='blue',
    weight=2.5,
    opacity=0.7
).add_to(site_map)

site_map.save(file_path)

webbrowser.open(f"file://{file_path}")









































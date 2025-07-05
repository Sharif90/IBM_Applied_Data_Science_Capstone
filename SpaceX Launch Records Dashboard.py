#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  5 19:07:30 2025

@author: mohammadalsharif
"""

# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import webbrowser
import threading
import requests
import os 
import io


URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"

# Fetch the content using requests
response = requests.get(URL)

# Raise an error if the request failed
response.raise_for_status()

# Convert response content into a BytesIO stream and read it into pandas
spacex_csv_file = io.BytesIO(response.content)
spacex_df = pd.read_csv(spacex_csv_file)
# Read the airline data into pandas dataframe
# spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=[
                                            {'label': 'All Sites', 'value': 'ALL'},
                                            *[{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]
                                        ],
                                        value='ALL',
                                        placeholder="Select a Launch Site here",
                                        searchable=True
                                    ),
                                    html.Br(),

                                    # TASK 2: Pie chart showing success stats
                                    html.Div(dcc.Graph(id='success-pie-chart')),
                                    html.Br(),

                                    html.P("Payload range (Kg):"),

                                    # TASK 3: Range slider (To be implemented)
                                    # dcc.RangeSlider(id='payload-slider', ...)
                                    dcc.RangeSlider(
                                        id='payload-slider',
                                        min=0,
                                        max=10000,
                                        step=1000,
                                        marks={i: f'{i}' for i in range(0, 10001, 2500)},  # Optional: show marks every 2500kg
                                        value=[min_payload, max_payload]  # Initial range from min to max payload in data
                                    ),
                                    # TASK 4: Scatter chart for payload vs. success
                                    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Filter only successful launches
        all_success_df = spacex_df[spacex_df['class'] == 1]
        # Create a pie chart showing total successful launches by site
        fig = px.pie(
            all_success_df,
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # Filter data for the selected site
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count both success and failure
        site_counts = site_df['class'].value_counts().reset_index()
        site_counts.columns = ['Outcome', 'Count']
        site_counts['Outcome'] = site_counts['Outcome'].replace({1: 'Success', 0: 'Failure'})
        # Create pie chart for this site
        fig = px.pie(
            site_counts,
            names='Outcome',
            values='Count',
            title=f'Success vs Failure Launches for site {entered_site}'
        )
        return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter data by payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    if selected_site == 'ALL':
        # Scatter plot for all sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for All Sites'
        )
    else:
        # Filter data for selected site
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {selected_site}'
        )

    return fig

# Run the app
if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:8050")

    threading.Timer(1, open_browser).start()  # open browser after 1 second delay
    app.run()

# if __name__ == '__main__':
#     app.run_server(debug=True, use_reloader=False)
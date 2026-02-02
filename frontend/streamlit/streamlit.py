import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopy
from geopy.geocoders import Nominatim
import calendar
import os
import seaborn as sns
from PIL import Image
import colorlover as cl
import matplotlib.colors as mcolors
from datetime import datetime
import numpy as np
# Load data with longitude and latitude information into a pandas DataFrame

st.header("Where's Conan?")

print(os.path)

image = Image.open('./conanimage.PNG')

st.image(image)
data = pd.read_csv(
    './berlin_final_table.csv')

def assign_color(row):
    for crime_type in row.index:
        if row[crime_type] == 1:
            return crime_types_color[crime_type]
    return 'default_color'


crime_types_color = {
    'homicide' :'orangered', 'property_damage':'blue',
    'drug_offenses': 'grey', 'general_assault':'black', 'sexual_assault':'purple',
    'sexual_assault':'yellow', 'property_crimes':'red','hate_crime-disability':'pink','hate_crime-gender':'salmon', 'hate_crime-gender_identity' :'violet',
    'hate_crime-religious' : 'tomato', 'hate_crime-sexual_orientation':'lightcoral',
    'hate_crime-sexual_orientation':'green','unclassified' : 'pink','I wanna see All':'green'
}

#Create a drop-down for users to select the crime
selected_crime_type = st.multiselect('Crime you want to detect', list(crime_types_color.keys()))
data['year_date'] = pd.to_datetime(data['year_date'])
min_date = data['year_date'].min().to_pydatetime().date()
max_date = data['year_date'].max().to_pydatetime().date()
default_date = datetime.today().date()  # Change this if you want a different default value
if default_date < min_date or default_date > max_date:
    default_date = min_date

selected_date = st.date_input('Select a date', value=default_date,min_value=min_date, max_value=max_date)

filtered_df = data[data['year_date'] == pd.Timestamp(selected_date)]


# Filter the data based on the selected options
# Filter the data based on the selected options
if 'I wanna see All' in selected_crime_type:
    crime_columns = [col for col in data.columns if col not in ['year_date', 'lat', 'lon', 'type_of_crime', 'location', 'unique_case_id', 'victim_sex', 'offender_sex', 'number_of_victims', 'number_of_offenders', 'Output', 'Good_output']]
    filtered_data = data.groupby(['lat', 'lon'])[crime_columns].sum().reset_index()
else:
    if len(selected_crime_type) == 0:
        filtered_data = pd.DataFrame(columns=['lat', 'lon'])
    else:
        columns_to_select = ['lat', 'lon'] + selected_crime_type
        filtered_data = data.groupby(['lat', 'lon'])[columns_to_select].sum().reset_index(drop=True)
        for option in selected_crime_type:
            color = crime_types_color[option]
            if option != 'I wanna see All' and option in filtered_data.columns:
                filtered_data.loc[filtered_data[option] > 0, 'color'] = color



# Update the 'color' column with a default color if no color has been assigned
filtered_data['color'] = filtered_data.get('color', 'default_color')

# Create a scatter mapbox plot with customized marker colors
fig = px.scatter_mapbox(filtered_data, lat='lat', lon='lon', color='color',
                        color_discrete_map=crime_types_color,
                        hover_data={'lat': False, 'lon': False, 'color': True},
                        zoom=10, mapbox_style='stamen-toner', opacity= 0.7)






selected_time = st.radio('Which time slot you will be there', options=[
'Midnight (0-4)',
'Early Morning (4-8)',
'Morning (8-12)',
'Afternoon (12-16)',
'Evening (16-20)',
'Night (20-24)'] ,horizontal=True)





radius_mapping = {
    'Midnight (0-4)': 20,
    'Early Morning (4-8)': 15,
    'Morning (8-12)': 15,
    'Afternoon (12-16)': 20,
    'Evening (16-20)': 20,
    'Night (20-24)': 25
}

radius = radius_mapping[selected_time]
fig.update_traces(marker=dict(size=radius))


# Customize the marker colors based on the selected options
# for i, option in enumerate(selected_crime_type):
#     color = crime_types_color[option]
#     fig.data[i].marker.color = [color] * len(fig.data[i].lat)

filtered_data['color'] = filtered_data.get('color', 'green')  # fallback

address = st.text_input('Where you are going', '')


st.write('Map of crime incidents in Berlin')


geolocator = Nominatim(user_agent='my_geocoder')

location = geolocator.geocode(address, country_codes='de')

if location:
    st.write(f"Geocoded address: {location.address}")
    st.write(f"Latitude: {location.latitude}, Longitude: {location.longitude}")
else:
    st.warning("Address could not be geocoded.")


if location:
    entered_lat = location.latitude
    entered_lon = location.longitude
    #Update the map with the new location
    fig.update_layout(mapbox_center={"lat": entered_lat, "lon": entered_lon}, mapbox_zoom=12)

    # Add a marker for the entered address
    fig.add_trace(go.Scattermapbox(
        lat=[entered_lat],
        lon=[entered_lon],
        mode='markers',
        marker={'size': 10, 'color': 'blue'}
    ))

st.plotly_chart(fig)


# Build a legend

st.sidebar.markdown('**Legend:**')

# Iterate over the crime_types_color dictionary and display legend entries
for crime_type, color in crime_types_color.items():
    st.sidebar.markdown(f'<span style="color: {color}">■</span> {crime_type}', unsafe_allow_html=True)



st.sidebar.write('Entered address:', address)

# Display the selected date
st.sidebar.write('Selected date:', selected_date)

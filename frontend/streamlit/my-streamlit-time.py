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


st.header("Finding Conan")

script_path = os.path.dirname(__file__)

pna_file = script_path+'/conanimage.PNG'
image = Image.open(pna_file)

st.image(image)

csv_file = script_path+'/final_table.csv'
data = pd.read_csv(csv_file)

default_color = 'black'
crime_types_color = {
    'homicide' :'Maroon',
    'drug_offenses': 'CornflowerBlue',
    'general_assault':'SteelBlue',
    'verbal_assault':'DarkOrange',
    'sexual_assault':'Gold',
    'sexual_harassment':'Orange',
    'property_crime':'rosybrown',
    'property_damage':'DarkGoldenRod',
    'hate_crime-disability':'Chocolate',
    'hate_crime-gender_identity':'IndianRed',
    'hate_crime-gender':'salmon',
    'hate_crime-racial/ethnicity' :'violet',
    'hate_crime-religious' : 'tomato',
    'hate_crime-sexual_orientation':'lightcoral',
    'unclassified' : 'Peru',
    'I wanna see All':'black'
}

data['year_date'] = pd.to_datetime(data['year_date'])


# Calculate the reference date for comparison
current_date = pd.Timestamp(2023, 5, 24)




#Create a drop-down for users to select the crime
selected_crime_type = st.multiselect('Crime you want to detect', list(crime_types_color.keys()))



selected_time = st.radio('Which time slot you will be there', options=['Midnight',
'Early Morning',
'Morning',
'Afternoon',
'Evening',
'Night'] ,horizontal=True)

selected_time_period = st.selectbox('Time Period', ['Past 1 week', 'Past 1 month', 'Past 3 months', 'Past 1 year', 'Past 2 years'])
# Filter the data based on the selected time period
if selected_time_period == 'Past 1 week':
    filtered_df = data[(current_date - data['year_date']).dt.days <= 7]
elif selected_time_period == 'Past 1 month':
    filtered_df = data[(current_date - data['year_date']).dt.days <= 30]
elif selected_time_period == 'Past 3 months':
    filtered_df = data[(current_date - data['year_date']).dt.days <= 90]
elif selected_time_period == 'Past 1 year':
    filtered_df = data[(current_date - data['year_date']).dt.days <= 365]
elif selected_time_period == 'Past 2 years':
    filtered_df = data[(current_date - data['year_date']).dt.days <= 730]


filtered_df1 = filtered_df[filtered_df['time_slot'] == selected_time]




# Assign colors based on selected crime types
if 'I wanna see All' in selected_crime_type:
    crime_columns = [col for col in data.columns if col not in ['year_date', 'lat', 'lon', 'type_of_crime', 'location', 'unique_case_id', 'victim_sex', 'offender_sex', 'number_of_victims', 'number_of_offenders', 'Output', 'Good_output']]
    filtered_data = filtered_df1.groupby(['lat', 'lon'])[crime_columns].sum().reset_index()
else:
    if len(selected_crime_type) == 0:
        filtered_data = pd.DataFrame(columns=['lat', 'lon','color'])
    else:
        columns_to_select = ['lat', 'lon'] + selected_crime_type
        filtered_data = filtered_df1.groupby(['lat', 'lon'])[columns_to_select].sum().reset_index(drop=True)
        # Assign colors for each selected crime type
        for option in selected_crime_type:
            color = crime_types_color[option]
            if option != 'I wanna see All' and option in filtered_data.columns:
                filtered_data.loc[filtered_data[option] > 0, 'color'] = color


# Update the 'color' column with a default color if no color has been assigned
filtered_data['color'] = filtered_data.get('color', default_color)



# Create a scatter mapbox trace
fig = px.scatter_mapbox(filtered_data, lat='lat', lon='lon',
                        hover_data={'lat': False, 'lon': False, 'color': True},
                        zoom=10, mapbox_style='stamen-toner', opacity=0.7)


radius_mapping = {
    'Midnight': 30,
    'Early Morning': 15,
    'Morning': 15,
    'Afternoon': 20,
    'Evening': 20,
    'Night': 25
}
# Set the marker size based on selected time
radius = radius_mapping[selected_time]

# Assign the marker size and color
fig.update_traces(marker=dict(size=radius, color=filtered_data['color']))




address = st.text_input('Where you are going', '')


st.write('Map of crime incidents in Berlin')


geolocator = Nominatim(user_agent='my_geocoder')
location = geolocator.geocode(address)

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
#st.sidebar.write('Selected date:', selected_date)

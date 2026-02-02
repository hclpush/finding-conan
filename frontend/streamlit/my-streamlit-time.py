import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
import os
from PIL import Image
from datetime import datetime

st.header("Finding Conan")

# Load image
script_path = os.path.dirname(__file__)
image_path = os.path.join(script_path, 'conanimage.PNG')
image = Image.open(image_path)
st.image(image)

# Load data
csv_path = os.path.join(script_path, 'final_table.csv')
data = pd.read_csv(csv_path)
data['year_date'] = pd.to_datetime(data['year_date'])

# Crime type colors
crime_types_color = {
    'homicide': 'Maroon',
    'drug_offenses': 'CornflowerBlue',
    'general_assault': 'SteelBlue',
    'verbal_assault': 'DarkOrange',
    'sexual_assault': 'Gold',
    'sexual_harassment': 'Orange',
    'property_crime': 'rosybrown',
    'property_damage': 'DarkGoldenRod',
    'hate_crime-disability': 'Chocolate',
    'hate_crime-gender_identity': 'IndianRed',
    'hate_crime-gender': 'salmon',
    'hate_crime-racial/ethnicity': 'violet',
    'hate_crime-religious': 'tomato',
    'hate_crime-sexual_orientation': 'lightcoral',
    'unclassified': 'Peru',
    'I wanna see All': 'black'
}
default_color = 'black'

# User filters
selected_crime_type = st.multiselect('Crime you want to detect', list(crime_types_color.keys()))
selected_time = st.radio(
    'Which time slot you will be there',
    ['Midnight', 'Early Morning', 'Morning', 'Afternoon', 'Evening', 'Night'],
    horizontal=True
)
selected_time_period = st.selectbox('Time Period', [
    'Past 1 week', 'Past 1 month', 'Past 3 months', 'Past 1 year', 'Past 2 years'])

# Sidebar: Bubble size slider
desired_max_marker_size_px = st.sidebar.slider("Max bubble size (px)", 10, 50, 20)

# Filter data by time
current_date = pd.Timestamp(2023, 5, 24)
days_map = {
    'Past 1 week': 7,
    'Past 1 month': 30,
    'Past 3 months': 90,
    'Past 1 year': 365,
    'Past 2 years': 730
}
filtered_df = data[(current_date - data['year_date']).dt.days <= days_map[selected_time_period]]
filtered_df = filtered_df[filtered_df['time_slot'] == selected_time]

# Prepare filtered data
if 'I wanna see All' in selected_crime_type:
    crime_columns = [col for col in data.columns if col not in [
        'year_date', 'lat', 'lon', 'type_of_crime', 'location',
        'unique_case_id', 'victim_sex', 'offender_sex',
        'number_of_victims', 'number_of_offenders', 'Output', 'Good_output'
    ]]
    filtered_data = filtered_df.groupby(['lat', 'lon'])[crime_columns].sum().reset_index()
else:
    if len(selected_crime_type) == 0:
        filtered_data = pd.DataFrame(columns=['lat', 'lon'])
    else:
        filtered_data = filtered_df.groupby(['lat', 'lon'])[selected_crime_type].sum().reset_index()

# Initialize map
fig = go.Figure()

# Add traces for each selected crime type
if not filtered_data.empty and len(selected_crime_type) > 0:
    for crime in selected_crime_type:
        if crime in filtered_data.columns:
            crime_data = filtered_data[filtered_data[crime] > 0]
            if not crime_data.empty:
                max_cases = crime_data[crime].max()
                sizeref = 2. * max_cases / (desired_max_marker_size_px ** 2)

                fig.add_trace(go.Scattermapbox(
                    lat=crime_data['lat'],
                    lon=crime_data['lon'],
                    mode='markers',
                    marker=dict(
                        size=crime_data[crime].clip(lower=1).astype(float),
                        color=crime_types_color[crime],
                        opacity=0.7,
                        sizemode='area',
                        sizeref=sizeref,
                        sizemin=5
                    ),
                    name=f"{crime} ({crime_data[crime].sum()} cases)",
                    hovertext=crime_data[crime].astype(str) + " case(s)",
                    hoverinfo="text"
                ))

# Default center: Berlin
fig.update_layout(
    mapbox=dict(
        style='open-street-map',
        zoom=10,
        center=dict(lat=52.52, lon=13.405)
    ),
    margin=dict(r=0, l=0, b=0, t=0)
)

# User address input
address = st.text_input('Where you are going', '')

if address:
    try:
        geolocator = Nominatim(user_agent='my_geocoder')
        location = geolocator.geocode(address)
        if location:
            entered_lat = location.latitude
            entered_lon = location.longitude

            fig.add_trace(go.Scattermapbox(
                lat=[entered_lat],
                lon=[entered_lon],
                mode='markers',
                marker=dict(size=15, color='red'),
                name="Your Location"
            ))

            fig.update_layout(mapbox_center=dict(lat=entered_lat, lon=entered_lon), mapbox_zoom=12)
        else:
            st.warning("Could not geocode the address. Try a more specific one.")
    except Exception as e:
        st.error(f"Geocoding error: {e}")

# Display map or warning
st.write('Map of crime incidents in Berlin')
if len(fig.data) > 0:
    st.plotly_chart(fig)
else:
    st.warning("No data matches your filters. Try different options.")

# Sidebar legend for selected crimes only
st.sidebar.markdown('**Legend (Selected Crimes):**')
for crime in selected_crime_type:
    color = crime_types_color.get(crime, 'black')
    st.sidebar.markdown(f'<span style="color:{color}">■</span> {crime}', unsafe_allow_html=True)

# Sidebar info
st.sidebar.write('Entered address:', address if address else 'None')

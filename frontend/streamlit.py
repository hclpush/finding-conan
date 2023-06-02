import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopy
from geopy.geocoders import Nominatim
import calendar

# Load data with longitude and latitude information into a pandas DataFrame

data = pd.read_csv('berlin_data.csv')
location_counts = data.groupby(['lat','lon']).size().reset_index(name = 'count')
data['Date'] = pd.to_datetime(data['Date']).dt.date

# Create a density heatmap using Plotly Express
fig = px.density_mapbox(data, lat=data['lat'], lon=data['lon'], radius=location_counts['count'],  opacity=0.7, color_continuous_scale='YlOrRd',
                        zoom=10, mapbox_style='carto-positron',animation_frame=data['Date'])


address = st.text_input('Enter an address', '')
geolocator = Nominatim(user_agent='my_geocoder')
location = geolocator.geocode(address)

if location:
    entered_lat = location.latitude
    entered_lon = location.longitude
    # Update the map with the new location
    fig.update_layout(mapbox_center={"lat": entered_lat, "lon": entered_lon}, mapbox_zoom=12)

    # Add a marker for the entered address
    fig.add_trace(go.Scattermapbox(
        lat=[entered_lat],
        lon=[entered_lon],
        mode='markers',
        marker={'size': 10, 'color': 'blue'}
    ))

    st.plotly_chart(fig)

selected_date = st.date_input('Select a date')



# Display the heatmap in Streamlit
st.write('Entered address:', address)

# Display the selected date
st.write('Selected date:', selected_date)

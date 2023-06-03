import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopy
from geopy.geocoders import Nominatim
import calendar
import seaborn as sns
# Load data with longitude and latitude information into a pandas DataFrame

data = pd.read_csv('dummy_table.csv')
#location_counts = data.groupby(['lat','lon']).size().reset_index(name = 'count')

data['Date'] = pd.to_datetime(data['Date']).dt.date

crime_types = data.columns[17:36]  # Assuming the first column contains dates
selected_crime_type = st.selectbox('Select a crime type', crime_types)

filtered_df = data[['Date', 'lat','lon',selected_crime_type]]

#Group the incident that happens in the same day
#grouped_df = data.groupby('Date')[selected_crime_type].sum().reset_index()
#pivoted_df = grouped_df.pivot_table(index='Date', values=selected_crime_type)
location_counts = filtered_df.groupby(['lat', 'lon']).size().reset_index(name='Incident Count')
# Create a density heatmap using Plotly Express
fig = px.density_mapbox(data, lat=data['lat'], lon=data['lon'], radius= location_counts['Incident Count']*10,  opacity=0.7, color_continuous_scale='YlOrRd',
                      zoom=10, mapbox_style='carto-positron',animation_frame = data["Date"] )
address = st.text_input('Enter an address', '')

st.write('Heatmap of crime incidents')

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

selected_date = st.date_input('Select a date')





st.write('Entered address:', address)

# Display the selected date
st.write('Selected date:', selected_date)

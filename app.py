# Code copied from here https://github.com/randyzwitch/streamlit-folium/blob/master/examples/interactive_app.py
import streamlit as st
from dataclasses import dataclass
from typing import Dict,  Optional
from streamlit_folium import st_folium
from google.cloud import bigquery
from google.oauth2 import service_account
import folium,json
import pandas as pd
@dataclass
class Point:
    lat: float
    lon: float

    @classmethod
    def from_dict(cls, data: Dict) -> "Point":
        if "lat" in data:
            return cls( float(data["lng"]),float(data["lat"]))
        elif "latitude" in data:
            return cls( float(data["longitude"]),float(data["latitude"]))
        else:
            raise NotImplementedError(data.keys())
#Update Varaible           
if 'key' not in st.session_state:
    st.session_state.key = '( 153.024198,-27.467276)'
    st.session_state.key1 = [-27.467276, 153.024198]
    st.session_state.key2 = 16
point_clicked = st.session_state.key
location_ini  = st.session_state.key1
zoom_Start    = st.session_state.key2

m = folium.Map(location=location_ini, zoom_start=zoom_Start)
################################################### Download Data from BigQuery#####################################################
# Retrieve and convert key file content.
bigquery_key_json = json.loads(st.secrets["bigquery_key"], strict=False)
credentials = service_account.Credentials.from_service_account_info(bigquery_key_json)
# Create API client.
client = bigquery.Client(credentials=credentials)
query = '''--Streamlit 
            WITH  params AS ( SELECT  ST_GeogPoint'''+point_clicked+''' AS center,500 AS maxdist_m )
            SELECT
            name,
            country,lng,lat,
            ST_Distance(ST_GeogPoint(lng,lat),params.center)/1000 AS distance
            FROM
            test-187010.gis_tokyo.cafe,params
            WHERE
            ST_DWithin(ST_GeogPoint(lng,lat),params.center,params.maxdist_m)'''

@st.experimental_memo()
def Get_Bq(query,_cred) :
        df=pd.read_gbq(query,credentials=_cred)
        return df
result = Get_Bq(query,credentials)
locations = result[['lat', 'lng']]
locationlist = locations.values.tolist()
# center on Brisbane

# add marker
for point in range(0, len(locationlist)):
    folium.Marker(locationlist[point], popup=result['name'][point]).add_to(m)
map_data = st_folium(m, width = 925)

# print point clicked
try:
    point_clicked: Optional[Point] = Point.from_dict(map_data["last_clicked"])

    if point_clicked is not None:
       point_clicked = str(point_clicked).replace('Point(lat=', '(')
       point_clicked = point_clicked.replace('lon=', '')
       location_ini = point_clicked.replace('(', '')
       location_ini = location_ini.replace(')', '')
       location_ini = str(location_ini).split(sep=',')
       location_ini[0],location_ini[1]= location_ini[1],location_ini[0]
       #st.write(location_ini)
       location_ini = [float(i) for i in location_ini]
       #st.write(point_clicked)
       st.session_state.key = point_clicked
       st.session_state.key1 = location_ini
       st.session_state.key2 = map_data['zoom']
except TypeError:
    point_clicked = None
#st.write(st.session_state.key)
#st.dataframe(result)

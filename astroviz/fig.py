from plotly.subplots import make_subplots
import plotly.graph_objects as go
import requests
import datetime
from datetime import date, timedelta, datetime
import json
import pandas as pd

# asteroid Neows API code
def fetchAsteroidNeowsFeed():
  URL_NeoFeed = "https://api.nasa.gov/neo/rest/v1/feed"
  apiKey = '6iYIMnqheSezBZgkZrRrcFv9i1MCwU6geIqDR4bq'
  date_ = date.today()
  today=date_.strftime("%Y-%m-%d")
  params = {
      'api_key':apiKey,
      'start_date':today,
      'end_date':today
  }
  response = requests.get(URL_NeoFeed,params=params).json()
  df_neo = pd.DataFrame(response['near_earth_objects'])
  df_neo = pd.DataFrame(response['near_earth_objects'][today])
  df_neo=df_neo.drop(['links','nasa_jpl_url'],axis=1)
  close_approach_data=pd.DataFrame()
  close_approach_data['close_approach_data']=df_neo["close_approach_data"]
  close_approach_data = close_approach_data['close_approach_data'].apply(pd.Series)
  close_approach_data = close_approach_data[0].apply(pd.Series)
  close_approach_data=close_approach_data.drop(['relative_velocity','orbiting_body','close_approach_date','epoch_date_close_approach'],axis=1)
  close_approach_data = close_approach_data['miss_distance'].apply(pd.Series).drop(['astronomical','lunar','miles'],axis=1)
  estimated_diameter=pd.DataFrame()
  estimated_diameter = df_neo['estimated_diameter'].apply(pd.Series)
  estimated_diameter=estimated_diameter.drop(['meters','miles','feet'],axis=1)
  estimated_diameter = estimated_diameter['kilometers'].apply(pd.Series)
  df_neo['estimated_diameter_min'],df_neo['estimated_diameter_max']=estimated_diameter['estimated_diameter_min'],estimated_diameter['estimated_diameter_max']
  df_neo.drop(['estimated_diameter','close_approach_data','id','neo_reference_id'],axis=1,inplace=True)
  df_neo['miss_distance_kilometers']=close_approach_data['kilometers']
  return df_neo

  # Solar Flare API code
def solar_flare():
  apiKey = '6iYIMnqheSezBZgkZrRrcFv9i1MCwU6geIqDR4bq'
  URL_NeoFeed = "https://api.nasa.gov/DONKI/FLR"
  date_ = date.today()
  today=date_.strftime("%Y-%m-%d")
  end_day_=date.today()-timedelta(40)
  end_day=end_day_.strftime("%Y-%m-%d")
  params = {
      'api_key':apiKey,
      'start_date':end_day,
      'end_date':today
  }
  response = requests.get(URL_NeoFeed,params=params).json()
  df_sf = pd.DataFrame(response)
  df_sf.drop(['instruments','linkedEvents','link',],axis=1,inplace=True)
  return df_sf
solar_data = solar_flare()

# CAD API code
def cad():
  URL_cad = "https://ssd-api.jpl.nasa.gov/cad.api?body=ALL"
  response = requests.get(URL_cad).json()
  df=pd.DataFrame(response['data'])
  df.columns=['primary_designation','orbit_ID','jd','time_of_close_approach','nominal_approach_distance','minimum_approach_distance','maximum_approach_distance','v_rel','v_inf','t_sigma_f','body','h']
  df.drop(['jd','v_rel','v_inf','t_sigma_f','h'],axis=1,inplace=True)
  return df
cad_data = cad()

#fetchAsteroidNeowsFeed()
file_data = fetchAsteroidNeowsFeed()

#stars classification csv file
stars = pd.read_csv("starclassification.csv")
#asteroid impact csv file
impact=pd.read_csv('impacts.csv')
#satellite classification
sat_data = pd.read_csv('UCS-Satellite-Database-Officialname-1-1-2021.csv') 

fig = make_subplots(rows=8, cols = 2,
                    subplot_titles = ("Temperature vs Star Type", "Temperature vs Star Color", "Relative Luminosity vs Star Type", "Relative Radius vs Star Type",
                                      "Beginning Time of Solar Flare ","Maximum Approach Distance of Comet ","Peak Time of Solar Flare", "Nominal Approach Distance of Comet","Ending Time of Solar Flare", "Minimum Approach Distance of Comet",
                                      "Near Earth Asteroids", "Possible Collision from Asteroids",
                                      "Satellite Count for each Launch Site", "Types of Users", "Satellite Count for each Launch Vehicle","Purpose"),
                    specs=[[{}, {}], [{}, {}], [{}, {}], [{}, {}], [{}, {}], [{}, {}], [{}, {"type": "pie"}], [{}, {"type": "pie"}]]
                    )



fig.add_trace(go.Scatter(y = stars.Star_type,
                         x = stars.Temperature,
                         mode = "markers",
                         name = 'type',
                         marker = dict(color = 'rgba(0,0,200,0.8)')),
              row = 1, col = 1)
#temp vs star color
fig.add_trace(go.Scatter(y = stars.Star_color,
                         x = stars.Temperature,
                         mode = "markers",
                         name = "color",
                         marker = dict(color = 'rgba(0,200,0,0.8)')),
              row = 1, col = 2)
fig.update_layout(height=1000, width=1400)

#relative luminosity vs star type
fig.add_trace(go.Scatter(y = stars.Star_type,
                         x = stars.Luminosity,
                         mode = "markers",
                         name = 'luminosity',
                         marker = dict(color = 'rgba(200,0,0,0.8)')),
              row = 2, col = 1)
fig.update_layout(height=1000, width=1400)

#relative radius vs star type
fig.add_trace(go.Scatter(y = stars.Star_type,
                         x = stars.Radius,
                         mode = "markers",
                         name = 'radius',
                         marker = dict(color = 'rgba(200,20,60,0.8)')),
              row = 2, col = 2)
fig.update_layout(height=3500, width=1800)
fig.update_xaxes(title_text="temperature", row=1, col=1)
fig.update_xaxes(title_text="temperature", row=1, col=2)
fig.update_xaxes(title_text="relative luminosity", row=2, col=1)
fig.update_xaxes(title_text="relative radius", row=2, col=2)
fig.update_yaxes(title_text="star type", row=1, col=1)
fig.update_yaxes(title_text="star color", row=1, col=2)
fig.update_yaxes(title_text="star type", row=2, col=1)
fig.update_yaxes(title_text="star type", row=2, col=2)


#solar flare
fig.add_trace(go.Scatter(x = solar_data.flrID,
                         y = solar_data.beginTime,
                         mode = "lines+markers",
                         name = "Begin Time of Solar Flare",
                         marker = dict(color = 'rgba(0,255,200,0.8)'),
                         text = "Class Type: " + solar_data["classType"].astype(str) + "<br>Source Location: " + solar_data["sourceLocation"].astype(str)),
              row = 3, col = 1)
fig.add_trace(go.Scatter(x = solar_data.flrID,
                         y = solar_data.peakTime,
                         mode = "lines+markers",
                         name = "Peak Time of Solar Flare",
                         marker = dict(color = 'rgba(255,128,255,0.8)'),
                         text = "Class Type: " + solar_data["classType"].astype(str) + "<br>Source Location: " + solar_data["sourceLocation"].astype(str)),
              row = 4, col = 1)
fig.add_trace(go.Scatter(x = solar_data.flrID,
                         y = solar_data.endTime,
                         mode = "lines+markers",
                         name = "End Time of Solar Flare",
                         marker = dict(color = 'rgba(255,25,0,0.8)'),
                         text = "Class Type: " + solar_data["classType"].astype(str) + "<br>Source Location: " + solar_data["sourceLocation"].astype(str)),
              row = 5, col = 1)

fig.update_xaxes(title_text="Solar Flare ID", row=5, col=1)
fig.update_yaxes(title_text="Time", row=4, col=1)


#CAD
fig.add_trace(go.Scatter(x = cad_data.time_of_close_approach,
                         y = cad_data.maximum_approach_distance,
                         mode = "lines+markers",
                         name = "Maximum Distance of Comet from Planet",
                         marker = dict(color = 'rgba(0,255,200,0.8)'),
                         text = "Celestial Body: " + cad_data["body"].astype(str) + "<br>Name of Comet: " + cad_data["primary_designation"].astype(str),),
              row = 3, col = 2)
fig.add_trace(go.Scatter(x = cad_data.time_of_close_approach,
                         y = cad_data.nominal_approach_distance,
                         mode = "lines+markers",
                         name = "Nominal Distance of Comet from Planet",
                         marker = dict(color = 'rgba(255,128,255,0.8)'),
                         text = "Celestial Body: " + cad_data["body"].astype(str) + "<br>Name of Comet: " + cad_data["primary_designation"].astype(str),),
              row = 4, col = 2)
fig.add_trace(go.Scatter(x = cad_data.time_of_close_approach,
                         y = cad_data.minimum_approach_distance,
                         mode = "lines+markers",
                         name = "Minimum Distance of Comet from Planet",
                         marker = dict(color = 'rgba(255,25,0,0.8)'),
                         text = "Celestial Body: " + cad_data["body"].astype(str) + "<br>Name of Comet: " + cad_data["primary_designation"].astype(str),),
              row = 5, col = 2)

fig.update_xaxes(title_text="Close Approach Time", row=5, col=2)
fig.update_yaxes(title_text="Distance", row=4, col=2)


#Asteroid
fig.add_trace(go.Scatter(x = file_data.name,
           y = file_data.miss_distance_kilometers,
           mode = "markers",
           name = "Asteroid",
           marker = dict(color=file_data.estimated_diameter_max,size = file_data.absolute_magnitude_h,colorscale='sunsetdark'),
           text = "Dangerous Asteroid: " + file_data["is_potentially_hazardous_asteroid"].astype(str) + "<br>Diameter of Asteroid:" + file_data["estimated_diameter_max"].astype(str)),
           row = 6, col =1)

fig.add_trace(go.Scatter(x = impact.Possible_Impacts,
           y = impact.Period_End,
           mode = "markers",
           name = "Impact Probability",
           marker = dict(color = impact.Diameter, 
                         size=impact.Asteroid_Magnitude,
                         colorscale = 'balance'),
           text= impact.Name),
           row =6, col =2)
#fig.update_layout(height=1400, width=1400)
fig.update_xaxes(title_text="Name of asteroid(km)", row=6, col=1)
fig.update_yaxes(title_text="Miss distance from Earth(km)", row=6, col=1)
fig.update_xaxes(title_text="Possible Impacts", row=6, col=2)
#fig.show(renderer="colab")


#satellite bar

fig.add_trace(go.Bar(x = sat_data.Launch_Site,
                     y = sat_data.Launch_Site.value_counts(),
                     name = "Total Satellite wrt Launch_Site",
                     marker = dict(color='rgba(255,128,255,0.8)',
                                   line=dict(color='rgb(0,0,0)',
                                             width = 0) 
                                   ),
                     text = sat_data.Launch_Site),
              row = 7, col = 1)

fig.add_trace(go.Bar(x = sat_data.Launch_Vehicle,
                     y = sat_data.Launch_Vehicle.value_counts(),
                     name = "Total Satellite wrt Launch_Vehicle",
                     marker = dict(color='rgba(255,25,0,0.8)',
                                   line=dict(color='rgb(0,0,0)',
                                             width = 0) 
                                   ),
                     text = sat_data.Launch_Vehicle),
              row = 8, col = 1)


#fig.update_layout(height=1400)

fig.update_xaxes(title_text="Owner", row=9, col=1)
fig.update_xaxes(title_text="Launch Sites", row=7, col=1)
fig.update_xaxes(title_text="Launch Vechicles", row=8, col=1)
fig.update_yaxes(titl1e_text="No. of Satellites", row=9, col=1)
fig.update_yaxes(title_text="No. of Satellites", row=7, col=1)
fig.update_yaxes(title_text="No. of Satellites", row=8, col=1)
#fig.show(renderer="colab")


fig.add_trace(go.Pie(
     values=sat_data.Users.value_counts(),
     labels=sat_data.Users,
     domain=dict(x=[0, 0.5]),
     name="Users"), 
     row=7, col=2)

#Pie chart for Purpose
fig.add_trace(go.Pie(values=sat_data.Purpose.value_counts(),
                     labels=sat_data.Purpose,
                     domain=dict(x=[0.5, 1.0]),
                     name="purpose"), 
              row=8, col=2)


fig.write_html('dashboard.html', auto_open=True)

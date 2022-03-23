
# Flask Site for Bike Rides and Walks in Nature ...

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import folium
import pandas as pd
import geoutils as gu
import osmnx as ox
import networkx as nx
import json
import os



app = Flask(__name__)

all_maps1 = [
    {
        'id' : 'SafeHouse1',
        'title': 'Safe House to Maroussi',
        'vehicle_id': "Βike",
        'image_file': "/static/images/Safe_House_to_Maroussi_.jpg",
        'map_loc' : [38.083, 23.831],
        'map_zs' : 13,
        'geo_file' : 'Safe_House_to_Maroussi_.geojson'
    },
    {
        'id' : 'Nemea_Palyvos',
        'title': 'Nemea Palyvos',
        'vehicle_id': "Bike",
        'image_file': "/static/images/Nemea.jpg",
        'map_loc' : [37.830, 22.629],
        'map_zs' : 13,
        'geo_file' : 'Nemea.geojson'
    },
    {
        'id' : 'Kalamata_Karveli',
        'title': 'Kalamata to Karveli mountain path',
        'vehicle_id': "Walk",
        'image_file': "/static/images/Hanakia2Karveli.jpg",
        'map_loc' : [37.067, 22.186],
        'map_zs' : 14,
        'geo_file' : 'Hanakia2Karveli.geojson'
    }
]

mdf = pd.read_json("/home/kvlahodim/mysite/all_maps.json")
all_maps = mdf.to_dict('records')

@app.route('/')
def index():
    return render_template('index.html', maps=all_maps, my_area = 'All')

@app.route('/routes/<string:route_name>/type/<int:vehicle_id>')
def display_map_name(route_name, vehicle_id):
    return "This is the map of route " + route_name + " for vehicle " + str(vehicle_id)

@app.route('/route_details/<string:route_id>')
def display_route_details(route_id):
    for p1 in all_maps:
        if route_id == p1['id'] :
            my_ride_file = '/home/kvlahodim/mysite/geo_data/' + p1['geo_file']
            elev_vector = gu.route_profile(my_ride_file)
            rmetrics = gu.route_metrics(my_ride_file)
            if p1['dist_km'] == 0 :
                p1['dist_km'] = rmetrics[0]
            if p1['elev'] == 0:
                p1['elev'] = rmetrics[1]
            return render_template('route_details.html', map=p1, route_prof = elev_vector)
    return "Invalid Route Id: " + route_id

@app.route('/route_map/<string:route_id>')
def display_map(route_id):
    for p in all_maps:
        if route_id == p['id'] :
            m = folium.Map(location = p['map_loc'], zoom_start=p['map_zs'])
            my_ride_file = '/home/kvlahodim/mysite/geo_data/' + p['geo_file']
            if (p['map_zs']==0) :
                if p['map_sw'] :
                    m.fit_bounds([p['map_sw'], p['map_ne']])
                else : # Calculate map bounding box if not provided (empty list)
                    m.fit_bounds(gu.bbox(my_ride_file))

            gj = folium.GeoJson(my_ride_file, name=p['title'])
            gj.add_to(m)
            folium.LayerControl().add_to(m)
            return m._repr_html_()
    return "No map exists for " + route_id

@app.route('/route_area/<string:rarea>')
def display_area_routes(rarea):
    area_mdf = mdf[mdf['area'] == rarea]
    area_maps = area_mdf.to_dict('records')
    return render_template('index.html', maps=area_maps, my_area = rarea)

@app.route('/maps0')
def maps0():
    return render_template('maps.html', maps=all_maps)

@app.route('/maps')
def maps():
    return render_template('main_maps.html', maps=all_maps)

@app.route('/mosh')
def mosh():
    return render_template('mosh.html')

@app.route('/osmnx')
def create_path():
    ox.config(log_console=True, use_cache=True)

 #   G_walk = ox.graph_from_place('Manhattan Island, New York City, New York, USA', network_type='walk')
 #   G_walk = ox.graph_from_place('Kalamata, Greece', network_type='walk')
 #   ox.save_graphml(G_walk, '/home/kvlahodim/mysite/geo_data/kalamata.graphml')
#    ox.save_graphml(G_walk, '/home/kvlahodim/mysite/geo_data/manhattan.graphml')
#    G_walk = ox.graph_from_place('Maroussi, Greece', network_type='walk')
#    G_walk = ox.elevation.add_node_elevations_raster(G_walk, filepath = '/home/kvlahodim/mysite/geo_data/marousi_geotiff.tiff')
 #   G_walk = ox.elevation.add_edge_grades(G_walk)
 #   ox.save_graphml(G_walk, '/home/kvlahodim/mysite/geo_data/marousi_elev.graphml')

    G = ox.load_graphml('/home/kvlahodim/mysite/geo_data/attiki_elev_2.graphml')
    fin = '/home/kvlahodim/mysite/geo_data/twopoints.geojson'
    f = open(fin)
    j = json.load(f)
    f.close()
    # os.remove(fin)
    orig_point = j['features'][0]['geometry']['coordinates']
    dest_point = j['features'][1]['geometry']['coordinates']
    orig_node = ox.nearest_nodes(G, orig_point[0], orig_point[1])
    dest_node = ox.nearest_nodes(G, dest_point[0], dest_point[1])
    route = nx.shortest_path(G, orig_node, dest_node, weight='length')

    route_map = ox.plot_route_folium(G, route)

    return route_map._repr_html_()

if __name__ == '__main__':
   app.run(debug=True)




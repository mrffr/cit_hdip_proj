#!/usr/bin/env python3

import folium
import folium.plugins
import json  # for making the tooltips
import configparser
import sys

from connect_db import run_query_db

# queries
cluster_query = ("""
SELECT DISTINCT location.latitude, location.longitude,
    description.description, subcategory.name, category.name,
    police_district.name, neighbourhood.name, intersection.name,
    date.date_time, day_of_week.day, incident.api_row_id
FROM location, incident, description, subcategory, category,
     police_district, neighbourhood, intersection,
     date, day_of_week
WHERE incident.location_id = location.id
    AND incident.description_id = description.id
    AND description.subcategory_id = subcategory.id
    AND subcategory.category_id = category.id
    AND location.police_district_id = police_district.id
    AND location.neighbourhood_id = neighbourhood.id
    AND location.intersection_id = intersection.id
    AND incident.date_id = date.id
    AND date.day_of_week_id = day_of_week.id
ORDER BY incident.api_row_id DESC
LIMIT 1000
""")
# limited size to make it usable

district_query = ("""
SELECT police_district.name
FROM police_district, location, incident
WHERE incident.location_id = location.id
    AND location.police_district_id = police_district.id
""")

neighbourhood_query = ("""
SELECT neighbourhood.name
FROM neighbourhood, location, incident
WHERE incident.location_id = location.id
    AND location.neighbourhood_id = neighbourhood.id
""")


# format the cluster popup so that it is readable
def format_cluster_popup(data):
    # add coords
    popup_text = """
<b>Coords</b>:<br/>
<i>lat</i> {0}, <i>lon</i> {1}""".format(data[0], data[1])
    # add category, subcategory, description
    popup_text += """
<br/>
<b>Crime</b>:<br/>
<i>{0}</i>,<br/>
<i>{1}</i>,<br/>
<i>{2}</i>""".format(data[4], data[3], data[2])
    # add street, neighbourhood, district
    popup_text += """
<br/>
<b>Area</b>:<br/>
<i>{0}</i>,<br/>
<i>{1}</i>,<br/>
<i>{2}</i>""".format(data[7], data[6], data[5])
    # add day and datetime
    popup_text += """
<br/>
<b>Date</b>:<br/>
<i>{0}</i>,<br/>
<i>{1}</i>""".format(data[9], data[8])
    return popup_text


def make_cluster_map(fname):
    m = get_map()
    marker_cluster = folium.plugins.MarkerCluster()

    cluster_data = run_query_db(cluster_query)

    # add markers to map
    for data in cluster_data:
        coords = [data[0], data[1]]
        popup_text = format_cluster_popup(data)
        # set the width of the popup otherwise it seems
        # to become cramped
        popup = folium.Popup(popup_text, max_width=250)

        # create the marker and add it to them map
        marker = folium.Marker(location=coords, popup=popup)
        marker_cluster.add_child(marker)

    # save the map
    m.add_child(marker_cluster)
    m.save(fname)


def make_choropleth_neighb(m, neighb_geo):
    # get neighbourhood of every incident
    data = run_query_db(neighbourhood_query)

    # for some reason it returns tuples
    data = [d[0] for d in data]

    # create list of neighbourhoods and number of incidents
    uniq = set(data)
    data = [[neighb, data.count(neighb)] for neighb in uniq]

    # TOOLTIP
    ddict = dict()
    for e in data:
        ddict[e[0]] = e[1]

    # create special geojson data
    # so the tooltip will work
    # also have to add an amount field to the
    # geojson data so tooltip can work
    geoj = json.load(open(neighb_geo))
    for i in range(len(geoj['features'])):
        neighb_name = geoj['features'][i]['properties']['nhood']

        # potentially zero crimes in area
        # so it would not be in the database results
        try:
            amount = ddict[neighb_name]
        except KeyError:
            amount = 0

        # add to geojson field
        geoj['features'][i]['properties']['amount'] = amount

    # choropleth
    chp = folium.Choropleth(
            name="Neighbourhoods",
            geo_data=geoj,
            data=data,
            columns=("Neighbourhood", "Amount"),
            key_on="feature.properties.nhood",
            fill_color='YlOrRd',  # yellow orange red
            legend_name="Incidents in neighbourhood",
            highlight=True)

    # add tooltip to show neighbourhood
    tt = folium.GeoJsonTooltip(
            fields=["nhood", "amount"],
            labels=False)

    chp.geojson.add_child(tt)

    return chp


def make_choropleth_district(m, district_geo):
    # get district of every incident
    data = run_query_db(district_query)

    # for some reason it returns tuples
    data = [d[0] for d in data]

    # create list of district and number of incidents
    uniq = set(data)
    # districts in geojson are CAPS so upper case
    data = [[distr.upper(), data.count(distr)] for distr in uniq]

    # TOOLTIP
    ddict = dict()
    for e in data:
        ddict[e[0]] = e[1]

    # create special geojson data so the tooltip will work
    # have to add an amount field to the geojson data so tooltip can work
    geoj = json.load(open(district_geo))
    for i in range(len(geoj['features'])):
        distr_name = geoj['features'][i]['properties']['district']

        # potentially zero crimes in area so it would not be in the database
        try:
            amount = ddict[distr_name]
        except KeyError:
            amount = 0

        # add to geojson data
        geoj['features'][i]['properties']['amount'] = amount

    # key_on is json file identifer to map district to area
    chp = folium.Choropleth(
            name="Police Districts",
            geo_data=geoj,
            data=data,
            columns=("District", "Amount"),
            key_on="feature.properties.district",
            fill_color='YlOrRd',
            legend_name="Incidents in police district",
            highlight=True)

    # make tooltip to show district name and value
    tt = folium.GeoJsonTooltip(
            fields=["district", "amount"],
            labels=False
            )

    # add tooltip to the maps geojson layer
    chp.geojson.add_child(tt)

    return chp


def get_map():
    san_francisco_coords = [37.76, -122.45]
    m = folium.Map(
        location=san_francisco_coords,
        zoom_start=12)

    return m


def make_choropleth_district_map(data_folder, fname):
    m = get_map()

    # geojson api file
    district_geo = data_folder + "Current Police Districts.geojson"

    # create map
    distr_map = make_choropleth_district(m, district_geo)

    m.add_child(distr_map)

    m.save(fname)


def make_choropleth_neighb_map(data_folder, fname):
    m = get_map()

    # geojson api file
    neighb_geo = data_folder + "Analysis Neighborhoods.geojson"

    # create map
    neigh_map = make_choropleth_neighb(m, neighb_geo)

    # add to map
    m.add_child(neigh_map)

    m.save(fname)


# generate the maps
def main():
    # read config for data folder
    conf = configparser.ConfigParser()
    conf.read('/home/hdip_proj/config.ini')
    data_folder = conf['folders']['data']

    # make cluster map
    cluster_file = "/var/www/html/images/clustermap.html"
    make_cluster_map(cluster_file)

    # generate choropleth maps
    neighb_file = "/var/www/html/images/choropleth_neighbourhood.html"
    make_choropleth_neighb_map(data_folder, neighb_file)

    district_file = "/var/www/html/images/choropleth_district.html"
    make_choropleth_district_map(data_folder, district_file)


if __name__ == "__main__":
    main()
    sys.exit(0)

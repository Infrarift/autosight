import math
import requests
import urllib
import os

GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

myloc = "./"  # replace with your own location
key = "&key=" + "AIzaSyAHMNFs_tJcjtCmP5QrW_giQUnZygUh7rA"

if not os.path.exists("./crawl"):
    os.mkdir("crawl")


def get_street(add, heading, save_dir):
    base = "https://maps.googleapis.com/maps/api/streetview?size=600x300&fov=50&heading={}&location=".format(heading)
    my_url = base + add + key
    file_name = "./crawl/{}_{}.jpg".format(add, heading)
    urllib.urlretrieve(my_url, os.path.join(save_dir, file_name))


# Tests = ["211 Royal Street, Yokine, WA 6060",
#          "151 Hensman Road, WA, 6008"]
#
# for i in Tests:
#     get_street(i, myloc)


def lerp(a, b, f):
    return a + f * (b - a)


class GeoLoc:
    def __init__(self):
        self.lat = 0
        self.long = 0


class GeoCoder:
    K_DISTANCE_BLOCK = 0.0015

    def __init__(self):
        print("Init GeoCoder")
        self.key = 'AIzaSyAHMNFs_tJcjtCmP5QrW_giQUnZygUh7rA'
        self.state = "WA, Australia"

    def process(self, street, start_num, end_num, postcode):
        address = "{}, {}, {}".format(street, postcode, self.state)
        start_address = "{} {}".format(start_num, address)
        end_address = "{} {}".format(end_num, address)
        g1 = self.get_geoloc(start_address)
        g2 = self.get_geoloc(end_address)
        return g1, g2

    def get_geoloc(self, address):
        params = {
            'address': address,
            'key': self.key
        }

        # Do the request and get the response data
        req = requests.get(GOOGLE_MAPS_API_URL, params=params)
        res = req.json()

        # Use the first result
        result = res['results'][0]

        geoloc = GeoLoc()
        geoloc.lat = result['geometry']['location']['lat']
        geoloc.long = result['geometry']['location']['lng']

        print("GEOLOC: {}, {}".format(geoloc.lat, geoloc.long))
        return geoloc

    def get_geo_line(self, g1, g2):
        distance = math.sqrt(pow(g1.lat - g2.lat, 2) + pow(g1.long - g2.long, 2))
        divs = math.ceil(distance / GeoCoder.K_DISTANCE_BLOCK)
        print(divs)
        print("distance: {}".format(distance))
        split_step = 1 / divs
        print ("Split Steps: {}".format(split_step))

        steps = []
        for i in range(int(divs) + 1):
            steps.append(i * split_step)

        print(steps)
        final_geos = []
        for step in steps:
            g = GeoLoc()
            g.lat = lerp(g1.lat, g2.lat, step)
            g.long = lerp(g1.long, g2.long, step)
            final_geos.append(g)
            # print("")
            # print("LAT: {}".format(g.lat))
            # print("LNG: {}".format(g.long))

        return final_geos


if __name__ == "__main__":
    print("Hello World")
    geocoder = GeoCoder()
    # geocoder.process("St Georges Terrace", 200, 20, 6000)

    # g1 = GeoLoc()
    # g1.lat = -31.9534685
    # g1.long = 115.8525777
    #
    # g2 = GeoLoc()
    # g2.lat = -31.9571264
    # g2.long = 115.8640418

    g1, g2 = geocoder.process("Fitzgerald Street", 2, 170, 6000)

    line = geocoder.get_geo_line(g1, g2)
    angle_rad = math.atan2(g2.long - g1.long, g2.lat - g1.lat)
    print("Angle Rad: {}".format(angle_rad))
    angle_heading = int((angle_rad / (math.pi * 2)) * 360)
    print("Angle Heading: {}".format(angle_heading))

    for geoloc in line:
        location = "{}, {}".format(geoloc.lat, geoloc.long)
        get_street(location, angle_heading, myloc)

        alt_angle = angle_heading - 180
        if alt_angle < 0:
            alt_angle += 360

        get_street(location, alt_angle, myloc)

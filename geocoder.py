import math
import requests
import urllib
import os


class StreetViewLoader:
    def __init__(self, save_path="./crawl", api_key=""):
        self.google_street_view_url = "https://maps.googleapis.com/maps/api/streetview"
        self.save_dir = save_path
        self.width = 800
        self.height = 600
        self.fov = 85
        self.api_key = api_key

        self._create_save_dir(self.save_dir)

    def save_street_image(self, location, heading, name):
        query_url = self._get_query_url(self.google_street_view_url, heading, location, self.api_key)
        sub_dir = os.path.join(self.save_dir, name)
        self._create_save_dir(sub_dir)
        save_path = os.path.join(sub_dir, "{}_{}.jpg".format(location, heading))
        urllib.urlretrieve(query_url, save_path)

    @staticmethod
    def _create_save_dir(save_path):
        if not os.path.exists(save_path):
            os.mkdir(save_path)

    def _get_query_url(self, api_address, heading, location, key):
        query_address = "{}?size={}x{}&fov={}&heading={}&location={}&key={}".format(
            api_address,
            self.width,
            self.height,
            self.fov,
            heading,
            location,
            key
        )
        return query_address


class GeoLoc:
    def __init__(self):
        self.lat = 0
        self.long = 0


class GeoCoder:
    K_DISTANCE_BLOCK = 0.0015

    def __init__(self, api_key=""):
        print("Init GeoCoder")
        self.key = api_key
        self.state = "WA, Australia"
        self.google_geocoder_url = "https://maps.googleapis.com/maps/api/geocode/json"

    def process(self, street, start_num, end_num, postcode):
        address = street

        if postcode is not None:
            address = "{}, {}".format(address, postcode)

        if self.state is not None:
            address = "{}, {}".format(address, self.state)

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
        req = requests.get(self.google_geocoder_url, params=params)
        res = req.json()

        # Use the first result
        result = res['results'][0]

        geoloc = GeoLoc()
        geoloc.lat = result['geometry']['location']['lat']
        geoloc.long = result['geometry']['location']['lng']

        return geoloc

    def get_geo_line(self, g1, g2):
        distance = math.sqrt(pow(g1.lat - g2.lat, 2) + pow(g1.long - g2.long, 2))
        divs = math.ceil(distance / GeoCoder.K_DISTANCE_BLOCK)
        split_step = 1 / divs

        steps = []
        for i in range(int(divs) + 1):
            steps.append(i * split_step)

        final_geos = []
        for step in steps:
            g = GeoLoc()
            g.lat = self._linear_interpolate(g1.lat, g2.lat, step)
            g.long = self._linear_interpolate(g1.long, g2.long, step)
            final_geos.append(g)

        return final_geos

    @staticmethod
    def _linear_interpolate(a, b, f):
        return a + f * (b - a)


class StreetScanner:
    def __init__(self):
        API_KEY = "AIzaSyAHMNFs_tJcjtCmP5QrW_giQUnZygUh7rA"
        self.geocoder = GeoCoder(api_key=API_KEY)
        self.street_loader = StreetViewLoader(save_path="./crawl", api_key=API_KEY)

    def scan_street(self, street_name, start_address, end_address, postcode=None):
        g1, g2 = self.geocoder.process(street_name, start_address, end_address, postcode)
        line = self.geocoder.get_geo_line(g1, g2)
        angle_rad = math.atan2(g2.long - g1.long, g2.lat - g1.lat)
        angle_heading = int((angle_rad / (math.pi * 2)) * 360)

        for geoloc in line:
            location = "{}, {}".format(geoloc.lat, geoloc.long)
            self.street_loader.save_street_image(location, angle_heading, street_name)

            alt_angle = angle_heading - 180
            if alt_angle < 0:
                alt_angle += 360

            self.street_loader.save_street_image(location, alt_angle, street_name)


    def scan_region(self, lat, long, range_km, heading_offset):
        scan_block_size = 0.0015
        scan_range = range_km * 0.01
        start_lat = lat - scan_range / 2
        start_long = long - scan_range / 2
        scan_steps = int(math.ceil(scan_range / scan_block_size))
        region_name = "Region {} {}".format(lat, long)
        print("Region Steps: {}".format(scan_steps))
        for i in range(scan_steps):
            scan_lat = start_lat + scan_block_size * i
            for j in range(scan_steps):
                scan_long = start_long + scan_block_size * j

                location = "{}, {}".format(scan_lat, scan_long)
                headings = [0, 90, 180, 270]
                print(location)
                for h in headings:
                    h2 = h + heading_offset
                    while h2 > 360:
                        h2 -= 360
                    self.street_loader.save_street_image(location, h2, region_name)

if __name__ == "__main__":
    street_scanner = StreetScanner()
    # street_scanner.scan_region(-31.950669, 115.824032, 0.5, 0)
    street_scanner.scan_street("Fitzgerald Street", 20, 200, 6000)
    street_scanner.scan_street("Rokeby Rd", 30, 400, 6008)
    street_scanner.scan_street("Hamersley Rd", 20, 250, 6008)
    street_scanner.scan_street("Adelaide Terrace", 50, 250, 6000)
    street_scanner.scan_street("Lake Street", 100, 240, 6000)


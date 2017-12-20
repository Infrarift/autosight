import urllib
import os


myloc = "./"  # replace with your own location
key = "&key=" + "AIzaSyAHMNFs_tJcjtCmP5QrW_giQUnZygUh7rA"  # got banned after ~100 requests with no key


def get_street(add, save_dir):
    base = "https://maps.googleapis.com/maps/api/streetview?size=1200x600&fov=50&heading=270&location="
    my_url = base + add + key
    file_name = add + ".jpg"
    urllib.urlretrieve(my_url, os.path.join(save_dir, file_name))


Tests = ["211 Royal Street, Yokine, WA 6060",
         "151 Hensman Road, WA, 6008"]

for i in Tests:
    get_street(i, myloc)

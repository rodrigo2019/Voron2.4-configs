import sys

import requests


def reset_db(inital_km):
    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=init_value&value={initial_km * 1000 * 1000}"
    requests.post(url)
    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_x&value={initial_km * 1000 * 1000}"
    requests.post(url)
    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_y&value={initial_km * 1000 * 1000}"
    requests.post(url)
    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_z&value={initial_km * 1000 * 1000}"
    requests.post(url)
    print(f"Database reset to: {initial_km} km")


def query_db():
    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=init_value"
    ret = requests.get(url)
    init_value = float(ret.json()["result"]["value"])
    init_value = init_value / 1000 / 1000

    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_x"
    ret = requests.get(url)
    curr_value_x = float(ret.json()["result"]["value"])
    curr_value_x = (curr_value_x - init_value) / 1000 / 1000

    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_y"
    ret = requests.get(url)
    curr_value_y = float(ret.json()["result"]["value"])
    curr_value_y = (curr_value_y - init_value) / 1000 / 1000

    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_z"
    ret = requests.get(url)
    curr_value_z = float(ret.json()["result"]["value"])
    curr_value_z = (curr_value_z - init_value) / 1000 / 1000

    print(f"Health of X axis: {curr_value_x / init_value:.2%}% (your X axis has traveled {curr_value_x:.2f} km)")
    print(f"Health of Y axis: {curr_value_y / init_value:.2%}% (your Y axis has traveled {curr_value_y:.2f} km)")
    print(f"Health of Z axis: {curr_value_z / init_value:.2%}% (your Z axis has traveled {curr_value_z:.2f} km)")


if __name__ == "__main__":

    arg = sys.argv[1].lower()
    if arg == "init_km":
        initial_km = float(sys.argv[2])
        reset_db(initial_km)
    elif arg == "query":
        query_db()

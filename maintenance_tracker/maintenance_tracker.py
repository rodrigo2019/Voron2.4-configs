import sys
import os

import requests


def read_gcode(filename):
    with open(filename) as f:
        lines = f.readlines()

    lines = [line for line in lines if
             line.startswith("G90") or line.startswith("G91") or line.startswith("G1") or line.startswith("G0")]

    # sum all distance from x, y and z
    mode = "absolute"
    x = 0
    y = 0
    z = 0
    last_x = 0
    last_y = 0
    last_z = 0
    for line in lines:
        if line.startswith("G90"):
            mode = "absolute"
            print("mode: ", mode)
        elif line.startswith("G91"):
            mode = "relative"
            print("mode: ", mode)
        elif line.startswith("G1") or line.startswith("G0"):
            if "X" in line:
                if mode == "absolute":
                    current_x = float(line.split("X")[1].split(" ")[0])
                    x += abs(current_x - last_x)
                    last_x = current_x
                else:
                    x += float(line.split("X")[1].split(" ")[0])
            if "Y" in line:
                if mode == "absolute":
                    current_y = float(line.split("Y")[1].split(" ")[0])
                    y += abs(current_y - last_y)
                    last_y = current_y
                else:
                    y += float(line.split("Y")[1].split(" ")[0])
            if "Z" in line:
                if mode == "absolute":
                    current_z = float(line.split("Z")[1].split(" ")[0])
                    z += abs(current_z - last_z)
                    last_z = current_z
                else:
                    z += float(line.split("Z")[1].split(" ")[0])
    return x, y, z


def process_history():
    # iterate over folder for all *.gcode files
    files = os.listdir("/home/rodrigo/printer_data/gcodes")
    files = [file for file in files if file.endswith(".gcode")]
    total_x = 0
    total_y = 0
    total_z = 0
    for file in files:
        x, y, z = read_gcode(file)
        total_x += x
        total_y += y
        total_z += z

    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_x"
    ret = requests.get(url)
    curr_value_x = float(ret.json()["result"]["value"])

    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_y"
    ret = requests.get(url)
    curr_value_y = float(ret.json()["result"]["value"])

    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_z"
    ret = requests.get(url)
    curr_value_z = float(ret.json()["result"]["value"])

    total_x += curr_value_x
    total_y += curr_value_y
    total_z += curr_value_z

    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_x&value={total_x}"
    requests.post(url)
    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_y&value={total_y}"
    requests.post(url)
    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_z&value={total_z}"
    requests.post(url)

    query_db()


def reset_db(inital_km):
    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=init_value&value={initial_km * 1000 * 1000}"
    requests.post(url)
    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_x&value={0}"
    requests.post(url)
    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_y&value={0}"
    requests.post(url)
    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_z&value={0}"
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
    curr_value_x = curr_value_x / 1000 / 1000

    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_y"
    ret = requests.get(url)
    curr_value_y = float(ret.json()["result"]["value"])
    curr_value_y = curr_value_y / 1000 / 1000

    url = f"http://192.168.100.96:7125/server/database/item?namespace=maintenance_tracker&key=curr_value_z"
    ret = requests.get(url)
    curr_value_z = float(ret.json()["result"]["value"])
    curr_value_z = curr_value_z / 1000 / 1000

    print(
        f"Health of X axis: {(init_value - curr_value_x) / init_value:.2%}% (your X axis has traveled {curr_value_x:.3f} km)")
    print(
        f"Health of Y axis: {(init_value - curr_value_y) / init_value:.2%}% (your Y axis has traveled {curr_value_y:.3f} km)")
    print(
        f"Health of Z axis: {(init_value - curr_value_z) / init_value:.2%}% (your Z axis has traveled {curr_value_z:.3f} km)")


if __name__ == "__main__":

    arg = sys.argv[1].lower()
    if arg == "init_km":
        initial_km = float(sys.argv[2])
        reset_db(initial_km)
    elif arg == "query":
        query_db()
    elif arg == "process_history":
        process_history()

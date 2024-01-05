import sys
import os

import requests

MOONRAKER_URL = "http://127.0.0.1:7125"


def _read_gcode(filename):
    with open(filename) as f:
        lines = f.readlines()

    valid_commands = {"G90", "G91", "G1", "G0"}
    lines = [line for line in lines if line.split()[0] in valid_commands]

    mode = "absolute"
    distances = {"x": 0, "y": 0, "z": 0}
    last_positions = {"x": 0, "y": 0, "z": 0}

    for line in lines:
        command, *values = line.split()

        if command == "G90":
            mode = "absolute"
        elif command == "G91":
            mode = "relative"
        elif command in ["G1", "G0"]:
            for axis in ["X", "Y", "Z"]:
                if axis in values:
                    current_value = float(values[values.index(axis) + 1])
                    distances[axis.lower()] += abs(
                        current_value - last_positions[axis.lower()]) if mode == "absolute" else current_value
                    last_positions[axis.lower()] = current_value

    return distances["x"], distances["y"], distances["z"]


def _update_odometer(x=None, y=None, z=None):
    base_url = f"{MOONRAKER_URL}/server/database/item?namespace=maintenance_tracker"

    def update_axis(axis, value):
        if value is not None:
            ret = requests.get(f"{base_url}&key=curr_value_{axis}")
            curr_value = float(ret.json()["result"]["value"])
            new_value = value + curr_value
            requests.post(f"{base_url}&key=curr_value_{axis}&value={new_value}")

    update_axis('x', x)
    update_axis('y', y)
    update_axis('z', z)


def process_gcode(filename):
    x, y, z = _read_gcode(filename)
    _update_odometer(x, y, z)
    query_db()


def process_history(gcode_folder):
    # iterate over folder for all *.gcode files

    files = os.listdir(gcode_folder)
    files = [file for file in files if file.endswith(".gcode")]
    total_x = 0
    total_y = 0
    total_z = 0
    for file in files:
        file = f"{gcode_folder}/{file}"
        x, y, z = _read_gcode(file)
        total_x += x
        total_y += y
        total_z += z

    _update_odometer(total_x, total_y, total_z)
    query_db()


def reset_db(initial_km):
    base_url = f"{MOONRAKER_URL}/server/database/item?namespace=maintenance_tracker"

    # Reset init_value
    init_value_url = f"{base_url}&key=init_value&value={initial_km * 1000 * 1000}"
    requests.post(init_value_url)

    # Reset curr_value_x, curr_value_y, curr_value_z
    for axis in ['x', 'y', 'z']:
        curr_value_url = f"{base_url}&key=curr_value_{axis}&value=0"
        requests.post(curr_value_url)

    print(f"Database reset to: {initial_km} km")


def query_db():
    base_url = f"{MOONRAKER_URL}/server/database/item?namespace=maintenance_tracker"

    def get_and_convert_value(key):
        url = f"{base_url}&key={key}"
        ret = requests.get(url)
        value = float(ret.json()["result"]["value"])
        return value / 1000 / 1000

    init_value = get_and_convert_value("init_value")
    curr_value_x = get_and_convert_value("curr_value_x")
    curr_value_y = get_and_convert_value("curr_value_y")
    curr_value_z = get_and_convert_value("curr_value_z")

    health_x = (init_value - curr_value_x) / init_value
    health_y = (init_value - curr_value_y) / init_value
    health_z = (init_value - curr_value_z) / init_value

    print(f"Health of X axis: {health_x:.2%} (your X axis has traveled {curr_value_x:.3f} km)")
    print(f"Health of Y axis: {health_y:.2%} (your Y axis has traveled {curr_value_y:.3f} km)")
    print(f"Health of Z axis: {health_z:.2%} (your Z axis has traveled {curr_value_z:.3f} km)")


if __name__ == "__main__":

    arg = sys.argv[1].lower()
    if arg == "init_km":
        initial_km_ = float(sys.argv[2])
        reset_db(initial_km_)
    elif arg == "query":
        query_db()
    elif arg == "process_history" or arg == "process_gcode":
        ret = requests.get(f"{MOONRAKER_URL}/server/files/roots")
        folders = ret.json()["result"]
        gcode_folder_ = [folder for folder in folders if folder["name"] == "gcodes"][0]["path"]
        if arg == "process_history":
            process_history(gcode_folder_)
        else:
            filename_ = f"{gcode_folder_}/{sys.argv[2]}"
            process_gcode(filename_)
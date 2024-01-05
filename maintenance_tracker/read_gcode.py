
with open("../BFI-V2.4_Housing_x2_ABS_1h42m.gcode") as f:
    lines = f.readlines()

# get all lines that starts with g90, g91, g1, or g0

lines = [line for line in lines if line.startswith("G90") or line.startswith("G91") or line.startswith("G1") or line.startswith("G0")]

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
print("x: ", x/1000)
print("y: ", y/1000)
print("z: ", z/1000)

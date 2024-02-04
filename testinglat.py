# from math import cos, asin, sqrt, pi

# def distance(lat1, lon1, lat2, lon2):
#     r = 6371000 # m
#     p = pi / 180

#     a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
#     return 2 * r * asin(sqrt(a))

# print(distance(43.488954, -80.536320, 43.488960, -80.536036))

import math

def calculate_angle_offset(lat1, lon1, lat2, lon2):
    # Convert latitudes and longitudes to radians
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    # Calculate the angle offset (bearing) using simplified tangent approximation
    angle_offset = math.atan2(lon2_rad - lon1_rad, lat2_rad - lat1_rad)

    # Convert angle offset from radians to degrees
    angle_offset_deg = math.degrees(angle_offset)

    return angle_offset_deg

angle_offset = calculate_angle_offset(43.661613, -80.66, 43.661613, -80.60)
print(f"Angle Offset: {angle_offset} degrees")
import socket
import random
from test_gps import get_rpi_coordinates
from test_obstacle_detection import detection
from math import cos, asin, sqrt, pi

serverIP = "192.168.2.52"
serverPORT = 8888

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverIP, serverPORT))
serverSocket.listen()

print("Waiting for connection")
connectionSocket, addr = serverSocket.accept()
print("connected to client!")

ACTION = "ACTION"
COORDINATE = "COORDINATE"

lat_avg = []
lon_avg = []
last = time.monotonic()

def distance(lat1, lon1, lat2, lon2):
    r = 6371000 # km
    p = pi / 180

    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 2 * r * asin(sqrt(a))

while True:
    message = connectionSocket.recv(1024).decode()
    code, content = message.split(":", 1)

    if code == ACTION:
        print(f"Incoming action: {content}")
    else:
        if lat_avg == []:
            pi_location_lat, pi_location_lon, last, lat_avg, lon_avg = get_rpi_coordinates()
        else:
            pi_location_lat, pi_location_lon, last, lat_avg, lon_avg = get_rpi_coordinates(last, lat_avg, lon_avg)

        # Parse the phone's coordinates
        phone_location = content.split(", ")
        phone_location_lat = float(phone_location[0])
        phone_location_lon = float(phone_location[1])
        print(f"Coordinates: {phone_location_lat}, {phone_location_lon}")

        distance_from_phone = distance(pi_location_lat, pi_location_lon, phone_location_lat, phone_location_lon)
        distance_from_phone = "PI:" + str(round(distance_from_phone, 2))

        # FOR NOW KEEPING THE BELOW CODE HERE BECAUSE WE HAVE THE SOCKET HERE AS WELL
        if detection():
            connectionSocket.send("ACTION:STOP".encode())

        print(f"Pi's distance from phone: {distance_from_phone}")
        connectionSocket.send(distance_from_phone.encode())
        
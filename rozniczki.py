import gpxpy
import gpxpy.gpx
from geopy.distance import geodesic
def parse_gpx(file_path):
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
    return gpx


def calculate_speed(point1, point2):
    coords_1 = (point1.latitude, point1.longitude)
    coords_2 = (point2.latitude, point2.longitude)
    distance = geodesic(coords_1, coords_2).meters  # odległość w metrach
    time_delta = (point2.time - point1.time).total_seconds()  # czas w sekundach
    speed = distance / time_delta if time_delta != 0 else 0  # prędkość w m/s
    return speed


def main(file_path):
    gpx = parse_gpx(file_path)
    speeds = []
    for track in gpx.tracks:
        for segment in track.segments:
            for i in range(1, len(segment.points)):
                point1 = segment.points[i - 1]
                point2 = segment.points[i]
                speed = calculate_speed(point1, point2)
                speeds.append(speed)
    avg_speed = sum(speeds) / len(speeds) if speeds else 0
    return avg_speed


file_path = 'pomiar_bez_zaklucen.gpx'
average_speed = main(file_path)
print(f'Średnia prędkość między punktami: {average_speed*3.6:.2f} km/h')
file_path = 'pomiar_lekkie_zaklucenia.gpx'
average_speed = main(file_path)
print(f'Średnia zaklocona prędkość między punktami: {average_speed*3.6:.2f} km/h')

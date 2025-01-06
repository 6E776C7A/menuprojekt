import gpxpy
import numpy as np
import plotly.graph_objects as go


def read_gpx_coordinates(file_name):
    with open(file_name, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
    coordinates = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if point.elevation is not None:
                    coordinates.append((point.latitude, point.longitude, point.elevation))
    return np.array(coordinates)


def calculate_speeds(coordinates, time_interval=2):
    speeds = []
    for i in range(1, len(coordinates)):
        lat1, lon1, ele1 = coordinates[i - 1]
        lat2, lon2, ele2 = coordinates[i]
        ele1_km = ele1 / 1000
        ele2_km = ele2 / 1000
        distance_km = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2 + (ele2_km - ele1_km)**2)
        speed_kmh = (distance_km / time_interval) * 3600 # czas pomiedzy pomiarami jest 2s okolo
        speeds.append(speed_kmh)                         # wiec zamiana na h
    return speeds


def plot_speeds(speeds):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=speeds, mode='lines', name='Speed (km/h)'))
    fig.update_layout(
        title="Speed vs. Point Index",
        xaxis_title="Point Index",
        yaxis_title="Speed (km/h)",
        template="plotly_white"
    )
    fig.show()


if __name__ == "__main__":
    file_name = "output.gpx"
    coordinates = read_gpx_coordinates(file_name)
    speeds = calculate_speeds(coordinates, time_interval=2)
    plot_speeds(speeds)

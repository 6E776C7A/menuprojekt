import gpxpy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
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

def plot_interactive_gradient_plotly(coordinates):
    x = coordinates[:, 1]
    y = coordinates[:, 0]
    z = coordinates[:, 2]
    fig = go.Figure(data=[go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            size=5,
            color=z,
            colorscale='Viridis',
            colorbar=dict(title="Elevation (m)")
        )
    )])

    fig.update_layout(
        title="Interaktywny wykres 3D drogi",
        scene=dict(
            xaxis_title="Longitude",
            yaxis_title="Latitude",
            zaxis_title="Elevation (m)"
        )
    )
    fig.show()

if __name__ == "__main__":
    file_name = "pomiar_bez_zaklocen.gpx"
    coordinates = read_gpx_coordinates(file_name)

    if coordinates.size > 0:
        plot_interactive_gradient_plotly(coordinates)


    file_name = "pomiar_lekkie_zaklocenia.gpx"
    coordinates = read_gpx_coordinates(file_name)

    if coordinates.size > 0:
        plot_interactive_gradient_plotly(coordinates)
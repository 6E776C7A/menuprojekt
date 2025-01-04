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

def smooth_elevation(coordinates, window_size=5):
    z = coordinates[:, 2]
    smoothed_z = np.convolve(z, np.ones(window_size) / window_size, mode='same')
    coordinates[:, 2] = smoothed_z

    return coordinates

def plot_interactive_gradient_matplotlib(coordinates):
    x = coordinates[:, 1]
    y = coordinates[:, 0]
    z = coordinates[:, 2]
    norm = Normalize(vmin=np.min(z), vmax=np.max(z))
    cmap = plt.cm.viridis
    sm = ScalarMappable(norm=norm, cmap=cmap)
    colors = sm.to_rgba(z)
    plt.ion()
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(x, y, z, c=colors, marker='o')
    ax.set_title("Interactive 3D Gradient (Smoothed Elevation)")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_zlabel("Elevation (m)")
    cbar = plt.colorbar(sm, ax=ax, shrink=0.5)
    cbar.set_label('Elevation (m)')
    plt.show(block=True)

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
        title="Interactive 3D Gradient (Smoothed Elevation)",
        scene=dict(
            xaxis_title="Longitude",
            yaxis_title="Latitude",
            zaxis_title="Elevation (m)"
        )
    )
    fig.show()

if __name__ == "__main__":
    file_name = "pomiar_bez_zaklucen.gpx"
    coordinates = read_gpx_coordinates(file_name)

    if coordinates.size > 0:
        coordinates = smooth_elevation(coordinates, window_size=6)
        print("Select the plotting library:")
        print("1. Matplotlib (Basic interactivity)")
        print("2. Plotly (Rich interactivity)")
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            plot_interactive_gradient_matplotlib(coordinates)
        elif choice == "2":
            plot_interactive_gradient_plotly(coordinates)
        else:
            print("Invalid choice. Please enter 1 or 2.")
    else:
        print("No valid coordinates found in the GPX file.")

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

def exclude_large_gradient_points(coordinates, gradient_threshold):
    delta_x = np.diff(coordinates[:, 1])
    delta_y = np.diff(coordinates[:, 0])
    delta_z = (np.diff(coordinates[:, 2])/1000)
    gradients = np.sqrt(delta_x ** 2 + delta_y ** 2 + delta_z ** 2)
    valid_points = [True]
    valid_points.extend(gradients < gradient_threshold)
    valid_points.append(True)
    valid_points = np.array(valid_points)
    if len(valid_points) != len(coordinates):
        valid_points = valid_points[:-1]
    return coordinates[valid_points], gradients

def plot_gradient_plotly(coordinates, gradients):
    x = coordinates[:, 1]
    y = coordinates[:, 0]
    z = coordinates[:, 2]/1000
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=x[1:],
        y=y[1:],
        z=z[1:],
        mode='markers',
        marker=dict(
            size=5,
            color=gradients,
            colorscale='YlOrRd',
            colorbar=dict(title="Gradient Strength")
        ),
        name='Gradient Plot'
    ))
    fig.update_layout(
        title="3D Gradient Plot (Yellow to Red)",
        scene=dict(
            xaxis_title="X (KM)", #od poludnika 0
            yaxis_title="Y (KM)",
            zaxis_title="Z (KM)"
        )
    )
    fig.show()

if __name__ == "__main__":
    file_name = "output.gpx"
    coordinates = read_gpx_coordinates(file_name)
    f= open("coordinates.txt", "w")
    f.write(str(coordinates))
    if coordinates.size > 0:
        gradient_threshold = 2
        coordinates, gradients = exclude_large_gradient_points(coordinates, gradient_threshold)
        plot_gradient_plotly(coordinates, gradients)
    else:
        print("No valid coordinates found in the GPX file.")

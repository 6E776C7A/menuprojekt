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

#uzywanie wielomianow chebysheva
def chebyshev_approximation(x, y, z, degree=5):
    # Skalowanie zmiennych x i y do zakresu [-1, 1], aby dopasować je do dziedziny wielomianów Czebyszewa.
    x_scaled = 2 * (x - np.min(x)) / (np.max(x) - np.min(x)) - 1
    y_scaled = 2 * (y - np.min(y)) / (np.max(y) - np.min(y)) - 1
    # Inicjalizacja macierzy współczynników o wymiarach (degree + 1) x (degree + 1).
    coeffs = np.zeros((degree + 1, degree + 1))
    # Obliczanie współczynników wielomianów Czebyszewa.
    for m in range(degree + 1):  # Iteracja po stopniach m dla x.
        for n in range(degree + 1):  # Iteracja po stopniach n dla y.
            # Obliczanie wartości wielomianów Czebyszewa Tm i Tn dla odpowiednich stopni.
            Tm = np.cos(m * np.arccos(x_scaled))  # Wielomian Czebyszewa m-tego stopnia dla x_scaled.
            Tn = np.cos(n * np.arccos(y_scaled))  # Wielomian Czebyszewa n-tego stopnia dla y_scaled.

            # Obliczanie współczynnika (iloczyn wagowany wartości z oraz Tm i Tn).
            coeffs[m, n] = np.sum(z * Tm * Tn) * 4 / len(x)  # Skalowanie współczynnika przez rozmiar danych.

    # Definicja funkcji do wyznaczania przybliżenia w punkcie (x_val, y_val).
    def chebyshev_poly(x_val, y_val):
        # Skalowanie wartości wejściowych x_val i y_val do zakresu [-1, 1].
        x_scaled_val = 2 * (x_val - np.min(x)) / (np.max(x) - np.min(x)) - 1
        y_scaled_val = 2 * (y_val - np.min(y)) / (np.max(y) - np.min(y)) - 1
        result = 0
        # Obliczanie wartości wielomianu Czebyszewa w punkcie
        for m in range(degree + 1):
            for n in range(degree + 1):
                # Dodanie wkładu współczynnika m, n do wyniku.
                result += coeffs[m, n] * np.cos(m * np.arccos(x_scaled_val)) * np.cos(n * np.arccos(y_scaled_val))
        return result
    return chebyshev_poly


def plot_approximation(coords, chebyshev_poly):
    latitudes = np.linspace(np.min(coords[:, 0]), np.max(coords[:, 0]), 100)
    longitudes = np.linspace(np.min(coords[:, 1]), np.max(coords[:, 1]), 100)
    X, Y = np.meshgrid(latitudes, longitudes)
    Z = np.vectorize(chebyshev_poly)(X, Y)
    Z = Z / 10
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=coords[:, 0],
        y=coords[:, 1],
        z=coords[:, 2] / 10,
        mode='markers',
        marker=dict(size=5, color='blue'),
        name='Original Data'
    ))
    fig.add_trace(go.Surface(
        x=X,
        y=Y,
        z=Z,
        colorscale='Viridis',
        opacity=0.7,
        name='Chebyshev Approximation'
    ))
    fig.update_layout(
        title='Aproksymacja wielomianu Chebysheva',
        scene=dict(
            xaxis_title='x(km)',
            yaxis_title='y(km)',
            zaxis_title='z(km)'
        ),
        showlegend=True
    )
    fig.show()


if __name__ == "__main__":
    file_name = "output.gpx"
    coordinates = read_gpx_coordinates(file_name)
    chebyshev_poly_fn = chebyshev_approximation(coordinates[:, 0], coordinates[:, 1], coordinates[:, 2], degree=5)
    plot_approximation(coordinates, chebyshev_poly_fn)
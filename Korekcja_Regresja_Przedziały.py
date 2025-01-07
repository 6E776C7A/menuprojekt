import gpxpy
import gpxpy.gpx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')


def read_gpx(file_path):
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append((point.latitude, point.longitude))
        return np.array(points)


# Interpolacja brakujących punktów potrzebnych do tego aby długośći list sie zgadzały
def interpolate_coordinates(latitudes, longitudes, target_length):
    current_length = len(latitudes)
    if current_length >= target_length:
        return latitudes, longitudes
    new_latitudes = np.interp(np.linspace(0, current_length - 1, target_length), np.arange(current_length), latitudes)
    new_longitudes = np.interp(np.linspace(0, current_length - 1, target_length), np.arange(current_length), longitudes)
    return new_latitudes, new_longitudes


# Obliczanie błedu średniej kwadratowej błędu
def calculate_rmse(predictions, targets):
    return np.sqrt(np.mean((predictions - targets) ** 2))


class LinearRegression:
    def __init__(self):
        self.weight = None
        self.bias = None

    def fit(self, X, y):
        X = X.reshape(-1)
        y = y.reshape(-1)

        X_mean = np.mean(X)
        y_mean = np.mean(y)

        numerator = np.sum((X - X_mean) * (y - y_mean))
        denominator = np.sum((X - X_mean) ** 2)

        self.weight = numerator / denominator
        self.bias = y_mean - self.weight * X_mean

    def predict(self, X):
        X = X.reshape(-1)
        return (X * self.weight) + self.bias


# Podzielenie danych na segmenty żeby działała regresja
def segment_data(data, segment_size):
    return [data[i:i + segment_size] for i in range(0, len(data), segment_size)]


# funkcja implementująca regresje na wcześniej stworzonych segmentach
def segment_regression(lat_noisy, lon_noisy, segment_size):
    lat_segments = segment_data(lat_noisy, segment_size)
    lon_segments = segment_data(lon_noisy, segment_size)

    lat_pred = []
    lon_pred = []

    for lat_seg, lon_seg in zip(lat_segments, lon_segments):
        indices = np.arange(len(lat_seg))

        model_lat = LinearRegression()
        model_lon = LinearRegression()

        model_lat.fit(indices, lat_seg)
        model_lon.fit(indices, lon_seg)

        lat_pred.extend(model_lat.predict(indices))
        lon_pred.extend(model_lon.predict(indices))

    return np.array(lat_pred), np.array(lon_pred)


reference_gpx_file_path = 'data/pomiar_bez_zaklucen.gpx'
noisy_gpx_file_path = 'data/pomiar_lekkie_zaklucenia.gpx'

reference_points = read_gpx(reference_gpx_file_path)
noisy_points = read_gpx(noisy_gpx_file_path)

lat_true = reference_points[:, 0]
lon_true = reference_points[:, 1]
lat_noisy = noisy_points[:, 0]
lon_noisy = noisy_points[:, 1]

# interpolacaj brakujących punktów
if len(lat_true) > len(lat_noisy):
    lat_noisy, lon_noisy = interpolate_coordinates(lat_noisy, lon_noisy, len(lat_true))
else:
    lat_true, lon_true = interpolate_coordinates(lat_true, lon_true, len(lat_noisy))

# Regresja na segmentach
segment_size = 3
lat_corrected, lon_corrected = segment_regression(lat_noisy, lon_noisy, segment_size)

# Obliczanie błędu
rmse_lat_corrected = calculate_rmse(lat_corrected, lat_true)
rmse_lon_corrected = calculate_rmse(lon_corrected, lon_true)

print(f"RMSE for corrected latitude: {rmse_lat_corrected}")
print(f"RMSE for corrected longitude: {rmse_lon_corrected}")

plt.figure(figsize=(12, 8))

plt.plot(lon_true, lat_true, label='Reference Data (Original)', color='green', alpha=0.7)
plt.scatter(lon_noisy, lat_noisy, label='Noisy Data', color='red', s=10, alpha=0.5)
plt.plot(lon_corrected, lat_corrected, label='Reconstructed Data (Linear Regression)', color='blue', alpha=0.7)

plt.title("GPS Data Denoising using Segment Linear Regression")
plt.ylabel("Latitude (lat)")
plt.xlabel("Longitude (lon)")
plt.legend()
plt.grid()
plt.show()

import gpxpy
import gpxpy.gpx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')


# Funkcja do odczytu danych z pliku GPX
def read_gpx(file_path):
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

        # Ekstrakcja punktów trasy
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append((point.latitude, point.longitude))
        return np.array(points)


# Funkcja do interpolacji punktów
def interpolate_coordinates(latitudes, longitudes, target_length):
    current_length = len(latitudes)
    if current_length >= target_length:
        return latitudes, longitudes  # Jeśli liczba punktów jest równa lub większa, nie trzeba interpolować

    new_latitudes = np.interp(np.linspace(0, current_length - 1, target_length), np.arange(current_length), latitudes)
    new_longitudes = np.interp(np.linspace(0, current_length - 1, target_length), np.arange(current_length), longitudes)

    return new_latitudes, new_longitudes


# Funkcja do obliczenia RMSE
def calculate_rmse(predictions, targets):
    return np.sqrt(np.mean((predictions - targets) ** 2))


# Funkcja do korekcji za pomocą metody Monte Carlo
def monte_carlo_correction(lat_noisy, lon_noisy, lat_true, lon_true, num_iterations=5000, num_trajectories=20,
                           noise_level=0.00001):
    lat_trajectories = []
    lon_trajectories = []
    errors = []

    # Generowanie losowych trajektorii początkowych
    for _ in range(num_trajectories):
        lat_traj = lat_noisy + np.random.normal(0, noise_level, len(lat_noisy))
        lon_traj = lon_noisy + np.random.normal(0, noise_level, len(lon_noisy))
        lat_trajectories.append(lat_traj)
        lon_trajectories.append(lon_traj)
        errors.append(calculate_rmse(lat_traj, lat_true) + calculate_rmse(lon_traj, lon_true))

    lat_trajectories = np.array(lat_trajectories)
    lon_trajectories = np.array(lon_trajectories)
    errors = np.array(errors)

    # Iteracyjne poprawianie trajektorii
    for _ in range(num_iterations):
        for i in range(num_trajectories):
            lat_traj_new = lat_trajectories[i] + np.random.normal(0, noise_level / 10, len(lat_noisy))
            lon_traj_new = lon_trajectories[i] + np.random.normal(0, noise_level / 10, len(lon_noisy))
            error_new = calculate_rmse(lat_traj_new, lat_true) + calculate_rmse(lon_traj_new, lon_true)

            if error_new < errors[i]:
                lat_trajectories[i] = lat_traj_new
                lon_trajectories[i] = lon_traj_new
                errors[i] = error_new

    # Znalezienie najlepszej trajektorii
    best_index = np.argmin(errors)
    lat_best = lat_trajectories[best_index]
    lon_best = lon_trajectories[best_index]

    return lat_best, lon_best


# Ścieżka do pliku GPX (użytkownik dostarcza plik)
reference_gpx_file_path = 'data/pomiar_bez_zaklucen.gpx'
noisy_gpx_file_path = 'data/pomiar_lekkie_zaklucenia.gpx'

# Odczyt danych z plików GPX
reference_points = read_gpx(reference_gpx_file_path)
noisy_points = read_gpx(noisy_gpx_file_path)

lat_true = reference_points[:, 0]
lon_true = reference_points[:, 1]
lat_noisy = noisy_points[:, 0]
lon_noisy = noisy_points[:, 1]

# Uzupełnianie brakujących punktów przez interpolację
if len(lat_true) > len(lat_noisy):
    lat_noisy, lon_noisy = interpolate_coordinates(lat_noisy, lon_noisy, len(lat_true))
else:
    lat_true, lon_true = interpolate_coordinates(lat_true, lon_true, len(lat_noisy))

# Korekcja za pomocą metody Monte Carlo
lat_corrected, lon_corrected = monte_carlo_correction(lat_noisy, lon_noisy, lat_true, lon_true)

# Obliczenie RMSE w szerokości i długości geograficznej po korekcji
rmse_lat_corrected = calculate_rmse(lat_corrected, lat_true)
rmse_lon_corrected = calculate_rmse(lon_corrected, lon_true)

print(f"RMSE dla szerokości geograficznej po korekcji: {rmse_lat_corrected}")
print(f"RMSE dla długości geograficznej po korekcji: {rmse_lon_corrected}")

# Wizualizacja wyników
plt.figure(figsize=(12, 8))

# Oryginalne dane
plt.plot(lon_true, lat_true, label='Dane referencyjne (oryginalne)', color='green', alpha=0.7)

# Zakłócone dane
plt.scatter(lon_noisy, lat_noisy, label='Dane zakłócone', color='red', s=10, alpha=0.5)

# Dane po korekcji Monte Carlo (połączone linią)
plt.plot(lon_corrected, lat_corrected, label='Dane po korekcji Monte Carlo', color='purple', alpha=0.7)

# Dostosowanie wykresu
plt.title("Odszumianie danych GPS za pomocą metody Monte Carlo")
plt.ylabel("Szerokość geograficzna (lat)")
plt.xlabel("Długość geograficzna (lon)")
plt.legend()
plt.grid()
plt.show()

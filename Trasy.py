import gpxpy.gpx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')


# Funkcja odczytująca dane zwracająca współrzędne x, y oraz z
def read_gpx_file(filename):
    latitude = []
    longitude = []
    elevation = []
    with open(filename, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    latitude.append(point.latitude)
                    longitude.append(point.longitude)
                    elevation.append(point.elevation)
    return latitude, longitude, elevation


# Funkcja zwracająca odległość punktów od siebie na sferze
def haversine(lat1, lon1, lat2, lon2):
    r = 6371.0  # Promień Ziemi w kilometrach
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return r * c


# Dopasowanie punktów (sprawdzanie najbliższego sąsiada)
def match_points(lat1, lon1, lat2, lon2):
    matched_indices = []
    for lat_a, lon_a in zip(lat1, lon1):
        distances = [haversine(lat_a, lon_a, lat_b, lon_b) for lat_b, lon_b in zip(lat2, lon2)]
        min_idx = np.argmin(distances)
        matched_indices.append(min_idx)
    return matched_indices


# Wykres drogi w funkcji czasu
def analyze_gpx(reference_gpx):
    with open(reference_gpx, 'r') as ref_file:
        ref_gpx = gpxpy.parse(ref_file)

    times = []
    distances = []
    cumulative_distance = 0

    for track in ref_gpx.tracks:
        for segment in track.segments:
            prev_point = None
            for point in segment.points:
                if point.time is not None:  # Sprawdź, czy punkt ma znacznik czasowy
                    times.append(point.time)
                    if prev_point:
                        distance = haversine(prev_point.latitude, prev_point.longitude,
                                             point.latitude, point.longitude)
                        cumulative_distance += distance
                        distances.append(cumulative_distance)
                    else:
                        distances.append(0)  # Pierwszy punkt, odległość 0
                    prev_point = point

    # Przetwarzanie czasu do formatu wykresu
    times_seconds = [(t - times[0]).total_seconds() for t in times]  # Czas w sekundach od początku

    # Rysowanie wykresu
    plt.figure(figsize=(10, 6))
    plt.plot(times_seconds, distances, label='Droga od czasu', color='blue')
    plt.title("Wykres drogi w funkcji czasu")
    plt.xlabel("Czas [s]")
    plt.ylabel("Droga [m]")
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()


reference_gpx = 'data/pomiar_bez_zaklucen.gpx'
noisy_gpx = 'data/pomiar_lekkie_zaklucenia.gpx'

lat_r, lon_r, ele_r = read_gpx_file(reference_gpx)
lat_z, lon_z, ele_z = read_gpx_file(noisy_gpx)

# Znajdowanie najbliższych punktów dla każdego punktu referencyjnego
matched_indices = match_points(lat_r, lon_r, lat_z, lon_z)

# Obliczanie błędów latitude i longitude
lat_errors = [abs(lat_r[i] - lat_z[idx]) for i, idx in enumerate(matched_indices)]
lon_errors = [abs(lon_r[i] - lon_z[idx]) for i, idx in enumerate(matched_indices)]

# Obliczanie odległości błędów w metrach
odleglosci = [haversine(lat_r[i], lon_r[i], lat_z[idx], lon_z[idx]) for i, idx in enumerate(matched_indices)]
odleglosci_metry = [d * 1000 for d in odleglosci]

# Obliczanie średnich błędów
sredni_blad_lat = np.mean(lat_errors)
sredni_blad_lon = np.mean(lon_errors)
sredni_blad_odleglosc = np.mean(odleglosci_metry)

print(f"Średni błąd szerokości geograficznej (latitude): {sredni_blad_lat:.6f} stopni")
print(f"Średni błąd długości geograficznej (longitude): {sredni_blad_lon:.6f} stopni")
print(f"Średni błąd odległości: {sredni_blad_odleglosc:.2f} m")

plt.figure(figsize=(12, 8))

plt.plot(lon_r, lat_r, label='Dane referencyjne (oryginalne)', color='green', alpha=0.7)
plt.plot(lon_z, lat_z, label='Dane zakłócone', color='red', linestyle='--')

plt.title("Wykres trasy referencyjnej względem trasy zakłóconej")
plt.ylabel("Szerokość geograficzna (latitude)")
plt.xlabel("Długość geograficzna (longitude)")
plt.legend()
plt.grid()
plt.show()

analyze_gpx(reference_gpx)

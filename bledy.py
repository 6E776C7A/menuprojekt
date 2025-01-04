import gpxpy.gpx
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import CubicSpline
import matplotlib
matplotlib.use('TkAgg')

# Dopasowanie punktów (najbliższy sąsiad) bez KDTree
def match_points(lat1, lon1, lat2, lon2):
    matched_distances = []
    for lat_a, lon_a in zip(lat1, lon1):
        # Oblicz odległość do wszystkich punktów z drugiej trasy
        distances = [haversine(lat_a, lon_a, lat_b, lon_b) for lat_b, lon_b in zip(lat2, lon2)]
        # Znajdź minimalną odległość (najbliższy sąsiad)
        matched_distances.append(min(distances))
    return matched_distances

# Funkcja odczytująca dane zwracająca współrzędne x oraz y
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
    a = np.sin(dlat / 2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return r * c

# Odczytywanie danych z plików
lat_r, lon_r, ele_r = read_gpx_file('data/pomiar_bez_zaklucen.gpx')
lat_z, lon_z, ele_z = read_gpx_file('data/pomiar_lekkie_zaklucenia.gpx')
lat_u, lon_u, ele_u = read_gpx_file('data/pomiar_utrata_gps.gpx')

# Lista współrzędnych tras
trasa_ref = list(zip(lat_r, lon_r))
trasa_zak = list(zip(lat_z, lon_z))

# Większa liczba punktów do interpolacji
new_points = len(trasa_ref) * 2  # Możemy zwiększyć liczbę punktów aby interpolacja była bardziej dokladna

# Interpolacja sześcienna trasy zakłóconej do większej liczby punktów
interpolate_lat = CubicSpline(np.linspace(0, 1, len(lat_z)), lat_z)
interpolate_lon = CubicSpline(np.linspace(0, 1, len(lon_z)), lon_z)
trasa_zak_interpol = [(interpolate_lat(i/new_points), interpolate_lon(i/new_points)) for i in range(new_points)]

lat_z_interpol, lon_z_interpol = zip(*trasa_zak_interpol)

# Znajdowanie najbliższych punktów i obliczanie odległości dla trasy z interpolacją
odleglosci_interpolacja = match_points(lat_r, lon_r, lat_z_interpol, lon_z_interpol)

# Znajdowanie najbliższych punktów i obliczanie odległości dla trasy bez interpolacji
odleglosci_bez_interpolacji = match_points(lat_r, lon_r, lat_z, lon_z)

# Konwersja odległości z kilometrów na metry
odleglosci_metry_interpolacja = [d * 1000 for d in odleglosci_interpolacja]
odleglosci_metry_bez_interpolacji = [d * 1000 for d in odleglosci_bez_interpolacji]

# Obliczanie błędów dla trasy z interpolacją
sredni_blad_interpolacja = np.mean(odleglosci_metry_interpolacja)
max_blad_interpolacja = np.max(odleglosci_metry_interpolacja)
min_blad_interpolacja = np.min(odleglosci_metry_interpolacja)

# Obliczanie błędów dla trasy bez interpolacji
sredni_blad_bez_interpolacji = np.mean(odleglosci_metry_bez_interpolacji)
max_blad_bez_interpolacji = np.max(odleglosci_metry_bez_interpolacji)
min_blad_bez_interpolacji = np.min(odleglosci_metry_bez_interpolacji)

print(f"Średni błąd (interpolacja): {sredni_blad_interpolacja} m")
print(f"Maksymalny błąd (interpolacja): {max_blad_interpolacja} m")
print(f"Minimalny błąd (interpolacja): {min_blad_interpolacja} m")

print(f"Średni błąd (bez interpolacji): {sredni_blad_bez_interpolacji} m")
print(f"Maksymalny błąd (bez interpolacji): {max_blad_bez_interpolacji} m")
print(f"Minimalny błąd (bez interpolacji): {min_blad_bez_interpolacji} m")

# Tworzenie wspólnego wykresu
plt.figure(figsize=(10, 6))
plt.plot(lon_r, lat_r, marker='o', label='Trasa 1 (pomiar bez zakłóceń)', color='blue')
plt.plot(lon_z_interpol, lat_z_interpol, marker='x', label='Trasa 2 (interpolacja)', color='red')
plt.plot(lon_z, lat_z, marker='x', label='Trasa 2 (bez interpolacji)', color='green')

# Dostosowanie wykresu
plt.title("Wykres wielu tras z plików GPX")
plt.xlabel("Długość geograficzna")
plt.ylabel("Szerokość geograficzna")
plt.legend()
plt.grid()

# Wyświetlenie wykresu
plt.show()

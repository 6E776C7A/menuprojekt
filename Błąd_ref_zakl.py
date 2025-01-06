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


# Funkcja zwracająca odległość punktów od siebie na sferze ponieważ x i y są podstawowo w stopniach dziesiętnych
def haversine(lat1, lon1, lat2, lon2):
    r = 6371.0  # Promień Ziemi w kilometrach
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return r * c


# Dopasowanie punktów (sprawdzanie najbliższego sąsiada)
def match_points(lat1, lon1, lat2, lon2):
    matched_distances = []
    for lat_a, lon_a in zip(lat1, lon1):
        # Oblicz odległość do wszystkich punktów z drugiej trasy
        distances = [haversine(lat_a, lon_a, lat_b, lon_b) for lat_b, lon_b in zip(lat2, lon2)]
        # Znajdź minimalną odległość (najbliższy sąsiad)
        matched_distances.append(min(distances))
    return matched_distances


# Odczytywanie danych z plików
lat_r, lon_r, ele_r = read_gpx_file('data/pomiar_bez_zaklucen.gpx')
lat_z, lon_z, ele_z = read_gpx_file('data/pomiar_lekkie_zaklucenia.gpx')

# Znajdowanie najbliższych punktów i obliczanie odległości dla trasy
odleglosci = match_points(lat_r, lon_r, lat_z, lon_z)

# Konwersja odległości z kilometrów na metry
odleglosci_metry = [d * 1000 for d in odleglosci]

# Obliczanie błędów dla trasy
sredni_blad = np.mean(odleglosci_metry)
max_blad = np.max(odleglosci_metry)
min_blad = np.min(odleglosci_metry)

print(f"Średni błąd (bez interpolacji): {sredni_blad} m")
print(f"Maksymalny błąd (bez interpolacji): {max_blad} m")
print(f"Minimalny błąd (bez interpolacji): {min_blad} m")

# Wizualizacja wyników
plt.figure(figsize=(12, 8))

plt.plot(lon_r, lat_r, label='Dane referencyjne (oryginalne)', color='green', alpha=0.7)
plt.plot(lon_z, lat_z, label='Dane zakłócone', color='red', linestyle='--')

# Dostosowanie wykresu
plt.title("Wykres trasy referencyjnej względem trasy zakłóconej")
plt.ylabel("Szerokość geograficzna (latitude)")
plt.xlabel("Długość geograficzna (longitude)")
plt.legend()
plt.grid()
plt.show()



import gpxpy.gpx
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')


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


# Odczytywanie danich z plikow
lat_r, lon_r, ele_r = read_gpx_file('data/pomiar_bez_zaklucen.gpx')
lat_z, lon_z, ele_z = read_gpx_file('data/pomiar_lekkie_zaklucenia.gpx')
lat_u, lon_u, ele_u = read_gpx_file('data/pomiar_utrata_gps.gpx')

# Tworzenie wykresów
fig, axs = plt.subplots(2, 2, figsize=(14, 10))

# 1. Wspólny wykres wszystkich tras
axs[0, 0].plot(lon_r, lat_r, marker='o', label='Trasa referencyjna', color='blue')
axs[0, 0].plot(lon_z, lat_z, marker='x', label='Trasa zakłucona', color='red')
axs[0, 0].plot(lon_u, lat_u, marker='s', label='Trasa utrata gps', color='green')
axs[0, 0].set_title("Wspólny wykres wszystkich tras")
axs[0, 0].set_xlabel("Długość geograficzna")
axs[0, 0].set_ylabel("Szerokość geograficzna")
axs[0, 0].legend()
axs[0, 0].grid()

# 2. Osobny wykres dla Trasy referencyjnej
axs[0, 1].plot(lon_r, lat_r, marker='o', color='blue', label='Trasa referencyjna')
axs[0, 1].set_title("Trasa referencyjna")
axs[0, 1].set_xlabel("Długość geograficzna")
axs[0, 1].set_ylabel("Szerokość geograficzna")
axs[0, 1].legend()
axs[0, 1].grid()

# 3. Osobny wykres dla Trasy zakłuconej
axs[1, 0].plot(lon_z, lat_z, marker='x', color='red', label='Trasa zakłucona')
axs[1, 0].set_title("Trasa zakłucona")
axs[1, 0].set_xlabel("Długość geograficzna")
axs[1, 0].set_ylabel("Szerokość geograficzna")
axs[1, 0].legend()
axs[1, 0].grid()

# 4. Osobny wykres dla Trasy utrata gps
axs[1, 1].plot(lon_u, lat_u, marker='s', color='green', label='Trasa utrata gps')
axs[1, 1].set_title("Trasa utrata gps")
axs[1, 1].set_xlabel("Długość geograficzna")
axs[1, 1].set_ylabel("Szerokość geograficzna")
axs[1, 1].legend()
axs[1, 1].grid()

# Dopasowanie rozmiaru i odstępów między wykresami
plt.tight_layout()

# Wyświetlenie wykresów
plt.show()

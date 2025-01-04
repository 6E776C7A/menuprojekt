import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import gpxpy

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
latitude, longitude, elevation = read_gpx_file('data/pomiar_bez_zaklucen.gpx')

# Dopasowanie wielomianu do danych (np. wielomian trzeciego stopnia)
degree = 3
poly_coeffs = np.polyfit(longitude, latitude, degree)

# Uzyskanie funkcji wielomianowej
poly_func = np.poly1d(poly_coeffs)

# Generowanie punktów do wizualizacji funkcji wielomianowej
long_new = np.linspace(min(longitude), max(longitude), 100)
lat_new = poly_func(long_new)

# Interpolacja sześcienna dla dokładniejszej aproksymacji trasy
cubic_spline_lat = CubicSpline(np.linspace(0, 1, len(longitude)), latitude)
cubic_spline_lon = CubicSpline(np.linspace(0, 1, len(longitude)), longitude)

new_points = 100  # Zwiększenie liczby punktów dla dokładniejszej interpolacji
long_interpol = cubic_spline_lon(np.linspace(0, 1, new_points))
lat_interpol = cubic_spline_lat(np.linspace(0, 1, new_points))

# Wizualizacja danych i funkcji aproksymującej
plt.figure(figsize=(10, 6))
plt.plot(longitude, latitude, 'o', label='Dane')
plt.plot(long_new, lat_new, '-', label='Funkcja wielomianowa')
plt.plot(long_interpol, lat_interpol, '--', label='Interpolacja sześcienna')
plt.xlabel('Długość geograficzna')
plt.ylabel('Szerokość geograficzna')
plt.title('Aproksymacja i interpolacja trasy')
plt.legend()
plt.grid()
plt.show()

# Wyświetlenie funkcji wielomianowej
print("Funkcja aproksymująca (wielomian):")
print(poly_func)

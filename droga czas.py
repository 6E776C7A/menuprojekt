import gpxpy
import math
import matplotlib.pyplot as plt
from datetime import datetime

def haversine(lat1, lon1, lat2, lon2):

    R = 6371000  # Promień Ziemi w metrach
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Odległość w metrach

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
                        # Oblicz odległość między punktami
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

# Użycie
reference_gpx = 'data/pomiar_bez_zaklucen.gpx'  # Plik referencyjny
analyze_gpx(reference_gpx)

import gpxpy
import gpxpy.gpx
import math
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Promień Ziemi w metrach
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Odległość w metrach


def correct_gpx(reference_gpx, noisy_gpx, max_distance):
    with open(reference_gpx, 'r') as ref_file:
        ref_gpx = gpxpy.parse(ref_file)
    with open(noisy_gpx, 'r') as noisy_file:
        noisy_gpx = gpxpy.parse(noisy_file)

    # Listy współrzędnych do wykresów
    ref_lat, ref_lon = [], []
    noisy_lat, noisy_lon = [], []
    corrected_lat, corrected_lon = [], []

    for ref_track, noisy_track in zip(ref_gpx.tracks, noisy_gpx.tracks):
        for ref_segment, noisy_segment in zip(ref_track.segments, noisy_track.segments):
            corrected_points = []
            for noisy_point in noisy_segment.points:
                # Zbierz współrzędne zakłócone
                noisy_lat.append(noisy_point.latitude)
                noisy_lon.append(noisy_point.longitude)

                # Znajdź najbliższy punkt w pliku referencyjnym
                closest_ref_point = min(
                    ref_segment.points,
                    key=lambda ref_point: haversine(ref_point.latitude, ref_point.longitude,
                                                    noisy_point.latitude, noisy_point.longitude)
                )

                # Zbierz współrzędne referencyjne
                ref_lat.append(closest_ref_point.latitude)
                ref_lon.append(closest_ref_point.longitude)

                # Oblicz odległość do najbliższego punktu referencyjnego
                distance = haversine(closest_ref_point.latitude, closest_ref_point.longitude,
                                     noisy_point.latitude, noisy_point.longitude)

                # Korekta punktu, jeśli odległość jest zbyt duża
                if distance > max_distance:
                    corrected_points.append(closest_ref_point)
                    corrected_lat.append(closest_ref_point.latitude)
                    corrected_lon.append(closest_ref_point.longitude)
                else:
                    corrected_points.append(noisy_point)
                    corrected_lat.append(noisy_point.latitude)
                    corrected_lon.append(noisy_point.longitude)

            # Nadpisz punkty w segmencie
            noisy_segment.points = corrected_points

    # Rysowanie wykresów
    plt.figure(figsize=(14, 8))

    # Wykres 1: Trasa referencyjna vs zakłócona
    plt.subplot(1, 2, 1)
    plt.plot(ref_lon, ref_lat, label='Trasa referencyjna', color='green')
    plt.plot(noisy_lon, noisy_lat, label='Trasa zakłócona', color='red', linestyle='--')
    plt.title("Trasa referencyjna vs. zakłócona")
    plt.xlabel("Długość geograficzna")
    plt.ylabel("Szerokość geograficzna")
    plt.legend()
    plt.grid()

    # Wykres 2: Trasa referencyjna vs poprawiona
    plt.subplot(1, 2, 2)
    plt.plot(ref_lon, ref_lat, label='Trasa referencyjna', color='green')
    plt.plot(corrected_lon, corrected_lat, label='Trasa poprawiona', color='blue', linestyle='--')
    plt.title("Trasa referencyjna vs. poprawiona")
    plt.xlabel("Długość geograficzna")
    plt.ylabel("Szerokość geograficzna")
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.show()


# Użycie
reference_gpx = 'data/pomiar_bez_zaklucen.gpx'  # Plik referencyjny
noisy_gpx = 'data/pomiar_lekkie_zaklucenia.gpx'  # Plik z zakłóceniami
max_distance = 3  # maksymalna odległość dopuszczalna pomiędzy punktami
correct_gpx(reference_gpx, noisy_gpx, max_distance)

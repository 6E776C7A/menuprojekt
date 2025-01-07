import gpxpy
import random
import numpy as np


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c


def monte_carlo_trajectory(reference_gpx, num_simulations=1000):
    with open(reference_gpx, 'r') as ref_file:
        ref_gpx = gpxpy.parse(ref_file)

    points = []
    for track in ref_gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append((point.latitude, point.longitude, point.time))

    # Lista do przechowywania wyników symulacji
    avg_speeds = []

    for _ in range(num_simulations):
        # Losowanie podzbioru punktów
        sampled_points = random.sample(points, k=len(points) // 2)  # Próbkowanie połowy punktów
        sampled_points.sort(key=lambda x: x[2])  # Sortowanie po czasie

        total_distance = 0
        total_time = 0

        for i in range(1, len(sampled_points)):
            lat1, lon1, time1 = sampled_points[i - 1]
            lat2, lon2, time2 = sampled_points[i]

            distance = haversine(lat1, lon1, lat2, lon2)
            time_diff = (time2 - time1).total_seconds()

            if time_diff > 0:
                total_distance += distance
                total_time += time_diff

        if total_time > 0:
            avg_speeds.append(total_distance / total_time * 3.6)  # Prędkość w km/h

    # Analiza wyników Monte Carlo
    mean_speed = np.mean(avg_speeds)
    std_dev_speed = np.std(avg_speeds)

    print(f"Średnia prędkość (Monte Carlo): {mean_speed:.2f} km/h")
    print(f"Odchylenie standardowe prędkości: {std_dev_speed:.2f} km/h")

    return avg_speeds, mean_speed, std_dev_speed


reference_gpx = 'data/pomiar_bez_zaklucen.gpx'
monte_carlo_trajectory(reference_gpx)

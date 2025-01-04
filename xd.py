from geopy.distance import geodesic
import gpxpy

# Ścieżki plików
input_gpx_path = "data/pomiar_lekkie_zaklucenia.gpx"  # Ścieżka do pliku wejściowego
output_gpx_path = "data/pomiar_lekkie_zaklucenia_updated.gpx"  # Ścieżka do pliku wyjściowego

# Punkty skrajne (start i koniec) z wysokościami
start_coords = (49 + 25/60 + 37/3600, 19 + 50/60 + 30/3600)  # (49°25'37"N, 19°50'30"E)
end_coords = (49 + 26/60 + 26/3600, 19 + 51/60 + 7/3600)     # (49°26'26"N, 19°51'07"E)
start_ele = 691  # Wysokość w metrach
end_ele = 676    # Wysokość w metrach

# Wczytaj plik GPX
with open(input_gpx_path, 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

# Oblicz całkowitą odległość między punktami skrajnymi
total_distance = geodesic(start_coords, end_coords).meters

# Iteracja przez punkty i aktualizacja wysokości
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            # Oblicz odległość od punktu startowego
            point_distance = geodesic(start_coords, (point.latitude, point.longitude)).meters
            # Sprawdź, czy punkt znajduje się między punktami skrajnymi
            if 0 <= point_distance <= total_distance:
                # Interpoluj wysokość
                point.elevation = start_ele + (point_distance / total_distance) * (end_ele - start_ele)

# Zapisz zaktualizowany plik GPX
with open(output_gpx_path, 'w') as updated_gpx_file:
    updated_gpx_file.write(gpx.to_xml())

print(f"Zapisano zaktualizowany plik GPX jako: {output_gpx_path}")
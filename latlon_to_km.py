import xml.etree.ElementTree as ET
import math
EARTH_RADIUS_KM = 6371.0

def haversine_distance(lat1, lon1, lat2, lon2):
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c

def latlon_to_xy(lat, lon):
    x = haversine_distance(0, 0, 0, lon) * (1 if lon >= 0 else -1)
    y = haversine_distance(0, 0, lat, 0) * (1 if lat >= 0 else -1)
    return x, y

def strip_namespace(element):
    for elem in element.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]

def convert_gpx(input_file, output_file):
    tree = ET.parse(input_file)
    root = tree.getroot()
    strip_namespace(root)
    for trkpt in root.findall('.//trkpt'):
        lat = float(trkpt.get('lat'))
        lon = float(trkpt.get('lon'))
        x, y = latlon_to_xy(lat, lon)
        trkpt.set('lat', f"{y:.3f}")
        trkpt.set('lon', f"{x:.3f}")
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    input_gpx = "pomiar_lekkie_zaklocenia.gpx"
    output_gpx = "output2.gpx"
    convert_gpx(input_gpx, output_gpx)
    print(f"Converted GPX saved to {output_gpx}")

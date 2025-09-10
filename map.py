# Helper: State centers (add more as needed)
STATE_CENTERS = {
    "gujarat": [22.2587, 71.1924],
    "maharashtra": [19.7515, 75.7139],
    "telangana": [18.1124, 79.0193],
    # Add more states as needed
}

# Function to render map for a specific state
def render_state_map(state_name):
    state_key = state_name.strip().lower()
    # Filter features by state
    filtered_features = [f for f in geojson_data['features'] if f['properties'].get('state_name', '').strip().lower() == state_key]
    print(f"Rendering {len(filtered_features)} mandals for state: {state_name}")
    # If state not in STATE_CENTERS, use average lat/lon of filtered features
    if state_key in STATE_CENTERS:
        center = STATE_CENTERS[state_key]
    elif filtered_features:
        lats = [float(f['properties'].get('latitude', 0)) for f in filtered_features]
        lons = [float(f['properties'].get('longitude', 0)) for f in filtered_features]
        center = [sum(lats)/len(lats), sum(lons)/len(lons)]
    else:
        center = [27.7, 93.3]
    filtered_geojson = geojson_data.copy()
    filtered_geojson['features'] = filtered_features
    m = folium.Map(location=center, zoom_start=7)
    folium.GeoJson(
        filtered_geojson,
        style_function=style_function_category,
        name='Groundwater Category',
        tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['Name:'])
    ).add_to(m)
    m.get_root().html.add_child(folium.Element(legend_html))
    map_file = f"map_{state_key}.html"
    m.save(map_file)
    print(f"Saved map to {map_file}")
    webbrowser.open(map_file)

import requests
import folium
import webbrowser
import random

# List of groundwater categories
categories = ["safe", "semi_critical"]

# Category to color mapping
category_colors = {
    "safe": "#1a9850",           # Green
    "semi_critical": "#fee08b",  # Yellow
    "critical": "#d73027",       # Red
    "over_exploited": "#6a3d9a", # Purple
    "saline": "#4575b4",         # Blue
    "hilly_area": "#a6cee3",     # Light Blue
    "no_data": "#cccccc"         # Grey
}

def get_category_color(cat):
    if not cat:
        return category_colors["no_data"]
    cat = cat.lower().replace(" ", "_")
    return category_colors.get(cat, category_colors["no_data"])


# 1️⃣ Load Mandal GeoJSON (all features)
wfs_url = "https://ingres.iith.ac.in/geoserver/gec/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=gec:indgec_mandal_all&outputFormat=application/json"
geojson_data = requests.get(wfs_url).json()
features = geojson_data.get('features', [])
print("GeoJSON features count (all):", len(features))
geojson_data['features'] = features

# Print property keys and values for first 3 features for debugging
for i, f in enumerate(features[:3]):
    print(f"Feature {i} property keys: {list(f['properties'].keys())}")
    print(f"Feature {i} property values: {f['properties']}")

def style_function_category(feature):
    import random
    uuid = feature['properties'].get('uuid', None)
    if uuid:
        # Mostly uniform: 80% safe, 15% semi_critical, 5% disturbance
        r = abs(hash(uuid)) % 100
        if r < 80:
            cat = "safe"
        elif r < 95:
            cat = "semi_critical"
        else:
            # Disturbance: pick from remaining categories
            disturbance = ["critical", "over_exploited", "saline", "hilly_area"]
            cat = disturbance[abs(hash(uuid + "d")) % len(disturbance)]
    else:
        cat = "no_data"
    color = get_category_color(cat)
    return {
        'fillOpacity': 0.7,
        'weight': 1,
        'color': 'black',
        'fillColor': color
    }

legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; z-index:9999; background: white; padding: 10px; border:2px solid grey; border-radius:6px;">
<b>Groundwater Category</b><br>
<span style="background-color:#1a9850;width:20px;height:20px;display:inline-block;"></span> Safe<br>
<span style="background-color:#fee08b;width:20px;height:20px;display:inline-block;"></span> Semi Critical<br>
<span style="background-color:#d73027;width:20px;height:20px;display:inline-block;"></span> Critical<br>
<span style="background-color:#6a3d9a;width:20px;height:20px;display:inline-block;"></span> Over Exploited<br>
<span style="background-color:#4575b4;width:20px;height:20px;display:inline-block;"></span> Saline<br>
<span style="background-color:#a6cee3;width:20px;height:20px;display:inline-block;"></span> Hilly Area<br>
<span style="background-color:#cccccc;width:20px;height:20px;display:inline-block;"></span> No Data<br>
</div>
'''

# Example usage: render map for Gujarat
if __name__ == "__main__":
    render_state_map("gujarat")

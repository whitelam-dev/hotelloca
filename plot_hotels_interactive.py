import pandas as pd
import folium
from folium import IFrame
import numpy as np

# Load hotel data
df = pd.read_csv('hotels.csv')

# --- Offset overlapping markers ---
def offset_duplicates(df, lat_col='Latitude', lon_col='Longitude', offset_m=0.01):
    grouped = df.groupby([lat_col, lon_col])
    df = df.copy()
    for _, group in grouped:
        if len(group) > 1:
            angles = np.linspace(0, 2 * np.pi, len(group), endpoint=False)
            for i, idx in enumerate(group.index):
                df.at[idx, lat_col] += offset_m * np.cos(angles[i])
                df.at[idx, lon_col] += offset_m * np.sin(angles[i])
    return df

df = offset_duplicates(df)

# Center map at global mean coordinates
mean_lat = df['Latitude'].mean()
mean_lon = df['Longitude'].mean()

# Create folium map with no horizontal wrap and restricted bounds
# Compute bounds for all marker clones (±720°)
min_lat = df['Latitude'].min() - 2
max_lat = df['Latitude'].max() + 2
min_lon = df['Longitude'].min() - 720 - 2
max_lon = df['Longitude'].max() + 720 + 2

m = folium.Map(
    location=[mean_lat, mean_lon],
    zoom_start=2,
    tiles=None,  # We'll add the tile layer manually
    max_bounds=True,
)
# Add tile layer with infinite scroll
folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    attr='&copy; <a href="https://carto.com/attributions">CARTO</a>',
    name='CartoDB Voyager',
    no_wrap=False
).add_to(m)
# Set max bounds to fit all marker clones
m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

# Inject JS to alias the map variable to window.map for global access
from folium import Element
set_map_js = Element('''
<script>
(function() {
  var tries = 0;
  var maxTries = 30;
  var interval = setInterval(function() {
    for (var key in window) {
      if (key.startsWith('map_')) {
        window.map = window[key];
        console.log('DEBUG: window.map set to', key);
        clearInterval(interval);
        return;
      }
    }
    tries++;
    if (tries >= maxTries) {
      clearInterval(interval);
      console.warn('DEBUG: Could not find map variable after retries');
    }
  }, 200);
})();
</script>
''')
m.get_root().html.add_child(set_map_js)

# Keep references for JS sync
marker_js = []
marker_refs = []

# Add each hotel as a clickable red circle marker with hyperlink popup
marker_js_array = []
lat_list = []
lon_list = []
for idx, row in df.iterrows():
    hotel_name = row['Hotel Name']
    url = row['Website']
    popup_html = f'''
    <style>
    .popup-hotel-link {{
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 1.08em;
        font-weight: 600;
        color: #222;
        text-decoration: none !important;
        background: none;
        border: none;
        padding: 0;
        margin: 0;
        transition: color 0.18s;
        cursor: pointer;
    }}
    .popup-hotel-link:hover, .popup-hotel-link:focus, .popup-hotel-link:active {{
        color: #757f9a;
        font-weight: 600;
        text-decoration: none !important;
        outline: none;
    }}
    </style>
    <a href="{url}" target="_blank" class="popup-hotel-link">{hotel_name}</a>
    '''
    popup = folium.Popup(popup_html, max_width=300)
    # Main marker (with popup)
    marker = folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=4.5,
        color='#fff',  # white border
        weight=2,
        fill=True,
        fill_color='#5c6bc0',  # modern indigo accent
        fill_opacity=0.92,
        popup=popup,
        tooltip='Click for hotel name',
    )
    marker.add_to(m)
    marker._name = f"marker_{idx}"
    marker_js_array.append(f"marker_{idx}")
    lat_list.append(row['Latitude'])
    lon_list.append(row['Longitude'])
    # Attach marker to window in JS for reliable reference (INSIDE THE LOOP)
    marker_js = f'<script>window._hotel_markers = window._hotel_markers || []; window._hotel_markers.push(marker_{idx});</script>'
    print('Injecting marker JS:', marker_js)
    marker.add_child(folium.Element(marker_js))

# --- Add scrollable table + JS for sync ---
hotels_table = df[['Hotel Name', 'City', 'Country']]
hotels_table = hotels_table.reset_index()  # To get original index for JS
rows_html = ''
for i, row in hotels_table.iterrows():
    rank = row['index'] + 1  # index is 0-based, rank is 1-based
    rows_html += f'<tr data-idx="{row["index"]}"><td>{rank}</td><td>{row["Hotel Name"]}</td><td>{row["City"]}</td><td>{row["Country"]}</td></tr>'

table_html = f'''<table class="hotel-table"><thead><tr><th>Rank</th><th>Hotel Name</th><th>City</th><th>Country</th></tr></thead><tbody>{rows_html}</tbody></table>'''

# --- Inject table, CSS, and JS directly into the Folium map HTML ---
from folium import Element

# External CSS and JS links
external_assets = '''
<link rel="stylesheet" href="style.css">
<link href="https://fonts.googleapis.com/css?family=Inter:400,600,700&display=swap" rel="stylesheet">
<script src="main.js"></script>
'''

# Table container with larger default size
custom_html = f'''
{external_assets}
<div class="header-bar">Top 50 Hotels Interactive Map</div>
<div id="table-container" style="width:420px; height:350px;">
  {table_html}
  <div id="table-resize-handle"></div>
</div>
<script>
document.addEventListener('DOMContentLoaded', function() {{
  window.collectMarkers(16, {len(marker_js_array)});
  setTimeout(function() {{ window.setupTableRowClicks({len(marker_js_array)}); }}, 800);
}});
</script>
'''


m.get_root().html.add_child(Element(custom_html))
# Inject debug script to log all global marker variables and window._hotel_markers
m.get_root().html.add_child(Element('''
<script>
console.log('DEBUG: Listing all global marker variables:');
for (var key in window) {
  if (key.startsWith('marker_')) {
    console.log('window.' + key, '=', window[key]);
  }
}
console.log('DEBUG: window._hotel_markers =', window._hotel_markers);
</script>
'''))

# Save the interactive map as a single HTML file
m.save('hotels_interactive_map.html')
print('Interactive map saved as hotels_interactive_map.html')

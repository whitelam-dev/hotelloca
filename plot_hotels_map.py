import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Load hotel data
df = pd.read_csv('hotels.csv')

# Set up the plot
fig = plt.figure(figsize=(16, 8), dpi=200)
ax = plt.axes(projection=ccrs.Mercator())
ax.set_global()
ax.set_facecolor('white')

# Draw country borders (no fill)
ax.add_feature(cfeature.BORDERS, edgecolor='black', linewidth=0.5)
ax.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=0.5)

# Plot hotels as red dots
ax.scatter(df['Longitude'], df['Latitude'],
           color='red', s=16,  # s is marker size in points^2 (4^2 = 16)
           transform=ccrs.PlateCarree(),
           zorder=5)

# Remove gridlines, labels, etc.
ax.gridlines(draw_labels=False)
ax.set_xticks([])
ax.set_yticks([])

# Optional title
plt.title('Top 50 Hotels of the World by Location', fontsize=18, pad=20)

# Save as PNG and SVG
plt.savefig('hotels_map.png', bbox_inches='tight', pad_inches=0.1)
plt.savefig('hotels_map.svg', bbox_inches='tight', pad_inches=0.1)
plt.close()

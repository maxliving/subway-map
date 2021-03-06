import pickle
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame, GeoSeries
from descartes import PolygonPatch
import numpy as np

def plot_border(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, color="#000000", linewidth=1, solid_capstyle='round', zorder=2)
def plot_line(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, linewidth=1, solid_capstyle='round', zorder=1)
stops = pickle.load(open('save/stops.p','rb'))
nyc = pickle.load(open('save/nyc.p','rb'))


stops['v_area'] = GeoSeries(index=np.arange(stops.shape[0]))
stops['v_larea'] = GeoSeries(index=np.arange(stops.shape[0]))
for i in np.arange(stops.shape[0]):
    stops['v_area'].ix[i] = stops.ix[i]['region'].area
    stops['v_larea'].ix[i] = np.log(stops.ix[i]['v_area'])


# Plotting

# # This is a choropleth according to area
fig = plt.figure(1,dpi=360,frameon=False)
ax = fig.add_subplot(111)

fig.set_size_inches(24,24)
ax.axis('off')

area_measure = 'v_larea'
# calculate percentiles for binning area
q = float(100)/6
qs = q*np.arange(7)
qs = np.percentile(stops[area_measure], qs.tolist())
qs = np.vstack([qs[:-1], qs[1:]]).T

# 'Blues' colorscheme from colorbrewer2.org; ascending from white to blue
colors = ['#EFF3FF', '#C6DBEF', '#9ECAE1', '#6BAED6', '#3182BD', '#08519C']
for row in stops.iterrows():
    row = row[1]
    polygon = row['region']

    # find index of bin for coloring
    comparison = row[area_measure] <= qs
    if np.all(comparison):
        color_index = 0
    else:
        color_index = np.where(np.logical_xor(comparison[:,0],comparison[:,1]))[0][0]
    c = colors[color_index]

    if polygon.geom_type == 'Polygon':
        ax.add_patch(PolygonPatch(polygon,facecolor=c,edgecolor="#000000"))
        # plot_line(ax, polygon.exterior)
    elif polygon.geom_type == 'MultiPolygon':
        for subpolygon in polygon:
            ax.add_patch(PolygonPatch(subpolygon,facecolor=c,edgecolor="#000000"))
            # plot_line(ax, subpolygon.exterior)

for clip in nyc:
    plot_border(ax,clip.exterior)

# plt.scatter(stops['x'].values,stops['y'].values,c='k',zorder=2)

plt.savefig('save/choropleth.png')

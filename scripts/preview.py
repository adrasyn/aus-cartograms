"""Render the cartogram with metropolitan group dividers."""
from pathlib import Path
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
g=gpd.read_file(ROOT/'data/australian_house_cartogram.gpkg',layer='electorates')
dividers=gpd.read_file(ROOT/'data/australian_house_cartogram.gpkg',layer='metro_boundaries')
fig,ax=plt.subplots(figsize=(7,8))
g.plot(ax=ax,color='#427E87',edgecolor='white',linewidth=.55)
dividers.plot(ax=ax,color='white',linewidth=1.2)
ax.set_aspect('equal');ax.axis('off')
ax.set_title('Australian House cartogram',fontsize=20,loc='left',pad=20)
fig.text(.08,.03,'150 seats · 2025 CED codes · approximate geographic placement',fontsize=9,color='#555555')
fig.tight_layout(rect=[.03,.06,.97,.97]);fig.savefig(ROOT/'docs/preview.png',dpi=180,facecolor='white');plt.close(fig)

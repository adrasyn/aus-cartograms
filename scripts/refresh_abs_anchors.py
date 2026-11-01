"""Optional online rebuild of ABS-only anchors, with source archive SHA256 checks."""
from pathlib import Path
import hashlib,json,urllib.request
import pandas as pd
import geopandas as gpd
ROOT=Path(__file__).resolve().parents[1]
cache=ROOT/'source/downloads';cache.mkdir(exist_ok=True)
manifest=json.loads((ROOT/'source/anchor_provenance.json').read_text())
archives=[]
for source in manifest['sources']:
    url=source['download_url'];path=cache/url.rsplit('/',1)[-1]
    if not path.exists():urllib.request.urlretrieve(url,path)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=source['sha256']:
        raise RuntimeError(f'Source checksum mismatch: {path.name}; inspect before accepting new data.')
    archives.append(path)
ced=gpd.read_file(archives[0]).to_crs(3577)
state=gpd.read_file(archives[1]).to_crs(3577)
ref=pd.read_csv(ROOT/'source/official_ced_crosswalk.csv',dtype=str).set_index('CED_CODE')
def largest(geom):
    if geom.geom_type=='Polygon':return geom
    parts=[p for p in geom.geoms if p.geom_type=='Polygon']
    if not parts:raise ValueError('No land polygon')
    return max(parts,key=lambda p:p.area)
rows=[]
for _,item in ced.iterrows():
    code=str(item.CED_CODE25)
    if code not in ref.index:continue
    cross=ref.loc[code];land=state[state.STE_CODE21.astype(str)==str(cross.STE_CODE)].geometry.iloc[0]
    main=largest(item.geometry.intersection(land));point=main.centroid
    rows.append({'AEC_ID':cross.AEC_DIVISION_ID,'CED_CODE':code,'CED_NAME':cross.CED_NAME,'state':cross.STATE,
                 'anchor_x_3577':point.x,'anchor_y_3577':point.y,'anchor_method':'largest ABS CED component clipped to ABS state land',
                 'retained_land_area_km2':main.area/1e6})
out=pd.DataFrame(rows)
points=gpd.GeoSeries(gpd.points_from_xy(out.anchor_x_3577,out.anchor_y_3577),crs=3577).to_crs(7844)
out['longitude']=points.x;out['latitude']=points.y
assert len(out)==150 and out.CED_CODE.nunique()==150
out.to_csv(ROOT/'source/abs_ced_anchors.csv',index=False)
print('Refreshed 150 ABS-only anchors. Run reassign_geographic.py, then validate.py.')

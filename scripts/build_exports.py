"""Rebuild interoperable exports from the frozen, selected cartogram geometry."""
from pathlib import Path
import json, zipfile, hashlib
import pandas as pd
import geopandas as gpd
from shapely import from_wkt
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

def build():
    DATA.mkdir(exist_ok=True)
    table = pd.read_csv(ROOT/'source/selected_geometry.csv', dtype={'CED_CODE':str,'AEC_ID':str,'VINTAGE':str})
    seats = gpd.GeoDataFrame(table.drop(columns='WKT'), geometry=table.WKT.map(from_wkt), crs=None)
    assert len(seats)==150 and seats.CED_CODE.nunique()==150
    master=DATA/'australian_house_cartogram.gpkg'
    if master.exists(): master.unlink()
    seats.to_file(master,layer='electorates',driver='GPKG')
    states=seats.dissolve(by='STATE',aggfunc={'CED_CODE':'count'})[['CED_CODE','geometry']].rename(columns={'CED_CODE':'SEATS'}).reset_index()
    states.to_file(master,layer='states',driver='GPKG')
    folder=DATA/'shapefile';folder.mkdir(exist_ok=True)
    for file in folder.glob('australian_house.*'):file.unlink()
    seats.to_file(folder/'australian_house.shp',driver='ESRI Shapefile',encoding='UTF-8',index=False)
    (folder/'australian_house.cpg').write_text('UTF-8\n')
    assert not (folder/'australian_house.prj').exists(), 'Diagram coordinates must not acquire a geographic CRS'
    with zipfile.ZipFile(DATA/'australian_house_cartogram_shapefile.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(folder.iterdir()):archive.write(file,file.name)
    table.to_csv(DATA/'australian_house_cartogram_wkt.csv',index=False)
    table.drop(columns='WKT').to_csv(DATA/'ced_crosswalk.csv',index=False)
    checksums={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DATA.rglob('*')) if p.is_file()}
    (ROOT/'checksums.json').write_text(json.dumps(checksums,indent=2)+'\n')
    print('Built 150 non-partisan geographic cartogram seats. CRS intentionally undefined.')
if __name__=='__main__':build()

"""Read-only portable validation: python validate_public_release.py [repository-root]."""
from pathlib import Path
import sys, json, zipfile, tempfile
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely import from_wkt
from shapely.ops import unary_union
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
data=root/'data'
seats=gpd.read_file(data/'australian_house_cartogram.gpkg',layer='electorates').sort_values('CED_CODE').reset_index(drop=True)
ref=pd.read_csv(root/'source/official_ced_crosswalk.csv',dtype=str)
assert len(seats)==150 and seats.CED_CODE.nunique()==150 and seats.AEC_ID.nunique()==150
assert seats.crs is None and seats.is_valid.all() and (seats.geom_type=='Polygon').all()
for field in ['CED_CODE','AEC_ID','VINTAGE']:assert seats[field].map(lambda v:isinstance(v,str)).all(),field
assert set(seats.VINTAGE)=={'2025'} and set(seats.LAYOUT)=={'geographic'}
x=seats.merge(ref,on='CED_CODE',suffixes=('','_ref'),validate='one_to_one')
assert len(x)==150 and (x.CED_NAME==x.CED_NAME_ref).all() and (x.STATE==x.STATE_ref).all()
assert (x.AEC_ID==x.AEC_DIVISION_ID).all()
assert (seats.METRO==seats.AEC_CLASS.isin(['Inner Metropolitan','Outer Metropolitan']).astype(int)).all()
assert seats.METRO.sum()==88
counts={'NSW':46,'VIC':38,'QLD':30,'WA':16,'SA':10,'TAS':5,'ACT':3,'NT':2}
assert seats.STATE.value_counts().to_dict()==counts
assert all(len(c)<=10 for c in seats.columns if c!='geometry')
with tempfile.TemporaryDirectory() as temp:
    with zipfile.ZipFile(data/'australian_house_cartogram_shapefile.zip') as archive:
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in archive.namelist())
        archive.extractall(temp)
    shp=next(Path(temp).rglob('*.shp'));shapes=gpd.read_file(shp).sort_values('CED_CODE').reset_index(drop=True)
    assert not shp.with_suffix('.prj').exists() and shapes.crs is None
    assert shp.with_suffix('.cpg').read_text().strip().upper()=='UTF-8'
    for field in ['CED_CODE','CED_NAME','AEC_ID','STATE','VINTAGE','AEC_CLASS','LAYOUT']:
        assert (seats[field]==shapes[field]).all(),field
    assert all(a.equals(b) for a,b in zip(seats.geometry,shapes.geometry))
table=pd.read_csv(data/'australian_house_cartogram_wkt.csv',dtype={'CED_CODE':str,'AEC_ID':str,'VINTAGE':str}).sort_values('CED_CODE').reset_index(drop=True)
assert list(table.CED_CODE)==list(seats.CED_CODE)
assert all(a.equals(from_wkt(b)) for a,b in zip(seats.geometry,table.WKT))
hexarea=3*np.sqrt(3)/2
assert np.allclose(seats.geometry.area/(5*hexarea),seats.AREA_RATIO,rtol=0,atol=1e-10)
assert np.allclose(100*(seats.AREA_RATIO-1),seats.AREA_ERR,rtol=0,atol=1e-10)
states=gpd.read_file(data/'australian_house_cartogram.gpkg',layer='states')
dividers=gpd.read_file(data/'australian_house_cartogram.gpkg',layer='metro_boundaries')
assert dividers.crs is None and set(dividers.STATE)==set(counts)-{'ACT'}
assert len(dividers)==7 and dividers.STATE.is_unique
assert (dividers.geom_type=='MultiLineString').all() and dividers.is_valid.all()
for _,divider in dividers.iterrows():
    part=seats[seats.STATE==divider.STATE]
    metro=unary_union(part.loc[part.METRO==1].geometry)
    other=unary_union(part.loc[part.METRO==0].geometry)
    expected=metro.boundary.intersection(other.boundary)
    assert divider.geometry.equals(expected),divider.STATE
    assert divider.geometry.intersection(unary_union(part.geometry).boundary).length<1e-8
with tempfile.TemporaryDirectory() as temp:
    with zipfile.ZipFile(data/'metro_boundaries_shapefile.zip') as archive:
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in archive.namelist())
        archive.extractall(temp)
    shp=Path(temp)/'metro_boundaries.shp'
    lines=gpd.read_file(shp)
    assert lines.crs is None and not shp.with_suffix('.prj').exists()
    assert shp.with_suffix('.cpg').read_text().strip().upper()=='UTF-8'
    assert len(lines)==7 and lines.STATE.is_unique and set(lines.STATE)==set(dividers.STATE)
    for _,line in lines.iterrows():
        assert line.geometry.equals(dividers.loc[dividers.STATE==line.STATE].geometry.iloc[0])
source=pd.read_csv(root/'source/selected_geometry.csv',dtype={'CED_CODE':str,'AEC_ID':str,'VINTAGE':str}).sort_values('CED_CODE').reset_index(drop=True)
assert all(a.equals(from_wkt(b)) for a,b in zip(seats.geometry,source.WKT))
for field in source.columns.drop('WKT'):
    assert (seats[field]==source[field]).all(),field
assert states.crs is None and len(states)==8
for _,state in states.iterrows():
    part=seats[seats.STATE==state.STATE];union=unary_union(part.geometry)
    assert union.symmetric_difference(state.geometry).area<1e-6
    assert abs(part.geometry.area.sum()-union.area)<1e-6
    assert abs(state.geometry.area/(counts[state.STATE]*5*hexarea)-1)<1e-7
assert max(states.geometry.iloc[i].intersection(states.geometry.iloc[j]).area for i in range(8) for j in range(i))<1e-6
assert not any(p.suffix.lower() in {'.ttf','.otf','.woff','.woff2','.pfb'} for p in root.rglob('*')
               if '.venv' not in p.relative_to(root).parts and p.is_file())
print(json.dumps({'status':'PASS','seats':150,'official_ABS_codes':150,'distinct_AEC_IDs':150,'metro':88,'metro_boundaries':7,'CRS':None,'formats':['GeoPackage','zipped UTF-8 Shapefile','CSV/WKT'],'max_abs_area_error_pct':float(seats.AREA_ERR.abs().max())},indent=2))

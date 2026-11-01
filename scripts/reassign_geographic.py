"""Regenerate geographic assignment from ABS-only land anchors and neutral frozen slots."""
from pathlib import Path
import math
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.stats import rankdata
from scipy.optimize import linear_sum_assignment
from build_exports import build
ROOT=Path(__file__).resolve().parents[1]
slots=gpd.read_file(ROOT/'source/slots.gpkg',layer='slots')
people=pd.read_csv(ROOT/'source/assignment_people.csv',dtype={'CED_CODE':str,'AEC_ID':str}).sort_values('ORDER')
anchors=pd.read_csv(ROOT/'source/abs_ced_anchors.csv',dtype={'CED_CODE':str,'AEC_ID':str})
people=people.merge(anchors[['CED_CODE','longitude','latitude']],on='CED_CODE',validate='one_to_one',sort=False)
table=pd.read_csv(ROOT/'source/selected_geometry.csv',dtype={'CED_CODE':str,'AEC_ID':str,'VINTAGE':str}).set_index('CED_CODE')
assignment=[]
for (state,metro),persons in people.groupby(['STATE','METRO'],sort=False):
    sub=slots[(slots.STATE==state)&(slots.METRO==metro)]
    n=len(sub);geo=persons[['longitude','latitude']].to_numpy();dst=np.array([[g.centroid.x,g.centroid.y] for g in sub.geometry])
    bands=max(1,round(np.sqrt(n)/1.4))
    if not metro and state in ['NSW','QLD']:bands=max(bands,math.ceil(n/4))
    if (not metro and state=='WA') or state in ['NT','ACT']:bands=n
    targetorder=np.argsort(-dst[:,1]);begin=0
    for band in np.array_split(np.argsort(-geo[:,1]),bands):
        target=targetorder[begin:begin+len(band)];begin+=len(band)
        ar=np.column_stack([rankdata(geo[band,k]) for k in range(2)])/len(band)
        dr=np.column_stack([rankdata(dst[target,k]) for k in range(2)])/len(target)
        cost=((ar[:,None,:]-dr[None,:,:])**2*np.array([1.8,1.0])).sum(2)
        ii,jj=linear_sum_assignment(cost)
        for i,j in zip(band[ii],target[jj]):
            code=persons.iloc[i].CED_CODE;geom=sub.iloc[j].geometry
            table.loc[code,'WKT']=geom.wkt;ratio=geom.area/(5*3*np.sqrt(3)/2)
            table.loc[code,'AREA_RATIO']=ratio;table.loc[code,'AREA_ERR']=100*(ratio-1)
            assignment.append({'CED_CODE':code,'SLOT_ID':int(sub.iloc[j].SLOT_ID)})
assert len(assignment)==150
pd.DataFrame(assignment).sort_values('CED_CODE').to_csv(ROOT/'source/geographic_assignment.csv',index=False)
table.reset_index().sort_values('CED_CODE').to_csv(ROOT/'source/selected_geometry.csv',index=False)
build()

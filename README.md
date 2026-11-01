# Aus Cartograms

The current release provides reusable **150-seat Australian House of Representatives cartogram polygons**, with official **2025 ABS CED codes and names**. The default layout places electorates approximately geographically; seats are **not grouped by party** and the files contain no political affiliations.

[GitHub repository](https://github.com/adrasyn/aus-cartograms). State electorates, SA2s and other geographies are planned for future releases.

![Non-partisan cartogram preview](docs/preview.png)

## Download

- [GeoPackage](data/australian_house_cartogram.gpkg) — recommended; `electorates` and `states` layers.
- [Zipped shapefile](data/australian_house_cartogram_shapefile.zip) — extract every companion file together; UTF-8 names.
- [Attributes / identifier crosswalk](data/ced_crosswalk.csv).
- [CSV with WKT geometry](data/australian_house_cartogram_wkt.csv).

**These are diagram coordinates, not longitude/latitude. The CRS is intentionally undefined.** Do not assign an EPSG code, transform these coordinates or overlay real geographic data. GeoJSON is deliberately omitted because RFC 7946 expects geographic longitude/latitude coordinates.

## Identifiers

`CED_CODE` and `CED_NAME` are taken directly from **ABS CED2025** (`CED_CODE25`, `CED_NAME25`). Codes are stored as strings and must be interpreted with `VINTAGE = "2025"`.

`AEC_ID` is the **separate national AEC DivisionID**, also stored as a string. The schemes are not interchangeable: **Banks is CED_CODE `101`, AEC_ID `103`**. All 150 codes and names are matched one-to-one against the official ABS source. Do not join a differently dated redistribution by code alone.

| Field | Meaning |
|---|---|
| `CED_CODE`, `CED_NAME` | Official ABS 2025 CED identifier and name |
| `AEC_ID` | National AEC DivisionID; different code scheme |
| `STATE`, `VINTAGE` | State abbreviation and electoral-geography vintage |
| `METRO`, `AEC_CLASS` | 1 for AEC Inner/Outer Metropolitan; 0 for Provincial/Rural; original classification retained |
| `AREA_RATIO`, `AREA_ERR` | Seat area / target area, and percentage deviation |
| `NOM_HEX` | Nominal target of five full hexagons' area; not exactly five cells |
| `LAYOUT` | `geographic` — approximate positions, not party grouping |

All shapefile field names are at most 10 characters. The shapefile has a UTF-8 `.cpg` and deliberately no `.prj`.

## Python

```python
import geopandas as gpd
seats = gpd.read_file("data/australian_house_cartogram.gpkg", layer="electorates")
assert len(seats) == 150 and seats["CED_CODE"].is_unique
assert seats.crs is None
seats.plot(color="#427E87", edgecolor="white", linewidth=0.4)
# Your data should use string, 2025-vintage CED codes:
# seats = seats.merge(values, on="CED_CODE", validate="one_to_one")
```

## R

```r
library(sf)
library(ggplot2)
seats <- st_read("data/australian_house_cartogram.gpkg", layer = "electorates")
# Some GDAL versions expose an "Undefined SRS" Cartesian placeholder.
# Remove that placeholder for plotting; this does not transform coordinates.
seats <- st_set_crs(seats, NA)
stopifnot(nrow(seats) == 150L, !anyDuplicated(seats$CED_CODE), is.na(st_crs(seats)))
ggplot(seats) +
  geom_sf(fill = "#427E87", colour = "white", linewidth = 0.15) +
  coord_sf(datum = NA) + theme_void()
# Join your data by CED_CODE, stored as character, using the 2025 code vintage.
```

Python/GeoPandas and GDAL shapefile round trips are tested. `tests/validate.R` also passes with R 4.6.0, `sf` 1.1.3 and GDAL 3.8.5: both GeoPackage and UTF-8 shapefile imports preserve all 150 official CED codes/names and separate AEC IDs. The plotting example uses standard `sf`/`ggplot2` interfaces; its rendering is not part of that import test.

## What the map represents

- State areas are proportional to seats: NSW46, VIC38, QLD30, WA16, SA10, TAS5, ACT3, NT2.
- Individual seat areas are **approximate**, because internal boundaries follow whole clipped regular-hex cell edges. Use `AREA_RATIO` rather than assuming every seat is exactly equal.
- Electorates are ordered geographically within fixed AEC metropolitan/non-metropolitan regions. Local position and adjacency are not exact; some regional coastal seats appear inland because metropolitan seats are expanded. These are **not official electoral boundaries**.
- Coastlines come from **ABS ASGS2021 State/Territory** data, not electoral marine envelopes. Small offshore islands are omitted; largest-landmass exteriors are simplified and interior holes filled. ACT is separately displayed, and its NSW enclave is filled.
- Sources are GDA2020. Straight-graticule display projections use standard parallel25°S generally and42°S for Tasmania to avoid stretching Tasmania. States are then uniformly area-normalized and translated. Final diagram coordinates are not GDA2020 coordinates.
- The 2025 CED vintage is intentionally fixed; this is not a rolling record of redistributions or current members.

See [methods](docs/methods.md), [source attribution](docs/sources.md) and [validation](docs/validation.json).

## Reproduction

```sh
python -m pip install -r requirements.txt
python scripts/build_exports.py       # exact selected geometry -> GPKG / SHP / CSV
python scripts/reassign_geographic.py # ABS-only anchors -> geographic label assignment
python scripts/preview.py             # neutral preview, standard open fonts
python tests/validate.py
```

The frozen selected geometry, original clipped cells, neutral placement slots and ABS-only anchors are retained. This reproduces the released geometry/assignment without proprietary fonts or AEC map files. It does not pretend that rerunning a stochastic layout search from scratch will select the identical design. Optional `scripts/refresh_abs_anchors.py` downloads checksum-verified official ABS sources and regenerates anchors.

## Licence and citation

Original code: [MIT](LICENSE). Data and preview: [CC BY 4.0](LICENSES/DATA-CC-BY-4.0.md), with attribution to James Wilson and the Australian Bureau of Statistics; AEC classification/identifier tables are separately attributed. These cartograms are modified/synthetic works, not official ABS/AEC products or endorsements. **No AEC map geometry or proprietary font is distributed or required.**

Please cite the version and 2025 CED vintage; machine-readable citation metadata is in [CITATION.cff](CITATION.cff).

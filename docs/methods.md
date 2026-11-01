# Methods and limitations

The released dataset contains 150 original synthetic seat polygons. It is not a simplified copy of official electorate boundaries.

1. Dedicated ABS2021 state land polygons provide the outer silhouettes. The largest mainland polygon is retained, interior holes filled, and outlines simplified at100 projected metres. This omits small offshore islands and fills NSW's ACT enclave because ACT is displayed separately.
2. GDA2020-based straight-graticule equidistant cylindrical display projections use standard parallel25°S, or42°S for Tasmania. Each state is subsequently uniformly normalized to its number of seats and translated into a compact Australian arrangement. These operations make final coordinates diagrammatic, not geographic.
3. Regular unit-side hexagons are clipped to the selected state silhouettes and partitioned into connected seat shapes, targeting five full hexagons' area per seat. Whole-cell assignments preserve hexagonal internal edges but permit unequal seat areas. Coastline clipping can create multiple atomic pieces from one hexagon; `NOM_HEX` does not promise exactly five cells per seat.
4. Coast/partition necks were visually inspected and tested using inward buffers0.03,0.06 and0.12 diagram units, flagging secondary lobes larger than0.03 full-hex area and comparing against the eroded state outline. Selected cells were reassigned to remove artificial coastal ribbons without changing the coastline. Natural or broader harbour features can remain; this is a bounded audit, not a universal minimum-width guarantee.
5. AEC's published classification defines metropolitan seats as Inner or Outer Metropolitan; Provincial and Rural are not metropolitan. Fixed connected regions retain these counts. Fadden is classified Outer Metropolitan by AEC even though other Gold Coast seats are Provincial. No manual city-rule override is applied.
6. Geographic assignment uses **ABS2025 CED polygons**, clipped to ABS2021 state land, with the centroid of the largest remaining land component as an anchor. This avoids offshore/marine-centroid errors. Within each state and metro/rest group, north–south bands and rank-based Hungarian matching approximate relative location. No party information enters the public pipeline.
7. The final choice of regular-hex partitions and state translations is preserved in neutral frozen geometry and cells. `build_exports.py` replays the exact selected geometry. `reassign_geographic.py` deterministically reassigns labels from the ABS-only anchor table and frozen neutral slots. The release does not include a promise of reconstructing the identical manually reviewed design by rerunning an unconstrained stochastic partition search.

## What is and is not equal

State areas are proportional to seat counts. Individual seats vary: consult each feature's `AREA_RATIO` and `AREA_ERR`. The current median absolute deviation is approximately1.14%; the maximum is approximately11.10%. Shape-to-name reassignment can change which electorate has an extreme area but cannot change the distribution of areas.

## Geographic approximation

The compact layout preserves broad state orientation but is not a geographic projection of Australia. Electorate locations and neighbours are approximate. Fixed metropolitan regions necessarily displace some non-metropolitan coastal seats inland. This dataset should not be used for geocoding, geographic distances, electoral administration, population overlays or official boundary analysis.

## Validation and reproducibility

Tests cover all150 official ABS code/name and separate AEC-ID joins, unique identifiers, string types, validity/connectivity, state/metro counts, state-area proportions, gaps/overlaps, shapefile round trips and CSV-WKT equality. All source code uses repository-relative paths; no AEC map archive or proprietary font is required.

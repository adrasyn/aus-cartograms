# Methods and limitations

The dataset contains 150 synthetic seat polygons arranged within simplified state silhouettes. The shapes represent seats in a cartogram rather than official electorate boundaries.

1. ABS ASGS2021 state land polygons provide the outer silhouettes. Each state's largest landmass is retained, interior holes filled, and outlines simplified at 100 projected metres. Small offshore islands are omitted. ACT is displayed separately, with its NSW enclave filled.
2. GDA2020-based equidistant cylindrical display projections use standard parallels of 25°S generally and 42°S for Tasmania. Each state is uniformly normalized to its number of seats and translated into a compact Australian arrangement. Final coordinates use local diagram space.
3. Regular unit-side hexagons are clipped to the state silhouettes and partitioned into connected seat shapes, targeting five full hexagons' area per seat. Whole-cell assignments preserve hexagonal internal edges and produce variation in seat areas. Coastline clipping can split one hexagon into multiple pieces; `NOM_HEX` expresses target area.
4. Narrow connections are assessed using inward buffers of 0.03, 0.06 and 0.12 diagram units. Secondary lobes larger than 0.03 full-hex area are compared with the eroded state outline. The assessment covers these thresholds; natural harbour features and broader connections can remain.
5. AEC classifications define metropolitan seats as Inner or Outer Metropolitan, and other seats as Provincial or Rural. Connected regions retain the published counts and classifications, including Fadden's Outer Metropolitan classification.
6. Geographic assignment uses **ABS ASGS2025 CED polygons**, clipped to ABS ASGS2021 state land. The centroid of the largest remaining land component supplies each electorate's geographic anchor. Within each state and metropolitan/non-metropolitan group, north–south bands and rank-based Hungarian matching approximate relative location.
7. Stored geometry, cells and placement slots preserve the released layout. `build_exports.py` exports the stored geometry. `reassign_geographic.py` deterministically assigns electorate names using the ABS anchor table and stored slots.

## Area variation

State areas are proportional to seat counts. Individual seats vary: consult each feature's `AREA_RATIO` and `AREA_ERR`. The median absolute deviation is approximately 1.14%; the maximum is approximately 11.10%.

## Geographic approximation

The compact layout preserves broad state orientation. Electorate locations and neighbours are approximate, and expanded metropolitan regions displace some coastal seats inland. Coordinates are diagrammatic, not a geographic reference system. Geocoding, distance measurement, spatial overlays and official boundary analysis require geographic boundary data.

## Validation and reproducibility

Tests cover all 150 official ABS code/name and separate AEC-ID joins, unique identifiers, string types, validity/connectivity, state/metropolitan counts, state-area proportions, gaps/overlaps, shapefile round trips and CSV-WKT equality. Scripts use repository-relative paths and the stored source inputs.

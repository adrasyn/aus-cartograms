# Run from the repository root: Rscript tests/validate.R
library(sf)
# GDAL versions may expose the GeoPackage's undefined Cartesian placeholder.
diagram_crs <- function(x) {
  crs <- st_crs(x)
  stopifnot(is.na(crs) || (is.na(crs$epsg) && identical(crs$Name, 'Undefined SRS') &&
                          identical(st_is_longlat(x), FALSE)))
  st_set_crs(x, NA)
}
s <- diagram_crs(st_read('data/australian_house_cartogram.gpkg',layer='electorates',quiet=TRUE))
r <- read.csv('source/official_ced_crosswalk.csv',colClasses='character',check.names=FALSE)
stopifnot(nrow(s)==150L,is.character(s$CED_CODE),is.character(s$AEC_ID),
          !anyDuplicated(s$CED_CODE),!anyDuplicated(s$AEC_ID),
          is.na(st_crs(s)),all(st_is_valid(s)),sum(s$METRO)==88L)
i <- match(s$CED_CODE,r$CED_CODE)
stopifnot(!anyNA(i),all(s$CED_NAME==r$CED_NAME[i]),all(s$AEC_ID==r$AEC_DIVISION_ID[i]))
stopifnot(s$AEC_ID[s$CED_NAME=='Banks']=='103',s$CED_CODE[s$CED_NAME=='Banks']=='101')
tmp <- tempfile('cartogram-shp-');dir.create(tmp)
unzip('data/australian_house_cartogram_shapefile.zip',exdir=tmp)
t <- st_read(file.path(tmp,'australian_house.shp'),quiet=TRUE)
stopifnot(nrow(t)==150L,is.character(t$CED_CODE),is.na(st_crs(t)),all(st_is_valid(t)))
j <- match(s$CED_CODE,t$CED_CODE)
stopifnot(!anyNA(j),all(s$CED_NAME==t$CED_NAME[j]),all(s$AEC_ID==t$AEC_ID[j]))
b <- diagram_crs(st_read('data/australian_house_cartogram.gpkg',layer='metro_boundaries',quiet=TRUE))
stopifnot(nrow(b)==7L,!anyDuplicated(b$STATE),all(st_is_valid(b)),
          setequal(b$STATE,setdiff(unique(s$STATE),'ACT')),
          all(st_geometry_type(b)=='MULTILINESTRING'))
for (state in b$STATE) {
  part <- s[s$STATE==state,]
  expected <- st_intersection(st_boundary(st_union(part[part$METRO==1,])),
                              st_boundary(st_union(part[part$METRO==0,])))
  actual <- st_geometry(b[b$STATE==state,])
  stopifnot(st_equals(actual,expected,sparse=FALSE)[1,1],
            sum(as.numeric(st_length(st_intersection(actual,st_boundary(st_union(part))))))<1e-8)
}
unzip('data/metro_boundaries_shapefile.zip',exdir=tmp)
bt <- st_read(file.path(tmp,'metro_boundaries.shp'),quiet=TRUE)
stopifnot(nrow(bt)==7L,is.na(st_crs(bt)),!anyDuplicated(bt$STATE),setequal(b$STATE,bt$STATE))
for (state in b$STATE) {
  stopifnot(st_equals(b[b$STATE==state,],bt[bt$STATE==state,],sparse=FALSE)[1,1])
}
unlink(tmp,recursive=TRUE)
cat('PASS: R/sf loaded 150 seats with official identifiers and seven internal metropolitan dividers; GeoPackage and UTF-8 shapefile geometries agree.\n')

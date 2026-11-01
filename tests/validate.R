# Run from the repository root: Rscript tests/validate.R
library(sf)
s <- st_read('data/australian_house_cartogram.gpkg',layer='electorates',quiet=TRUE)
# GDAL versions may expose the GeoPackage's undefined Cartesian placeholder.
crs <- st_crs(s)
stopifnot(is.na(crs) || (is.na(crs$epsg) && identical(crs$Name, 'Undefined SRS') &&
                        identical(st_is_longlat(s), FALSE)))
s <- st_set_crs(s, NA)
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
unlink(tmp,recursive=TRUE)
cat('PASS: R/sf loaded 150 GeoPackage and UTF-8 shapefile seats with official string CED codes and names.\n')

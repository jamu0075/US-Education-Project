import os
import pandas as pd
import geopandas as gpd
from pathlib import Path


# directory = Path("../data_raw/unsd_shps/")
# files = directory.glob("tl_2016_*_unsd.shp")
#
# gdf = gpd.GeoDataFrame(pd.concat([gpd.read_file(i) for i in files],
#                         ignore_index=True), crs=gpd.read_file(files[0]).crs).pipe(geopandas.GeoDataFrame)
#
# gdf.to_file('../data_clean/unsd_compiled.shp')

folder = Path("../data_raw/unsd_shps/")
shapefiles = folder.glob("tl_2016_*_unsd.shp")
gdf = (pd.concat([gpd.read_file(shp) for shp in shapefiles])).pipe(gpd.GeoDataFrame)

gdf.to_file('../data_clean/unsd_compiled.shp')

# Reddit post

## Title

[OC] Where the wind blows: the world's winds month by month, and are wind farms in the windy places? 82% of onshore wind farm capacity sits on ground windier than its country's median

## Body (optional)

Land winds are WorldClim's monthly means at 10 m (1970 to 2000, about 9 km cells); sea winds and the streamlines are from the NCEP/NCAR reanalysis (1991 to 2020). The Roaring Forties average 10.2 m/s over the ocean at 40 to 50° S, against 8.8 m/s at the same latitudes in the north, and in the Arabian Sea the wind swings from the north-east in January to the south-west in July. On northern land the windiest month is April, not midwinter. I then set the 5,344 wind farms in WRI's Global Power Plant Database (a 2021 snapshot) against the wind at their sites: the average farm stands on ground windier than 72% of its country's land, most of all in Mexico (98%) and Brazil (88%); Chile's farms (31%) sit far from its windy Patagonia. Caveats: 10 m is not hub height, 9 km cells cannot see the ridge a farm is built on, and the database's coverage is uneven. Explore it month by month: https://maps.tristanhotham.com/wind-map/

## Source comment

Sources: WorldClim 2.1 monthly mean wind speed at 5 arc minutes (Fick, S.E. and Hijmans, R.J. 2017, WorldClim 2: new 1 km spatial resolution climate surfaces for global land areas, International Journal of Climatology; free for research and non-commercial use); NCEP/NCAR Reanalysis 1 long-term monthly means, 1991 to 2020, sigma level 0.995 (NOAA PSL, public domain; Kalnay et al. 1996); WRI Global Power Plant Database v1.3 (CC BY 4.0); boundaries and places from Natural Earth and ONS.

Tools: Python (numpy, pandas, rasterio, netCDF4, matplotlib, Pillow); Leaflet for the interactive map.

Interactive map: https://maps.tristanhotham.com/wind-map/
Blog post: https://blog.tristanhotham.com/2026/10/31/wind-map/
Paper and data: https://doi.org/10.5281/zenodo.23844511

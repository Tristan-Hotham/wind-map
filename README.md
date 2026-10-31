# Where the wind blows: the world's winds month by month, its windiest places, and whether wind farms stand in them

A month by month map of the world's winds. Mean wind speed over land comes from WorldClim 2.1 (10 m above the ground, 1970 to 2000, 5 arc minutes, about 9 km); ocean winds and the direction of the near-surface flow come from the NCEP/NCAR Reanalysis 1 long-term monthly means (1991 to 2020, 2.5°). The study maps the trade winds, the westerlies, the Roaring Forties and the monsoon reversal, finds the windiest and most seasonal places on land, zooms into the UK and Ireland, and sets the wind farms of the WRI Global Power Plant Database (a 2021 snapshot) against the wind at their sites.

**Interactive version:** https://maps.tristanhotham.com/wind-map/

**Paper and archived release:** https://doi.org/10.5281/zenodo.23844511

**Blog post:** https://blog.tristanhotham.com/2026/10/31/wind-map/

A data study by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349).

## Headline results

- **Wind farms are mostly in the windy places.** Weighted by capacity, the average onshore wind farm stands on ground windier than 72% of its country's land; 82% of onshore capacity is above the national median and 53% in the windiest quarter. In 17 of 21 countries with at least 400 MW in 8 or more listed onshore farms, the farms are windier than the land. Mexico 98% (Isthmus of Tehuantepec), Brazil 88%, United States 76%, China 73%, UK 61%, Chile 31%.
- **The Roaring Forties.** Over the ocean at 40 to 50° S the wind averages 10.2 m/s, against 8.8 m/s at 40 to 50° N; the fastest band is at 52.5° S (11.4 m/s). The trade winds are the steadiest: the mean wind vector keeps 76% of the mean speed, against 38% in the northern westerlies.
- **The monsoon.** Arabian Sea wind from the north-east at 6.3 m/s in January, from the south-west at 11.7 m/s in July; 12% of the area between 60° N and 60° S reverses its wind between January and July.
- **Windiest places on land** (outside Antarctica): Vatnajökull ice cap, Iceland (15.8 m/s), Jan Mayen, the East Greenland ice sheet, the Southern Patagonian Ice Field. Land mean 2.9 m/s; 5% of land averages 5 m/s or more. Windiest big city: Marseille (5.8 m/s).
- **Spring is windiest.** On northern land the windiest month is April and the calmest August; 57% of northern extratropical land peaks in March to May.
- **UK and Ireland.** UK land averages 4.9 m/s (1.7 times the world's land), Scotland 5.6, England 4.6; Ireland 4.6. Windiest county Shetland (7.6), calmest Herefordshire (3.3); windiest cell St Kilda (8.9). 23.2 GW of UK wind farms listed, 32% of it at sea.

Every number is in `data/results.json`, which the page, paper, blog and collage are built from.

## Files

| Path | What it is |
|---|---|
| `index.html` | The interactive page (tables embedded; grids, farms, places and borders load from `data/page/`). |
| `header.png` | Social card (1200 by 630). |
| `data/results.json` | Every number quoted anywhere. |
| `data/countries.csv` | Every country: land area, mean wind over land (annual and monthly), windiest and calmest month, and its listed wind farms with their capacity-weighted wind and percentile. |
| `data/wind_farms.csv` | The 5,344 wind farms of the WRI database (CC BY 4.0) with site class (land, coast, sea), the WorldClim wind at the site and its percentile within the country's land. |
| `data/windiest_places.csv` | The 20 windiest distinct places on land outside Antarctica, with monthly values. |
| `data/most_seasonal_places.csv` | The 12 places with the highest ratio of windiest to calmest month. |
| `data/cities.csv` | Natural Earth cities of a million or more, with annual and monthly wind. |
| `data/uk_counties.csv` | UK counties: annual and monthly mean wind, windiest cell. |
| `data/zonal_winds.csv` | NCEP ocean and all-longitude means by latitude: west to east wind, south to north wind, speed, January and July. |
| `data/page/` | Page files: WorldClim pictures (`vis_*.png`, palette images in colour classes, no values), a 0.5° summary of WorldClim rounded to 0.5 m/s for click readouts (`sum_*.png`), NCEP winds (`ncep.png`), farms, places and borders. |
| `code/common.py` | Paths to the raw inputs and shared helpers. |
| `code/01_grids.py` to `code/04_page_data.py` | Read the rasters, compute every statistic, write `results.json` and the page files. |
| `code/05_build_site.py` to `code/09_release.py` | Page, figures, social card, paper, blog post, Zenodo files and this README. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `release/` | Paper PDF and source, blog post and figures, Zenodo files. |

## Method in brief

- **Land.** WorldClim 2.1 monthly mean wind speed at 10 m, 1970 to 2000, 5 arc minutes. Annual mean = mean of the twelve months. 10,196 cells with no Natural Earth land within one cell (mostly the Caspian Sea) are dropped. Area averages weight cells by the cosine of latitude; "land" excludes Antarctica unless stated.
- **Seasonality.** Windiest month divided by calmest, for cells with an annual mean of at least 1.5 m/s; 3,634 cells with one month below 0.35 or above 2.5 times its neighbours' mean are treated as station artefacts.
- **Circulation.** NCEP/NCAR Reanalysis 1 long-term monthly means at sigma 0.995 (u, v, and speed from daily vectors), 1991 to 2020. Ocean = cells under 10% land. Steadiness = |mean vector| / mean speed. Monsoon reversal = January and July vectors both at least 2 m/s and at least 135° apart.
- **Windiest places.** Cells ranked by annual mean, each kept only if at least 500 km from a windier kept cell.
- **Farms.** WRI Global Power Plant Database v1.3, primary fuel Wind. On land if in a WorldClim land cell; coast if a neighbour is land; otherwise at sea. Percentile = share of the country's land area with a lower annual mean. Overseas territories without farms are left out of country land averages (United States = lower 48).
- **Check.** Over 2,017 cells of solid land the reanalysis speed is a median 1.39 times WorldClim (it is higher up and from a later period); correlation 0.79.

## Known limits

- Wind at 10 m is not wind at hub height, and a 9 km cell cannot see the ridge a farm is built on: farm winds are probably understated.
- WorldClim is interpolated from stations and is least certain where they are few: ice caps, mountains, deserts and remote islands, which dominate the windiest list.
- Monthly means say nothing about gusts, storms, calm spells or the distribution of speeds that sets wind power output.
- The WRI database is a 2021 snapshot with uneven coverage (for example Germany has 25 listed plants and India 108, far below their real fleets), and some positions are approximate.
- The reanalysis and WorldClim differ in height, period and resolution; the page draws the sea faded to show they are not like for like.

## Sources and licences

- WorldClim 2.1: Fick, S.E. and Hijmans, R.J. (2017) WorldClim 2: new 1 km spatial resolution climate surfaces for global land areas. International Journal of Climatology 37(12): 4302 to 4315. https://doi.org/10.1002/joc.5086. Free for research and other non-commercial use with citation.
- NCEP/NCAR Reanalysis 1 long-term monthly means, NOAA Physical Sciences Laboratory, https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.derived.html (public domain). Kalnay, E. et al. (1996) The NCEP/NCAR 40-year reanalysis project. Bulletin of the American Meteorological Society 77: 437 to 471.
- Global Energy Observatory, Google, KTH Royal Institute of Technology in Stockholm, Enipedia, World Resources Institute (2021) Global Power Plant Database v1.3.0 (CC BY 4.0).
- Natural Earth (public domain); UK counties from Office for National Statistics boundaries (Open Government Licence v3).
- Base map and hill shading tiles on the page © Esri. Map library: Leaflet.

Text, figures and derived data: CC BY 4.0, with one exception. WorldClim's terms do not allow its data to be redistributed, so this repository does not contain the WorldClim grids or any value encoding of them. WorldClim appears only as pictures (the figures, and the palette images `data/page/vis_*.png`, whose colours are broad classes) and as summaries (area means, values at named points and farm sites, and a 0.5° grid of means rounded to 0.5 m/s in `data/page/sum_*.png`). These WorldClim-derived pictures and summaries are shared for research and non-commercial use under the WorldClim terms; for the data itself go to worldclim.org. Code: MIT (see `LICENSE`).

## How to rerun

Raw inputs (paths in `code/common.py`, overridable with `WIND_RAW`, `WIND_GPPD`, `WIND_GEO`): the twelve WorldClim 2.1 5 arc minute wind GeoTIFFs (`wc2.1_5m_wind_01.tif` to `_12.tif`), the NCEP long-term means `uwnd.mon.ltm.nc`, `vwnd.mon.ltm.nc` and `wspd.mon.ltm.nc` (sigma 0.995), the WRI `global_power_plant_database.csv`, and Natural Earth and UK boundaries. Then run `code/01_grids.py` to `code/09_release.py` in order and `reddit/collage.py`. Intermediates go to `WIND_WORK` (default `/dev/shm/wind-map`). Python 3 with numpy, pandas, rasterio, netCDF4, shapely, scipy, Pillow and matplotlib; xelatex for the paper.

## Cite

Hotham, T. (2026) Where the wind blows: the world's winds month by month, its windiest places, and whether wind farms stand in them. Zenodo. https://doi.org/10.5281/zenodo.23844511

# Where the wind blows: the world's winds month by month, its windiest places, and whether wind farms stand in them

A month by month map of the world's winds. Mean wind speed over land comes from WorldClim 2.1 (10 m above the ground, 1970 to 2000, 5 arc minutes, about 9 km); ocean winds and the direction of the near-surface flow come from the NCEP/NCAR Reanalysis 1 long-term monthly means ({{meta.ncep_period|raw}}, 2.5°). The study maps the trade winds, the westerlies, the Roaring Forties and the monsoon reversal, finds the windiest and most seasonal places on land, zooms into the UK and Ireland, and sets the wind farms of the WRI Global Power Plant Database (a 2021 snapshot) against the wind at their sites.

**Interactive version:** https://maps.tristanhotham.com/wind-map/

**Paper and archived release:** {{DOI_URL}}

**Blog post:** https://blog.tristanhotham.com/2026/10/31/wind-map/

A data study by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349).

## Headline results

- **Wind farms are mostly in the windy places.** Weighted by capacity, the average onshore wind farm stands on ground windier than {{farms.land_cw_pctile|pct}} of its country's land; {{farms.share_cap_above_median|pct}} of onshore capacity is above the national median and {{farms.share_cap_top_quarter|pct}} in the windiest quarter. In {{farm_countries_windier|int}} of {{farm_countries_n|int}} countries with at least 400 MW in 8 or more listed onshore farms, the farms are windier than the land. Mexico {{fc.MEX.farm_cw_pctile|pct}} (Isthmus of Tehuantepec), Brazil {{fc.BRA.farm_cw_pctile|pct}}, United States {{fc.USA.farm_cw_pctile|pct}}, China {{fc.CHN.farm_cw_pctile|pct}}, UK {{fc.GBR.farm_cw_pctile|pct}}, Chile {{fc.CHL.farm_cw_pctile|pct}}.
- **The Roaring Forties.** Over the ocean at 40 to 50° S the wind averages {{circ.roar_s|f1}} m/s, against {{circ.roar_n|f1}} m/s at 40 to 50° N; the fastest band is at {{circ.sh_max_lat|abs1}}° S ({{circ.sh_max_speed|f1}} m/s). The trade winds are the steadiest: the mean wind vector keeps {{circ.trade_steady|pct}} of the mean speed, against {{circ.west_steady_n|pct}} in the northern westerlies.
- **The monsoon.** Arabian Sea wind from the {{monsoon.arabian_jan.from_pt|raw}} at {{monsoon.arabian_jan.vec|f1}} m/s in January, from the {{monsoon.arabian_jul.from_pt|raw}} at {{monsoon.arabian_jul.vec|f1}} m/s in July; {{monsoon.reversal_share|pct}} of the area between 60° N and 60° S reverses its wind between January and July.
- **Windiest places on land** (outside Antarctica): Vatnajökull ice cap, Iceland ({{windiest_places.0.wind|f1}} m/s), Jan Mayen, the East Greenland ice sheet, the Southern Patagonian Ice Field. Land mean {{land.mean|f1}} m/s; {{land.share_ge5|pct}} of land averages 5 m/s or more. Windiest big city: Marseille ({{cities_windiest.0.wind|f1}} m/s).
- **Spring is windiest.** On northern land the windiest month is {{land.nh_windiest_month|raw}} and the calmest {{land.nh_calmest_month|raw}}; {{derived.nh_spring_share|pct}} of northern extratropical land peaks in March to May.
- **UK and Ireland.** UK land averages {{uk.mean|f1}} m/s ({{derived.uk_vs_land|f1}} times the world's land), Scotland {{uk.Scotland|f1}}, England {{uk.England|f1}}; Ireland {{ireland.mean|f1}}. Windiest county Shetland ({{uk_county.Shetland Islands.wind|f1}}), calmest Herefordshire ({{uk_county.Herefordshire.wind|f1}}); windiest cell St Kilda ({{uk.max.wind|f1}}). {{uk_farms.cap_gw|f1}} GW of UK wind farms listed, {{derived.sea_share_uk|pct}} of it at sea.

Every number is in `data/results.json`, which the page, paper, blog and collage are built from.

## Files

| Path | What it is |
|---|---|
| `index.html` | The interactive page (tables embedded; grids, farms, places and borders load from `data/page/`). |
| `header.png` | Social card (1200 by 630). |
| `data/results.json` | Every number quoted anywhere. |
| `data/countries.csv` | Every country: land area, mean wind over land (annual and monthly), windiest and calmest month, and its listed wind farms with their capacity-weighted wind and percentile. |
| `data/wind_farms.csv` | The {{farms.n|int}} wind farms of the WRI database (CC BY 4.0) with site class (land, coast, sea), the WorldClim wind at the site and its percentile within the country's land. |
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

- **Land.** WorldClim 2.1 monthly mean wind speed at 10 m, 1970 to 2000, 5 arc minutes. Annual mean = mean of the twelve months. {{meta.wc_dropped|int}} cells with no Natural Earth land within one cell (mostly the Caspian Sea) are dropped. Area averages weight cells by the cosine of latitude; "land" excludes Antarctica unless stated.
- **Seasonality.** Windiest month divided by calmest, for cells with an annual mean of at least 1.5 m/s; {{meta.spike_cells|int}} cells with one month below 0.35 or above 2.5 times its neighbours' mean are treated as station artefacts.
- **Circulation.** NCEP/NCAR Reanalysis 1 long-term monthly means at sigma 0.995 (u, v, and speed from daily vectors), {{meta.ncep_period|raw}}. Ocean = cells under 10% land. Steadiness = |mean vector| / mean speed. Monsoon reversal = January and July vectors both at least 2 m/s and at least 135° apart.
- **Windiest places.** Cells ranked by annual mean, each kept only if at least 500 km from a windier kept cell.
- **Farms.** WRI Global Power Plant Database v1.3, primary fuel Wind. On land if in a WorldClim land cell; coast if a neighbour is land; otherwise at sea. Percentile = share of the country's land area with a lower annual mean. Overseas territories without farms are left out of country land averages (United States = lower 48).
- **Check.** Over {{check.n|int}} cells of solid land the reanalysis speed is a median {{check.ratio_median|f2}} times WorldClim (it is higher up and from a later period); correlation {{check.r|f2}}.

## Known limits

- Wind at 10 m is not wind at hub height, and a 9 km cell cannot see the ridge a farm is built on: farm winds are probably understated.
- WorldClim is interpolated from stations and is least certain where they are few: ice caps, mountains, deserts and remote islands, which dominate the windiest list.
- Monthly means say nothing about gusts, storms, calm spells or the distribution of speeds that sets wind power output.
- The WRI database is a 2021 snapshot with uneven coverage (for example Germany has {{fc_DEU.farms|int}} listed plants and India {{fc.IND.land_farms|int}}, far below their real fleets), and some positions are approximate.
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

Hotham, T. (2026) Where the wind blows: the world's winds month by month, its windiest places, and whether wind farms stand in them. Zenodo. {{DOI_URL}}

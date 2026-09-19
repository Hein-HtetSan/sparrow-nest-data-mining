# Adapting to Urban Heights: Flexible Nest-site Selection Strategies of a Human Commensal Bird Along Climate and Anthropogenic Gradients

Dataset DOI: [10.5061/dryad.rn8pk0ppz](https://doi.org/10.5061/dryad.rn8pk0ppz)

## Description of the data and file structure

The data collection involved systematic field surveys of Eurasian Tree Sparrow nests (availability and occupancy) on buildings across 22 northern Chinese cities over two breeding seasons, coupled with extensive collection of corresponding environmental data (climate, vegetation, human population, economic activity, light, noise, and building characteristics) from both field measurements and global/spatial databases, all georeferenced to the nest locations.

### Files and variables

File: Appendix_Core_R_Code_.txt

Description: Plain-text file containing the core analysis code (SEM, mixed-effects modeling, visualization).

Can be opened with any text editor. See the “Code/software” section for required packages and workflow.

File: NestHeight_SiteMean_raw-1.csv

Description:

Variable Name (in raw data) | Description | Unit | Source

* Building_ID | Unique identifier for the building | categorical | Field collection
* City_ID | Identifier for the city (1-22) | categorical | Field collection
* Building_width | Width of the building (used for density calculation) | meters (m) | Field collection
* GPS_latitude | Latitude of the building | decimal degrees | Field collection
* GPS_longitude | Longitude of the building | decimal degrees | Field collection
* Building_height | Height of the building | meters (m) | Field collection
* Number_potential_nests | Count of potential nest sites (air conditioner inlets, etc.) on the building | count | Field collection
* Number_occupied_nests | Count of nests occupied by ETS on the building | count | Field collection
* NDa | Available nest density: Number_potential_nests / Building_width | nests per meter (nests/m) | Calculated
* NDo | Occupied nest density: Number_occupied_nests / Building_width | nests per meter (nests/m) | Calculated
* NHP | Nest height preference: Average height of occupied nests (weighted by density per building) | meters (m) | Calculated (from nest height measurements)
* Altitude | Elevation above sea level at the building location | meters (m) | WorldClim (or derived from a DEM)
* Bio10 | Mean air temperature during the warmest season (summer) | °C | WorldClim
* Bio18 | Precipitation during the warmest season (summer) | mm | WorldClim
* Wind_speed | Wind speed during the warmest season (summer) | m/s | WorldClim (or other source)
* NDVI | Normalized Difference Vegetation Index (average during warmest season) | dimensionless (range -1 to 1) | NASA VIP dataset
* NPP | Net Primary Productivity (average during warmest season) | kg/m^2^/s? (But note: typical units for NPP are kg/m^2^/year. The paper lists "kg/m2/s1", which might be a typo. The source is "CMIP6 data archive", so we use the unit from that dataset) | CMIP6 data archive
* Nest_direction | Direction of the nest (average or main direction for the building? The paper says recorded per nest) | categorical (e.g., N, NE, etc.) or degrees | Field collection (then averaged per building?)
* Population_density | Human population density | persons per km^2^ | GPWv4
* GDP_per_cell | Gross Domestic Product per grid cell | USD | Kummu et al., 2018
* ALAN | Artificial Light at Night (digital number) | DN (0-63) | Harmonized DMSP/VIIRS
* Urban_land_extent | Fraction of urban land in the grid cell | fraction (0-1) | Gao and Pesaresi, 2021
* Noise_level | Measured noise level (at ground level below nests) | decibels (dB) | Field measurement (Sound Meter app)

*Note: The R code uses "nd" for NDVI, "gdpp" for GDP_per_cell, and "alt_group_quantile" for a grouped version of altitude.

Missing Values: Coded as NA in all datasets

Coordinate System: WGS84 (EPSG:4326) for spatial data

Temporal Coverage: Field surveys: April-July 2021-2022

Environmental variables: 2000-2020 (see sources for specifics)

Statistical Transformations:

* Nest density variables weighted per SEM requirements
* Variables scaled (0-1) in R analysis
* Altitude stratified into 5 quantile groups for variance modeling

## Code/software

I. Free/Open-Source Software for Data Viewing

Tabular Data (CSV):

* LibreOffice Calc (v7.0+), GNOME Calculator, or any text editor
* Python/R with pandas (no specialized tools needed)

Geospatial Data (TIFF/SHP):

* QGIS (v3.28+): Open-source GIS platform for raster/climate data and shapefiles
* Alternative: R terra/sf packages or Python geopandas/rasterio

Statistical Outputs:

* R/RStudio for SEM/mixed-model results
* Free PDF viewers for supplementary figures/tables

II. Analysis Software & Packages (with Versions)

Core environment: R v4.1.0+ with the following packages:

Package	Version	Purpose	Critical Functions

* nlme	3.1-164	Mixed-effects modeling	lme(), varIdent()
* piecewiseSEM	2.3.0	Structural Equation Modeling	psem(), summary()
* interactions	1.1.5	Johnson-Neyman analysis	johnson_neyman(), interact_plot()
* raster	3.5-15	Geospatial processing	brick(), crop(), mask()
* sf	1.0-12	Spatial vector handling	st_read(), spatial ops
* ggplot2	3.4.0	Visualization	Base plotting system
* ggMarginal	0.3.0	Marginal distribution plots	ggMarginal()
* gridExtra	2.3	Multi-panel layouts	grid.arrange()

Working directory: Before running the script, set the R working directory to the folder containing the data file (NestHeight_SiteMean_raw.csv) and all required spatial datasets. The script assumes all input files are located in this directory.

III. Code Description & Workflow

The analysis script (Appendix_Core_R_Code_.txt) performs the following steps:

1. Data Preparation – Load and crop spatial climate data to the study area.
2. Mixed-Effects Modeling – Fit linear mixed-effects models with altitude-stratified variance structures.
3. Structural Equation Modeling – Build and reduce a piecewise SEM using the fitted models.
4. Interaction Analysis – Conduct Johnson-Neyman tests for interactions (e.g., GDP × altitude).
5. Visualization – Generate publication-quality figures with marginal histograms.

The script contains detailed comments explaining each block of code. To reproduce the analyses, run the script line-by-line or source it in R after installing the required packages.

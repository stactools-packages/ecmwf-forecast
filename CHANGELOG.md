# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This project attempts to match the major and minor versions of [stactools](https://github.com/stac-utils/stactools) and increments the patch number as needed.


## [v0.0.0]

### Added

- Functionality to support the split of the ecmwf-forecast collection into 7 separate collections (ecmwf-forecast-wave-fc, ecmwf-forecast-cda-fc, ecmwf-forecast-oper-fc, ecmwf-forecast-enfo-ep, ecmwf-forecast-waef-ef, ecmwf-forecast-waef-ep, ecmwf-forecast-scwv-fc)
- Functionality to add kerchunk indices to the STAC item

### Deprecated

- Nothing.

### Removed

- Nothing.

### Fixed

- Nothing.


## [Unreleased]

### Added

- Nothing.

### Deprecated

- Nothing.

### Removed

- Automatic kerchunk generation and `kerchunk:indices` asset metadata during
  STAC item creation. Item construction no longer opens GRIB2 files, including
  for `wave/fc` products, so private source-storage access is not required.

### Fixed

- Parse optional ECMWF product suffixes such as `-sfc` separately from file
  extensions, require a literal extension separator and a full filename match.
- Preserve suffixes in item IDs, aggregated asset keys, grouping, and sibling
  filenames to prevent product variants from colliding while retaining legacy
  item and asset IDs.
- Fix item-assets type checking with newer PySTAC versions without changing
  collection metadata or requiring a newer PySTAC API.
- Correct the Black configuration key used to exclude notebooks.
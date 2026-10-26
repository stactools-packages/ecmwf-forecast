# ecmwf-forecast

Create STAC metadata for [ECMWF Open Data - Real Time](https://confluence.ecmwf.int/display/UDOC/ECMWF+Open+Data+-+Real+Time).


## Planetary Computer collection


```console
stac ecmwf-forecast create-collection template.json \
    --thumbnail="https://ai4edatasetspublicassets.blob.core.windows.net/assets/pc_thumbnails/sentinel-2.png" \
    --extra-field "msft:short_description=ECMWF Open Data (Real Time) forecasts" \
    --extra-field "msft:storage_account=ai4edatauewest" \
    --extra-field "msft:container=ecmwf"
```

## Planetary Computer item

```console
stac ecmwf-forecast create-item \
    "ecmwf/20220201/00z/0p4-beta/enfo/20220201000000-0h-enfo-ef.grib2" \
    "/ecmwf/20220201/00z/0p4-beta/enfo/20220201000000-0h-enfo-ef.index" \
    examples/item.json
```

For a complete, human-readable output example, see
[`tests/fixtures/item.json`](tests/fixtures/item.json). It contains the `0h` and
`3h` GRIB2/index assets for a suffixed product at resolution `0.10`.
The regression test compares the entire generated JSON against this fixture,
using STAC `1.0.0` explicitly so PySTAC's default version does not affect it.

## Filename compatibility

Both legacy filenames such as `20261021180000-0h-waef-ef.grib2` and filenames
with a product suffix such as `20261021180000-0h-waef-ef-sfc.grib2` are supported,
along with their `.index` counterparts. The entire basename must match the
filename pattern, including the literal dot before the extension.

Product suffixes are kept separate from `ecmwf:type` and recorded as
`ecmwf:suffix`. They distinguish item IDs, grouping keys, and sibling filenames.
The grouping-key helpers append the suffix (or an empty string for legacy
filenames) to their returned tuples.

For example, with `resolution="0.10"`, the suffixed filename above produces item
ID `ecmwf-2026-10-21T18-waef-ef-sfc-0.10` and asset key `0h-sfc-grib2`.
Split-by-step items also include the suffix in their item IDs and retain the
standard item-scoped `data` and `index` asset keys. Legacy item and asset IDs
are unchanged.

These changes must be installed in the runtime that constructs STAC items;
changing asset discovery or resolution alone does not update an older
installed parser.

## Metadata-only item creation

Item construction uses asset filenames and does not open GRIB2 files, including
for `wave/fc` products. Both explicit asset lists and representative-asset item
creation preserve the original asset HREFs without making source-storage
requests.

Kerchunk indices are not generated or attached as `kerchunk:indices` during
item creation. This allows STAC items to be constructed for private storage
without requiring source-storage credentials in the item-construction process.

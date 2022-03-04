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

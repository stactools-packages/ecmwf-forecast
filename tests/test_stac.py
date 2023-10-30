import datetime

import pytest

from stactools.ecmwf_forecast import stac


def test_create_collection():
    # Write tests for each for the creation of a STAC Collection
    # Create the STAC Collection...
    collection = stac.create_collection()
    collection.set_self_href("")

    # Check that it has some required attributes
    assert collection.id == "ecmwf-forecast-wave-fc"

    # Validate
    collection.validate()


@pytest.mark.parametrize(
    "filename",
    [
        "20231019000000-0h-wave-fc.grib2",
        "20231019/00z/0p4-beta/wave/20231019000000-0h-wave-fc.grib2",
        ("https://ai4edataeuwest.blob.core.windows.net/ecmwf/20231019/00z/"
         "0p4-beta/wave/20231019000000-0h-wave-fc.grib2"),
    ],
)
def test_create_items(filename):
    item = stac.create_item_from_representative_asset(filename)
    assert item.id == "ecmwf-2023-10-19T00-wave-fc-0h"
    assert len(item.assets) == 2
    assert item.bbox == [-180.0, -90.0, 180.0, 90.0]
    assert item.properties["ecmwf:stream"] == "wave"
    assert item.properties["ecmwf:type"] == "fc"
    assert item.properties["ecmwf:forecast_datetime"] == "2023-10-19T00:00:00Z"
    assert item.properties[
        "ecmwf:reference_datetime"] == "2023-10-19T00:00:00Z"
    assert item.properties["ecmwf:step"] == "0h"
    assert item.properties["kerchunk_indices"] == {
        'refs': {
            'step/0':
            'base64:AAAAAAAAAAA=',
            'time/0':
            'base64:gHEwZQAAAAA=',
            '.zattrs':
            '{"GRIB_centre":"ecmf","GRIB_centreDescription":"European Centre for Medium-Range Weather Forecasts","GRIB_edition":2,"GRIB_subCentre":0,"coordinates":"meanSea latitude longitude step time valid_time","institution":"European Centre for Medium-Range Weather Forecasts"}',
            '.zgroup':
            '{"zarr_format":2}',
            'meanSea/0':
            'base64:AAAAAAAAAAA=',
            'mp2/0.0.0': [
                'https://ai4edataeuwest.blob.core.windows.net/ecmwf/20231019/00z/0p4-beta/wave/20231019000000-0h-wave-fc.grib2',
                1333081, 354874
            ],
            'mwd/0.0.0': [
                'https://ai4edataeuwest.blob.core.windows.net/ecmwf/20231019/00z/0p4-beta/wave/20231019000000-0h-wave-fc.grib2',
                322850, 342261
            ],
            'mwp/0.0.0': [
                'https://ai4edataeuwest.blob.core.windows.net/ecmwf/20231019/00z/0p4-beta/wave/20231019000000-0h-wave-fc.grib2',
                665111, 327350
            ],
            'swh/0.0.0': [
                'https://ai4edataeuwest.blob.core.windows.net/ecmwf/20231019/00z/0p4-beta/wave/20231019000000-0h-wave-fc.grib2',
                0, 322850
            ],
            'latitude/0':
            'base64:AAAAAACAVkCamZmZmZlWwJqZmZmZmdm/',
            'pp1d/0.0.0': [
                'https://ai4edataeuwest.blob.core.windows.net/ecmwf/20231019/00z/0p4-beta/wave/20231019000000-0h-wave-fc.grib2',
                992461, 340620
            ],
            'longitude/0':
            'base64:AAAAAACAZsAAAAAAAIBmQJqZmZmZmdk/',
            'mp2/.zarray':
            '{"chunks":[1,451,900],"compressor":null,"dtype":"<f8","fill_value":null,"filters":[{"dtype":"float64","id":"grib","var":"mp2"}],"order":"C","shape":[1,451,900],"zarr_format":2}',
            'mp2/.zattrs':
            '{"GRIB_NV":0,"GRIB_Nx":900,"GRIB_Ny":451,"GRIB_cfName":"unknown","GRIB_cfVarName":"mp2","GRIB_dataType":"fc","GRIB_gridDefinitionDescription":"Latitude\\/longitude","GRIB_gridType":"regular_ll","GRIB_iDirectionIncrementInDegrees":0.4,"GRIB_iScansNegatively":0,"GRIB_jDirectionIncrementInDegrees":0.4,"GRIB_jPointsAreConsecutive":0,"GRIB_jScansPositively":0,"GRIB_latitudeOfFirstGridPointInDegrees":90.0,"GRIB_latitudeOfLastGridPointInDegrees":-90.0,"GRIB_longitudeOfFirstGridPointInDegrees":180.0,"GRIB_longitudeOfLastGridPointInDegrees":179.6,"GRIB_missingValue":3.4028234663852886e+38,"GRIB_name":"Mean zero-crossing wave period","GRIB_numberOfPoints":405900,"GRIB_paramId":140221,"GRIB_shortName":"mp2","GRIB_stepType":"instant","GRIB_stepUnits":1,"GRIB_typeOfLevel":"meanSea","GRIB_units":"s","_ARRAY_DIMENSIONS":["time","latitude","longitude"],"long_name":"Mean zero-crossing wave period","standard_name":"unknown","units":"s"}',
            'mwd/.zarray':
            '{"chunks":[1,451,900],"compressor":null,"dtype":"<f8","fill_value":null,"filters":[{"dtype":"float64","id":"grib","var":"mwd"}],"order":"C","shape":[1,451,900],"zarr_format":2}',
            'mwd/.zattrs':
            '{"GRIB_NV":0,"GRIB_Nx":900,"GRIB_Ny":451,"GRIB_cfName":"unknown","GRIB_cfVarName":"mwd","GRIB_dataType":"fc","GRIB_gridDefinitionDescription":"Latitude\\/longitude","GRIB_gridType":"regular_ll","GRIB_iDirectionIncrementInDegrees":0.4,"GRIB_iScansNegatively":0,"GRIB_jDirectionIncrementInDegrees":0.4,"GRIB_jPointsAreConsecutive":0,"GRIB_jScansPositively":0,"GRIB_latitudeOfFirstGridPointInDegrees":90.0,"GRIB_latitudeOfLastGridPointInDegrees":-90.0,"GRIB_longitudeOfFirstGridPointInDegrees":180.0,"GRIB_longitudeOfLastGridPointInDegrees":179.6,"GRIB_missingValue":3.4028234663852886e+38,"GRIB_name":"Mean wave direction","GRIB_numberOfPoints":405900,"GRIB_paramId":140230,"GRIB_shortName":"mwd","GRIB_stepType":"instant","GRIB_stepUnits":1,"GRIB_typeOfLevel":"meanSea","GRIB_units":"Degree true","_ARRAY_DIMENSIONS":["time","latitude","longitude"],"long_name":"Mean wave direction","standard_name":"unknown","units":"Degree true"}',
            'mwp/.zarray':
            '{"chunks":[1,451,900],"compressor":null,"dtype":"<f8","fill_value":null,"filters":[{"dtype":"float64","id":"grib","var":"mwp"}],"order":"C","shape":[1,451,900],"zarr_format":2}',
            'mwp/.zattrs':
            '{"GRIB_NV":0,"GRIB_Nx":900,"GRIB_Ny":451,"GRIB_cfName":"unknown","GRIB_cfVarName":"mwp","GRIB_dataType":"fc","GRIB_gridDefinitionDescription":"Latitude\\/longitude","GRIB_gridType":"regular_ll","GRIB_iDirectionIncrementInDegrees":0.4,"GRIB_iScansNegatively":0,"GRIB_jDirectionIncrementInDegrees":0.4,"GRIB_jPointsAreConsecutive":0,"GRIB_jScansPositively":0,"GRIB_latitudeOfFirstGridPointInDegrees":90.0,"GRIB_latitudeOfLastGridPointInDegrees":-90.0,"GRIB_longitudeOfFirstGridPointInDegrees":180.0,"GRIB_longitudeOfLastGridPointInDegrees":179.6,"GRIB_missingValue":3.4028234663852886e+38,"GRIB_name":"Mean wave period","GRIB_numberOfPoints":405900,"GRIB_paramId":140232,"GRIB_shortName":"mwp","GRIB_stepType":"instant","GRIB_stepUnits":1,"GRIB_typeOfLevel":"meanSea","GRIB_units":"s","_ARRAY_DIMENSIONS":["time","latitude","longitude"],"long_name":"Mean wave period","standard_name":"unknown","units":"s"}',
            'swh/.zarray':
            '{"chunks":[1,451,900],"compressor":null,"dtype":"<f8","fill_value":null,"filters":[{"dtype":"float64","id":"grib","var":"swh"}],"order":"C","shape":[1,451,900],"zarr_format":2}',
            'swh/.zattrs':
            '{"GRIB_NV":0,"GRIB_Nx":900,"GRIB_Ny":451,"GRIB_cfName":"unknown","GRIB_cfVarName":"swh","GRIB_dataType":"fc","GRIB_gridDefinitionDescription":"Latitude\\/longitude","GRIB_gridType":"regular_ll","GRIB_iDirectionIncrementInDegrees":0.4,"GRIB_iScansNegatively":0,"GRIB_jDirectionIncrementInDegrees":0.4,"GRIB_jPointsAreConsecutive":0,"GRIB_jScansPositively":0,"GRIB_latitudeOfFirstGridPointInDegrees":90.0,"GRIB_latitudeOfLastGridPointInDegrees":-90.0,"GRIB_longitudeOfFirstGridPointInDegrees":180.0,"GRIB_longitudeOfLastGridPointInDegrees":179.6,"GRIB_missingValue":3.4028234663852886e+38,"GRIB_name":"Significant height of combined wind waves and swell","GRIB_numberOfPoints":405900,"GRIB_paramId":140229,"GRIB_shortName":"swh","GRIB_stepType":"instant","GRIB_stepUnits":1,"GRIB_typeOfLevel":"meanSea","GRIB_units":"m","_ARRAY_DIMENSIONS":["time","latitude","longitude"],"long_name":"Significant height of combined wind waves and swell","standard_name":"unknown","units":"m"}',
            'pp1d/.zarray':
            '{"chunks":[1,451,900],"compressor":null,"dtype":"<f8","fill_value":null,"filters":[{"dtype":"float64","id":"grib","var":"pp1d"}],"order":"C","shape":[1,451,900],"zarr_format":2}',
            'pp1d/.zattrs':
            '{"GRIB_NV":0,"GRIB_Nx":900,"GRIB_Ny":451,"GRIB_cfName":"unknown","GRIB_cfVarName":"pp1d","GRIB_dataType":"fc","GRIB_gridDefinitionDescription":"Latitude\\/longitude","GRIB_gridType":"regular_ll","GRIB_iDirectionIncrementInDegrees":0.4,"GRIB_iScansNegatively":0,"GRIB_jDirectionIncrementInDegrees":0.4,"GRIB_jPointsAreConsecutive":0,"GRIB_jScansPositively":0,"GRIB_latitudeOfFirstGridPointInDegrees":90.0,"GRIB_latitudeOfLastGridPointInDegrees":-90.0,"GRIB_longitudeOfFirstGridPointInDegrees":180.0,"GRIB_longitudeOfLastGridPointInDegrees":179.6,"GRIB_missingValue":3.4028234663852886e+38,"GRIB_name":"Peak wave period","GRIB_numberOfPoints":405900,"GRIB_paramId":140231,"GRIB_shortName":"pp1d","GRIB_stepType":"instant","GRIB_stepUnits":1,"GRIB_typeOfLevel":"meanSea","GRIB_units":"s","_ARRAY_DIMENSIONS":["time","latitude","longitude"],"long_name":"Peak wave period","standard_name":"unknown","units":"s"}',
            'step/.zarray':
            '{"chunks":[1],"compressor":null,"dtype":"<f8","fill_value":null,"filters":null,"order":"C","shape":[1],"zarr_format":2}',
            'step/.zattrs':
            '{"_ARRAY_DIMENSIONS":["time"],"long_name":"time since forecast_reference_time","standard_name":"forecast_period","units":"hours"}',
            'time/.zarray':
            'base64:ewogICAgImNodW5rcyI6IFsKICAgICAgICAxCiAgICBdLAogICAgImNvbXByZXNzb3IiOiBudWxsLAogICAgImR0eXBlIjogIjxpOCIsCiAgICAiZmlsbF92YWx1ZSI6IG51bGwsCiAgICAiZmlsdGVycyI6IG51bGwsCiAgICAib3JkZXIiOiAiQyIsCiAgICAic2hhcGUiOiBbCiAgICAgICAgMQogICAgXSwKICAgICJ6YXJyX2Zvcm1hdCI6IDIKfQ==',
            'time/.zattrs':
            'base64:ewogICAgIl9BUlJBWV9ESU1FTlNJT05TIjogWwogICAgICAgICJ0aW1lIgogICAgXSwKICAgICJjYWxlbmRhciI6ICJwcm9sZXB0aWNfZ3JlZ29yaWFuIiwKICAgICJsb25nX25hbWUiOiAiaW5pdGlhbCB0aW1lIG9mIGZvcmVjYXN0IiwKICAgICJzdGFuZGFyZF9uYW1lIjogImZvcmVjYXN0X3JlZmVyZW5jZV90aW1lIiwKICAgICJ1bml0cyI6ICJzZWNvbmRzIHNpbmNlIDE5NzAtMDEtMDFUMDA6MDA6MDAiCn0=',
            'valid_time/0':
            'base64:gHEwZQAAAAA=',
            'meanSea/.zarray':
            '{"chunks":[1],"compressor":null,"dtype":"<f8","fill_value":null,"filters":null,"order":"C","shape":[1],"zarr_format":2}',
            'meanSea/.zattrs':
            '{"_ARRAY_DIMENSIONS":["time"]}',
            'latitude/.zarray':
            '{"chunks":[451],"compressor":null,"dtype":"<f8","fill_value":null,"filters":[{"id": "range"}],"order":"C","shape":[451],"zarr_format":2}',
            'latitude/.zattrs':
            '{"_ARRAY_DIMENSIONS":["latitude"],"long_name":"latitude","standard_name":"latitude","units":"degrees_north"}',
            'longitude/.zarray':
            '{"chunks":[900],"compressor":null,"dtype":"<f8","fill_value":null,"filters":[{"id": "range"}],"order":"C","shape":[900],"zarr_format":2}',
            'longitude/.zattrs':
            '{"_ARRAY_DIMENSIONS":["longitude"],"long_name":"longitude","standard_name":"longitude","units":"degrees_east"}',
            'valid_time/.zarray':
            '{"chunks":[1],"compressor":null,"dtype":"<i8","fill_value":null,"filters":null,"order":"C","shape":[1],"zarr_format":2}',
            'valid_time/.zattrs':
            '{"_ARRAY_DIMENSIONS":["time"],"calendar":"proleptic_gregorian","long_name":"time","standard_name":"time","units":"seconds since 1970-01-01T00:00:00"}'
        },
        'version': 1
    }


@pytest.mark.parametrize(
    "filename",
    [
        "20231019000000-0h-wave-fc.grib2",
        "20231019/00z/0p4-beta/wave/20231019000000-0h-wave-fc.grib2",
        ("https://ai4edataeuwest.blob.core.windows.net/ecmwf/20231019/00z/"
         "0p4-beta/wave/20231019000000-0h-wave-fc.grib2"),
    ],
)
def test_parts(filename):
    result = stac.Parts.from_filename(filename)
    assert result.reference_datetime == datetime.datetime(2023, 10, 19)
    assert result.stream == "wave"
    assert result.step == "0h"
    assert result.type == "fc"
    assert result.format == "grib2"
    assert result.filename == filename
    assert result.name == "20231019000000-0h-wave-fc.grib2"
    assert result.item_id == "ecmwf-2023-10-19T00-wave-fc"
    assert result.asset_id == "0h-grib2"
    if not filename.startswith("20231019000000-0h"):
        assert result.filename != result.name
        assert result.prefix == filename.rsplit("/", 1)[0] + "/"


@pytest.mark.parametrize(
    "filename",
    [
        "20231019000000-0h-wave-fc.grib2",
        "20231019/00z/0p4-beta/wave/20231019000000-0h-wave-fc.grib2",
        ("https://ai4edataeuwest.blob.core.windows.net/ecmwf/20231019/00z/"
         "0p4-beta/wave/20231019000000-0h-wave-fc.grib2"),
    ],
)
def test_list_sibling_assets(filename):
    siblings = stac.list_sibling_assets(filename)
    # include both index and grib2
    assert len(siblings) % 2 == 0
    # matches the prefix
    me = siblings[0]
    for item in siblings[2:]:
        assert item.item_id == me.item_id
        assert item.reference_datetime == me.reference_datetime
        assert item.stream == me.stream
        assert item.type == me.type
        assert item.step != me.step


def test_split_by_parts():
    files = [
        "ecmwf/20231019/00z/0p4-beta/wave/20231019000000-0h-wave-fc.grib2",
        "ecmwf/20231019/00z/0p4-beta/wave/20231019000000-0h-wave-fc.index",
        "ecmwf/20231019/00z/0p4-beta/wave/20231019000000-3h-wave-fc.grib2",
        "ecmwf/20231019/00z/0p4-beta/wave/20231019000000-3h-wave-fc.index",
    ]

    stac.create_item(files)

    with pytest.raises(ValueError, match="different Item ID"):
        stac.create_item(files, split_by_step=True)

    i0, i1 = stac.create_item(files[:2], split_by_step=True), stac.create_item(
        files[2:], split_by_step=True)
    assert i0.properties["ecmwf:step"] == "0h"
    assert i1.properties["ecmwf:step"] == "3h"
    assert i0.assets["data"].extra_fields == {}
    assert i1.datetime == datetime.datetime(2023, 10, 19, 3)
    assert i1.id.endswith("3h")


def test_item_assets():
    collection = stac.create_collection()
    assert collection.extra_fields["item_assets"]["data"]["roles"] == ["data"]
    assert (collection.extra_fields["item_assets"]["data"]["type"] ==
            "application/wmo-GRIB2")
    assert collection.extra_fields["item_assets"]["index"]["roles"] == [
        "index"
    ]
    assert (collection.extra_fields["item_assets"]["index"]["type"] ==
            "application/x-ndjson")

    # assert collection.extra_fields["item_assets"]["index"] == {
    #     "roles": ["index"],
    #     "type": "application/x-ndjson",
    # }

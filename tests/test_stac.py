import datetime

import pytest

from stactools.ecmwf_forecast import stac
import json
import os
import urllib.request

blob_file = ("https://ai4edataeuwest.blob.core.windows.net/ecmwf/20231019/00z/"
         "0p4-beta/wave/20231019000000-0h-wave-fc.grib2")

local_files = ["20231019000000-0h-wave-fc.grib2",
               "20231019/00z/0p4-beta/wave/20231019000000-0h-wave-fc.grib2"]
for i in range(len(local_files)):
    if not os.path.exists(local_files[i]):
        if i==1:
            os.makedirs(local_files[i].split('.')[0], exist_ok=True)
        urllib.request.urlretrieve(blob_file, local_files[i])


def test_create_collection():
    # Write tests for each for the creation of a STAC Collection
    # Create the STAC Collection...
    collection = stac.create_collection()
    collection.set_self_href("")

    # Check that it has some required attributes
    assert collection.id == "ecmwf-forecast"

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
        
    assert item.id == "ecmwf-2023-10-19T00-wave-fc"
    assert len(item.assets) == 130
    assert item.bbox == [-180.0, -90.0, 180.0, 90.0]
    assert item.properties["ecmwf:stream"] == "wave"
    assert item.properties["ecmwf:type"] == "fc"
    assert item.properties["ecmwf:forecast_datetime"] == "2023-10-19T00:00:00Z"
    assert item.properties[
        "ecmwf:reference_datetime"] == "2023-10-19T00:00:00Z"
    if filename.startswith("https://ai4edataeuwest.blob.core.windows.net/"):
        with open("tests/blob_kerchunk_indices.json") as jsonfile:
            kerchunk_indices = json.load(jsonfile)
        assert item.properties["kerchunk:indices"] == kerchunk_indices
            
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

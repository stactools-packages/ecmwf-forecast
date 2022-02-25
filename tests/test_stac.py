import datetime

import pytest

from stactools.ecmwf_forecast import stac


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
        "20220202000000-0h-enfo-ef.grib2",
        "20220202/00z/0p4-beta/enfo/20220202000000-0h-enfo-ef.grib2",
        (
            "https://ai4edataeuwest.blob.core.windows.net/ecmwf/20220202/00z/"
            "0p4-beta/enfo/20220202000000-0h-enfo-ef.grib2"
        ),
    ],
)
def test_create_items(filename):
    item = stac.create_item_from_representative_asset(filename)
    assert item.id == "ecmwf-2022-02-02T00-enfo-ef"
    assert len(item.assets) == 170
    assert item.bbox == [-180.0, -90.0, 180.0, 90.0]
    assert item.properties["ecmwf:stream"] == "enfo"
    assert item.properties["ecmwf:type"] == "ef"
    assert item.properties["start_datetime"] == "2022-02-02T00:00:00Z"
    assert item.properties["end_datetime"] == "2022-02-17T00:00:00Z"


@pytest.mark.parametrize(
    "filename",
    [
        "20220202000000-0h-enfo-ef.grib2",
        "20220202/00z/0p4-beta/enfo/20220202000000-0h-enfo-ef.grib2",
        (
            "https://ai4edataeuwest.blob.core.windows.net/ecmwf/20220202/00z/"
            "0p4-beta/enfo/20220202000000-0h-enfo-ef.grib2"
        ),
    ],
)
def test_parts(filename):
    result = stac.Parts.from_filename(filename)
    assert result.reference_datetime == datetime.datetime(2022, 2, 2)
    assert result.stream == "enfo"
    assert result.step == "0h"
    assert result.type == "ef"
    assert result.format == "grib2"
    assert result.filename == filename
    assert result.name == "20220202000000-0h-enfo-ef.grib2"
    assert result.item_id == "ecmwf-2022-02-02T00-enfo-ef"
    assert result.asset_id == "0h-grib2"
    if not filename.startswith("20220202000000-0h"):
        assert result.filename != result.name
        assert result.prefix == filename.rsplit("/", 1)[0] + "/"


@pytest.mark.parametrize(
    "filename",
    [
        "20220202000000-0h-enfo-ef.grib2",
        "20220202/00z/0p4-beta/enfo/20220202000000-0h-enfo-ef.grib2",
        (
            "https://ai4edataeuwest.blob.core.windows.net/ecmwf/20220202/00z/"
            "0p4-beta/enfo/20220202000000-0h-enfo-ef.grib2"
        ),
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
        "ecmwf/20220222/00z/0p4-beta/enfo/20220222000000-0h-enfo-ef.grib2",
        "ecmwf/20220222/00z/0p4-beta/enfo/20220222000000-0h-enfo-ef.index",
        "ecmwf/20220222/00z/0p4-beta/enfo/20220222000000-3h-enfo-ef.grib2",
        "ecmwf/20220222/00z/0p4-beta/enfo/20220222000000-3h-enfo-ef.index",
    ]

    stac.create_item(files)

    with pytest.raises(ValueError, match="different Item ID"):
        stac.create_item(files, split_by_step=True)

    i0, i1 = stac.create_item(files[:2], split_by_step=True), stac.create_item(
        files[2:], split_by_step=True
    )
    assert i0.properties["ecmwf:step"] == "0h"
    assert i1.properties["ecmwf:step"] == "3h"
    assert i0.assets["data"].extra_fields == {}
    assert i1.datetime == datetime.datetime(2022, 2, 22, 3)
    assert i1.id.endswith("3h")


def test_item_assets():
    collection = stac.create_collection()
    assert collection.extra_fields["item_assets"]["data"] == {
        "roles": ["data"],
        "type": "application/wmo-GRIB2",
    }
    assert collection.extra_fields["item_assets"]["index"] == {
        "roles": ["index"],
        "type": "application/x-ndjson",
    }

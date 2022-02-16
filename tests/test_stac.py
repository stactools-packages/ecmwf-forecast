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
        "20220202/00z/0p4-beta/enfo/20220202000000-0h-enfo-ef.grib2",
        "20220202000000-0h-enfo-ef.grib2",
    ],
)
def test_parts(filename):
    result = stac.Parts.from_filename(filename)
    assert result.reference_datetime == datetime.datetime(2022, 2, 2)
    assert result.stream == "enfo"
    assert result.step == "0h"
    assert result.type == "ef"
    assert result.format == "grib2"
    assert result.filename == "20220202000000-0h-enfo-ef.grib2"

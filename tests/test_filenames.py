import datetime

import fsspec
import pytest

from stactools.ecmwf_forecast import stac


@pytest.fixture(autouse=True)
def forbid_asset_access(monkeypatch):
    def fail(*args, **kwargs):
        pytest.fail("STAC item construction must not access asset storage")

    monkeypatch.setattr(fsspec, "open", fail)
    monkeypatch.setattr(fsspec.AbstractFileSystem, "open", fail)


@pytest.mark.parametrize("suffix", [None, "sfc", "pl"])
@pytest.mark.parametrize("format_", ["grib2", "index", "bufr"])
@pytest.mark.parametrize("split_by_step", [False, True])
@pytest.mark.parametrize(
    "prefix",
    [
        "",
        "20261021/18z/0p1/waef/",
        "https://example.com/ecmwf/20261021/18z/0p1/waef/",
    ],
)
def test_parts_filename_variants(suffix, format_, split_by_step, prefix):
    qualifier = f"-{suffix}" if suffix else ""
    name = f"20261021180000-0h-waef-ef{qualifier}.{format_}"
    filename = prefix + name

    parts = stac.Parts.from_filename(
        filename, split_by_step=split_by_step, resolution="0.10"
    )

    assert parts.reference_datetime == datetime.datetime(2026, 10, 21, 18)
    assert parts.stream == "waef"
    assert parts.type == "ef"
    assert parts.suffix == suffix
    assert parts.step == "0h"
    assert parts.format == format_
    assert parts.filename == filename
    assert parts.name == name
    assert parts.prefix == (prefix or None)
    step = "-0h" if split_by_step else ""
    assert parts.item_id == f"ecmwf-2026-10-21T18-waef-ef{qualifier}{step}-0.10"
    if split_by_step:
        assert parts.asset_id == ("index" if format_ == "index" else "data")
    else:
        assert parts.asset_id == f"0h{qualifier}-{format_}"


@pytest.mark.parametrize(
    "filename",
    [
        "20261021180000-0h-waef-ef-grib2",
        "20261021180000-0h-waef-ef_sfc-grib2",
        "20261021180000-0h-waef-ef-sfc-grib2",
        "20261021180000-0h-waef-ef+sfc.grib2",
        "20261021180000-0h-waef-ef-.grib2",
        "20261021180000-0h-waef-ef-sfc-extra.grib2",
        "20261021180000-0|-waef-ef.grib2",
        "prefix-20261021180000-0h-waef-ef.grib2",
        "20261021180000-0h-waef-ef.grib2.extra",
        "20261021180000-0h-waef-ef-sfc.grib2.extra",
        "20261021180000-0h-waef-ef-sfc.grib2-extra",
        "20261021180000-0h-waef-ef-sfc.grib2?download=1",
        "20261021180000-0h-waef-ef-sfc.grib2\n",
    ],
)
def test_parts_rejects_incomplete_filename_matches(filename):
    with pytest.raises(ValueError):
        stac.Parts.from_filename(filename)


@pytest.mark.parametrize("suffix", [None, "sfc", "pl"])
@pytest.mark.parametrize("stream, type_", [("waef", "ef"), ("wave", "fc")])
@pytest.mark.parametrize("split_by_step", [False, True])
@pytest.mark.parametrize("resolution", [None, "0.25", "0.10"])
def test_create_item_filename_variants(
    suffix, stream, type_, split_by_step, resolution
):
    qualifier = f"-{suffix}" if suffix else ""
    steps = ["3h"] if split_by_step else ["0h", "3h"]
    filenames = [
        f"20261021180000-{step}-{stream}-{type_}{qualifier}.{format_}"
        for step in steps
        for format_ in ["grib2", "index"]
    ]

    item = stac.create_item(
        filenames, split_by_step=split_by_step, resolution=resolution
    )

    step_id = "-3h" if split_by_step else ""
    resolution_id = f"-{resolution}" if resolution else ""
    assert item.id == (
        f"ecmwf-2026-10-21T18-{stream}-{type_}{qualifier}{step_id}{resolution_id}"
    )
    assert item.properties["ecmwf:type"] == type_
    assert item.properties["ecmwf:stream"] == stream
    assert item.properties["ecmwf:resolution"] == resolution
    assert item.stac_extensions == [
        "https://stac-extensions.github.io/forecast/v0.2.0/schema.json"
    ]
    assert (
        item.properties["forecast:reference_datetime"]
        == (item.properties["ecmwf:reference_datetime"])
        == "2026-10-21T18:00:00Z"
    )
    if suffix:
        assert item.properties["ecmwf:suffix"] == suffix
    else:
        assert "ecmwf:suffix" not in item.properties
    if split_by_step:
        assert set(item.assets) == {"data", "index"}
        assert item.properties["ecmwf:step"] == "3h"
        assert item.properties["forecast:horizon"] == "PT3H"
        assert item.datetime == datetime.datetime(2026, 10, 21, 21)
    else:
        assert "forecast:horizon" not in item.properties
        assert set(item.assets) == {
            f"{step}{qualifier}-{format_}"
            for step in steps
            for format_ in ["grib2", "index"]
        }
        assert item.properties["start_datetime"] == "2026-10-21T18:00:00Z"
        assert item.properties["end_datetime"] == "2026-10-21T21:00:00Z"
    assert len(item.assets) == len(filenames)
    assert {asset.href for asset in item.assets.values()} == set(filenames)
    for asset in item.assets.values():
        step = asset.href.split("-")[1]
        valid_datetime = datetime.datetime(2026, 10, 21, 18) + datetime.timedelta(
            hours=int(step[:-1])
        )
        assert asset.extra_fields == (
            {}
            if split_by_step
            else {
                "ecmwf:step": step,
                "forecast:horizon": f"PT{step[:-1]}H",
                "datetime": valid_datetime.isoformat() + "Z",
            }
        )
        if asset.href.endswith(".grib2"):
            assert asset.media_type == stac.GRIB2_MEDIA_TYPE
            assert asset.roles == ["data"]
        else:
            assert asset.media_type == stac.NDJSON_MEDIA_TYPE
            assert asset.roles == ["index"]


@pytest.mark.parametrize("split_by_step", [False, True])
@pytest.mark.parametrize(
    "step, hours, horizon",
    [
        ("0h", 0, "PT0H"),
        ("3h", 3, "PT3H"),
        ("120h", 120, "PT120H"),
        ("003h", 3, "PT3H"),
    ],
)
def test_forecast_times(step, hours, horizon, split_by_step):
    reference = datetime.datetime(2026, 10, 21, 18)
    valid_datetime = reference + datetime.timedelta(hours=hours)
    filenames = [
        f"20261021180000-{step}-waef-ef-sfc.{extension}"
        for extension in ["grib2", "index"]
    ]
    item = stac.create_item(filenames, split_by_step=split_by_step)

    assert (
        item.properties["forecast:reference_datetime"]
        == (item.properties["ecmwf:reference_datetime"])
        == "2026-10-21T18:00:00Z"
    )
    assert item.properties["ecmwf:forecast_datetime"] == (
        valid_datetime.isoformat() + "Z"
    )
    if split_by_step:
        assert item.properties["forecast:horizon"] == horizon
        assert item.properties["ecmwf:step"] == step
        assert item.datetime == valid_datetime
    else:
        assert "forecast:horizon" not in item.properties
        for asset in item.assets.values():
            assert asset.extra_fields["forecast:horizon"] == horizon
            assert asset.extra_fields["ecmwf:step"] == step
            assert asset.extra_fields["datetime"] == valid_datetime.isoformat() + "Z"


@pytest.mark.parametrize("split_by_step", [False, True])
def test_suffix_variants_have_distinct_identities(split_by_step):
    variants = [
        stac.Parts.from_filename(
            f"20261021180000-0h-waef-ef{qualifier}.grib2",
            split_by_step=split_by_step,
        )
        for qualifier in ["", "-sfc", "-pl"]
    ]
    assert len({part.item_id for part in variants}) == 3
    assert len({(part.item_id, part.asset_id) for part in variants}) == 3
    if not split_by_step:
        assert len({part.asset_id for part in variants}) == 3


@pytest.mark.parametrize("qualifiers", [("", "-sfc"), ("-sfc", "-pl")])
@pytest.mark.parametrize("split_by_step", [False, True])
def test_create_item_rejects_mixed_suffixes(qualifiers, split_by_step):
    filenames = [
        f"20261021180000-0h-waef-ef{qualifier}.grib2" for qualifier in qualifiers
    ]
    with pytest.raises(ValueError, match="different Item ID"):
        stac.create_item(filenames, split_by_step=split_by_step)


@pytest.mark.parametrize(
    "key, expected_groups",
    [(stac.item_key, 3), (stac.item_key_split_by_parts, 6)],
)
@pytest.mark.parametrize("stream, type_", [("waef", "ef"), ("wave", "fc")])
def test_group_assets_separates_suffix_variants(key, expected_groups, stream, type_):
    filenames = [
        f"20261021180000-{step}-{stream}-{type_}{qualifier}.{format_}"
        for step in ["3h", "0h"]
        for qualifier in ["-sfc", "", "-pl"]
        for format_ in ["grib2", "index"]
    ]
    groups = [
        (group_key, list(hrefs))
        for group_key, hrefs in stac.group_assets(filenames, key=key)
    ]
    assert len(groups) == expected_groups
    assert sum(len(hrefs) for _, hrefs in groups) == len(filenames)
    for group_key, hrefs in groups:
        assert {key(href) for href in hrefs} == {group_key}
        assert len({stac.Parts.from_filename(href).suffix for href in hrefs}) == 1
        item = stac.create_item(
            hrefs, split_by_step=(key is stac.item_key_split_by_parts)
        )
        assert len(item.assets) == len(hrefs)


@pytest.mark.parametrize("suffix", [None, "sfc", "pl"])
@pytest.mark.parametrize(
    "stream, type_, reference_datetime, expected_assets",
    [
        ("waef", "ef", "20261021180000", 98),
        ("wave", "fc", "20261021120000", 130),
    ],
)
@pytest.mark.parametrize("url_prefix", ["", "https://example.com/ecmwf/"])
def test_sibling_assets_preserve_suffix(
    suffix, stream, type_, reference_datetime, expected_assets, url_prefix
):
    prefix = (
        f"{url_prefix}20261021/{reference_datetime[8:10]}z/0p1/{stream}/"
        if url_prefix
        else ""
    )
    qualifier = f"-{suffix}" if suffix else ""
    filename = f"{prefix}{reference_datetime}-0h-{stream}-{type_}{qualifier}.grib2"
    representative = stac.Parts.from_filename(filename)

    siblings = stac.list_sibling_assets(filename)

    assert len(siblings) == expected_assets
    assert filename in {part.filename for part in siblings}
    assert {part.suffix for part in siblings} == {suffix}
    assert {part.item_id for part in siblings} == {representative.item_id}
    assert {part.format for part in siblings} == {"grib2", "index"}
    assert {part.prefix for part in siblings} == {prefix or None}
    assert len({part.asset_id for part in siblings}) == len(siblings)
    assert all(
        part.filename.endswith(f"-{type_}{qualifier}.{part.format}")
        for part in siblings
    )

    item = stac.create_item_from_representative_asset(filename)
    assert item.id == representative.item_id
    assert len(item.assets) == len(siblings)
    assert {asset.href for asset in item.assets.values()} == {
        part.filename for part in siblings
    }
    assert all(
        "kerchunk:indices" not in asset.extra_fields for asset in item.assets.values()
    )
    assert item.properties["forecast:reference_datetime"] == (
        item.properties["ecmwf:reference_datetime"]
    )
    for part in siblings:
        asset = item.assets[part.asset_id]
        assert asset.extra_fields["forecast:horizon"] == f"PT{part.step[:-1]}H"
        assert (
            asset.extra_fields["datetime"] == part.forecast_datetime.isoformat() + "Z"
        )

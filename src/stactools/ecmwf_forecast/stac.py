from __future__ import annotations

import dataclasses
import operator
import datetime
import itertools
import logging
import pathlib
import re
import ujson
from typing import Any

import pystac
from pystac import (
    CatalogType,
    Collection,
    Extent,
    Item,
    Provider,
    ProviderRole,
    SpatialExtent,
    TemporalExtent,
)
from . import constants

from kerchunk.combine import MultiZarrToZarr
from kerchunk.grib2 import scan_grib
import base64
import fsspec
import numpy as np

logger = logging.getLogger(__name__)


xpr = re.compile(
    r"(?P<reference_datetime>\d{10})0000-"
    r"(?P<step>\d+[h|m])-"
    r"(?P<stream>\w+)-"
    r"(?P<type>\w+)."
    r"(?P<format>\w+)"
)
NDJSON_MEDIA_TYPE = "application/x-ndjson"
GRIB2_MEDIA_TYPE = "application/wmo-GRIB2"

@dataclasses.dataclass
class Parts:
    reference_datetime: datetime.datetime
    stream: str
    step: str
    type: str
    format: str
    filename: str
    split_by_step: bool = False

    @property
    def datetime(self):
        if self.split_by_step:
            return self.forecast_datetime
        else:
            return self.reference_datetime

    @classmethod
    def from_filename(cls, filename: str, split_by_step=False) -> "Parts":
        name = pathlib.Path(filename).name
        m = xpr.match(name)
        if not m:
            raise ValueError(name)
        d = m.groupdict()
        d["filename"] = filename
        d["reference_datetime"] = datetime.datetime.strptime(
            d["reference_datetime"], "%Y%m%d%H"
        )  # type: ignore
        #  error: Argument 1 to "Parts" has incompatible type
        # "**Dict[str, Union[str, Any]]"; expected "datetime"
        return cls(**d, split_by_step=split_by_step)  # type: ignore

    @property
    def item_id(self) -> str:
        parts = [
            "ecmwf",
            self.reference_datetime.isoformat(timespec="hours"),
            self.stream,
            self.type,
        ]
        if self.split_by_step:
            parts.append(self.step)
        return "-".join(parts)

    @property
    def asset_id(self) -> str:
        if self.split_by_step:
            return "data" if self.format != "index" else "index"
        else:
            return f"{self.step}-{self.format}"

    # mypy complains about  error: Name "datetime.timedelta" is not defined
    # for offset and forecast_datetime
    @property
    def offset(self):
        v, u = self.step[:-1], self.step[-1]
        offset_value = int(v)

        if u == "h":
            offset = datetime.timedelta(hours=offset_value)
        else:
            # TODO: this is wrong. Need to something like a DateOffset
            raise NotImplementedError()

        return offset

    @property
    def forecast_datetime(self):
        return self.reference_datetime + self.offset

    @property
    def prefix(self) -> str | None:
        if self.filename.count("/"):
            prefix = self.filename.rsplit("/", 1)[0]
            return prefix + "/"
        return None

    @property
    def name(self):
        return pathlib.Path(self.filename).name


def create_collection(
    thumbnail=None, extra_fields: dict[str, Any] | None = None
) -> Collection:
    """Create a STAC Collection

    This function includes logic to extract all relevant metadata from
    an asset describing the STAC collection and/or metadata coded into an
    accompanying constants.py file.

    See `Collection<https://pystac.readthedocs.io/en/latest/api.html#collection>`_.

    Returns:
        Collection: STAC Collection object
    """
    providers = [
        Provider(
            name="ECMWF",
            roles=[ProviderRole.PRODUCER],
            url="https://www.ecmwf.int/",
        )
    ]
    links = [
        pystac.Link(
            rel=pystac.RelType.LICENSE,
            target="https://creativecommons.org/licenses/by/4.0/",
            media_type="text/html",
            title="CC-BY-4.0 license",
        ),
        pystac.Link(
            rel="documentation",
            target="https://confluence.ecmwf.int/display/UDOC/ECMWF+Open+Data+-+Real+Time",
            media_type="text/html",
            title="ECMWF Open Data (Real Time) documentation",
        ),
    ]

    extent = Extent(
        SpatialExtent([[-180.0, -90.0, 180.0, 90.0]]),
        TemporalExtent([[None, None]]),  # type: ignore
    )
    keywords = [
        "ECMWF",
        "forecast",
        "weather",
    ]

    collection = Collection(
        id="ecmwf-forecast",
        title="ECMWF Open Data (real-time)",
        description="{{ collection.description }}",
        license="CC-BY-4.0",
        providers=providers,
        extent=extent,
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
        keywords=keywords,
    )
    collection.add_links(links)

    # Summaries
    collection.summaries.maxcount = 50
    summaries: dict[str, list[Any]] = {
        "ecmwf:reference_times": constants.REFERENCE_TIMES,
        "ecmwf:streams": constants.STREAMS,
        "ecmwf:steps": constants.STEPS,
        "ecmwf:types": constants.TYPES,
        "ecmwf:pressure_levels": constants.PRESSURE_LEVELS,
    }
    for k, v in summaries.items():
        collection.summaries.add(k, v)

    if thumbnail is not None:
        # TODO: guess media type?
        collection.add_asset(
            "thumbnail",
            pystac.Asset(
                thumbnail,
                title="thumbnail",
                roles=[thumbnail],
                media_type=pystac.MediaType.PNG,
            ),
        )

    if extra_fields:
        collection.extra_fields.update(extra_fields)

    item_assets = {
        "data": pystac.extensions.item_assets.AssetDefinition(
            {
                "type": GRIB2_MEDIA_TYPE,
                "roles": ["data"],
                "title": "GRIB2 data file",
                "description": (
                    "The forecast data, as a grib2 file. Subsets of the data can be loaded "
                    "using information from the associated index file."
                ),
            }
        ),
        "index": pystac.extensions.item_assets.AssetDefinition(
            {
                "type": NDJSON_MEDIA_TYPE,
                "roles": ["index"],
                "title": "Index file",
                "description": (
                    "The index file contains information on each message within "
                    "the GRIB2 file."
                ),
            }
        ),
    }

    item_assets_ext = pystac.extensions.item_assets.ItemAssetsExtension.ext(
        collection, add_if_missing=True
    )
    item_assets_ext.item_assets = item_assets

    return collection


def item_key(filename) -> tuple[datetime.datetime, str, str]:
    """
    Gives tuple of attributes in a filename used to determine its item.

    This uses the

    * reference datetime
    * stream
    * type
    """
    parts = Parts.from_filename(filename)
    return parts.reference_datetime, parts.stream, parts.type


def item_key_split_by_parts(
    filename,
) -> tuple[datetime.datetime, str, str, datetime.timedelta]:
    """
    Gives tuple of attributes in a filename used to determine its item.

    This uses the

    * reference datetime
    * stream
    * type
    * step
    """
    parts = Parts.from_filename(filename)
    return parts.reference_datetime, parts.stream, parts.type, parts.offset


def group_assets(asset_hrefs: list[str], key=item_key):
    """
    Groups a list of asset HREFs according to which item they belong in.
    """
    asset_hrefs = sorted(asset_hrefs, key=key)
    grouped = itertools.groupby(asset_hrefs, key=key)
    return grouped


def create_item(asset_hrefs: list[str], split_by_step=False) -> Item:
    """
    Create an item for the hrefs.

    Parameters
    ----------
    asset_hrefs: list[str]
        The HREFs for the item's assets. These should all belong to the item, according
        to `item_key`. Use `group_assets` prior on a list of assets possibly belonging
        to multiple items.

    Returns
    -------
    pystac.Item
    """
    parts = [
        Parts.from_filename(href, split_by_step=split_by_step) for href in asset_hrefs
    ]
    return _create_item_from_parts(parts, split_by_step=split_by_step)


def create_item_from_representative_asset(asset_href: str) -> Item:
    """
    Create an item from a "representative" asset HREF.

    This method takes a single HREF, and uses the guidance from the ECMWF
    on which assets are published together and belong in the same item.

    Parameters
    ----------
    asset_href:
        The "representative" asset for an item. This should typically be
        the first asset for the item (e.g. the "-0h" asset for most products).

    Returns
    -------
    pystac.Item

    Examples
    --------
    >>> href = "ecmwf/20220201/00z/0p4-beta/enfo/20220201000000-0h-enfo-ef.grib2"
    >>> stac.create_item_from_representative_asset(href)
    """
    siblings = list_sibling_assets(asset_href)
    return _create_item_from_parts(siblings)


def _create_item_from_parts(parts: list[Parts], split_by_step=False) -> Item:
    part = parts[0]
    for i, other in enumerate(parts):
        if part.item_id != other.item_id:
            raise ValueError(
                f"Asset {i} has different Item ID ({part.item_id} != {other.item_id}). "
                f"URL = {part.filename}"
            )

    geometry = {
        "type": "Polygon",
        "coordinates": (
            (
                (180.0, -90.0),
                (180.0, 90.0),
                (-180.0, 90.0),
                (-180.0, -90.0),
                (180.0, -90.0),
            ),
        ),
    }
    bbox = [-180.0, -90.0, 180.0, 90.0]

    item = pystac.Item(
        part.item_id,
        geometry=geometry,
        bbox=bbox,
        datetime=part.datetime,
        properties={},
    )

    item.properties["ecmwf:stream"] = part.stream
    item.properties["ecmwf:type"] = part.type
    item.properties["ecmwf:reference_datetime"] = (
        part.reference_datetime.isoformat() + "Z"
    )
    item.properties["ecmwf:forecast_datetime"] = (
        part.forecast_datetime.isoformat() + "Z"
    )
    
    mzz = MultiZarrToZarr(scan_grib(part.filename),
                          concat_dims=['valid_time','time'],
                          identical_dims=['latitude', 'longitude', 'meanSea', 'step'])
    d = mzz.translate()
    d['refs']['latitude/0'] = 'RANGE({},{},{})'.format(*get_start_stop_inc(np.frombuffer(base64.b64decode(d['refs']['latitude/0'][7:]))))
    d['refs']['longitude/0'] = 'RANGE({},{},{})'.format(*get_start_stop_inc(np.frombuffer(base64.b64decode(d['refs']['longitude/0'][7:]))))
    item.properties["kerchunk_indices"] = d#ujson.dumps(d).encode()
    fs = fsspec.filesystem('')
    fs.clear_instance_cache()    
    
    if split_by_step:
        item.properties["ecmwf:step"] = part.step
    else:
        offset = max(p.offset for p in parts)
        item.properties["start_datetime"] = part.reference_datetime.isoformat() + "Z"
        item.properties["end_datetime"] = (
            part.reference_datetime + offset
        ).isoformat() + "Z"

    for p in parts:
        if p.format == "grib2":
            media_type = GRIB2_MEDIA_TYPE
            roles = ["data"]
        elif p.format == "index":
            media_type = NDJSON_MEDIA_TYPE
            roles = ["index"]
        elif p.format == "bufr":
            media_type = None
            roles = ["data"]
        else:
            raise ValueError(f"Bad extension: {p.format}")

        item.add_asset(
            p.asset_id,
            pystac.Asset(
                p.filename,
                media_type=media_type,
                roles=roles,
                extra_fields={"ecmwf:step": p.step} if not split_by_step else {},
            ),
        )

    return item


def _assets_key(combination):
    return combination[:4]


def list_sibling_assets(filename) -> list[Parts]:
    """
    List the other files that belong in the same item as `file` (have the same item_id).

    This is based purely on the filename. It doesn't list any directories to determine whether
    the other files are present.

    Examples
    --------
    >>> siblings = list_sibling_assets("20220202000000-0h-enfo-ef.grib2")
    """
    p = Parts.from_filename(filename)

    # mypy failing on python 3.7
    combinations = constants.get_combinations()  # type: ignore
    d = {k: list(v) for k, v in itertools.groupby(combinations, key=_assets_key)}  # type: ignore
    combos = list(d[p.format, p.type, p.reference_datetime.strftime("%H"), p.stream])
    prefix = p.prefix or ""

    other_files = [
        f"{prefix}{p.reference_datetime:%Y%m%d%H}0000-{combo.step}-{combo.stream}"
        f"-{combo.type}.{combo.format}"
        for combo in combos
    ]

    if p.format == "grib2":
        other_files.extend([file.rsplit(".", 1)[0] + ".index" for file in other_files])
    parts = [Parts.from_filename(other_file) for other_file in other_files]
    parts = sorted(parts, key=operator.attrgetter("step"))

    return parts

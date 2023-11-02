import base64

import fsspec
from kerchunk.combine import MultiZarrToZarr
from kerchunk.grib2 import scan_grib

from stactools.ecmwf_forecast.range_codec import Range


def get_kerchunk_indices(part):

    # clear instance cache, prevents memory leak
    fs = fsspec.filesystem("")
    fs.clear_instance_cache()

    out = scan_grib(part.filename)

    if ((part.stream == "scda") or (part.stream == "oper")) and (part.type == "fc"):
        messages_iso = [
            out[i]
            for i in range(len(out))
            if "isobaricInhPa/.zarray" in list(out[i]["refs"].keys())
        ]
        mzz = MultiZarrToZarr(messages_iso, concat_dims=["time", "isobaricInhPa"])
        d1 = mzz.translate()

        messages_not_iso = [
            out[i]
            for i in range(len(out))
            if "isobaricInhPa/.zarray" not in list(out[i]["refs"].keys())
        ]
        mzz = MultiZarrToZarr(
            messages_not_iso,
            identical_dims=[
                "depthBelowLandLayer",
                "entireAtmosphere",
                "heightAboveGround",
                "meanSea",
                "surface",
            ],
            concat_dims=["time"],
        )
        d2 = mzz.translate()
        mzz = MultiZarrToZarr(
            [d1, d2],
            identical_dims=[
                "depthBelowLandLayer",
                "entireAtmosphere",
                "heightAboveGround",
                "meanSea",
                "surface",
            ],
            concat_dims=["time"],
        )

    elif (part.stream == "enfo") and (part.type == "ep"):
        mzz = MultiZarrToZarr(
            out,
            identical_dims=["heightAboveGround", "isobaricInhPa", "surface", "meanSea"],
            concat_dims=["step", "time"],
        )

    elif (part.stream == "waef") and (part.type == "ef"):
        mzz = MultiZarrToZarr(out, concat_dims=["number", "time"])

    elif (part.stream == "waef") and (part.type == "ep"):
        mzz = MultiZarrToZarr(
            out, identical_dims=["meanSea"], concat_dims=["step", "time"]
        )

    elif ((part.stream == "scwv") or (part.stream == "wave")) and (part.type == "fc"):
        mzz = MultiZarrToZarr(out, concat_dims=["time"])

    #get output, filter down and only keep the unique d['refs'] items
    d = convert_base64(compress_lat_lon(mzz.translate()))
    filtered_d = {}
    wanted_keys = ['time/0',
                   'mp2/0.0.0',
                   'mwd/0.0.0',
                   'mwp/0.0.0',
                   'swh/0.0.0',
                   'pp1d/0.0.0',
                   'valid_time/0',
                   'step/0']
    filtered_d['refs'] = {k:v for k,v in d['refs'].items() if k in wanted_keys}

    return filtered_d

def convert_base64(d):
    for key in d['refs']:
        if (('/0' in key) & ('.' not in key) & ('latitude' not in key) & ('longitude' not in key)):
            if d['refs'][key][0:6]!='base64':
                d['refs'][key] = (b"base64:" + base64.b64encode(d['refs'][key].encode())).decode()

    return d


def compress_lat_lon(d):
    d["refs"]["latitude/0"] = (
        "base64:"
        + base64.b64encode(
            Range().encode(base64.b64decode(d["refs"]["latitude/0"][7:]))
        ).decode()
    )
    d["refs"]["longitude/0"] = (
        "base64:"
        + base64.b64encode(
            Range().encode(base64.b64decode(d["refs"]["longitude/0"][7:]))
        ).decode()
    )
    d["refs"]["latitude/.zarray"] = ",".join(
        [
            ":".join([i.split(":")[0], '[{"id": "range"}]']) if "filter" in i else i
            for i in d["refs"]["latitude/.zarray"].split(",")
        ]
    )
    d["refs"]["longitude/.zarray"] = ",".join(
        [
            ":".join([i.split(":")[0], '[{"id": "range"}]']) if "filter" in i else i
            for i in d["refs"]["longitude/.zarray"].split(",")
        ]
    )

    return d

import functools
import typing


class Combination(typing.NamedTuple):
    format: str
    type: str
    reference_time: str
    stream: str
    step: str


REFERENCE_TIMES = ["00", "06", "12", "18"]
STREAMS = ["oper", "enfo", "waef", "scda", "scwv", "mmsf", "wave"]
# maybe do steps as two Intervals? hour_steps, minute_steps?
STEPS = (
    [f"{i}h" for i in range(0, 144, 3)]
    + [f"{i}h" for i in range(144, 361, 6)]
    + [f"{i}m" for i in range(1, 8)]  # TODO: double check this endpoint, and below
)
STEP_UNITS = ["h", "m"]
TYPES = ["fc", "ef", "ep", "tf"]
FORMATS = ["grib2", "bufr"]
PRESSURE_LEVELS = [1000, 925, 850, 700, 500, 300, 250, 200, 50]

# mypy failing on python 3.7


@functools.lru_cache(maxsize=10)
def get_combinations(fmt="grib2"):
    combinations = []
    if fmt != "grib2":
        raise NotImplementedError("Only 'grib2' format is supported currently.")

    for reference_time in REFERENCE_TIMES:
        for stream in STREAMS:
            for type_ in TYPES:
                # print(reference_time, stream, type_)
                # we'll do steps here.
                if reference_time in {"00", "12"}:
                    if stream in {"enfo", "waef"}:
                        if type_ == "ef":
                            combinations.extend(
                                [
                                    Combination(
                                        fmt, type_, reference_time, stream, f"{i}h"
                                    )
                                    for i in range(0, 144, 3)
                                ]
                            )
                            combinations.extend(
                                [
                                    Combination(
                                        fmt, type_, reference_time, stream, f"{i}h"
                                    )
                                    for i in range(144, 361, 6)
                                ]
                            )
                        elif type_ == "ep":
                            combinations.extend(
                                [
                                    Combination(
                                        fmt, type_, reference_time, stream, "240h"
                                    ),
                                    Combination(
                                        fmt, type_, reference_time, stream, "360h"
                                    ),
                                ]
                            )
                    elif stream in {"oper", "wave"}:
                        if type_ == "fc":
                            combinations.extend(
                                [
                                    Combination(
                                        fmt, type_, reference_time, stream, f"{i}h"
                                    )
                                    for i in range(0, 144, 3)
                                ]
                            )
                            combinations.extend(
                                [
                                    Combination(
                                        fmt, type_, reference_time, stream, f"{i}h"
                                    )
                                    for i in range(144, 241, 6)
                                ]
                            )
                elif reference_time in {"06", "18"}:
                    if stream in {"enfo", "waef"}:
                        if type_ == "ef":
                            combinations.extend(
                                # TODO: check this endpoint!
                                [
                                    Combination(
                                        fmt, type_, reference_time, stream, f"{i}h"
                                    )
                                    for i in range(0, 145, 3)  # include 144
                                ]
                            )
                    elif stream in {"scda", "scwv"}:
                        if type_ == "fc":
                            combinations.extend(
                                [
                                    Combination(
                                        fmt, type_, reference_time, stream, f"{i}h"
                                    )
                                    for i in range(0, 91, 3)  # include 90
                                ]
                            )
                elif reference_time == "00":
                    if stream == "mmsf" and type_ == "fc":
                        # TODO:
                        combinations.extend(
                            [
                                Combination(fmt, type_, reference_time, stream, f"{i}m")
                                for i in range(1, 8)
                            ]
                        )
    return combinations

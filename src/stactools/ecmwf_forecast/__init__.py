import stactools.core

from stactools.ecmwf_forecast.stac import create_collection, create_item

__all__ = ["create_collection", "create_item"]

stactools.core.use_fsspec()


def register_plugin(registry):
    from stactools.ecmwf_forecast import commands

    registry.register_subcommand(commands.create_ecmwfforecast_command)


__version__ = "0.3.0"

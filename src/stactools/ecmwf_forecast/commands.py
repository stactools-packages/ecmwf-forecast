import logging

import click

from stactools.ecmwf_forecast import stac

logger = logging.getLogger(__name__)


def create_ecmwfforecast_command(cli):
    """Creates the stactools-ecmwf-forecast command line utility."""

    @cli.group(
        "ecmwf-forecast",
        short_help=("Commands for working with stactools-ecmwf-forecast"),
    )
    def ecmwfforecast():
        pass

    @ecmwfforecast.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("destination")
    @click.option(
        "--thumbnail", default=None, help="URL for the collection thumbnail asset."
    )
    @click.option(
        "--extra-field",
        default=None,
        help="Key-value pairs to include in extra-fields",
        multiple=True,
    )
    def create_collection_command(destination: str, thumbnail: str, extra_field):
        """Creates a STAC Collection

        Args:
            destination (str): An HREF for the Collection JSON
        """
        extra_fields = dict(k.split("=") for k in extra_field)

        collection = stac.create_collection(
            thumbnail=thumbnail, extra_fields=extra_fields
        )

        collection.set_self_href(destination)

        collection.save_object()

        return None

    @ecmwfforecast.command("create-item", short_help="Create a STAC item")
    @click.argument("source-pattern")
    @click.argument("destination")
    @click.option("-p", "--protocol")
    @click.option("--storage-options", default=None)
    def create_item_command(
        source_pattern: str, destination: str, protocol: str, storage_options: str
    ):
        """Creates a STAC Item

        Args:
            source (str): HREF of the Asset associated with the Item
            destination (str): An HREF for the STAC Collection
        """
        if storage_options:
            storage_options = dict(
                [x.split("=", 1) for x in storage_options.split(",")]
            )

        item = stac.create_item_from_pattern(
            source_pattern, protocol=protocol, storage_options=storage_options
        )

        item.save_object(dest_href=destination)

        return None

    return ecmwfforecast

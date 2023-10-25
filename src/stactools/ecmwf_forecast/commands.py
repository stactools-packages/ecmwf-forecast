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
    @click.argument("asset-href")
    @click.argument("index-href")
    @click.argument("destination")
    def create_item_command(asset_href, index_href: str, destination: str):
        """Creates a STAC Item

        Args:
            source (str): HREF of the Asset associated with the Item
            destination (str): An HREF for the STAC Collection
        """
        item = stac.create_item([asset_href, index_href], split_by_step=True)
        item.save_object(dest_href=destination)

        return None

    @ecmwfforecast.command(
        "plot-combinations", short_help="Plot the valid combinations"
    )
    @click.option("-d", "--destination", default="ecmwf-forecast-coverage.png")
    def _(destination):
        import matplotlib.pyplot as plt

        from stactools.ecmwf_forecast import constants, plots

        plots.plot_combinations(constants.get_combinations())
        plt.savefig(
            destination,
            format="png",
            bbox_inches="tight",
            pad_inches=0,
            dpi=200,
            transparent=False,
        )

    return ecmwfforecast

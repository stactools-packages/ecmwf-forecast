try:
    import matplotlib.font_manager
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
except ImportError as e:
    raise ImportError(
        "stactools.ecmwf_forecast.plots requires matplotlib, pandas, and seaborn."
    ) from e


def plot_combinations(combinations):
    df = pd.DataFrame(combinations)
    df["group"] = df["stream"] + "-" + df["reference_time"] + "-" + df["type"]

    series = []

    for _, (k, v) in enumerate(df.groupby("group")):
        series.append(pd.Series(1, index=v.step, name=k))

    m = (
        pd.concat(series, axis=1)
        .fillna(0)
        .astype(int)
        .rename(lambda x: x.rstrip("h"))
        .T.reindex(columns=list(map(str, range(0, 361, 3))), fill_value=0)
    )
    _, ax = plt.subplots(figsize=(24, 24))
    ax.set_facecolor("white")
    sns.heatmap(
        m,
        square=True,
        center=0.5,
        cmap="RdGy",
        vmin=0.5,
        vmax=1,
        cbar=False,
        ax=ax,
        linewidths=0.1,
    )
    for tick in ax.get_xticklabels():
        tick.set_rotation(55)

    properties = matplotlib.font_manager.FontProperties(family="monospace")
    for label in ax.get_yticklabels():
        label.set_fontproperties(properties)

    ax.set(
        title="ECMWF forecast coverage",
        xlabel="Forecast time (hours since reference time)",
    )
    # plt.savefig("ecmwf-forecast-coverage.png", format="png", bbox_inches="tight",
    #             pad_inches=0, dpi=200, transparent=False)
    return ax
import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image

# Use a non-GUI backend to make sure that this can run in background workers
matplotlib.use("Agg")


def plot_and_save_chart(folder_path, symbol, id, candles):
    # Prepare the data
    daily = pd.DataFrame(
        np.row_stack(candles),
        columns=["Open", "High", "Low", "Close", "Volume", "Date"],
    )
    daily[["Open", "High", "Low", "Close", "Volume"]] = daily[
        ["Open", "High", "Low", "Close", "Volume"]
    ].astype(float)
    daily["Date"] = pd.to_datetime(daily["Date"])
    daily.set_index("Date", inplace=True)

    # Plot the chart
    mc = mpf.make_marketcolors(volume="black", ohlc="black")
    s = mpf.make_mpf_style(gridstyle="", marketcolors=mc, edgecolor="white")

    image_filename = folder_path + "/" + symbol + "__" + str(id) + ".png"

    fig, axes = mpf.plot(
        daily,
        type="ohlc",
        volume=False,
        style=s,
        returnfig=True,
        axisoff=True,
        figscale=1.2,
        scale_padding=0,
        figsize=(5, 5),
    )

    ax1 = axes[0]  # The candlestick chart axis
    ax2 = fig.add_axes(
        ax1.get_position()
    )  # Create a new axis on top of the existing one
    ax2.set_axis_off()

    volume_plot_height = 0.15  # The height of the volume plot in percentage

    pos = ax1.get_position()
    pos.y0 = (
        pos.y0 + volume_plot_height * pos.height
    )  # Adjust the y0 value to prevent overlap
    ax1.set_position(pos)

    ax2.set_ylim(
        0, 1
    )  # Set the y-limit so that only 20% is used for the volume indicator
    ax2.set_anchor("S")  # Anchor the volume axis to the bottom of the figure

    # Draw the custom volume plot
    x_values = range(len(daily))
    y_values = (
        daily["Volume"] / daily["Volume"].max() * volume_plot_height
    ).tolist()  # Scale volume
    ax2.plot(x_values, y_values, marker="|", markersize=2, linewidth=0, color="black")

    fig.savefig(image_filename)

    # Optimize the image and save it
    Image.open(image_filename).convert("L").save(image_filename, optimize=True)

    # Close the figure to prevent memory leaks
    plt.close(fig)

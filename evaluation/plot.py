#!/usr/bin/env python3

import click
import uuid
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path
from pybars import Compiler
from functools import partial
from shutil import copyfile
import plotly
import time

plotly.io.orca.ensure_server()

def applyAttributes(figure, attributes):
    pass

def valueToLoadChart(data, attributes, name, unit, valueGetter, precision=2):
    fig = go.Figure()

    for voltage in data["Input voltage @ V"].unique():
        source = data[data["Input voltage @ V"] == voltage]
        fig.add_trace(
            go.Scatter(
                x=source["Load @ A"],
                y=valueGetter(source),
                text=valueGetter(source).round(precision).astype(str) + f" {unit}",
                mode="lines+markers+text",
                name=f"{voltage} V input",
                line={"shape": "spline"}
            )
        )
    fig.update_xaxes(title_text="Load current [A]")
    fig.update_yaxes(title_text=f"{name} [{unit}]")
    fig.update_traces(textposition='top center')
    fig.update_layout(
        legend={
            "x": 0,
            "y": 1
        },
        title={
            "text": f"{name} according to load",
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top"
        },
        margin={
            "t": 50,
            "b": 0,
            "l": 0,
            "r": 0,
            "pad": 0
        })
    applyAttributes(fig, attributes)
    return fig

def coilTemperatureChart(data, attributes):
    return valueToLoadChart(data, attributes, "Coil temperature", "°C",
        lambda x: x["Coil temperature after 5 minutes @ °C"])

def chipTemperatureChart(data, attributes):
    return valueToLoadChart(data, attributes, "Chip temperature", "°C",
        lambda x: x["Chip temperature after 5 minutes @ °C"])

def efficiency(data, attributes):
    def eff(source):
        inputPower = source["Input voltage @ V"] * source["Input current @ A"]
        outputPower = source["Output voltage @ V"] * source["Load @ A"]
        return outputPower / inputPower * 100
    fig = valueToLoadChart(data, attributes, "Efficiency", "%", eff)
    fig.update_layout(
        legend={
            "x": 1,
            "y": 1,
            "xanchor": "right",
            "yanchor": "top"
        })
    return fig

def rippleChart(data, attributes):
    return valueToLoadChart(data, attributes, "Output ripple", "mV",
        lambda x: x["Noise - Vpp @ mV"])

def outputVoltageChart(data, attributes):
    fig = valueToLoadChart(data, attributes, "Output voltage", "V",
        lambda x: x["Output voltage @ V"])
    fig.update_layout(
        legend={
            "x": 1,
            "y": 1,
            "xanchor": "right",
            "yanchor": "top"
        })
    return fig

charts = {
    "Coil temperature": coilTemperatureChart,
    "Chip temperature": chipTemperatureChart,
    "Efficiency": efficiency,
    "Ripple": rippleChart,
    "Output voltage": outputVoltageChart
}

def tableDataRow(row):
    return {
        "inputVoltage": row["Input voltage @ V"],
        "load": row["Load @ A"],
        "inputCurrent": row["Input current @ A"],
        "outputVoltage": row["Output voltage @ V"],
        "coilTemperature": row["Coil temperature after 5 minutes @ °C"],
        "chipTemperature": row["Chip temperature after 5 minutes @ °C"],
        "ripple": row["Noise - Vpp @ mV"],
        "scopeImage": "assets/waveforms/" + row["Scope image"]
    }

def dataToTable(data):
    return [tableDataRow(x) for _, x in data.iterrows()]

def chartSrcHelper(outputdir, data, this, *args, **kwargs):
    chartName = args[0]
    figure = charts[chartName](data, kwargs)

    path = Path(outputdir) / "resources"
    path.mkdir(parents=True, exist_ok=True)
    filename = uuid.uuid4().hex + ".svg"
    figure.write_image(str(path / filename))
    return f"resources/{filename}"

def resourceHelper(outputdir, this, *args, **kwargs):
    resource = args[0]
    path = Path(outputdir) / "resources"
    path.mkdir(parents=True, exist_ok=True)
    suffix = Path(resource).suffix
    filename = uuid.uuid4().hex + suffix
    copyfile(resource, path / filename)
    return f"resources/{filename}"

def fixedPointHelper(this, number):
    return f"{number:.2f}".rstrip('0').rstrip('.')

def buildHelpers(outputdir, data):
    return {
        "chartSrc": partial(chartSrcHelper, outputdir, data),
        "resource": partial(resourceHelper, outputdir),
        "fixedPoint": fixedPointHelper
    }

@click.command()
@click.argument("template", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.argument("source", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.argument("outputDir", type=click.Path(file_okay=False))
@click.option("--pagename", help="Title of the page")
def cli(template, source, outputdir, pagename):
    outputdir = Path(outputdir)
    outputdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(source)

    compiler = Compiler()
    template = compiler.compile(open(template).read())

    with open(outputdir / "index.html", "w") as f:
        f.write(template(
            {
                "data": df,
                "dataPerVoltage": {
                    voltage: dataToTable(df[df["Input voltage @ V"] == voltage])
                        for voltage in df["Input voltage @ V"].unique()},
                "pageName": pagename
            },
            helpers=buildHelpers(outputdir, df)))

if __name__ == "__main__":
    cli()
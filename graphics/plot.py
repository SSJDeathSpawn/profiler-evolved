from __future__ import annotations

from typing import TYPE_CHECKING
from functools import partial

from bokeh.layouts import row
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource        
from tornado import gen
if TYPE_CHECKING:
    from bokeh.plotting import Figure, Document
    from bokeh.models import GlyphRenderer, DataSource

plots: dict[str, Figure] = dict()
doc: Document = curdoc()

def get_plot(title: str) -> Figure:
    return plots.get(title)


def _add_plot(title: str, x_range: tuple[int, int], y_range: tuple[int, int], first_value: int, line_color: str = '#000000') -> DataSource:
    """Adds a new plot"""
    
    global plots  # kill me
    
    # create a plot and style its properties
    plot: Figure = figure(title=title, x_range=x_range, y_range=y_range, toolbar_location=None)

    plot.outline_line_color = None
    plot.grid.grid_line_color = None

    ds = ColumnDataSource(data=dict(x=[0], y=[first_value]))

    plots[title] = plot
    doc.add_root(row(plot))

    # add a text renderer to the plot (no data yet)
    renderer: GlyphRenderer = plot.line(x=[0], y=[first_value], line_color=line_color, source=ds)
    return ds


def add_plot(title: str, x_range: tuple[int, int], y_range: tuple[int, int], first_value: int, line_color: str = '#000000') -> DataSource:
    """Adds a new plot"""

    doc.add_next_tick_callback(partial(_add_plot, title=title, x_range=x_range, y_range=y_range, first_value=first_value, line_color=line_color))

@gen.coroutine
def _update_ds(title: str, ds: DataSource, y:int, x_step:int):
    """Updates existing plot"""
    
    ds.stream(dict(x=[ds.data['x'][-1]+x_step], y=[y]))

    # new_dict = dict()
    # new_dict['x'] = ds.data['x'] + [ds.data['x'][-1] + x_step]
    # new_dict['y'] = ds.data['y'] + [y]
    # ds.data = new_dict 

    plot = plots[title]
    plot.x_range.start = plot.x_range.start + x_step
    plot.x_range.end = plot.x_range.end + x_step


def update_ds(title: str, ds: DataSource, y:int, x_step:int):
    """Updates existing plot"""

    doc.add_next_tick_callback(partial(_update_ds, title=title, ds=ds, y=y, x_step=x_step))

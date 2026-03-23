"""
Chart Generator — Create Email-Embeddable Charts
==================================================
Generates Plotly charts styled for email embedding. Each method produces
a PNG file saved to the images/ directory, ready for <img src="images/...">.

Usage by Agent:
    1. Read rules/chart-design-system.md for visual constraints
    2. Analyze user's data → choose chart type
    3. Call the appropriate method to generate PNG
    4. Reference the output path in HTML: <img src="images/chart_name.png">

Dependencies: plotly, kaleido (auto-installed by deps-checker.py)
"""

import plotly.graph_objects as go
from pathlib import Path


# ---------------------------------------------------------------------------
# Design system constants (from rules/chart-design-system.md)
# ---------------------------------------------------------------------------

FONT_FAMILY = (
    "PingFang SC, Heiti SC, STHeiti, Songti SC, "
    "Arial Unicode MS, Microsoft YaHei, sans-serif"
)

FONT_SIZES = {
    "title": 14,
    "axis_title": 14,
    "base": 14,
    "tick": 11,
    "legend": 11,
    "data_label": 10,
    "annotation": 10,
}

COLORS = {
    # Status colors
    "danger": "#dc2626",
    "warning": "#f59e0b",
    "success": "#059669",
    "info": "#3b82f6",
    # Infrastructure
    "axis_label": "#9ca3af",
    "legend_text": "#6b7280",
    "grid_line": "#e5e7eb",
    "text_on_dark": "#ffffff",
    "text_on_light": "#1a1a1a",
    "fallback": "#94a3b8",
    "white": "#ffffff",
}

# Default categorical palette (max 6 colors)
CATEGORICAL_PALETTE = [
    "#3b82f6", "#059669", "#f59e0b", "#8b5cf6", "#ec4899", "#94a3b8",
]

# Warm gradient (critical → low)
WARM_GRADIENT = ["#dc2626", "#f97316", "#fbbf24", "#fef08a"]

# Heatmap color scale (white → deep orange)
HEATMAP_COLORSCALE = [
    [0.0, "#ffffff"],
    [0.2, "#fed7aa"],
    [0.4, "#fdba74"],
    [0.6, "#fb923c"],
    [0.8, "#f97316"],
    [1.0, "#ea580c"],
]

EXPORT_SCALE = 2.0


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _font(size_key: str, color: str = None, weight: str = "normal") -> dict:
    """Build a Plotly font dict."""
    return {
        "family": FONT_FAMILY,
        "size": FONT_SIZES.get(size_key, FONT_SIZES["base"]),
        "color": color or COLORS["legend_text"],
        **({"weight": weight} if weight != "normal" else {}),
    }


def _base_layout(
    width: int,
    height: int,
    title: str = "",
    show_legend: bool = True,
) -> dict:
    """Build base Plotly layout dict."""
    layout = {
        "title": {
            "text": title,
            "font": _font("title", COLORS["text_on_light"]),
            "x": 0.5,
            "xanchor": "center",
        },
        "font": _font("base"),
        "plot_bgcolor": COLORS["white"],
        "paper_bgcolor": COLORS["white"],
        "width": width,
        "height": height,
        "margin": {"l": 5, "r": 5, "t": 60, "b": 0},
        "showlegend": show_legend,
        "xaxis": {
            "showgrid": False,
            "zeroline": False,
            "tickfont": _font("tick"),
            "type": "category",
        },
        "yaxis": {
            "showgrid": False,
            "zeroline": False,
            "tickfont": _font("tick"),
        },
    }
    if show_legend:
        layout["legend"] = {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
            "font": _font("legend"),
        }
    return layout


def _hide_zero(values: list) -> list:
    """Replace 0 values with empty string for data labels."""
    return ["" if v == 0 else v for v in values]


def _save_fig(fig: go.Figure, output_path: str) -> str:
    """Save figure to PNG and return absolute path."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.write_image(str(p), scale=EXPORT_SCALE)
    return str(p.resolve())


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class EmailChartGenerator:
    """Generate email-embeddable charts following the chart design system.

    All methods save a PNG to the specified output path and return the path.
    Charts are styled according to rules/chart-design-system.md.

    Usage:
        gen = EmailChartGenerator(container_width=1200, output_dir='images')
        path = gen.bar_chart(
            categories=['Q1', 'Q2', 'Q3', 'Q4'],
            series={'Revenue': [100, 150, 130, 170]},
            title='Quarterly Revenue',
            filename='quarterly_revenue.png',
        )
        # Use in HTML: <img src="images/quarterly_revenue.png" ...>
    """

    def __init__(self, container_width: int = 1200, output_dir: str = "images"):
        """Initialize with email container width for chart sizing.

        Args:
            container_width: Email container width in pixels (600/800/1200)
            output_dir: Directory to save chart PNGs (default: 'images')
        """
        self.container_width = container_width
        self.content_width = container_width - 32  # 16px side padding
        self.output_dir = output_dir

    def _full_dims(self) -> tuple:
        """Full-width chart dimensions."""
        return self.content_width, 432

    def _half_dims(self) -> tuple:
        """Half-width chart dimensions."""
        return (self.content_width - 24) // 2, 360

    def _output_path(self, filename: str) -> str:
        """Build output path from filename."""
        return str(Path(self.output_dir) / filename)

    def bar_chart(
        self,
        categories: list,
        series: dict,
        title: str = "",
        filename: str = "bar_chart.png",
        orientation: str = "v",
        stacked: bool = False,
        colors: list = None,
        half_width: bool = False,
    ) -> str:
        """Generate bar chart.

        Args:
            categories: Category labels (X-axis for vertical, Y-axis for horizontal)
            series: Dict of {series_name: [values]}. Single series = simple bar.
            title: Chart title
            filename: Output filename (saved to output_dir)
            orientation: 'v' (vertical) or 'h' (horizontal)
            stacked: If True, stack series. If False, group them.
            colors: Optional list of colors. Defaults to categorical palette.
            half_width: If True, use half-width dimensions

        Returns:
            Path to saved PNG file
        """
        w, h = self._half_dims() if half_width else self._full_dims()
        colors = colors or CATEGORICAL_PALETTE
        fig = go.Figure()

        for i, (name, values) in enumerate(series.items()):
            color = colors[i % len(colors)]
            is_dark = color in (COLORS["danger"], COLORS["info"], COLORS["success"])
            text_color = COLORS["text_on_dark"] if is_dark else COLORS["text_on_light"]

            bar_kwargs = {
                "name": name,
                "marker_color": color,
                "text": _hide_zero(values),
                "textfont": {"size": FONT_SIZES["data_label"], "color": text_color,
                             "family": FONT_FAMILY, "weight": "bold"},
            }

            if stacked:
                bar_kwargs["textposition"] = "auto"
                bar_kwargs["insidetextfont"] = {
                    "size": FONT_SIZES["data_label"], "color": COLORS["text_on_dark"],
                    "family": FONT_FAMILY, "weight": "bold",
                }
                bar_kwargs["outsidetextfont"] = {
                    "size": FONT_SIZES["data_label"], "color": COLORS["text_on_light"],
                    "family": FONT_FAMILY, "weight": "bold",
                }
                bar_kwargs["constraintext"] = "none"
            else:
                bar_kwargs["textposition"] = "inside"

            if orientation == "h":
                fig.add_trace(go.Bar(y=categories, x=values, orientation="h", **bar_kwargs))
            else:
                fig.add_trace(go.Bar(x=categories, y=values, **bar_kwargs))

        layout = _base_layout(w, h, title, show_legend=len(series) > 1)
        layout["barmode"] = "stack" if stacked else "group"
        layout["bargap"] = 0.3

        if orientation == "h":
            layout["margin"]["l"] = 80
        if len(categories) > 6:
            layout["xaxis"]["tickangle"] = -30

        # Add headroom for labels above bars
        if orientation == "v":
            all_vals = [v for vals in series.values() for v in vals]
            if stacked:
                # Sum across series per category
                totals = [sum(s[i] for s in series.values() if i < len(s)) for i in range(len(categories))]
                max_val = max(totals) if totals else 0
            else:
                max_val = max(all_vals) if all_vals else 0
            layout["yaxis"]["range"] = [0, max_val * 1.15]
            layout["yaxis"]["showticklabels"] = False

        fig.update_layout(**layout)
        return _save_fig(fig, self._output_path(filename))

    def line_chart(
        self,
        x_values: list,
        y_series: dict,
        title: str = "",
        filename: str = "line_chart.png",
        colors: list = None,
        half_width: bool = False,
        show_percentage: bool = False,
    ) -> str:
        """Generate line chart.

        Args:
            x_values: X-axis labels (typically time periods)
            y_series: Dict of {series_name: [values]}
            title: Chart title
            filename: Output filename
            colors: Optional color list
            half_width: If True, use half-width dimensions
            show_percentage: If True, format labels as percentages

        Returns:
            Path to saved PNG file
        """
        w, h = self._half_dims() if half_width else self._full_dims()
        colors = colors or CATEGORICAL_PALETTE
        fig = go.Figure()

        for i, (name, values) in enumerate(y_series.items()):
            color = colors[i % len(colors)]
            text_vals = [f"{v}%" for v in values] if show_percentage else values

            fig.add_trace(go.Scatter(
                x=x_values,
                y=values,
                name=name,
                mode="lines+markers+text",
                line={"color": color, "width": 2},
                marker={"size": 6, "color": color},
                text=text_vals,
                textposition="bottom center",
                textfont=_font("annotation", color, "bold"),
            ))

        layout = _base_layout(w, h, title, show_legend=len(y_series) > 1)
        fig.update_layout(**layout)
        return _save_fig(fig, self._output_path(filename))

    def heatmap(
        self,
        x_labels: list,
        y_labels: list,
        values: list,
        title: str = "",
        filename: str = "heatmap.png",
        colorscale: list = None,
        half_width: bool = False,
    ) -> str:
        """Generate heatmap chart.

        Args:
            x_labels: Column labels
            y_labels: Row labels
            values: 2D list [rows][cols] of numeric values
            title: Chart title
            filename: Output filename
            colorscale: Optional Plotly colorscale. Defaults to warm orange.
            half_width: If True, use half-width dimensions

        Returns:
            Path to saved PNG file
        """
        w, h = self._half_dims() if half_width else self._full_dims()
        colorscale = colorscale or HEATMAP_COLORSCALE

        fig = go.Figure(data=go.Heatmap(
            z=values,
            x=x_labels,
            y=y_labels,
            colorscale=colorscale,
            colorbar={
                "thickness": 15,
                "len": 0.7,
                "tickfont": _font("tick"),
            },
            hovertemplate="<b>%{x}</b><br>%{y}: %{z}<extra></extra>",
            showscale=True,
        ))

        layout = _base_layout(w, h, title, show_legend=False)
        layout["margin"]["l"] = 80
        layout["margin"]["b"] = 100
        if len(x_labels) > 6:
            layout["xaxis"]["tickangle"] = -30

        # Add cell value annotations
        max_val = max((max(row) for row in values if row), default=1)
        annotations = []
        for i, y_label in enumerate(y_labels):
            for j, x_label in enumerate(x_labels):
                val = values[i][j]
                text_color = COLORS["text_on_dark"] if val > max_val * 0.4 else COLORS["text_on_light"]
                annotations.append({
                    "x": x_label, "y": y_label, "text": str(val),
                    "font": {"family": FONT_FAMILY, "size": FONT_SIZES["tick"], "color": text_color},
                    "showarrow": False, "xanchor": "center", "yanchor": "middle",
                })
        layout["annotations"] = annotations

        fig.update_layout(**layout)
        return _save_fig(fig, self._output_path(filename))

    def pie_chart(
        self,
        labels: list,
        values: list,
        title: str = "",
        filename: str = "pie_chart.png",
        colors: list = None,
        half_width: bool = True,
        donut: bool = False,
    ) -> str:
        """Generate pie or donut chart.

        Args:
            labels: Slice labels
            values: Slice values
            title: Chart title
            filename: Output filename
            colors: Optional color list
            half_width: If True, use half-width (default True for pie)
            donut: If True, render as donut chart (hole in center)

        Returns:
            Path to saved PNG file
        """
        w, h = self._half_dims() if half_width else self._full_dims()
        colors = colors or CATEGORICAL_PALETTE

        fig = go.Figure(data=go.Pie(
            labels=labels,
            values=values,
            marker={"colors": colors[:len(labels)]},
            textinfo="label+percent",
            textfont={"family": FONT_FAMILY, "size": FONT_SIZES["data_label"]},
            hole=0.4 if donut else 0,
        ))

        layout = _base_layout(w, h, title, show_legend=False)
        fig.update_layout(**layout)
        return _save_fig(fig, self._output_path(filename))

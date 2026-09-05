"""Matplotlib helpers: wordcloud and skill co-occurrence network images."""

from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".mplconfig")
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from PIL import Image
from wordcloud import WordCloud

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

_FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/msyh.ttf"),
]


def _font_path() -> str | None:
    for font in _FONT_CANDIDATES:
        if font.exists():
            return str(font)
    return None


def _figure_to_image(figure: plt.Figure) -> Image.Image:
    buffer = BytesIO()
    figure.savefig(buffer, format="png", bbox_inches="tight", dpi=120)
    plt.close(figure)
    buffer.seek(0)
    return Image.open(buffer)


def wordcloud_figure(skill_counts: dict[str, int]) -> Image.Image:
    """Render a skill wordcloud as a PIL image for st.image."""
    cloud = WordCloud(
        width=900,
        height=480,
        background_color="white",
        font_path=_font_path(),
        colormap="viridis",
    ).generate_from_frequencies(skill_counts)
    figure, axis = plt.subplots(figsize=(10, 5))
    axis.imshow(cloud, interpolation="bilinear")
    axis.axis("off")
    return _figure_to_image(figure)


def skill_network_figure(
    edges: pd.DataFrame, top_skills: pd.DataFrame
) -> Image.Image:
    """Render the skill co-occurrence graph as a PIL image."""
    graph = nx.Graph()
    for _, row in top_skills.iterrows():
        graph.add_node(row["skill"], weight=int(row["count"]))
    for _, row in edges.iterrows():
        graph.add_edge(row["source"], row["target"], weight=int(row["weight"]))

    figure, axis = plt.subplots(figsize=(10, 7))
    if graph.number_of_nodes() == 0:
        axis.text(0.5, 0.5, "暂无足够数据绘制共现网络", ha="center", va="center")
        axis.axis("off")
        return _figure_to_image(figure)

    position = nx.spring_layout(graph, k=0.9, seed=42, weight="weight")
    node_sizes = [graph.nodes[node]["weight"] * 250 for node in graph.nodes]
    nx.draw_networkx_nodes(graph, position, node_size=node_sizes, node_color="#3b82f6", alpha=0.85)
    nx.draw_networkx_edges(
        graph,
        position,
        width=[weight for _, _, weight in graph.edges(data="weight")],
        edge_color="#94a3b8",
        alpha=0.7,
    )
    nx.draw_networkx_labels(graph, position, font_family="Microsoft YaHei", font_size=11)
    axis.axis("off")
    return _figure_to_image(figure)


def boxplot_by_group(df: pd.DataFrame, group_column: str, limit: int = 8) -> Image.Image:
    """Box plot of salaries grouped by a categorical column."""
    data = df.dropna(subset=["salary_avg"]).copy()
    order = data.groupby(group_column)["salary_avg"].median().sort_values(ascending=False)
    groups = list(order.index[:limit])
    values = [data.loc[data[group_column] == group, "salary_avg"].astype(float) for group in groups]

    figure, axis = plt.subplots(figsize=(10, 5))
    axis.boxplot(
        values, tick_labels=[str(group) for group in groups], showmeans=True
    )
    axis.set_title(f"各{group_column}薪资分布（K/月）")
    axis.set_ylabel("月薪（K）")
    figure.tight_layout()
    return _figure_to_image(figure)

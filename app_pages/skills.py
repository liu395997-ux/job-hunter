"""技能图谱：热门技能、词云与共现网络。"""

from __future__ import annotations

import streamlit as st

from analysis.skill_graph import skill_cooccurrence, top_skills
from ui.charts import skill_network_figure, wordcloud_figure
from ui.data import load_cleaned_data

df = load_cleaned_data()

skill_counts = top_skills(df, top_n=20)

with st.container(border=True):
    st.subheader("热门技能 Top 20")
    bar_data = skill_counts.rename(columns={"skill": "技能", "count": "出现次数"})
    st.bar_chart(bar_data, x="技能", y="出现次数", horizontal=True)

with st.container(border=True):
    st.subheader("技能词云")
    st.image(
        wordcloud_figure(dict(zip(skill_counts["skill"], skill_counts["count"], strict=True)))
    )

edges = skill_cooccurrence(df, top_n=15, min_weight=1)
with st.container(border=True):
    st.subheader("技能共现网络（同岗位共现次数）")
    if edges.empty:
        st.info("样本不足，暂无共现关系")
    else:
        st.image(skill_network_figure(edges, skill_counts))
        st.dataframe(
            edges.rename(columns={"source": "技能A", "target": "技能B", "weight": "共现次数"}),
            hide_index=True,
        )

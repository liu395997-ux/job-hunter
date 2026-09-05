"""市场总览：KPI、城市/学历/岗位分布与薪资分布。"""

from __future__ import annotations

import altair as alt
import streamlit as st

from analysis.skill_graph import top_skills
from ui.data import load_cleaned_data

df = load_cleaned_data()

with st.sidebar:
    cities = st.multiselect(
        "城市",
        sorted(df["city"].dropna().unique()),
        default=sorted(df["city"].dropna().unique()),
    )
    st.caption("数据来自样例集，可用 scripts/run_pipeline.py 更新")

filtered = df[df["city"].isin(cities)] if cities else df
salary_avg = filtered["salary_avg"].dropna()

with st.container(horizontal=True):
    st.metric("职位总数", f"{len(filtered):,}", border=True)
    st.metric("平均月薪", f"{salary_avg.mean():.1f}K" if len(salary_avg) else "—", border=True)
    st.metric("覆盖城市", f"{filtered['city'].nunique()}", border=True)
    st.metric("技能种类", f"{len(top_skills(filtered))}", border=True)

left, right = st.columns(2)
with left:
    with st.container(border=True):
        st.subheader("城市岗位分布")
        city_counts = (
            filtered["city"].value_counts().rename_axis("城市").reset_index(name="岗位数")
        )
        st.bar_chart(city_counts, x="城市", y="岗位数", horizontal=True)
with right:
    with st.container(border=True):
        st.subheader("学历要求分布")
        edu_counts = (
            filtered["education"].value_counts().rename_axis("学历").reset_index(name="岗位数")
        )
        st.bar_chart(edu_counts, x="学历", y="岗位数")

with st.container(border=True):
    st.subheader("月薪分布")
    salary_data = filtered.dropna(subset=["salary_avg"])
    if len(salary_data):
        histogram = (
            alt.Chart(salary_data)
            .mark_bar()
            .encode(
                x=alt.X("salary_avg:Q", bin=alt.Bin(maxbins=20), title="月薪（K）"),
                y=alt.Y("count()", title="岗位数"),
            )
        )
        st.altair_chart(histogram)
    else:
        st.info("当前筛选条件下没有薪资数据")

with st.container(border=True):
    st.subheader("热门岗位 Top 10")
    title_counts = (
        filtered["title"].value_counts().head(10).rename_axis("岗位").reset_index(name="岗位数")
    )
    st.bar_chart(title_counts, x="岗位", y="岗位数")

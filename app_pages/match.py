"""我的匹配：输入求职画像，输出 TF-IDF 个性化推荐。"""

from __future__ import annotations

import streamlit as st

from analysis.recommend import recommend_jobs
from ui.data import load_cleaned_data

df = load_cleaned_data()
cities = ["不限"] + sorted(df["city"].dropna().unique())

with st.form("match_form", border=True):
    st.subheader("我的求职画像")
    skills = st.text_input(
        "技能（逗号分隔）",
        value="python, 数据分析, sql",
        help="例如：python, 数据分析, 机器学习, sql",
    )
    left, right = st.columns(2)
    with left:
        city = st.selectbox("求职城市", cities)
        education = st.selectbox("最高学历", ["不限", "大专", "本科", "硕士", "博士"], index=2)
    with right:
        salary_max = st.slider("期望月薪上限（K）", 10, 60, 30)
        top_n = st.slider("推荐数量", 1, 10, 5)
    submitted = st.form_submit_button("开始匹配", icon=":material/search:", type="primary")

if submitted:
    profile = {
        "skills": skills,
        "city": None if city == "不限" else city,
        "education": education,
        "salary_max": float(salary_max),
    }
    result = recommend_jobs(df, profile, top_n=top_n)
    if result.empty:
        st.warning("没有满足条件的岗位，请放宽城市 / 学历 / 薪资条件。")
    else:
        st.subheader("推荐结果")
        st.dataframe(
            result.rename(
                columns={
                    "title": "职位",
                    "company": "公司",
                    "city": "城市",
                    "education": "学历",
                    "salary_avg": "平均月薪(K)",
                    "match_score": "匹配度",
                    "link": "链接",
                }
            ),
            column_config={
                "匹配度": st.column_config.ProgressColumn(
                    "匹配度", min_value=0.0, max_value=1.0, format="%.2f"
                ),
                "链接": st.column_config.LinkColumn("链接"),
            },
            hide_index=True,
        )
        st.caption(
            "匹配度 = 简历画像与岗位文本的 TF-IDF 余弦相似度，"
            "已先按城市 / 学历 / 薪资硬过滤。"
        )

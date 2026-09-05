"""薪资分析：分组箱线图 + 随机森林薪资预测器。"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from analysis.salary_predict import predict_salary
from ui.charts import boxplot_by_group
from ui.data import load_cleaned_data, load_salary_metrics, load_salary_pipeline

df = load_cleaned_data()

dimension = st.segmented_control(
    "分组维度",
    ["城市", "学历", "经验"],
    default="城市",
)
column_map = {"城市": "city", "学历": "education", "经验": "experience"}
group_column = column_map[dimension]

with st.container(border=True):
    st.subheader(f"各{dimension}薪资箱线图")
    st.image(boxplot_by_group(df, group_column))

metrics = load_salary_metrics()
with st.container(border=True):
    st.subheader("薪资预测模型（随机森林回归）")
    with st.container(horizontal=True):
        st.metric("平均绝对误差 MAE", f"{metrics['mae']:.2f}K", border=True)
        st.metric("决定系数 R2", f"{metrics['r2']:.3f}", border=True)
        st.metric("训练样本", f"{metrics['train_size']}", border=True)
        st.metric("验证样本", f"{metrics['test_size']}", border=True)
    importance = pd.DataFrame(
        [{"特征": name, "重要性": value} for name, value in metrics["feature_importance"].items()]
    )
    st.bar_chart(importance, x="特征", y="重要性")
    st.caption("特征：城市、学历、经验、公司规模、技能数量；指标在验证集上计算")

with st.form("predict_form", border=True):
    st.subheader("薪资预测器")
    left, right = st.columns(2)
    with left:
        predict_city = st.selectbox("城市", sorted(df["city"].dropna().unique()))
        predict_education = st.selectbox("学历", ["不限", "大专", "本科", "硕士", "博士"])
    with right:
        predict_experience = st.selectbox(
            "经验", ["经验不限", "在校/应届", "1-3年", "3-5年", "5-10年"]
        )
        predict_skills = st.slider("技能数量", 0, 10, 4)
    submitted = st.form_submit_button("预测月薪", icon=":material/calculate:", type="primary")

if submitted:
    row = {
        "city": predict_city,
        "education": predict_education,
        "experience": predict_experience,
        "company_size": "150-500人",
        "skill_count": predict_skills,
    }
    prediction = predict_salary(load_salary_pipeline(), row)
    st.success(f"预测月薪：**{prediction:.1f}K**（仅供参考，基于样例数据训练）")

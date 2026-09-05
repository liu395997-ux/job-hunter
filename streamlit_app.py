"""自动化求职工具 - Streamlit 入口。运行：streamlit run streamlit_app.py"""

from __future__ import annotations

import os

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import streamlit as st

st.set_page_config(
    page_title="自动化求职工具",
    page_icon=":material/work:",
    layout="wide",
)

pages = [
    st.Page("app_pages/overview.py", title="市场总览", icon=":material/dashboard:"),
    st.Page("app_pages/salary.py", title="薪资分析", icon=":material/savings:"),
    st.Page("app_pages/skills.py", title="技能图谱", icon=":material/query_stats:"),
    st.Page("app_pages/match.py", title="我的匹配", icon=":material/thumb_up:"),
]

page = st.navigation(pages, position="top")
st.title(f"{page.icon} {page.title}")
page.run()

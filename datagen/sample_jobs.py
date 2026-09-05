"""Deterministic sample job data generator used when live crawling fails."""

from __future__ import annotations

import random
from datetime import date, timedelta

import pandas as pd

SAMPLE_FIELDS = [
    "title",
    "city",
    "education",
    "experience",
    "company",
    "company_size",
    "company_type",
    "salary_text",
    "skills",
    "description",
    "publish_date",
    "link",
]

TITLES = [
    "数据分析师",
    "Python开发工程师",
    "数据挖掘工程师",
    "机器学习工程师",
    "大数据开发工程师",
    "算法工程师",
    "BI工程师",
    "数据产品经理",
    "数据运营",
    "ETL工程师",
]

CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京"]
EDUCATIONS = ["本科", "本科", "本科", "硕士", "硕士", "大专", "学历不限"]
EXPERIENCES = ["经验不限", "在校/应届", "1-3年", "1-3年", "3-5年", "3-5年", "5-10年"]
COMPANY_SIZES = ["少于50人", "50-150人", "150-500人", "500-2000人", "2000人以上"]
COMPANY_TYPES = ["民营", "国企", "外资", "合资", "上市公司"]

SKILL_BY_TITLE: dict[str, list[str]] = {
    "数据分析师": ["python", "sql", "pandas", "numpy", "数据可视化", "excel", "统计学"],
    "Python开发工程师": ["python", "linux", "docker", "sql", "flask", "django", "爬虫"],
    "数据挖掘工程师": ["python", "机器学习", "数据挖掘", "sql", "pandas", "统计学", "spark"],
    "机器学习工程师": ["python", "机器学习", "深度学习", "tensorflow", "pytorch", "nlp"],
    "大数据开发工程师": ["java", "spark", "hadoop", "flink", "hive", "linux", "sql"],
    "算法工程师": ["python", "算法", "机器学习", "深度学习", "推荐系统", "nlp", "数据结构"],
    "BI工程师": ["sql", "tableau", "powerbi", "数据可视化", "etl", "excel"],
    "数据产品经理": ["数据可视化", "需求分析", "sql", "产品设计", "用户研究", "excel"],
    "数据运营": ["excel", "sql", "数据可视化", "用户增长", "数据分析", "python"],
    "ETL工程师": ["sql", "etl", "hive", "spark", "数据仓库", "linux", "python"],
}

RESPONSIBILITIES = [
    "负责业务数据的采集、清洗与指标体系搭建",
    "参与数据模型设计与报表开发，支持业务决策",
    "负责核心算法的调研、实现与线上效果优化",
    "与产品和运营协作，输出数据专题分析报告",
    "参与数据平台建设，保障数据质量与时效性",
]

REQUIREMENT_TEXT = (
    "要求具备扎实的编程基础与数据敏感度，"
    "熟悉主流工具链，有良好的团队协作与文档习惯。"
)

CITY_FACTOR = {
    "北京": 1.25,
    "上海": 1.2,
    "深圳": 1.2,
    "杭州": 1.15,
    "广州": 1.1,
    "成都": 0.95,
    "武汉": 0.9,
    "南京": 0.9,
}
EDUCATION_BONUS = {"硕士": 4.0, "本科": 2.0, "大专": 0.0, "学历不限": 0.0}
EXPERIENCE_BONUS = {
    "在校/应届": -2.0,
    "经验不限": -1.0,
    "1-3年": 1.0,
    "3-5年": 3.0,
    "5-10年": 5.0,
}


def _salary_text(rng: random.Random, city: str, education: str, experience: str) -> str:
    """Produce a realistic salary string from several common formats."""
    roll = rng.random()
    if roll < 0.15:
        return rng.choice(["面议", "薪资面议"])
    base = (
        10.0 * CITY_FACTOR.get(city, 1.0)
        + EDUCATION_BONUS.get(education, 0.0)
        + EXPERIENCE_BONUS.get(experience, 0.0)
    )
    low = int(round(base + rng.randint(-1, 2)))
    high = low + rng.randint(3, 10)
    if roll < 0.65:
        months = rng.choice(["", "", "", "·13薪", "·14薪", "·15薪", "·16薪"])
        return f"{low}-{high}K{months}"
    return f"{low / 10}-{high / 10}万/月"


def _publish_date(rng: random.Random) -> str:
    start = date(2026, 6, 1)
    return (start + timedelta(days=rng.randint(0, 90))).isoformat()


def generate_sample_jobs(count: int = 320, seed: int = 42) -> pd.DataFrame:
    """Generate a deterministic sample job dataset with ``count`` rows."""
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []
    for index in range(count):
        title = rng.choice(TITLES)
        city = rng.choice(CITIES)
        education = rng.choice(EDUCATIONS)
        experience = rng.choice(EXPERIENCES)
        skills = rng.sample(SKILL_BY_TITLE[title], k=min(5, len(SKILL_BY_TITLE[title])))
        description = (
            f"{title}岗位：{rng.choice(RESPONSIBILITIES)}。"
            f"核心技能：{'、'.join(skills)}。"
            f"{REQUIREMENT_TEXT}"
        )
        company = (
            f"{rng.choice(['云', '星', '蓝', '启', '锐', '海', '智'])}"
            f"{rng.choice(['途', '帆', '数', '合', '创', '图', '脉'])}"
            f"{rng.choice(['科技', '数据', '网络', '软件', '智能'])}有限公司"
        )
        rows.append(
            {
                "title": title,
                "city": city,
                "education": education,
                "experience": experience,
                "company": company,
                "company_size": rng.choice(COMPANY_SIZES),
                "company_type": rng.choice(COMPANY_TYPES),
                "salary_text": _salary_text(rng, city, education, experience),
                "skills": ", ".join(skills),
                "description": description,
                "publish_date": _publish_date(rng),
                "link": f"https://job.example.com/{seed}_{index:05d}",
            }
        )
    return pd.DataFrame(rows, columns=SAMPLE_FIELDS)

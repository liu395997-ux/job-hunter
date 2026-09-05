"""Skill extraction from free text using jieba and a curated lexicon."""

from __future__ import annotations

SKILL_LEXICON = {
    "python",
    "sql",
    "pandas",
    "numpy",
    "机器学习",
    "深度学习",
    "数据挖掘",
    "数据可视化",
    "数据仓库",
    "etl",
    "spark",
    "hadoop",
    "hive",
    "flink",
    "java",
    "linux",
    "docker",
    "flask",
    "django",
    "爬虫",
    "excel",
    "tableau",
    "powerbi",
    "统计学",
    "nlp",
    "推荐系统",
    "tensorflow",
    "pytorch",
    "算法",
    "数据结构",
    "需求分析",
    "产品设计",
    "用户研究",
    "用户增长",
}


def extract_skills(text: str | None) -> list[str]:
    """Return the curated skills present in ``text`` (case-insensitive)."""
    if not text:
        return []
    lowered = text.lower()
    return sorted(skill for skill in SKILL_LEXICON if skill.lower() in lowered)


def skills_string_to_list(skills: str | None) -> list[str]:
    """Split a comma-separated skill string into a cleaned list."""
    if not skills:
        return []
    return [item.strip() for item in skills.split(",") if item.strip()]

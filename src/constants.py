from __future__ import annotations

JOBSEARCH_BASE_URL = "https://jobsearch.api.jobtechdev.se/search"
CACHE_DIR = "data/cache"

ROLE_QUERIES: dict[str, str] = {
    "Data Analyst": "data analyst",
    "Data Engineer": "data engineer",
    "Data Scientist": "data scientist",
    "BI Analyst / BI Developer": "bi analyst OR power bi OR bi developer",
    "Analytics Engineer": "analytics engineer"
}

# Skill name -> regex pattern.
# Keep these readable and easy to tweak; start small and expand as needed.
SKILL_PATTERNS: dict[str, str] = {
    "SQL": r"\bsql\b",
    "Python": r"\bpython\b",
    "Excel": r"\bexcel\b",
    "Power BI": r"\bpower\s*bi\b|\bpbi\b",
    "Tableau": r"\btableau\b",
    "Git": r"\bgit\b|\bgithub\b|\bgitlab\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b|\bk8s\b",
    "Linux": r"\blinux\b",
    "Spark": r"\bspark\b|\bpyspark\b",
    "Databricks": r"\bdatabricks\b",
    "Airflow": r"\bairflow\b",
    "dbt": r"\bdbt\b",
    "Azure": r"\bazure\b",
    "AWS": r"\baws\b|\bamazon web services\b",
    "GCP": r"\bgcp\b|\bgoogle cloud\b",
    "BigQuery": r"\bbigquery\b|\bbig query\b",
    "Snowflake": r"\bsnowflake\b",
    "Statistics": r"\bstatistics\b|\bstatistical\b",
    "Machine Learning": r"\bmachine learning\b|\bml\b",
}

# Skill name -> category (used for higher-level summaries).
# Keep this simple and editable; any skill not listed falls back to "Other".
SKILL_CATEGORIES: dict[str, str] = {
    # Programming / core
    "Python": "Programming",
    "SQL": "Programming",
    "Git": "Programming",
    "Linux": "Programming",
    "Statistics": "Programming",
    "Machine Learning": "Programming",

    # BI / Visualization
    "Excel": "BI / Visualization",
    "Power BI": "BI / Visualization",
    "Tableau": "BI / Visualization",

    # Cloud / Big Data
    "AWS": "Cloud / Big Data",
    "Azure": "Cloud / Big Data",
    "GCP": "Cloud / Big Data",
    "Spark": "Cloud / Big Data",
    "Databricks": "Cloud / Big Data",
    "BigQuery": "Cloud / Big Data",
    "Snowflake": "Cloud / Big Data",
    "Docker": "Cloud / Big Data",
    "Kubernetes": "Cloud / Big Data",
    "Airflow": "Cloud / Big Data",
    "dbt": "Cloud / Big Data",
}

# Optional: stable ordering for charts/tables.
SKILL_CATEGORY_ORDER: list[str] = [
    "Programming",
    "BI / Visualization",
    "Cloud / Big Data",
    "Other",
]

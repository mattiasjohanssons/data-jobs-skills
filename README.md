# Data Jobs Skills Explorer

Interactive Streamlit app that fetches real job postings from the **JobSearch API** and summarizes **which skills are most frequently mentioned** for selected data roles.

Built to be **simple, explainable, and interview-friendly**: Python + pandas + regex-based extraction + clean charts.

## Highlights

- **Multi-role comparison**: select one or many roles and compare skill mentions side-by-side
- **Skill table + chart**: mentions and *share of postings* (shown as percentages)
- **Skill categories**: roll up skills into categories (Programming, BI/Visualization, Cloud/Big Data, Other)
- **Local caching**: saves API responses to `data/cache/` for faster iteration and reproducible demos

## Demo

- Select a couple roles (e.g. **Data Analyst** + **Data Engineer**) and click **Analyze**
- Explain the query logic using **Show search query**
- Walk through:
  - **Skill comparison** chart (mentions by role)
  - **Long** table (role/skill/category/mentions/share)
  - **Wide** table (skill vs role, mentions + share)
  - **Skill categories** chart
- Toggle **Refresh (ignore cache)** to show fresh vs cached results

## Quickstart

From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
streamlit run app/Home.py
```

Then open the Streamlit URL shown in the terminal and go to **Role Skills** in the sidebar.

## Troubleshooting

### `ModuleNotFoundError: No module named 'src'`

This should be fixed by the editable install in Quickstart (`pip install -e .`).

If you still hit it, make sure you start Streamlit from the project root (the folder that contains `src/`):

```bash
cd "/path/to/Project_Data_Jobs"
streamlit run app/Home.py
```

If you still hit it:

```bash
export PYTHONPATH="$PWD"
streamlit run app/Home.py
```

## How it works (simple pipeline)

1. **Fetch postings** per selected role from the JobSearch API  
2. **Normalize JSON → pandas DataFrame** (headline, description, employer, dates, url, …)  
3. **Extract skills** by regex matching against `headline + description`  
4. **Aggregate**:
   - per role × skill (mentions + share of postings)
   - per role × category (sum of mentions by category)
5. **Visualize** in Streamlit (Altair charts + tables)

## Project structure

```text
Project_Data_Jobs/
  app/
    Home.py
    pages/
      1_Role_Skills.py
  src/
    constants.py         # role queries, skill patterns, skill categories
    jobsearch_client.py  # API client + local JSON cache
    normalize.py         # JSON -> DataFrame
    skills.py            # skill extraction + counting
  data/
    cache/               # cached API responses (JSON)
  requirements.txt
  README.md
```



## Method notes & limitations

- **Regex-based extraction**: explainable and fast, but not perfect (synonyms and context can be missed).
- **Language mix**: postings can be Swedish/English; expand patterns/queries to match your target market.
- **Counts vs “importance”**: a mention indicates demand signals, not true proficiency requirements.
- **Category rollups**: category chart is based on **sum of skill mentions**, not unique postings per category.

## Data source

- JobSearch API: `https://jobsearch.api.jobtechdev.se/search`


from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from src.constants import ROLE_QUERIES, SKILL_CATEGORIES, SKILL_CATEGORY_ORDER, SKILL_PATTERNS
from src.jobsearch_client import JobSearchRequest, search_jobs
from src.normalize import hits_to_dataframe
from src.skills import compile_skill_patterns, skill_counts


st.title("Role Skills")
st.caption("Select one or more roles and compare the most mentioned skills in job postings.")

roles = st.multiselect(
    "Roles",
    options=list(ROLE_QUERIES.keys()),
    default=["Data Analyst"] if "Data Analyst" in ROLE_QUERIES else None,
)
with st.expander("Show search query"):
    if roles:
        for r in roles:
            st.code(f"{r}: {ROLE_QUERIES[r]}", language="text")
    else:
        for r, q in ROLE_QUERIES.items():
            st.code(f"{r}: {q}", language="text")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    limit = st.slider("How many postings to fetch", min_value=20, max_value=200, value=100, step=20)
with col2:
    use_cache = st.checkbox("Use local cache", value=True)
with col3:
    timeout_s = st.number_input("Timeout (seconds)", min_value=5, max_value=60, value=25, step=5)

col4, col5 = st.columns([1, 2])
with col4:
    top_n = st.slider("Top skills", min_value=5, max_value=30, value=15, step=1)
with col5:
    show_postings = st.checkbox("Show sample postings", value=False)

refresh = st.toggle("Refresh (ignore cache)", value=False)

if st.button("Analyze", type="primary"):
    if not roles:
        st.info("Select at least one role to analyze.")
        st.stop()

    patterns = compile_skill_patterns(SKILL_PATTERNS)

    role_dfs: dict[str, pd.DataFrame] = {}
    fetch_summary_rows: list[dict[str, object]] = []

    with st.spinner("Fetching from JobSearch API..."):
        for r in roles:
            req = JobSearchRequest(query=ROLE_QUERIES[r], limit=int(limit), offset=0)
            payload = search_jobs(req, use_cache=(use_cache and not refresh), timeout_s=int(timeout_s))
            hits = payload.get("hits", []) or []

            df_r = hits_to_dataframe(hits)
            df_r["role"] = r

            role_dfs[r] = df_r
            fetch_summary_rows.append(
                {
                    "role": r,
                    "postings": len(hits),
                    "cache_hit": bool(payload.get("_cache", {}).get("hit")),
                }
            )

    st.subheader("Fetch summary")
    st.dataframe(fetch_summary_rows, use_container_width=True)

    dfs = [df for df in role_dfs.values() if getattr(df, "empty", True) is False]
    if not dfs:
        st.warning("No postings were fetched for the selected roles.")
        st.stop()

    df_all = pd.concat(dfs, ignore_index=True)
    st.caption(f"Columns: {', '.join(df_all.columns)}")

    # Skill counts per role (long format)
    counts_long_parts: list[pd.DataFrame] = []
    for r, df_r in role_dfs.items():
        if df_r.empty:
            continue
        c = skill_counts(df_r, skill_patterns=patterns)
        c.insert(0, "role", r)
        counts_long_parts.append(c)

    if not counts_long_parts:
        st.warning("No skills matched. Try increasing the fetch limit or expanding the skill patterns.")
        st.stop()

    counts_long = pd.concat(counts_long_parts, ignore_index=True)

    # Determine which skills to display (top N across selected roles)
    skill_rank = (
        counts_long.groupby("skill", as_index=False)["mentions"]
        .sum()
        .rename(columns={"mentions": "score"})
        .sort_values(["score", "skill"], ascending=[False, True])
    )
    top_skills = skill_rank["skill"].head(int(top_n)).tolist()
    plot_df = counts_long[counts_long["skill"].isin(top_skills)].copy()

    st.subheader("Skill comparison")
    chart = (
        alt.Chart(plot_df)
        .mark_bar()
        .encode(
            x=alt.X("skill:N", sort=top_skills, title="Skill"),
            y=alt.Y("mentions:Q", title="Mentions"),
            color=alt.Color("role:N", title="Role"),
            tooltip=[
                alt.Tooltip("role:N", title="Role"),
                alt.Tooltip("skill:N", title="Skill"),
                alt.Tooltip("mentions:Q", title="Mentions"),
                alt.Tooltip("share_of_postings:Q", title="Share", format=".1%"),
            ],
        )
        .properties(height=380)
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Skill table (long format)")
    counts_long_display = counts_long.copy()
    counts_long_display["Category"] = counts_long_display["skill"].map(SKILL_CATEGORIES).fillna("Other")
    counts_long_display["share_pct"] = (counts_long_display["share_of_postings"] * 100).round(1)
    st.dataframe(
        counts_long_display[["role", "skill", "Category", "mentions", "share_pct"]].sort_values(
            ["skill", "mentions"], ascending=[True, False]
        ),
        use_container_width=True,
        column_config={
            "share_pct": st.column_config.NumberColumn("share_of_postings", format="%.1f%%"),
        },
    )

    st.subheader("Skill table (wide format)")
    wide_mentions = counts_long.pivot_table(
        index="skill", columns="role", values="mentions", aggfunc="max", fill_value=0
    )
    wide_share_pct = (
        counts_long.pivot_table(
            index="skill", columns="role", values="share_of_postings", aggfunc="max", fill_value=0.0
        )
        * 100
    ).round(1)
    wide = pd.concat({"mentions": wide_mentions, "share_of_postings": wide_share_pct}, axis=1)
    wide_display = wide.loc[top_skills].copy()
    # Format the share section with a % sign (MultiIndex columns).
    share_cols = [c for c in wide_display.columns if isinstance(c, tuple) and c[0] == "share_of_postings"]
    for c in share_cols:
        wide_display[c] = wide_display[c].map(lambda x: f"{x:.1f}%")
    st.dataframe(wide_display, use_container_width=True)

    # --- New: category-level summary ---
    st.subheader("Skill categories")
    cat_df = counts_long.copy()
    cat_df["category"] = cat_df["skill"].map(SKILL_CATEGORIES).fillna("Other")

    cat_mentions = (
        cat_df.groupby(["role", "category"], as_index=False)["mentions"]
        .sum()
    )

    # Stable category ordering (if provided)
    cat_order = [c for c in SKILL_CATEGORY_ORDER if c in set(cat_mentions["category"])]
    if not cat_order:
        cat_order = sorted(cat_mentions["category"].unique().tolist())

    cat_chart = (
        alt.Chart(cat_mentions)
        .mark_bar()
        .encode(
            x=alt.X("category:N", sort=cat_order, title="Category",
                    axis=alt.Axis(labelAngle=0)),
            y=alt.Y("mentions:Q", title="Mentions (sum of skill mentions)"),
            color=alt.Color("role:N", title="Role"),
            tooltip=[
                alt.Tooltip("role:N", title="Role"),
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("mentions:Q", title="Mentions"),
            ],
        )
        .properties(height=300)
    )
    st.altair_chart(cat_chart, use_container_width=True)

    st.dataframe(
        cat_mentions.sort_values(["category", "mentions"], ascending=[True, False]),
        use_container_width=True,
    )

    if show_postings:
        st.subheader("Sample postings")
        preview_cols = ["role", "headline", "employer_name", "publication_date", "webpage_url"]
        preview_cols = [c for c in preview_cols if c in df_all.columns]
        st.dataframe(df_all[preview_cols].head(30), use_container_width=True)


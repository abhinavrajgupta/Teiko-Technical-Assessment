import os
import pandas as pd
import streamlit as st

OUTPUT_DIR = "outputs"


def get_output_path(filename):
    return os.path.join(OUTPUT_DIR, filename)


st.set_page_config(page_title="Teiko Technical Assessment Dashboard", layout="wide")

st.title("Teiko Technical Dashboard")
st.write("Interactive review of outputs.")

# Part 2
st.header("Part 2: Data Overview")

summary_path = get_output_path("part2_summary_table.csv")
if os.path.exists(summary_path):
    summary_df = pd.read_csv(summary_path)
    st.dataframe(summary_df, use_container_width=True)
else:
    st.warning("Part 2 outputs not found. Run `make pipeline` first.")

# Part 3
st.header("Part 3: Statistical Analysis")

plot_path = get_output_path("part3_boxplot.png")
stats_path = get_output_path("part3_statistical_results.csv")

col1, col2 = st.columns([2, 1])

with col1:
    if os.path.exists(plot_path):
        st.image(plot_path, caption="Relative frequencies by response group")
    else:
        st.warning("Part 3 boxplot not found. Run `make pipeline` first.")

with col2:
    if os.path.exists(stats_path):
        stats_df = pd.read_csv(stats_path)
        st.dataframe(stats_df, use_container_width=True)
    else:
        st.warning("Part 3 statistics not found. Run `make pipeline` first.")

# Part 4
st.header("Part 4: Data Subset Analysis")

project_counts_path = get_output_path("part4_project_counts.csv")
response_counts_path = get_output_path("part4_response_counts.csv")
sex_counts_path = get_output_path("part4_sex_counts.csv")
answer_path = get_output_path("part4_answer.txt")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Samples per Project")
    if os.path.exists(project_counts_path):
        st.dataframe(pd.read_csv(project_counts_path), use_container_width=True)
    else:
        st.warning("Project counts not found.")

with col2:
    st.subheader("Responders vs Non-responders")
    if os.path.exists(response_counts_path):
        st.dataframe(pd.read_csv(response_counts_path), use_container_width=True)
    else:
        st.warning("Response counts not found.")

with col3:
    st.subheader("Males vs Females")
    if os.path.exists(sex_counts_path):
        st.dataframe(pd.read_csv(sex_counts_path), use_container_width=True)
    else:
        st.warning("Sex counts not found.")

st.subheader("Average B Cells Answer")
if os.path.exists(answer_path):
    with open(answer_path, "r") as f:
        answer = f.read().strip()
    st.metric(
        label="Melanoma males, responders, time = 0, average B cells",
        value=answer
    )
else:
    st.warning("Final Part 4 answer not found.")

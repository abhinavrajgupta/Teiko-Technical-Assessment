import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu

DB_NAME = "teiko.db"
OUTPUT_DIR = "outputs"

POPULATIONS = [
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte",
]


def get_repo_root():
    return os.path.dirname(os.path.abspath(__file__))

def get_db_path():
    return os.path.join(get_repo_root(), DB_NAME)

def get_output_dir():
    output_dir = os.path.join(get_repo_root(), OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def main():
    db_path = get_db_path()
    output_dir = get_output_dir()

    conn = sqlite3.connect(db_path)

    try:
        # PART 2: Initial Analysis - Data Overview
        counts_df = pd.read_sql_query(
            """
            SELECT sample, population, count
            FROM cell_counts
            """,
            conn
        )

        total_counts_df = (
            counts_df.groupby("sample", as_index=False)["count"]
            .sum()
            .rename(columns={"count": "total_count"})
        )

        summary_df = counts_df.merge(total_counts_df, on="sample", how="left")
        summary_df["percentage"] = (
            summary_df["count"] / summary_df["total_count"] * 100
        )

        summary_df = summary_df[
            ["sample", "total_count", "population", "count", "percentage"]
        ].sort_values(["sample", "population"])

        summary_df.to_csv(
            os.path.join(output_dir, "part2_summary_table.csv"),
            index=False
        )

        print("Part 2 complete: outputs/part2_summary_table.csv created")

        # PART 3: Statistical Analysis
        metadata_df = pd.read_sql_query(
            """
            SELECT sample, condition, treatment, response, sample_type
            FROM samples
            """,
            conn
        )

        part3_df = summary_df.merge(metadata_df, on="sample", how="left")

        part3_df = part3_df[
            (part3_df["condition"].str.lower() == "melanoma") &
            (part3_df["treatment"].str.lower() == "miraclib") &
            (part3_df["sample_type"].str.lower() == "pbmc") &
            (part3_df["response"].str.lower().isin(["yes", "no"]))
        ].copy()

        part3_df["response_group"] = part3_df["response"].str.lower().map({
            "yes": "Responder",
            "no": "Non-responder"
        })

        plt.figure(figsize=(12, 6))
        sns.boxplot(
            data=part3_df,
            x="population",
            y="percentage",
            hue="response_group",
            order=POPULATIONS
        )
        plt.title("Melanoma PBMC Samples on Miraclib: Relative Frequencies by Response")
        plt.xlabel("Population")
        plt.ylabel("Relative Frequency (%)")
        plt.xticks(rotation=20)
        plt.tight_layout()
        plt.savefig(
            os.path.join(output_dir, "part3_boxplot.png"),
            dpi=300,
            bbox_inches="tight"
        )
        plt.close()

        stats_rows = []

        for population in POPULATIONS:
            population_df = part3_df[part3_df["population"] == population]

            responders = population_df[
                population_df["response"].str.lower() == "yes"
            ]["percentage"]

            non_responders = population_df[
                population_df["response"].str.lower() == "no"
            ]["percentage"]

            if len(responders) > 0 and len(non_responders) > 0:
                stat, p_value = mannwhitneyu(
                    responders,
                    non_responders,
                    alternative="two-sided"
                )
                significant = p_value < 0.05
            else:
                stat = None
                p_value = None
                significant = False

            stats_rows.append({
                "population": population,
                "n_responders": len(responders),
                "n_non_responders": len(non_responders),
                "mean_responder_percentage": responders.mean() if len(responders) > 0 else None,
                "mean_non_responder_percentage": non_responders.mean() if len(non_responders) > 0 else None,
                "mannwhitney_u_stat": stat,
                "p_value": p_value,
                "significant_p_lt_0_05": significant
            })

        stats_df = pd.DataFrame(stats_rows)
        stats_df.to_csv(
            os.path.join(output_dir, "part3_statistical_results.csv"),
            index=False
        )

        print("Part 3 complete: outputs/part3_boxplot.png created")
        print("Part 3 complete: outputs/part3_statistical_results.csv created")

        # PART 4: Data Subset Analysis
        baseline_df = pd.read_sql_query(
            """
            SELECT *
            FROM samples
            WHERE LOWER(condition) = 'melanoma'
              AND LOWER(treatment) = 'miraclib'
              AND LOWER(sample_type) = 'pbmc'
              AND time_from_treatment_start = 0
            """,
            conn
        )

        project_counts_df = (
            baseline_df.groupby("project")
            .size()
            .reset_index(name="count")
            .sort_values("project")
        )
        project_counts_df.to_csv(
            os.path.join(output_dir, "part4_project_counts.csv"),
            index=False
        )

        response_counts_df = (
            baseline_df.groupby("response")
            .size()
            .reset_index(name="count")
            .sort_values("response")
        )
        response_counts_df.to_csv(
            os.path.join(output_dir, "part4_response_counts.csv"),
            index=False
        )

        sex_counts_df = (
            baseline_df.groupby("sex")
            .size()
            .reset_index(name="count")
            .sort_values("sex")
        )
        sex_counts_df.to_csv(
            os.path.join(output_dir, "part4_sex_counts.csv"),
            index=False
        )

        avg_bcell_df = pd.read_sql_query(
            """
            SELECT AVG(cc.count) AS avg_b_cell
            FROM samples s
            JOIN cell_counts cc
              ON s.sample = cc.sample
            WHERE LOWER(s.condition) = 'melanoma'
              AND LOWER(s.treatment) = 'miraclib'
              AND LOWER(s.sample_type) = 'pbmc'
              AND s.time_from_treatment_start = 0
              AND LOWER(s.sex) = 'male'
              AND LOWER(s.response) = 'yes'
              AND cc.population = 'b_cell'
            """,
            conn
        )

        avg_b_cell = avg_bcell_df.loc[0, "avg_b_cell"]

        with open(os.path.join(output_dir, "part4_answer.txt"), "w") as f:
            if pd.notna(avg_b_cell):
                f.write(f"{avg_b_cell:.2f}\n")
            else:
                f.write("No matching samples found.\n")

        print("Part 4 complete: outputs/part4_project_counts.csv created")
        print("Part 4 complete: outputs/part4_response_counts.csv created")
        print("Part 4 complete: outputs/part4_sex_counts.csv created")

        if pd.notna(avg_b_cell):
            print(f"The average number of B cells for responders at time=0: {avg_b_cell:.2f}")
        else:
            print("The average number of B cells for responders at time=0: No samples found.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()

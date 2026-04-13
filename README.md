# Teiko Technical Assessment

## Overview

This project is my solution to the Teiko technical assessment.

The goal of this project is to analyze immune cell population data from `cell-count.csv`, store the data in a relational SQLite database, generate summary tables and statistical outputs, and provide an interactive dashboard to review the results.

The project is organized around the four required parts in the prompt:

- **Part 1: Data Management**
- **Part 2: Initial Analysis – Data Overview**
- **Part 3: Statistical Analysis**
- **Part 4: Data Subset Analysis**

I also included:

- a **Makefile** with the exact targets requested in the prompt,
- a **README.md** with setup and run instructions,
- generated output files,
- and a **Streamlit dashboard** to explore the results interactively.

---

## Repository Structure

The repository is intentionally kept simple so that it is easy to run, test, and grade in GitHub Codespaces.

```text
.
├── cell-count.csv
├── load_data.py
├── run_analysis.py
├── app.py
├── requirements.txt
├── Makefile
├── README.md
├── teiko.db                  # created after running the pipeline
└── outputs/                  # created after running the pipeline
    ├── part2_summary_table.csv
    ├── part3_boxplot.png
    ├── part3_statistical_results.csv
    ├── part4_project_counts.csv
    ├── part4_response_counts.csv
    ├── part4_sex_counts.csv
    └── part4_answer.txt
```

### Main files

- **`load_data.py`**
  - Implements **Part 1**
  - Creates the SQLite database
  - Loads `cell-count.csv` into database tables

- **`run_analysis.py`**
  - Implements **Part 2, Part 3, and Part 4**
  - Generates summary tables, statistical results, plots, and subset outputs

- **`app.py`**
  - Implements the interactive dashboard
  - Reads the generated outputs and displays them in a Streamlit app

- **`Makefile`**
  - Provides the exact required commands:
    - `make setup`
    - `make pipeline`
    - `make dashboard`

---

## How to Run the Project

The assignment states that the project will be tested using **GitHub Codespaces**, so I designed the project to run with only the Makefile commands.

### Step 1: Open in GitHub Codespaces

1. Clone the repository to your GitHub space.
2. Open the repository in your browser.
3. Click **Code**.
4. Click the **Codespaces** tab.
5. Click **Create codespace on main**.

This will open a browser-based development environment with a terminal.

---

### Step 2: Install dependencies

Run:

```bash
make setup
```

This installs the dependencies from `requirements.txt`.

---

### Step 3: Run the full pipeline

Run:

```bash
make pipeline
```

This executes the full project from start to finish without any manual intervention.

Specifically, this command does the following:

1. Creates the SQLite database
2. Loads the CSV data into the database
3. Builds the Part 2 summary table
4. Runs the Part 3 statistical analysis
5. Generates the Part 3 boxplot
6. Runs the Part 4 subset analysis
7. Writes all output files to the `outputs/` folder

After this step, the database file `teiko.db` and the output files in `outputs/` should exist.

---

### Step 4: Run the dashboard

Run:

```bash
make dashboard
```

This starts the Streamlit dashboard locally.

When Streamlit starts, it will print a local URL in the terminal. It usually looks like this:

```text
http://localhost:8501
```

If you are using GitHub Codespaces, the port will usually be forwarded automatically. You can open the forwarded port in the browser from the **Ports** tab in Codespaces.

---

## Dashboard Link

The prompt asks for a link to the dashboard. The dashboard is started locally using:

```bash
make dashboard
```

In local development or GitHub Codespaces, the dashboard link is the forwarded Streamlit URL shown after launch, usually on port `8501`.

### Example

- Local URL: `http://localhost:8501`
- In GitHub Codespaces: use the forwarded URL provided by Codespaces for port 8501

### Important note

Because GitHub Codespaces generates a temporary forwarded URL, the exact dashboard link may change across sessions. For grading and reproduction, the correct way to access the dashboard is:

1. run `make dashboard`
2. open the forwarded Streamlit URL shown in Codespaces

---

## Makefile Commands

The prompt requires these exact Makefile targets.

### `make setup`

Installs all dependencies.

```bash
make setup
```

### `make pipeline`

Runs the entire data pipeline end-to-end.

```bash
make pipeline
```

This includes:
- Part 1 database creation and data loading
- Part 2 summary table generation
- Part 3 boxplot and significance testing
- Part 4 subset analysis and final answer file

### `make dashboard`

Starts the local server for the dashboard.

```bash
make dashboard
```

---

## Part 1: Database Design

Part 1 of the prompt asks for a relational database schema using SQLite and a script named `load_data.py` in the repository root that creates the database and loads all rows from `cell-count.csv`.

### Tables used

I used **2 database tables**:

1. **`samples`**
2. **`cell_counts`**

This design keeps the database simple and avoids confusion while still supporting all later analyses.

---

### Table 1: `samples`

This table stores one row per sample and keeps the sample metadata.

Columns:

- `sample` — primary key
- `project`
- `subject`
- `condition`
- `age`
- `sex`
- `treatment`
- `response`
- `sample_type`
- `time_from_treatment_start`

This table answers questions such as:

- Which samples are melanoma?
- Which samples are PBMC?
- Which samples are responders?
- Which baseline samples are from miraclib-treated patients?

---

### Table 2: `cell_counts`

This table stores immune cell counts in a **long format**.

Columns:

- `id` — primary key
- `sample` — foreign key to `samples.sample`
- `population`
- `count`

Each sample has 5 rows in this table, one for each immune cell population:

- `b_cell`
- `cd8_t_cell`
- `cd4_t_cell`
- `nk_cell`
- `monocyte`

### Example

If one sample in the CSV contains:

- `b_cell = 10908`
- `cd8_t_cell = 24440`
- `cd4_t_cell = 20491`
- `nk_cell = 13864`
- `monocyte = 23511`

then this becomes 5 rows in `cell_counts`:

| sample | population | count |
|---|---|---:|
| sample00000 | b_cell | 10908 |
| sample00000 | cd8_t_cell | 24440 |
| sample00000 | cd4_t_cell | 20491 |
| sample00000 | nk_cell | 13864 |
| sample00000 | monocyte | 23511 |

---

## Why I chose this schema

I chose this schema because it is both simple and useful.

### Why not keep everything in one wide table?

The original CSV is in a wide format, where each immune cell population has its own column. That is fine for raw storage, but it is less convenient for analytics.

For example, in Part 2 and Part 3, I need to:
- compare populations,
- calculate percentages,
- group by population,
- make boxplots by population,
- and run statistical tests per population.

Those tasks are much easier when the population names are stored in one column (`population`) and the corresponding numeric values are stored in another column (`count`).

### Example rationale

For example, if I had kept all five populations as separate columns everywhere, then each comparison would need custom code for `b_cell`, then separate code again for `cd8_t_cell`, and so on. By reshaping the data into the `cell_counts` table, I can handle all five populations uniformly using grouping, filtering, plotting, and statistical testing.

---

## How this schema scales

The prompt asks how the design would scale to hundreds of projects, thousands of samples, and different analytics workloads.

This design scales reasonably well for that case.

### Why it scales

- The `samples` table stores metadata once per sample.
- The `cell_counts` table stores repeated per-population measurements in a normalized structure.
- If new immune cell populations are added later, I would not need to redesign the schema. I would simply insert more rows into `cell_counts`.
- If there are many more projects or samples, queries can still be written cleanly using joins between `samples` and `cell_counts`.
- This design also works well for dashboards, summary statistics, subgroup analysis, and future machine learning feature generation.

### Example

For example, if there were 200 projects, 20,000 samples, and 25 immune cell populations instead of 5, I could still use the same schema. The only difference would be more rows in `cell_counts`, not a redesign of the whole database.

That is why I chose this design: it is simple enough for this assessment, but flexible enough for larger data. If the dataset became very large in a real-world setting, performance could be improved further through batching, indexing, and parallel processing. For example, parts of the pipeline such as file preprocessing, summary generation, or independent analyses could be parallelized to make use of additional CPU cores.
---

## Part 2: Initial Analysis – Data Overview

Part 2 asks:

> “What is the frequency of each cell type in each sample?” 

To answer this, I compute a summary table where each row represents one population from one sample.

The required columns are:

- `sample`
- `total_count`
- `population`
- `count`
- `percentage`

### What these mean

- **`count`**
  - the raw count for one immune cell population in one sample
- **`total_count`**
  - the sum of all 5 population counts for that sample
- **`percentage`**
  - the relative frequency of that population in the sample

### Formula used

For each sample:

```text
total_count = b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte
```

Then for each population:

```text
percentage = (count / total_count) * 100
```

### Example

For example, if a sample has:

- `b_cell = 10908`
- `cd8_t_cell = 24440`
- `cd4_t_cell = 20491`
- `nk_cell = 13864`
- `monocyte = 23511`

then:

```text
total_count = 93214
```

and:

```text
b_cell percentage = 10908 / 93214 * 100 = 11.70
```

The Part 2 result is saved as:

- `outputs/part2_summary_table.csv`

---

## Part 3: Statistical Analysis

Part 3 asks for a comparison of **melanoma PBMC samples treated with miraclib**, grouped by **responders** vs **non-responders**, using the relative frequencies calculated in Part 2. It also asks for boxplots and statistical evidence of significance.
### Filters used

I filtered the data to include only samples where:

- `condition = melanoma`
- `treatment = miraclib`
- `sample_type = PBMC`
- `response` is `yes` or `no`

### What was compared

For each immune cell population:

- `b_cell`
- `cd8_t_cell`
- `cd4_t_cell`
- `nk_cell`
- `monocyte`

I compared the **percentage values** between:
- responders
- non-responders

### Plot used

I created a **boxplot** for each immune cell population showing the relative frequency distribution in the two response groups.

This is saved as:

- `outputs/part3_boxplot.png`

### Statistical test used

I used the **Mann–Whitney U test** to compare responders vs non-responders for each population.

### Why I chose this test

I chose Mann–Whitney U because:

- the comparison is between **two groups**
- the data being compared are **percentages**
- in this kind of biological data, distributions are often **not normally distributed**
- sample sizes may be small
- this is a common and reasonable non-parametric choice for immune profiling comparisons

### Example justification

For example, if CD8 T-cell frequencies are higher in responders than in non-responders, Mann–Whitney U helps test whether that difference is likely to be real rather than random variation.

This is saved as:

- `outputs/part3_statistical_results.csv`

### Important note

If a test dataset does not contain both melanoma responders and melanoma non-responders, then a valid statistical comparison cannot be made. In that case, the code still runs, but the corresponding p-values may be missing.

---

## Part 4: Data Subset Analysis

Part 4 asks for a focused subset analysis on:

- melanoma
- PBMC
- miraclib-treated samples
- baseline only, where `time_from_treatment_start = 0`

### Step 1

Identify all melanoma PBMC baseline samples from patients treated with miraclib.

### Step 2

Within that subset, compute:

- how many samples came from each project
- how many were responders vs non-responders
- how many were males vs females

### Step 3

Answer the final question:

> Considering melanoma males, what is the average number of B cells for responders at time = 0? 

### Output files

Part 4 generates:

- `outputs/part4_project_counts.csv`
- `outputs/part4_response_counts.csv`
- `outputs/part4_sex_counts.csv`
- `outputs/part4_answer.txt`

### Example justification

For example, if Bob wants to understand early treatment effects specifically at baseline, this filter isolates the exact subset the prompt asks for. Then the project, response, and sex counts summarize the composition of that subset, while the B-cell average answers the final question directly.

---

## Code Structure and Design Choices

The prompt asks for a brief overview of the code structure and why it was designed this way. 

I intentionally kept the project structure simple.

### `load_data.py`

This file only handles Part 1.

It:
- checks that `cell-count.csv` exists
- creates the SQLite database
- creates the two tables
- loads the data into the database

I kept this separate because database initialization is logically different from downstream analytics.

### `run_analysis.py`

This file handles Part 2, Part 3, and Part 4 in sequence.

I chose to keep Parts 2–4 together because:
- Part 3 depends on the summary table from Part 2
- Part 4 queries the same database and generated results
- the pipeline becomes easier to run and easier to grade
- the file reads in the same order as the assignment prompt

### `app.py`

This file is only for the dashboard.

It reads the generated output files and displays them interactively using Streamlit.

### Why this structure works well

For example, if the grader wants to verify only the data loading step, they can inspect `load_data.py`. If they want to verify all analysis outputs, they can inspect `run_analysis.py`. If they want to see the user-facing interface, they can run `app.py` through `make dashboard`.

This separation keeps the project organized without making it overly complex.

---

## Output Files

After running:

```bash
make pipeline
```

the following files should be created:

- `teiko.db`
- `outputs/part2_summary_table.csv`
- `outputs/part3_boxplot.png`
- `outputs/part3_statistical_results.csv`
- `outputs/part4_project_counts.csv`
- `outputs/part4_response_counts.csv`
- `outputs/part4_sex_counts.csv`
- `outputs/part4_answer.txt`

These files correspond directly to the outputs requested across Parts 1–4. 

---

## How to Verify Everything Works

A good test sequence is:

```bash
make setup
make pipeline
make dashboard
```

### After `make pipeline`

Check that:
- the database file exists
- the `outputs/` folder exists
- all expected output files are present

Useful commands:

```bash
ls
ls outputs
head outputs/part2_summary_table.csv
cat outputs/part3_statistical_results.csv
cat outputs/part4_answer.txt
```

### After `make dashboard`

Check that:
- Streamlit starts successfully
- the dashboard opens in the browser
- the summary table is visible
- the Part 3 boxplot is visible
- the statistics table is visible
- the Part 4 summary tables are visible
- the final B-cell answer is displayed

---

## Notes

- The database column names were kept close to the CSV field names to reduce confusion and make querying easier.
- The project is designed for reproducibility first: simple structure, direct Makefile targets, and outputs written to a single folder.

---

## Final Summary

This project provides:

- a relational SQLite database for the sample data
- a reproducible data pipeline
- summary tables for cell frequency analysis
- statistical testing and visualization for response analysis
- targeted subset analysis for baseline melanoma PBMC samples
- an interactive dashboard
- and the required Makefile commands for grading in GitHub Codespaces

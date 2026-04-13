import os
import sqlite3
import pandas as pd 

DB_NAME = "teiko.db"
CSV_NAME = "cell-count.csv"

POPULATION_COLUMNS = [
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte",
]


def get_repo_root():
    return os.path.dirname(os.path.abspath(__file__))


def get_csv_path():
    return os.path.join(get_repo_root(), CSV_NAME)


def get_db_path():
    return os.path.join(get_repo_root(), DB_NAME)


def read_csv(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = [col.strip() for col in df.columns]
    return df


def initialize_database(conn):
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS cell_counts;")
    cur.execute("DROP TABLE IF EXISTS samples;")

    cur.execute(
        """
        CREATE TABLE samples (
            sample TEXT PRIMARY KEY,
            project TEXT,
            subject TEXT,
            condition TEXT,
            age REAL,
            sex TEXT,
            treatment TEXT,
            response TEXT,
            sample_type TEXT,
            time_from_treatment_start REAL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE cell_counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample TEXT NOT NULL,
            population TEXT NOT NULL,
            count INTEGER NOT NULL,
            FOREIGN KEY(sample) REFERENCES samples(sample)
        );
        """
    )

    conn.commit()


def load_samples_table(conn, df):
    samples_df = df[
        [
            "sample",
            "project",
            "subject",
            "condition",
            "age",
            "sex",
            "treatment",
            "response",
            "sample_type",
            "time_from_treatment_start",
        ]
    ].drop_duplicates()

    samples_df.to_sql("samples", conn, if_exists="append", index=False)


def load_cell_counts_table(conn, df):
    long_df = df.melt(
        id_vars=["sample"],
        value_vars=POPULATION_COLUMNS,
        var_name="population",
        value_name="count",
    )

    long_df["count"] = long_df["count"].astype(int)

    long_df.to_sql("cell_counts", conn, if_exists="append", index=False)


def main():
    csv_path = get_csv_path()
    db_path = get_db_path()

    df = read_csv(csv_path)

    conn = sqlite3.connect(db_path)
    try:
        initialize_database(conn)
        load_samples_table(conn, df)
        load_cell_counts_table(conn, df)
    finally:
        conn.close()

    print(f"Database created: {db_path}")
    print("Part I complete: Database Management")

if __name__ == "__main__":
    main()

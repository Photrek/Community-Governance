import duckdb
import glob


def load(con: duckdb.DuckDBPyConnection, model_path: str):
    """
    Creates a table from a SQL script file similar to dbt.
    """

    model_name = model_path.split('/')[-1].split('.')[0]
    print("create table", model_name)
    with open(model_path, 'r') as file:
        sql_script = file.read()
        con.sql(f"CREATE TABLE IF NOT EXISTS {model_name} AS {sql_script}")

def load_all(con: duckdb.DuckDBPyConnection, path: str):
    for model_path in glob.glob(f"{path}/silver*.sql"):
        print("loading", model_path)
        load(con, model_path)

    gold_transformations(con)

def gold_transformations(con: duckdb.DuckDBPyConnection, path: str):
    for model_path in glob.glob(f"{path}/gold*.sql"):
        print("loading", model_path)
        load(con, model_path)


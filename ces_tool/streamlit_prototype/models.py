import duckdb
import glob


def load(con: duckdb.DuckDBPyConnection, model_path: str, model_name: str = None):
    """
    Creates a table from a SQL script file similar to dbt.
    """

    file_model_name = model_path.split('/')[-1].split('.')[0]
    if model_name is None:
        model_name = file_model_name
    print("create table", model_name)
    with open(model_path, 'r') as file:
        sql_script = file.read()
        con.sql(f"CREATE TABLE IF NOT EXISTS {model_name} AS {sql_script}")

def perform_transformations(con: duckdb.DuckDBPyConnection, path: str):
    for model_path in glob.glob(f"{path}/*.sql"):
        print("loading", model_path)
        load(con, model_path)


# CES MVP

CES MVP demonstrating Meltano (extract & load), dbt-core (transformation) and evidence (ui).

## Getting Started
* Install DuckDB `brew install duckdb`
* Make sure to install pipenv `brew install pipenv`
* Place the data in the `extract` folder (not included in the repo, but you can download it from [here](https://docs.google.com/spreadsheets/d/1S8AGK7ffVEu9La73yrv9BKlPMvocq9w1RPCjPrn1w6Q/edit#gid=706641192))
    * `answers.csv`
    * `questions.csv`
    * `users.csv`
    * `wallet-links.csv`
* Perform the whole ELT process `pipenv run meltano run --full-refresh tap-csv target-duckdb dbt-duckdb:run`
    > This will create `output/warehouse.duckdb` and is used by evidence or can be queried directly using `duckdb output/warehouse.duckdb`
* Launch evidence UI `pipenv run meltano invoke evidence dev` and open `http://localhost:3000` in your browser to explore the data

## Development
* For example you want to add a new .csv file to the ELT process
    * In the `meltano.yml` and add the new csv file to the `files` section of the `tap-csv` extractor and add the file to the `extract` folder
    * In the `transfom/models/bronze/source.yml` add your new table
    * In the `transfom/models/silver/<your-new-model>.sql` add your new model converting it to the correct data types
    * In the `transfom/models/gold/<your-new-model>.sql` add your new model with the final transformations you want to use in the evidence UI
    * In the `analyze/evidence/sources/ces_mvp` add your new a new data source definition in sql (NOTE: this will be converted to parquet and used by evidence)
    * In `analyze/evidence/pages` either adjust the index.md or add a new one and make use of your new datasource (aka name of the .sql files you added int the previous step)
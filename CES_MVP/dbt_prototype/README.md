# DBT & Evidence prototype

# Setup
* Install DuckDB `brew install duckdb`
* Install pipenv `brew install pipenv`
* Install nvm `brew install nvm`
* Install dependencies `make setup`
* Place the data in the `data` folder (not included in the repo, but you can download it from [here](https://docs.google.com/spreadsheets/d/1S8AGK7ffVEu9La73yrv9BKlPMvocq9w1RPCjPrn1w6Q/edit#gid=706641192))
    * `answers.csv`
    * `questions.csv`
    * `users.csv`
    * `wallet-links.csv`
* Run dbt transformations `make run`
* Inspect data using `make db`
* Inspect documentation `make docs`

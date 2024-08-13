# DBT & Evidence prototype

# Setup
* Install DuckDB `brew install duckdb`
* Install pipenv `brew install pipenv`
* Install nvm `brew install nvm`
* Install dependencies `make setup`
* Place the data in the `data` folder (not included in the repo, but can be downloaded from [here](https://docs.google.com/spreadsheets/d/1S8AGK7ffVEu9La73yrv9BKlPMvocq9w1RPCjPrn1w6Q/edit#gid=706641192))
    * `answers.csv`
    * `questions.csv`
    * `users.csv`
    * `wallet-links.csv`
* Run the whole ELT process `make generate` which will also export the voting results to `exports/dfr4_voting_results.csv`
    * (Optional) Run `make reports` to start the evidence UI to analyze the data
* (Optional) Alternatively you can run `make ui` to perform the ELT pipeline and start the UI
* (Optional) Run `make docs` to start the dbt documentation server
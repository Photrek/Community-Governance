# 001 Use Meltano DBT Core and Evidence

## Status

Accepted

## Context

We need to decide on the technology stack for the data transformation and modeling layer of the CES MVP. We have identified the following requirements:

- We need to be able to transform and model data from multiple sources (e.g. DeepFund, Voting Portal, Wallets, etc.)
- We need to be able to run the transformations and models on a schedule


## Decision

We will use Meltano and DBT Core for the data transformation and modeling layer and Evidence for the visualization of the data.

## Consequences

- We will need to do the transformation and modeling work in SQL

Alternative technologies were considered, such as [RillData](https://docs.rilldata.com/), but Meltano and DBT Core were chosen because they are more flexible.


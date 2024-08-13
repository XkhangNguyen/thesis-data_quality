# Data Quality Project

## Overview

This project utilizes Great Expectations, an open-source library, to define, manage, and evaluate data expectations. Great Expectations helps ensure data quality, reliability, and consistency by enabling the specification of expectations for datasets and validating them against actual data.

## Features

- **Automated Testing**: Automate the testing process by integrating with Airflow to continuously monitor and ensure data integrity.
- **Datadocs**: UI to document and visualize data quality metrics and validation results, providing insights into the integrity of data assets.
- **MT notifications**: Integrate Microsoft Teams notifications for immediate updates on validation results.

## Resources

- **Data Sources**: The sources from which data is retrieved.
- **Data Assets**:
  - These are representations of data in the form of queries to which tests are applied. They are named based on their function and are stored in folders named after the database containing the data.
  - **name**: This should be defined based on the purpose or goal for which the data is used. Each name must be unique within a data asset YAML file.
  - **query**: SQL statements to retrieve data to be test.
  - **suffix**:
- **Expectation Suites**: Sets of expectations applied to data.
- **Expectations**:
  - Rules that tests must follow.
  - **expectation_type**: The type of expectation.
  - **kwargs**: Additional parameters for the expectation.
- **Jobs**:
  - Defines tests on data by specifying which data assets to use with a suite.
  - Tags: A job can have multiple tags. All jobs with satisfied tags will be run. Multiple tags can be seperated by '-'.

## Arguments Retrieved from Airflow

- **start_date**: start_date param that can be used in query
- **end_date**: end_date param that can be used in query
- **job_name**: name of the job to run individually
- **job_tags**: jobs that have all tags matched will be run
- **webhook**: optional webhook for Teams notification

## Getting Started

To get started with this project, follow these steps:

1. Clone this repository

2. Install requirements:

   ```bash
   pip3 install -r requirements.txt
   ```

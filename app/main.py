from datetime import datetime
import os
from typing import List, Union
import yaml
import argparse

import great_expectations as gx
from great_expectations.data_context import FileDataContext
from great_expectations.core.expectation_suite import ExpectationConfiguration
from great_expectations.exceptions.exceptions import (
    InvalidExpectationConfigurationError,
)
from great_expectations.checkpoint.configurator import ActionDict

from models.suite import Suite
from models.job import Job

from utils.job_selector_factory import JobSelectorFactory
from utils.logger import logger
from core.config import settings


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_date", type=str)
    parser.add_argument("--end_date", type=str)
    parser.add_argument("--job_name", type=str)
    parser.add_argument("--job_tags", type=str)
    parser.add_argument("--webhook", type=str)
    return parser.parse_args()


def load_context(project_path, runtime_environment=None):
    """
    Loads the Great Expectations context from path.

    Args:
        project_path (str): The path to the project.
    """
    return gx.get_context(
        project_root_dir=project_path, runtime_environment=runtime_environment
    )


def load_data_source(context: FileDataContext, ds_name):
    """
    Loads the data source.

    Args:
        context (gx.data_context.DataContext): The Great Expectations context.
        env (str): The environment.
    """
    data_source_path = os.path.join(
        project_path, "resources/data_sources", f"{ds_name}.yml"
    )
    with open(data_source_path, "r") as file:
        data_source_params = yaml.safe_load(file)
    return context.sources.add_or_update_postgres(
        data_source_params["name"],
        connection_string=data_source_params["connection_string"],
    )


def build_suite(context, suite_config: Suite):
    """
    Builds an expectation suite.

    Args:
        context: The Great Expectations context.
        suite_config (Suite): The suite configuration.

    Returns:
        str: The name of the created suite.
    """
    suite_name = suite_config.name
    suite = context.add_or_update_expectation_suite(expectation_suite_name=suite_name)
    for expectation in suite_config.expectations:
        expectation = ExpectationConfiguration(
            expectation_type=expectation.expectation_type, kwargs=expectation.kwargs
        )
        suite.add_expectation(expectation)
    context.update_expectation_suite(suite)
    return suite_name


def log_jobs_run(jobs: List[Job]):
    """
    Logs the jobs to be run.

    Args:
        jobs (List[Job]): The list of jobs.
    """
    job_names = ", ".join(job.name for job in jobs)
    logger.info("%s", "========================================================")
    logger.info("")
    logger.info("Jobs to be run: " + job_names)
    logger.info("")
    logger.info("%s", "========================================================")


def build_validations(context, data_source, jobs: Union[Job, List[Job]]):
    """
    Builds validations for the given jobs.

    Args:
        context: The Great Expectations context.
        data_source: The data source.
        jobs (Union[Job, List[Job]]): The job or list of jobs.

    Returns:
        List[dict]: The list of validations.
    """
    validations = []

    if isinstance(jobs, Job):
        jobs = [jobs]

    log_jobs_run(jobs)

    for job in jobs:
        for run in job.runs:
            for data_asset_config in run.data_assets:
                # find asset with name, if not found then create one.
                try:
                    data_asset = data_source.get_asset(data_asset_config.name)
                except:
                    data_asset = data_source.add_query_asset(
                        name=data_asset_config.name, query=data_asset_config.query
                    )
                batch_request = data_asset.build_batch_request()
                suite_name = build_suite(context, run.suite)
                validations.append(
                    {
                        "batch_request": batch_request,
                        "expectation_suite_name": suite_name,
                    }
                )
    return validations


def build_teams_noti_action(notify_on: str, webhook: str) -> ActionDict:
    """
    Builds an Microsoft Teams notification action configuration dictionary.

    Args:
        notify_on (str): The event to notify on (Possible values: "all", "failure", "success")
        webhook(str): The webhook for Microsoft Teams
    Returns:
        Dict[str, dict]: The MicrosoftTeamsNotificationAction configurations dictionary.
    """
    return {
        "name": "send_teams_noti_on_validation_result",
        "action": {
            "class_name": "MicrosoftTeamsNotificationAction",
            "notify_on": notify_on,
            "microsoft_teams_webhook": webhook,
            "renderer": {
                "module_name": "great_expectations.render.renderer.microsoft_teams_renderer",
                "class_name": "MicrosoftTeamsRenderer",
            },
        },
    }


def run_checkpoint(context, job_name, validations, webhook):
    """
    Runs a checkpoint.

    Args:
        context: The Great Expectations context.
        job_name (StrictStr): The name of the job.
        validations (List[dict]): The list of validations.
        webhook: The Microsoft Teams webhook for trigger notification
    Returns:
        gx.checkpoint.CheckpointResult: The result of the checkpoint run.
    """

    action_list = [
        {
            "name": "store_validation_result",
            "action": {"class_name": "StoreValidationResultAction"},
        },
        {
            "name": "store_evaluation_params",
            "action": {"class_name": "StoreEvaluationParametersAction"},
        },
        {"name": "update_data_docs", "action": {"class_name": "UpdateDataDocsAction"}},
    ]

    action_list.append(build_teams_noti_action("failure", webhook))

    checkpoint = context.add_or_update_checkpoint(
        name=job_name,
        run_name_template=job_name,
        validations=validations,
        action_list=action_list,
    )
    return checkpoint.run()


if __name__ == "__main__":
    args = parse_arguments()
    env = settings.env
    project_path = settings.project_path
    webhook = args.webhook if args.webhook else settings.microsoft_teams_webhook
    logger.info("Job name: %s", args.job_name)
    logger.info("Tags: %s", args.job_tags)
    logger.info("Using webhook: %s", webhook)

    try:
        context = load_context(project_path, runtime_environment={"ENV": env})
        data_source = load_data_source(context, "staging_postgres")
        if args.job_name:
            jobs = JobSelectorFactory.select_job(args.job_name)
            validations = build_validations(context, data_source, jobs)
            checkpoint_result = run_checkpoint(
                context, args.job_name, validations, webhook
            )
        elif args.job_tags:
            tags_list = args.job_tags.split("-")
            jobs = JobSelectorFactory.select_job(tags_list)
            validations = build_validations(context, data_source, jobs)
            checkpoint_result = run_checkpoint(
                context, args.job_tags, validations, webhook
            )
        else:
            raise Exception("No job name or tags provided")
        logger.info("result ----- %s", checkpoint_result)
        if not checkpoint_result.success:
            raise Exception("Expectations are not met")

    except InvalidExpectationConfigurationError as error:
        raise Exception("ERROR: " + error.message)
    except Exception as error:
        raise Exception("ERROR: ", error)

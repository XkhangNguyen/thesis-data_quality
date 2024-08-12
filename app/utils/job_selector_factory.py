from typing import List, Union
import os
from pydantic import StrictStr
import yaml
from utils.selector import select_asset, select_suite
from models.job import Job, Run
from core.config import settings


class JobSelectorFactory:
    @staticmethod
    def select_job(fname_or_tags: Union[str, list]) -> List[Job]:
        """
        Selects job(s) based on either a filename or a list of tags.

        Args:
            fname_or_tags (Union[str, list]): Either a filename (str) or a list of tags (List[str]).

        Returns:
            List[Job]: A list of Job objects selected based on the input argument.

        Raises:
            ValueError: If the input argument is not of type str or List[str].
        """
        if isinstance(fname_or_tags, str):
            return JobSelectorFactory._select_job_by_filename(fname_or_tags)
        elif isinstance(fname_or_tags, list):
            return JobSelectorFactory._select_jobs_by_tags(fname_or_tags)
        else:
            raise ValueError("Invalid argument type. Expected str or List[str].")

    @staticmethod
    def _select_job_by_filename(fname: str) -> Job:
        """
        Selects a job based on the filename.

        Args:
            fname (str): The filename of the job configuration.

        Returns:
            Job: The Job object corresponding to the filename.

        Raises:
            ValueError: If no job is found for the given filename.
        """
        sub_folder, job_name = fname.split(".")
        path = os.path.join(
            settings.project_path, "resources/jobs", sub_folder, job_name + ".yml"
        )
        job_data = yaml.safe_load(open(path))
        if job_data:
            job = handle_job_data(job_data)
        else:
            raise ValueError(f"No job found for filename: {fname}")
        return job

    @staticmethod
    def _select_jobs_by_tags(tags: List[StrictStr]) -> List[Job]:
        """
        Selects jobs based on a list of tags.

        Args:
            tags (List[StrictStr]): A list of tags to filter jobs.

        Returns:
            List[Job]: A list of Job objects that match the given tags.

        Raises:
            ValueError: If no jobs are found for the given tags.
        """
        jobs = []
        for root, dirs, files in os.walk(
            os.path.join(settings.project_path, "resources/jobs")
        ):
            for file in files:
                if file.endswith(".yml"):
                    file_path = os.path.join(root, file)
                    job_data = yaml.safe_load(open(file_path))
                    job = handle_job_data(job_data)
                    if all(tag in job.tags for tag in tags):
                        jobs.append(job)
        if len(jobs) == 0:
            raise ValueError(f"No job found for tags: {tags}")
        return jobs


def handle_job_data(job_data: dict) -> Job:
    """
    Creates a Job object based on job data.

    Args:
        job_data (dict): Dictionary containing the job configuration data.

    Returns:
        Job: A Job object created from the job data.
    """
    runs = []
    for run in job_data.get("runs"):
        data_assets = []
        for data_asset_name in run["data_assets"]:
            data_asset = select_asset(data_asset_name)
            data_assets.append(data_asset)
        suite = select_suite(run["suite"])
        runs.append(Run(data_assets=data_assets, suite=suite))
    return Job(name=job_data.get("name"), runs=runs, tags=job_data.get("tags"))
4
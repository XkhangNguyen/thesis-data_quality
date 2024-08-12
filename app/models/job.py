from typing import List, Optional
from pydantic import BaseModel, StrictStr

from models.suite import Suite
from models.data_asset import DataAsset


class Run(BaseModel):
    """
    Represents a run configuration containing data assets and a suite.

    Attributes:
        data_assets (List[DataAsset]): A list of data assets for the run.
        suite (Suite): The suite configuration for the run.
    """

    data_assets: List[DataAsset]
    suite: Suite


class Job(BaseModel):
    """
    Represents a job configuration containing its name and runs.

    Attributes:
        name (StrictStr): The name of the job.
        runs (List[Run]): A list of run configurations for the job.
        tags (Optional[List[StrictStr]]): A list of tags for the job.
    """

    name: StrictStr
    runs: List[Run]
    tags: Optional[List[StrictStr]]

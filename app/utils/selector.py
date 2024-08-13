import os
from models.suite import Expectation, Suite
from models.data_asset import DataAsset
from core.config import settings
import yaml


def select_asset(fname: str) -> DataAsset:
    """
    Selects a data asset based on the given full name, including subfolder to the file.
    Eg: way4.doc (subfolder is way4, doc is the DataAsset name)

    Args:
        fname (str): The full name of the data asset.

    Returns:
        DataAsset: The selected data asset.

    Raises:
        Exception: If the data asset with the given filename is not found.
    """
    tbl_name, asset_name = fname.split(".")
    path = os.path.join(
        settings.project_path, "resources/data_assets", tbl_name + ".yml"
    )
    assets = yaml.safe_load(open(path))["data_assets"]
    for asset in assets:
        if asset.get("name") == asset_name:
            return DataAsset(name=fname, query=asset["query"])
    raise Exception(f"Asset {fname} is not found")


def select_suite(suite_name: str) -> Suite:
    """
    Selects a suite configuration based on the given suite name.

    Args:
        suite_name (str): The name of the suite.

    Returns:
        Suite: The selected suite configuration.

    Raises:
        Exception: If the suite with the given name is not found.
    """
    path = os.path.join(settings.project_path, "resources/suites", suite_name + ".yml")
    suite_data = yaml.safe_load(open(path))

    expectations = []
    for expectation in suite_data.get("expectations"):
        expectation_type = expectation["expectation_type"]
        kwargs = expectation["kwargs"]
        expectation = Expectation(expectation_type=expectation_type, kwargs=kwargs)
        expectations.append(expectation)

    return Suite(name=suite_data["name"], expectations=expectations)

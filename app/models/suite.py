from typing import List
from pydantic import BaseModel, StrictStr


class Expectation(BaseModel):
    """
    Represents an expectation configuration.

    Attributes:
        expectation_type (StrictStr): The type of expectation.
        kwargs (dict): Additional keyword arguments for the expectation.
    """

    expectation_type: StrictStr
    kwargs: dict


class Suite(BaseModel):
    """
    Represents a suite configuration.

    Attributes:
        name (StrictStr): The name of the suite.
        expectations (List[Expectation]): A list of expectation configurations for the suite.
    """

    name: StrictStr
    expectations: List[Expectation]

from pydantic import BaseModel, StrictStr


class DataAsset(BaseModel):
    name: StrictStr
    query: StrictStr

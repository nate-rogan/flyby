from pydantic import BaseModel


class ModelOut(BaseModel):
    name: str
    size_gb: float

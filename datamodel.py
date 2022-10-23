from pydantic import BaseModel
from typing import Dict, Union


class Dist(BaseModel):
    """Dist data model"""
    distribution: str
    type: str
    translation: str
    scale: Union[str, float]
    beta1: Union[str, float, None] = None
    beta2: Union[str, float, None] = None


class RequestModel(BaseModel):
    """Request data model"""
    poly: str
    dist: Dict[str, Dist]
    order: Union[int, None] = None


class ResponseModel(BaseModel):
    """Response data model"""
    result: str
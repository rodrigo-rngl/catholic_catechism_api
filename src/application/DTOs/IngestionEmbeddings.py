from typing import List, TypeVar, Union
from pydantic import BaseModel

float_vec = List[float]
float_mat = List[List[float]]


class SparseDict(BaseModel):
    indices: List[int]
    values: List[float]


# Tipos concretos
class IngestionHybridEmbeddings(BaseModel):
    dense: List[float_vec]
    sparse: List[SparseDict]
    late: List[float_mat]


class IngestionDenseEmbeddings(BaseModel):
    dense: List[float_vec]


IngestionEmbeddingsBase = Union[IngestionHybridEmbeddings,
                                IngestionDenseEmbeddings]

IngestionEmbeddingsType = TypeVar(
    "IngestionEmbeddingsType", bound=IngestionEmbeddingsBase)

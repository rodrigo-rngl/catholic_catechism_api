from typing import List, TypeVar, Union
from pydantic import BaseModel

float_vec = List[float]
float_mat = List[List[float]]


class SparseDict(BaseModel):
    indices: List[int]
    values: List[float]


# Tipos concretos
class QueryHybridEmbedding(BaseModel):
    dense: float_vec
    sparse: SparseDict
    late: float_mat


class QueryDenseEmbedding(BaseModel):
    dense: float_vec


QueryEmbeddingBase = Union[QueryHybridEmbedding, QueryDenseEmbedding]


QueryEmbeddingType = TypeVar(
    "QueryEmbeddingType", bound=QueryEmbeddingBase)

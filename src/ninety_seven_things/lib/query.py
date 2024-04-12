# Standard Library Imports
import datetime
from enum import Enum
from typing import Union

# 3rd-Party Imports
from beanie.odm.operators.find.comparison import GT, GTE, LT, LTE, NE, Eq, In
from pydantic import BaseModel, model_validator


class Op(str, Enum):
    includes = "includes"
    contains = "contains"
    lt = "<"
    lte = "<="
    gte = ">="
    gt = ">"
    eq = "="
    ne = "!="


class QueryFilter(BaseModel):
    field: str
    operator: Op
    value: Union[str, int, datetime.date]

    @model_validator(mode="before")
    def validate_value(cls, values):
        operator, value = values.get("operator"), values.get("value")

        if not isinstance(value, int):
            if operator in {"<=", "<", ">", ">="}:
                raise ValueError("Can't do this kind of comparison on non-digit values")

        return values

    def to_query(self):
        match self.operator:
            case "contains":
                return_value = In(self.field, self.value)
            case "<":
                return_value = LT(self.field, self.value)
            case "<=":
                return_value = LTE(self.field, self.value)
            case ">=":
                return_value = GTE(self.field, self.value)
            case ">":
                return_value = GT(self.field, self.value)
            case "=":
                return_value = Eq(self.field, self.value)
            case "!=":
                return_value = NE(self.field, self.value)
            case other:
                raise ValueError(f"Unknown operator: {other}")

        return return_value

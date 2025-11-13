from typing import Annotated

from pydantic import BaseModel, PositiveFloat, StringConstraints
from pydantic.types import FutureDate


class CreateJobDto(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)]
    description: Annotated[str, StringConstraints(min_length=1)]
    budget: PositiveFloat
    location: Annotated[str, StringConstraints(min_length=1)]
    start_date: FutureDate
    end_date: FutureDate


class UpdateJobDto(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)] | None = None
    description: Annotated[str, StringConstraints(min_length=1)] | None = None
    budget: PositiveFloat | None = None
    location: Annotated[str, StringConstraints(min_length=1)] | None = None
    start_date: FutureDate | None = None
    end_date: FutureDate | None = None

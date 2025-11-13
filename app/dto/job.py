from typing import Optional, Annotated

from pydantic import BaseModel, StringConstraints, PositiveFloat
from pydantic.types import FutureDate


class CreateJobDto(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)]
    description: Annotated[str, StringConstraints(min_length=1)]
    budget: PositiveFloat
    location: Annotated[str, StringConstraints(min_length=1)]
    start_date: FutureDate
    end_date: FutureDate


class UpdateJobDto(BaseModel):
    title: Optional[Annotated[str, StringConstraints(min_length=1)]] = None
    description: Optional[Annotated[str, StringConstraints(min_length=1)]] = None
    budget: Optional[PositiveFloat] = None
    location: Optional[Annotated[str, StringConstraints(min_length=1)]] = None
    start_date: Optional[FutureDate] = None
    end_date: Optional[FutureDate] = None

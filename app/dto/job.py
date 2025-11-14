from datetime import date
from fastapi import HTTPException, status
from typing import Annotated

from pydantic import BaseModel, StringConstraints, field_validator


class CreateJobDto(BaseModel):
    title: Annotated[str, StringConstraints(min_length=5)]
    description: Annotated[str, StringConstraints(min_length=10)]
    budget: float
    location: Annotated[str, StringConstraints(min_length=1)]
    start_date: date
    end_date: date

    @field_validator("budget", mode="after")
    @classmethod
    def validate_budget_positive(cls, value: float) -> float:
        if value <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Budget must be greater than 0",
            )
        return value

    @field_validator("start_date", "end_date", mode="after")
    @classmethod
    def validate_date_not_in_past(cls, value: date) -> date:
        if value < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date cannot be in the past",
            )
        return value

    @field_validator("end_date", mode="after")
    @classmethod
    def validate_end_date_after_start_date(cls, value: date, info) -> date:
        if "start_date" in info.data and value < info.data["start_date"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be on or after start date",
            )
        return value


class UpdateJobDto(BaseModel):
    title: Annotated[str, StringConstraints(min_length=5)] | None = None
    description: Annotated[str, StringConstraints(min_length=10)] | None = None
    budget: float | None = None
    location: Annotated[str, StringConstraints(min_length=1)] | None = None
    start_date: date | None = None
    end_date: date | None = None

    @field_validator("budget", mode="after")
    @classmethod
    def validate_budget_positive(cls, value: float | None) -> float | None:
        if value is not None and value <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Budget must be greater than 0",
            )
        return value

    @field_validator("start_date", "end_date", mode="after")
    @classmethod
    def validate_date_not_in_past(cls, value: date | None) -> date | None:
        if value is not None and value < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date cannot be in the past",
            )
        return value

    @field_validator("end_date", mode="after")
    @classmethod
    def validate_end_date_after_start_date(cls, value: date | None, info) -> date | None:
        if value is not None and "start_date" in info.data and info.data["start_date"] is not None:
            if value < info.data["start_date"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date must be on or after start date",
                )
        return value

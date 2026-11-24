from pydantic import AwareDatetime, BaseModel, Field, StrictInt, field_validator, model_validator
from typing import Literal, Self


class Intensity(BaseModel):
    forecast: StrictInt = Field(ge=0)
    actual: StrictInt | None = Field(ge=0)
    index: Literal["very low", "low", "moderate", "high", "very high"]


class IntensityData(BaseModel):
    from_: AwareDatetime = Field(alias="from")
    to: AwareDatetime
    intensity: Intensity

    @field_validator("from_", "to", mode="before")
    @classmethod
    def validate_timestamp(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("Timestamp must be a string")
        return value


    @model_validator(mode="after")
    def validate_time_range(self) -> Self:
        from_ = self.from_
        to = self.to
        if from_ >= to:
            raise ValueError("'from' timestamp must be earlier than 'to' timestamp")
        return self


class CarbonIntensityResponse(BaseModel):
    data: list[IntensityData] = Field(min_length=1)

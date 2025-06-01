from pydantic import BaseModel, Field, field_validator


class EmployeeBase(BaseModel):
    gpn: str = Field(..., min_length=2, max_length=15)
    employee_name: str = Field(..., min_length=2, max_length=50)
    team_name: str | None = Field(None, min_length=2, max_length=20)

    # noinspection PyNestedDecorators
    @field_validator("gpn", "team_name")
    @classmethod
    def gpn_is_uppercase(cls, value: str) -> str:
        return value.upper() if value else value

    # noinspection PyNestedDecorators
    @field_validator("gpn", "employee_name", "team_name")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        return value.strip() if value else value

    # noinspection PyNestedDecorators
    @field_validator("employee_name")
    @classmethod
    def capitalize_name(cls, value: str) -> str:
        return value.title()


class EmployeeCreateRequest(EmployeeBase):
    pass


class EmployeeUpdateRequest(EmployeeBase):
    pass


class EmployeeResponse(BaseModel):
    employee_id: int
    gpn: str
    employee_name: str
    team_name: str | None

    class Config:
        from_attributes = True

from pydantic import BaseModel, Field, field_validator


class EmployeeBase(BaseModel):
    gpn: str = Field(..., min_length=2, max_length=15)
    employee_name: str = Field(..., min_length=2, max_length=50)
    team_id: int | None = None

    # noinspection PyNestedDecorators
    @field_validator("gpn")
    @classmethod
    def gpn_is_uppercase(cls, value: str) -> str:
        return value.upper() if value else value

    # noinspection PyNestedDecorators
    @field_validator("gpn", "employee_name")
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
    team_id: int | None = None

    class Config:
        from_attributes = True

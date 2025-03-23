import enum
from datetime import datetime
from typing import Optional, List, Literal, Any

import pydantic

from app.models.task import PropertyEnum, TaskStatus


class TaskCreate(pydantic.BaseModel):
    user_id: int
    q: List[str] = pydantic.Field(
        description="Search topic(s). List of strings."
    )
    geo: Optional[str] = pydantic.Field(
        default="Worldwide",
        description="Geographical region (e.g., 'US', 'DE', 'Worldwide')."
    )
    time: Optional[str] = pydantic.Field(
        default=None,
        description="Time range (e.g., 'now 7-d', '2023-01-01 2023-01-31')."
    )
    cat: Optional[int] = pydantic.Field(
        default=0,
        description="Category ID (e.g., 0 for all categories, 7 for Arts & Entertainment)."
    )
    gprop: Optional[PropertyEnum] = pydantic.Field(
        default=PropertyEnum.WEB_SEARCH,
        description="Google property (Web Search, YouTube Search, Image Search)."
    )
    tz: Optional[int] = pydantic.Field(
        default=0,
        description="Time zone offset in minutes."
    )
    schedule_at: Optional[datetime] = pydantic.Field(default_factory=datetime.now)

    @pydantic.field_validator("time")
    def validate_time(cls, v):
        if v is None:
            return v
        parts = v.split()
        if len(parts) == 1:
            try:
              datetime.strptime(parts[0], '%Y-%m-%d')
              raise ValueError("Time range must be two dates if using the YYYY-MM-DD format.")
            except ValueError:
              ... #if it fails we assume it is a now time range such as now 7-d.
        elif len(parts) == 2:
            try:
                datetime.strptime(parts[0], '%Y-%m-%d')
                datetime.strptime(parts[1], '%Y-%m-%d')
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD.")
        elif len(parts) > 2:
            raise ValueError("Invalid time range format.")

        return v

    def custom_model_dump(
        self,
        *,
        mode: Literal['json', 'python'] | str = 'python',
        include: pydantic.main.IncEx | None = None,
        exclude: pydantic.main.IncEx | None = None,
        context: Any | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal['none', 'warn', 'error'] = True,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:

        data = self.model_dump(
            mode=mode,
            by_alias=by_alias,
            include=include,
            exclude=exclude,
            context=context,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any
        )

        for key, value in data.items():
            if isinstance(value, enum.Enum):
                data[key] = value.value

        return data

    class Config:
        from_attributes=True


class TrendResponseQListItem(pydantic.BaseModel):
    query: str
    value: int

    class Config:
        from_attributes=True


class TrendResponse(pydantic.BaseModel):
    date: datetime
    is_partial: str
    q_list: List[TrendResponseQListItem]

    class Config:
        from_attributes=True


class TrendError(pydantic.BaseModel):
    code: int
    error: str

    class Config:
        from_attributes=True


class TaskRetrieve(TaskCreate):
    task_id: str
    status: TaskStatus
    result_data: Optional[List[TrendResponse]] = None
    error: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes=True


class TaskUpdate(pydantic.BaseModel):
    q: List[str] = pydantic.Field(
        description="Search topic(s). List of strings."
    )
    geo: Optional[str] = pydantic.Field(
        default="Worldwide",
        description="Geographical region (e.g., 'US', 'DE', 'Worldwide')."
    )
    time: Optional[str] = pydantic.Field(
        default=None,
        description="Time range (e.g., 'now 7-d', '2023-01-01 2023-01-31')."
    )
    cat: Optional[int] = pydantic.Field(
        default=0,
        description="Category ID (e.g., 0 for all categories, 7 for Arts & Entertainment)."
    )
    gprop: Optional[PropertyEnum] = pydantic.Field(
        default=PropertyEnum.WEB_SEARCH,
        description="Google property (Web Search, YouTube Search, Image Search)."
    )
    tz: Optional[int] = pydantic.Field(
        default=0,
        description="Time zone offset in minutes."
    )

    class Config:
        from_attributes=True


class TrendTaskUpdate(pydantic.BaseModel):
    status: Optional[TaskStatus] = None
    result_data: Optional[List[TrendResponse]] = None
    error: Optional[str] = None
    increment_retry_count: Optional[bool] = False
    updated_at: Optional[datetime] = pydantic.Field(default_factory=datetime.now)

    class Config:
        from_attributes=True

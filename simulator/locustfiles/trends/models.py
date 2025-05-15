from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, List, Any


@dataclass
class Trends:
    task_id: str
    user_id: str
    q: List[str]
    geo: str
    time: str
    cat: int
    gprop: str
    tz: int
    status: str
    result_data: List[Dict[str, Any]]
    error: Optional[str]
    retry_count: int
    schedule_at: datetime
    created_at: datetime
    updated_at: datetime

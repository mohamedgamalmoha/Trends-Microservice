from typing import Optional

import pydantic


class Token(pydantic.BaseModel):
    access_token: str
    token_type: Optional[str] = 'Bearer'

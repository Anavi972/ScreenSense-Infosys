# backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class PredictRequest(BaseModel):
    age: int = Field(..., example=22)
    gender: str = Field(..., example="Male")
    device: str = Field(..., example="Smartphone")
    avg_daily_screen_time_hr: float = Field(..., example=5.0)
    educational_hr: Optional[float] = Field(None, example=2.0)
    recreational_hr: Optional[float] = Field(None, example=3.0)

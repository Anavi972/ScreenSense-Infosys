# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from uuid import uuid4
import os

# helpers to convert numpy/pandas -> python
from typing import Any

# import numpy/pandas if available
try:
    import numpy as np
except Exception:
    np = None
try:
    import pandas as pd
except Exception:
    pd = None

from recommender import (
    recommendation_system,
    get_edu_rec_limits,
    find_health_impacts_near_time,
)
from report_generator import create_pdf_report
from schemas import PredictRequest

app = FastAPI(title="Screen-Sense API")

REPORT_DIR = "backend/reports"
os.makedirs(REPORT_DIR, exist_ok=True)


def _to_py(x: Any) -> Any:
    """
    Recursively convert numpy/pandas objects to plain Python types:
    - numpy/pandas scalars -> python scalars (via .item())
    - numpy arrays / pandas Series / Index -> lists
    - pandas DataFrame -> list of dicts (if needed)
    - dicts/lists/tuples -> converted recursively
    """
    # None stays None
    if x is None:
        return None

    # numpy scalars (np.bool_, np.int64, etc.)
    if np is not None and isinstance(x, np.generic):
        try:
            return x.item()
        except Exception:
            # fallback to builtin conversion
            return bool(x) if isinstance(x, (np.bool_,)) else float(x)

    # numpy arrays / pandas Series / Index -> lists
    if np is not None and isinstance(x, (np.ndarray,)):
        return [_to_py(v) for v in x.tolist()]

    if pd is not None:
        if isinstance(x, (pd.Series, pd.Index)):
            return [_to_py(v) for v in x.tolist()]
        if isinstance(x, pd.DataFrame):
            # convert DataFrame to list of dicts
            return [ {str(k): _to_py(v) for k,v in row.items()} for _, row in x.to_dict(orient="records") ]

    # dict -> convert values
    if isinstance(x, dict):
        return {str(k): _to_py(v) for k, v in x.items()}

    # list/tuple/set -> list
    if isinstance(x, (list, tuple, set)):
        return [_to_py(v) for v in x]

    # builtin python types (int, float, bool, str) are fine
    if isinstance(x, (str, int, float, bool)):
        return x

    # fallback: try to coerce
    try:
        # e.g., numpy.bool_ may reach here if np is None
        if hasattr(x, "item"):
            return _to_py(x.item())
    except Exception:
        pass

    # as last resort, cast to string
    return str(x)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/predict")
def predict(payload: PredictRequest):
    # 1) Run recommendation logic (may return numpy/pandas types)
    raw_summary = recommendation_system(
        payload.age,
        payload.gender.capitalize(),
        payload.device.capitalize(),
        payload.avg_daily_screen_time_hr,
    )

    # 2) Convert raw_summary to pure python types
    safe_summary = _to_py(raw_summary)

    # 3) Educational/recreational analysis
    edu_limit, rec_limit = get_edu_rec_limits()
    # convert limits to native float
    try:
        edu_limit = float(_to_py(edu_limit))
    except Exception:
        edu_limit = None
    try:
        rec_limit = float(_to_py(rec_limit))
    except Exception:
        rec_limit = None

    edu_impacts = []
    rec_impacts = []
    if payload.educational_hr is not None and edu_limit is not None and float(payload.educational_hr) > edu_limit:
        edu_impacts = find_health_impacts_near_time(payload.educational_hr)
    if payload.recreational_hr is not None and rec_limit is not None and float(payload.recreational_hr) > rec_limit:
        rec_impacts = find_health_impacts_near_time(payload.recreational_hr)

    # convert impacts to plain python
    edu_impacts = _to_py(edu_impacts)
    rec_impacts = _to_py(rec_impacts)

    result = {
        "summary": safe_summary,
        "educational_limit": edu_limit,
        "recreational_limit": rec_limit,
        "educational_impacts_near_time": edu_impacts,
        "recreational_impacts_near_time": rec_impacts,
    }

    # convert whole result to pure python types and return
    safe_result = _to_py(result)
    return JSONResponse(content=safe_result)


@app.post("/api/v1/report")
def report(payload: PredictRequest):
    raw_summary = recommendation_system(
        payload.age,
        payload.gender.capitalize(),
        payload.device.capitalize(),
        payload.avg_daily_screen_time_hr,
    )

    safe_summary = _to_py(raw_summary)

    inputs = payload.dict()
    if inputs.get("educational_hr") is None and inputs.get("recreational_hr") is None:
        inputs["educational_hr"] = None
        inputs["recreational_hr"] = None

    report_id = str(uuid4())
    filename = os.path.join(REPORT_DIR, f"report-{report_id}.pdf")

    # create_pdf_report expects python types; pass safe_summary
    create_pdf_report(inputs, safe_summary, filename)

    return JSONResponse(content=_to_py({"report_id": report_id, "report_url": f"/api/v1/report/{report_id}"}))


@app.get("/api/v1/report/{report_id}")
def download_report(report_id: str):
    filename = os.path.join(REPORT_DIR, f"report-{report_id}.pdf")
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(filename, media_type="application/pdf", filename=f"screen-sense-report-{report_id}.pdf")

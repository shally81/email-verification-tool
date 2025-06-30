from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import asyncio, csv, io, datetime
from utils import verify_email
from models import Base, VerificationLog, engine, SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bulk Email Verification API", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

class EmailIn(BaseModel):
    email: EmailStr

@app.post("/verify")
async def verify_endpoint(payload: EmailIn):
    status, reason = await verify_email(payload.email)
    with SessionLocal() as db:
        db.add(VerificationLog(email=payload.email, status=status, reason=reason))
        db.commit()
    return {"email": payload.email, "status": status, "reason": reason}

@app.post("/bulk")
async def bulk_verify(file: UploadFile = File(...)):
    if not file.filename.endswith((".csv", ".txt")):
        return JSONResponse(status_code=400, content={"detail": "Please upload .csv or .txt file"})
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    reader = csv.reader(io.StringIO(text))
    emails = [row[0].strip() for row in reader if row]

    sem = asyncio.Semaphore(20)
    results = []

    async def worker(addr):
        async with sem:
            status, reason = await verify_email(addr)
            with SessionLocal() as db:
                db.add(VerificationLog(email=addr, status=status, reason=reason))
                db.commit()
            results.append({"email": addr, "status": status, "reason": reason})

    await asyncio.gather(*(worker(e) for e in emails))
    return {"total": len(results), "results": results}

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()
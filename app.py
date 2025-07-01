from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import asyncio, csv, io
from utils import verify_email, get_message_for_reason
from models import Base, VerificationLog, engine, SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bulk Email Verification API", version="1.2")
app.mount("/static", StaticFiles(directory="static"), name="static")

class EmailIn(BaseModel):
    email: EmailStr

@app.post("/verify")
async def verify_endpoint(payload: EmailIn):
    status, reason = await verify_email(payload.email)
    message = get_message_for_reason(status, reason)
    with SessionLocal() as db:
        db.add(VerificationLog(email=payload.email, status=status, reason=reason))
        db.commit()
    return {"email": payload.email, "status": status, "reason": reason, "message": message}

@app.post("/bulk")
async def bulk_verify(file: UploadFile = File(...)):
    filename = (file.filename or "").lower()
    if not filename.endswith((".csv", ".txt")):
        return JSONResponse(status_code=400, content={"detail": "File must be .csv or .txt"})

    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig", errors="ignore")
    except UnicodeDecodeError:
        text = raw.decode("latin1", errors="ignore")

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    reader = csv.reader(io.StringIO(text))
    emails = [row[0].strip() for row in reader if row and "@" in row[0]]
    if not emails:
        return JSONResponse(status_code=400, content={"detail": "No valid email addresses found in file."})

    sem = asyncio.Semaphore(20)
    results = []

    async def worker(addr):
        async with sem:
            status, reason = await verify_email(addr)
            message = get_message_for_reason(status, reason)
            with SessionLocal() as db:
                db.add(VerificationLog(email=addr, status=status, reason=reason))
                db.commit()
            results.append({"email": addr, "status": status, "reason": reason, "message": message})

    await asyncio.gather(*(worker(e) for e in emails))
    return {"total": len(results), "results": results}

@app.get("/", response_class=HTMLResponse)
async def root():
    return open("templates/index.html", encoding="utf-8").read()
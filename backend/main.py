from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pydantic import BaseModel, EmailStr
from typing import Optional
from dotenv import load_dotenv
import os
import logging
import time

load_dotenv()

# ── Logger setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("student_api")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Student Management API", version="1.0.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MongoDB connection ─────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not found. Make sure your .env file exists in the backend folder.")

client = AsyncIOMotorClient(MONGO_URI)
db = client["studentdb"]
collection = db["students"]

# ── Startup / Shutdown events ─────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    logger.info("=" * 55)
    logger.info("  Student Management API  —  STARTED")
    logger.info("  MongoDB connected to cluster")
    logger.info("  Listening on http://127.0.0.1:8000")
    logger.info("=" * 55)

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("=" * 55)
    logger.info("  Student Management API  —  STOPPED")
    logger.info("=" * 55)

# ── Request logging middleware ────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    logger.info(f"→  {request.method}  {request.url.path}  |  client: {request.client.host}")
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    level = logging.WARNING if response.status_code >= 400 else logging.INFO
    logger.log(level, f"←  {request.method}  {request.url.path}  |  status: {response.status_code}  |  {elapsed:.1f}ms")
    return response

# ── Helpers ───────────────────────────────────────────────────────────────────
def student_serializer(student) -> dict:
    return {
        "id": str(student["_id"]),
        "name": student["name"],
        "age": student["age"],
        "branch": student["branch"],
        "email": student["email"],
    }

# ── Schemas ───────────────────────────────────────────────────────────────────
class StudentCreate(BaseModel):
    name: str
    age: int
    branch: str
    email: EmailStr

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    branch: Optional[str] = None
    email: Optional[EmailStr] = None

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "Student Management API is running"}


@app.get("/students", summary="Get all students")
async def get_students():
    students = []
    async for s in collection.find():
        students.append(student_serializer(s))
    logger.info(f"[DB]  READ  all students  |  {len(students)} record(s) returned")
    return students


@app.get("/students/{student_id}", summary="Get a student by ID")
async def get_student(student_id: str):
    if not ObjectId.is_valid(student_id):
        logger.warning(f"[ERROR]  GET student  |  invalid ID format: {student_id}")
        raise HTTPException(status_code=400, detail="Invalid student ID")
    student = await collection.find_one({"_id": ObjectId(student_id)})
    if not student:
        logger.warning(f"[ERROR]  GET student  |  not found: {student_id}")
        raise HTTPException(status_code=404, detail="Student not found")
    logger.info(f"[DB]  READ  student: {student['name']}  |  id: {student_id}")
    return student_serializer(student)


@app.post("/students", status_code=201, summary="Create a new student")
async def create_student(student: StudentCreate):
    new_student = student.model_dump()
    logger.info(f"[DB]  INSERT  name: {student.name}  age: {student.age}  branch: {student.branch}  email: {student.email}")
    try:
        result = await collection.insert_one(new_student)
        created = await collection.find_one({"_id": result.inserted_id})
        logger.info(f"[DB]  INSERT  success  |  new id: {result.inserted_id}")
        return student_serializer(created)
    except Exception as e:
        logger.error(f"[ERROR]  INSERT failed  |  {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create student")


@app.put("/students/{student_id}", summary="Update a student")
async def update_student(student_id: str, student: StudentUpdate):
    if not ObjectId.is_valid(student_id):
        logger.warning(f"[ERROR]  UPDATE student  |  invalid ID format: {student_id}")
        raise HTTPException(status_code=400, detail="Invalid student ID")
    update_data = {k: v for k, v in student.model_dump().items() if v is not None}
    if not update_data:
        logger.warning(f"[ERROR]  UPDATE student  |  no fields provided  |  id: {student_id}")
        raise HTTPException(status_code=400, detail="No fields to update")
    logger.info(f"[DB]  UPDATE  id: {student_id}  |  fields: {list(update_data.keys())}  |  values: {update_data}")
    try:
        result = await collection.update_one(
            {"_id": ObjectId(student_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            logger.warning(f"[ERROR]  UPDATE  |  student not found: {student_id}")
            raise HTTPException(status_code=404, detail="Student not found")
        updated = await collection.find_one({"_id": ObjectId(student_id)})
        logger.info(f"[DB]  UPDATE  success  |  id: {student_id}")
        return student_serializer(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR]  UPDATE failed  |  {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update student")


@app.delete("/students/{student_id}", summary="Delete a student")
async def delete_student(student_id: str):
    if not ObjectId.is_valid(student_id):
        logger.warning(f"[ERROR]  DELETE student  |  invalid ID format: {student_id}")
        raise HTTPException(status_code=400, detail="Invalid student ID")
    logger.info(f"[DB]  DELETE  id: {student_id}")
    try:
        result = await collection.delete_one({"_id": ObjectId(student_id)})
        if result.deleted_count == 0:
            logger.warning(f"[ERROR]  DELETE  |  student not found: {student_id}")
            raise HTTPException(status_code=404, detail="Student not found")
        logger.info(f"[DB]  DELETE  success  |  id: {student_id}")
        return {"message": "Student deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR]  DELETE failed  |  {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete student")
from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from os import getenv
from bson import ObjectId

router = APIRouter()
mongo_client = MongoClient(getenv("MONGO_URI"))
db = mongo_client["mind_database"]  # oder wie im .env angegeben

@router.get("/hive/knowledge")
def get_knowledge():
    return list(db["knowledge_base"].find({}, {"_id": 0}))

@router.post("/hive/knowledge")
def upsert_knowledge(item: dict):
    if "_id" not in item:
        raise HTTPException(status_code=400, detail="Missing _id")
    db["knowledge_base"].replace_one({"_id": item["_id"]}, item, upsert=True)
    return {"status": "ok"}

@router.get("/hive/markers")
def get_markers():
    return list(db["marker_store"].find({}, {"_id": 0}))

@router.post("/hive/markers")
def upsert_marker(marker: dict):
    if "_id" not in marker:
        raise HTTPException(status_code=400, detail="Missing _id")
    db["marker_store"].replace_one({"_id": marker["_id"]}, marker, upsert=True)
    return {"status": "ok"}

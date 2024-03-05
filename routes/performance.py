from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from models.schemas import ResponseMessage
from models.schemas import PerformanceMetric
from config.db import Database
from typing import List
from bson import ObjectId
from motor.motor_asyncio import  AsyncIOMotorDatabase
from models.user import UserOut
from authentication.auth import get_current_user

performance = APIRouter()

# Access the 'db' attribute of the Database singleton
db: AsyncIOMotorDatabase = Database().db # type: ignore

@performance.put("/assets/{asset_id}/update/performance_metric", responses = {200: {"model" : ResponseMessage}})
async def update_metric(asset_id: str, updated_metric: PerformanceMetric,  user: UserOut = Depends(get_current_user)):
    metric_id =  await db.assets.find_one({"_id": ObjectId(asset_id)}, projection={"performance_metric_id": 1})
    metric_id = metric_id["performance_metric_id"] if metric_id else None
    
    if metric_id is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    performance_metric = await db.performance_metrics.find_one({"_id": ObjectId(metric_id)})
    updated_metric = updated_metric.dict()
    for key, value in updated_metric.items():
        if value is not None:
            performance_metric[key] = value

    await db.performance_metrics.replace_one({"_id": ObjectId(metric_id)}, performance_metric)

    return JSONResponse(status_code=200, content={"detail" : "Updated performance metric successfully"})

    

@performance.delete("/assets/{asset_id}/delete/performance_metric", responses = {200: {"model" : ResponseMessage}})
async def delete_metric(asset_id: str, metric : str, user: UserOut = Depends(get_current_user)):
    metric_id =  await db.assets.find_one({"_id": ObjectId(asset_id)}, projection={"performance_metric_id": 1})
    metric_id = metric_id["performance_metric_id"] if metric_id else None

    if metric_id is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    query = {"_id": ObjectId(metric_id), metric: {"$exists": True}}
    
    #result = await db.performance_metrics.update_one({"_id": ObjectId(metric_id)}, {"$set": {metric : None}})
    result = await db.performance_metrics.update_one(query, {"$set": {metric: None}})
    if result.modified_count > 0:
        return JSONResponse(status_code=200, content={"detail" : f"{metric} deleted for asset_id: {asset_id}"})
    else:
        raise HTTPException(status_code=404, detail=f"{metric} not found for asset_id: {asset_id}")


    
    
    

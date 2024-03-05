from fastapi import APIRouter, HTTPException
from models.schemas import PerformanceMetric
from config.db import Database
from typing import List
from bson import ObjectId
from motor.motor_asyncio import  AsyncIOMotorDatabase

performance = APIRouter()

# Access the 'db' attribute of the Database singleton
db: AsyncIOMotorDatabase = Database().db # type: ignore

@performance.put("/assets/{asset_id}/update/performance_metric")
async def update_metric(asset_id: str, updated_metric: PerformanceMetric):
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

    return {"message" : "Updated performance metric successfully"}

@performance.delete("/assets/{asset_id}/delete/performance_metric")
async def delete_metric(asset_id: str, metric : str):
    metric_id =  await db.assets.find_one({"_id": ObjectId(asset_id)}, projection={"performance_metric_id": 1})
    metric_id = metric_id["performance_metric_id"] if metric_id else None

    if metric_id is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    result = await db.performance_metrics.update_one({"_id": ObjectId(metric_id)}, {"$set": {metric : None}})
    if result.modified_count > 0:
        return { "message" : f"{metric} deleted for asset_id: {asset_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"{metric} not found")


    
    
    

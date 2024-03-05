from fastapi import APIRouter, HTTPException, Depends
from models.schemas import PerformanceMetric, Asset, AssetCreate, AssetUpdate
from config.db import Database, close_database_client
from typing import List
from bson import ObjectId
from motor.motor_asyncio import  AsyncIOMotorDatabase

aggregation = APIRouter() # Aggregation Router

# Access the 'db' attribute of the Database singleton
db: AsyncIOMotorDatabase = Database().db # type: ignore

@aggregation.get("/average_downtime", response_model=float)
async def calculate_average_downtime():
    # Calculate average downtime logic

    total_downtime = await db.performance_metrics.aggregate([
        {"$group": {"_id": None, "total_downtime": {"$sum": "$downtime"}}}
    ]).to_list(1)

    if total_downtime:
        total_downtime = total_downtime[0]['total_downtime']
        total_assets = await db.performance_metrics.count_documents({"downtime": {"$ne": None}})
        
        average_downtime = total_downtime / total_assets
        return average_downtime

    raise HTTPException(status_code=404, detail="No performance metrics found")

@aggregation.get("/total_maintenance_costs", response_model=float)
async def calculate_total_maintenance_costs():
    # Calculate total maintenance costs logic
    total_costs = await db.performance_metrics.aggregate([
        {"$group": {"_id": None, "total_costs": {"$sum": "$maintenance_costs"}}}
    ]).to_list(1)

    if total_costs:
        return total_costs[0]['total_costs']
    
    raise HTTPException(status_code=404, detail="No performance metrics found")


@aggregation.get("/high_failure_rate_assets", response_model=List[Asset])
async def identify_high_failure_rate_assets():
    # Step 1: Fetch all assets
    assets = await db.assets.find().to_list(None)
    if not assets:
        raise HTTPException(status_code=404, detail="No assets found")
    
    high_failure_rate_assets = []

    # For each asset, retrieve performance_metric_id and find high failure rate assets
    
    for asset in assets:
        performance_metric_id = asset.get("performance_metric_id")
        if performance_metric_id:
            performance_metric = await db.performance_metrics.find_one({"_id": performance_metric_id})
            failure_rate = performance_metric.get("failure_rate")
            if not failure_rate:
                continue
            if performance_metric and failure_rate > 0.1:  # Adjust the threshold as needed
                asset["performance_metric"] = performance_metric
                asset["id"] = str(asset["_id"])
                high_failure_rate_assets.append(asset)
    
    if not high_failure_rate_assets:
        raise HTTPException(status_code=404, detail="No assets with high failure rates found")

    return high_failure_rate_assets


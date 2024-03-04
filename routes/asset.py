from fastapi import APIRouter, HTTPException, Depends
from models.schemas import PerformanceMetric, Asset, AssetCreate, AssetUpdate
from config.db import Database, close_database_client
from typing import List
from bson import ObjectId
from motor.motor_asyncio import  AsyncIOMotorDatabase

asset = APIRouter() # Asset Router

# Access the 'db' attribute of the Database singleton
db: AsyncIOMotorDatabase = Database().db # type: ignore

# Route for creating an asset with a performance metric reference
@asset.post("/assets")
async def create_asset(asset: AssetCreate):
    
    asset_data = asset.dict()
    print(asset_data)
    # Extract and remove the performance_metric field
    performance_metric_data = asset_data.pop("performance_metric")
    
    result = await db.performance_metrics.insert_one(performance_metric_data)
    performance_metric_id = result.inserted_id

    # Update the asset with performance metric id
    asset_data["performance_metric_id"] = performance_metric_id
    result = await db.assets.insert_one(asset_data)
    
    return {"Asset added successfully"}


# Get all assets with their respective performance metrics
@asset.get("/assets", response_model=List[Asset])
async def get_all_assets():
    assets = await db.assets.find().to_list(1000)
    for asset in assets:
        asset["performance_metric"] = await get_performance_metrics_for_asset(asset["performance_metric_id"])
        asset["id"] = str(asset["_id"])
    
    return assets

async def get_performance_metrics_for_asset(metric_id):
    #metrics = []
    '''for metric_id in metric_ids:
        metric = await db.performance_metrics.find_one({"_id": ObjectId(metric_id)})
        if metric:
            metrics.append(metric)'''
    metric = await db.performance_metrics.find_one({"_id": ObjectId(metric_id)})
          
    return metric

# Get a single asset by ID
@asset.get("/assets/{asset_id}", response_model=Asset)
async def get_asset(asset_id: str):
    asset = await db.assets.find_one({"_id": ObjectId(asset_id)})
    if asset:
        asset["id"] = str(asset["_id"]) 
        asset["performance_metric"] = await get_performance_metrics_for_asset(asset["performance_metric_id"])
        return asset
    
    raise HTTPException(status_code=404, detail="Asset not found")

# Delete an asset
@asset.delete("/assets/{asset_id}")
async def delete_asset_endpoint(asset_id: str):
    # Delete the asset
    deleted_asset_data  = await db.assets.find_one_and_delete({"_id": ObjectId(asset_id)})
    
    if not deleted_asset_data:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    metric_id = deleted_asset_data['performance_metric_id']
    
    # Delete the associated performance metrics
    await db.performance_metrics.delete_one({"_id": ObjectId(metric_id)})
    
    return {"message": "Asset and associated performance metrics deleted successfully"}


@asset.put("/assets/{asset_id}/update")
async def update_asset(asset_id: str, asset_update: AssetUpdate):
    # Find the asset by ID
    existing_asset = await db.assets.find_one({"_id": ObjectId(asset_id)})

    # Check if the asset exists
    if not existing_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Update only the specified fields
    asset_update = asset_update.dict()
    
    for key, value in asset_update.items():
        if  value is not None:
            existing_asset[key] = value

    # Save the updated document back to MongoDB
    await db.assets.replace_one({"_id": ObjectId(asset_id)}, existing_asset)

    return {"message" : "Updated asset successfully"}












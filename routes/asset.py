from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from models.schemas import PerformanceMetric, Asset, AssetCreate, AssetUpdate, ResponseMessage
from config.db import Database, close_database_client
from typing import List
from bson import ObjectId
from motor.motor_asyncio import  AsyncIOMotorDatabase
from pydantic import BaseModel
from authentication.auth import get_current_user
from models.user import UserOut

asset = APIRouter() # Asset Router

# Access the 'db' attribute of the Database singleton
db: AsyncIOMotorDatabase = Database().db # type: ignore

# Route for creating an asset with a performance metric reference
@asset.post("/assets", responses={200: {"model" : ResponseMessage}})
async def create_asset(asset: AssetCreate, user: UserOut = Depends(get_current_user)):
    
    asset_data = asset.dict()
    
    # Extract and remove the performance_metric field
    performance_metric_data = asset_data.pop("performance_metric")
    
    result = await db.performance_metrics.insert_one(performance_metric_data)
    performance_metric_id = result.inserted_id

    # Update the asset with performance metric id
    asset_data["performance_metric_id"] = performance_metric_id
    result = await db.assets.insert_one(asset_data)
    
    return JSONResponse(status_code=200, content={"detail" : "Asset added successfully"})


# Get all assets with their respective performance metrics
@asset.get("/assets", response_model=List[Asset])
async def get_all_assets():
    assets = await db.assets.find().to_list(1000)
    for asset in assets:
        asset["performance_metric"] = await get_performance_metrics_for_asset(asset["performance_metric_id"])
        asset["id"] = str(asset["_id"])
    
    return assets

async def get_performance_metrics_for_asset(metric_id):
    metric = await db.performance_metrics.find_one({"_id": ObjectId(metric_id)})
    return metric

# Get a single asset by ID
@asset.get("/assets/{asset_id}", response_model=Asset, responses={404: {"model" : ResponseMessage}})
async def get_asset(asset_id: str):
    asset = await db.assets.find_one({"_id": ObjectId(asset_id)})
    if asset:
        asset["id"] = str(asset["_id"]) 
        asset["performance_metric"] = await get_performance_metrics_for_asset(asset["performance_metric_id"])
        return asset
    
    raise HTTPException(status_code=404, detail="Asset not found")
    

# Delete an asset
@asset.delete("/assets/{asset_id}", responses={404: {"model" : ResponseMessage}, 200: {"model" : ResponseMessage}})
async def delete_asset_endpoint(asset_id: str, user: UserOut = Depends(get_current_user)):
    # Delete the asset
    deleted_asset_data  = await db.assets.find_one_and_delete({"_id": ObjectId(asset_id)})
    
    if not deleted_asset_data:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    metric_id = deleted_asset_data['performance_metric_id']
    
    # Delete the associated performance metrics
    await db.performance_metrics.delete_one({"_id": ObjectId(metric_id)})
    
    return JSONResponse(status_code=200, content={"detail" : "Asset and its associated metrics deleted successfully"})


@asset.put("/assets/{asset_id}/update", responses={404: {"model" : ResponseMessage}, 200: {"model" : ResponseMessage}})
async def update_asset(asset_id: str, asset_update: AssetUpdate, user: UserOut = Depends(get_current_user)):
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

    return JSONResponse(status_code=200, content={"detail" : "Asset details updated successfully"})


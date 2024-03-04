from typing import List
from pydantic import BaseModel, Field
from bson import ObjectId


class PerformanceMetric(BaseModel):
    uptime: float | None = Field(default=None, description="Uptime percentage")
    downtime: float |  None= Field(default=None, description="Downtime percentage")
    maintenance_costs: float | None = Field(default=None, description="Total maintenance costs")
    failure_rate: float | None = Field(default=None, description="Failure rate")
    efficiency: float | None = Field(default=None, description="Efficiency percentage")


class AssetBase(BaseModel):
    
    asset_name: str = Field(..., description="Name of the asset")
    asset_type: str = Field(..., description="Type of the asset")
    location: str = Field(..., description="Location of the asset")
    purchase_date: str = Field(..., description="Purchase date of the asset")
    initial_cost: float = Field(..., description="Initial cost of the asset")
    operational_status: str = Field(..., description="Operational status of the asset")
    performance_metric: PerformanceMetric = Field(default_factory=PerformanceMetric)

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: str
    class Config:
       from_attributes = True

class AssetUpdate(BaseModel):
    asset_name: str = None
    asset_type: str = None
    location: str = None
    purchase_date: str = None
    initial_cost: float = None
    operational_status: str = None
   
       
  

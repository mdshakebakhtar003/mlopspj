from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class CustomerFeatures(BaseModel):
    credit_score: int = Field(
        ..., ge=300, le=850, description="Credit score between 300 and 850", json_schema_extra={"example": 650}
    )
    country: Literal["France", "Germany", "Spain"] = Field(
        ..., description="Customer residence country", json_schema_extra={"example": "Germany"}
    )
    gender: Literal["Female", "Male"] = Field(
        ..., description="Customer gender", json_schema_extra={"example": "Female"}
    )
    age: int = Field(
        ..., ge=18, le=100, description="Customer age between 18 and 100", json_schema_extra={"example": 42}
    )
    tenure: int = Field(
        ..., ge=0, le=20, description="Years customer has been with bank", json_schema_extra={"example": 5}
    )
    balance: float = Field(
        ..., ge=0.0, description="Customer bank account balance", json_schema_extra={"example": 85000.50}
    )
    num_of_products: int = Field(
        ..., ge=1, le=4, description="Number of bank products used", json_schema_extra={"example": 2}
    )
    has_cr_card: int = Field(
        ..., ge=0, le=1, description="Has credit card (1=Yes, 0=No)", json_schema_extra={"example": 1}
    )
    is_active_member: int = Field(
        ..., ge=0, le=1, description="Is active member (1=Yes, 0=No)", json_schema_extra={"example": 1}
    )
    estimated_salary: float = Field(
        ..., ge=0.0, description="Estimated annual salary", json_schema_extra={"example": 65000.0}
    )


class PredictionResponse(BaseModel):
    churn_prediction: int = Field(..., description="0 = Retain, 1 = Churn")
    churn_probability: float = Field(..., description="Predicted probability of churning")
    risk_level: Literal["Low", "Medium", "High"] = Field(..., description="Customer churn risk level")
    model_version: str = Field(..., description="Model version tag or timestamp")


class BatchCustomerFeatures(BaseModel):
    customers: List[CustomerFeatures]


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    total_processed: int


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str
    environment: Optional[str] = "development"

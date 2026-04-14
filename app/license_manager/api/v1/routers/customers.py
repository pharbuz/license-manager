from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.license_manager.api.dependencies import get_uow
from app.license_manager.api.v1.schemas.customers import (
    CustomerCreateSchema,
    CustomerSchema,
    CustomerUpdateSchema,
)
from app.license_manager.audit import audit_event
from app.license_manager.services.customers_service import CustomersService
from app.license_manager.services.errors import EntityNotFoundError
from app.license_manager.services.models.customers import (
    CustomerCreateDto as ServiceCustomerCreateDto,
)
from app.license_manager.services.models.customers import (
    CustomerUpdateDto as ServiceCustomerUpdateDto,
)
from app.license_manager.uow import UnitOfWork

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CustomerSchema)
async def create_customer(
    payload: CustomerCreateSchema,
    uow: UnitOfWork = Depends(get_uow),
) -> CustomerSchema:
    """Create a new customer."""
    service = CustomersService(uow)
    result = await service.create_customer(
        ServiceCustomerCreateDto.model_validate(payload.model_dump())
    )
    await audit_event(
        uow,
        action="customers.create",
        entity_type="customer",
        entity_id=str(result.id),
        summary=f"Created customer {result.customer_symbol}",
        metadata={"name": result.name, "email": str(result.email)},
    )
    return CustomerSchema.model_validate(result.model_dump())


@router.get("", response_model=list[CustomerSchema])
async def list_customers(
    uow: UnitOfWork = Depends(get_uow),
) -> list[CustomerSchema]:
    """List all customers."""
    service = CustomersService(uow)
    result = await service.list_customers()
    return [CustomerSchema.model_validate(item.model_dump()) for item in result]


@router.get("/{customerId}", response_model=CustomerSchema)
async def get_customer(
    customer_id: UUID = Path(..., alias="customerId"),
    uow: UnitOfWork = Depends(get_uow),
) -> CustomerSchema:
    """Get a customer by ID."""
    service = CustomersService(uow)
    try:
        result = await service.get_customer(customer_id)
        return CustomerSchema.model_validate(result.model_dump())
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.patch("/{customerId}", response_model=CustomerSchema)
async def update_customer(
    payload: CustomerUpdateSchema,
    customer_id: UUID = Path(..., alias="customerId"),
    uow: UnitOfWork = Depends(get_uow),
) -> CustomerSchema:
    """Update a customer."""
    service = CustomersService(uow)
    try:
        result = await service.update_customer(
            customer_id,
            ServiceCustomerUpdateDto.model_validate(payload.model_dump()),
        )
        await audit_event(
            uow,
            action="customers.update",
            entity_type="customer",
            entity_id=str(customer_id),
            summary=f"Updated customer {result.customer_symbol}",
            metadata={"updated_fields": list(payload.model_dump(exclude_unset=True))},
        )
        return CustomerSchema.model_validate(result.model_dump())
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/{customerId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID = Path(..., alias="customerId"),
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    """Delete a customer."""
    service = CustomersService(uow)
    try:
        await service.delete_customer(customer_id)
        await audit_event(
            uow,
            action="customers.delete",
            entity_type="customer",
            entity_id=str(customer_id),
            summary=f"Deleted customer {customer_id}",
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

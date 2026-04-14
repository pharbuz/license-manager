from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.license_manager.api.dependencies import get_uow
from app.license_manager.api.v1.schemas.products import (
    ProductCreateSchema,
    ProductSchema,
    ProductUpdateSchema,
)
from app.license_manager.audit import audit_event
from app.license_manager.services.errors import EntityNotFoundError
from app.license_manager.services.models.products import (
    ProductCreateDto as ServiceProductCreateDto,
)
from app.license_manager.services.models.products import (
    ProductUpdateDto as ServiceProductUpdateDto,
)
from app.license_manager.services.products_service import ProductsService
from app.license_manager.uow import UnitOfWork

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProductSchema)
async def create_product(
    payload: ProductCreateSchema,
    uow: UnitOfWork = Depends(get_uow),
) -> ProductSchema:
    """Create a new product."""
    service = ProductsService(uow)
    result = await service.create_product(
        ServiceProductCreateDto.model_validate(payload.model_dump())
    )
    await audit_event(
        uow,
        action="products.create",
        entity_type="product",
        entity_id=str(result.id),
        summary=f"Created product {result.name}",
        metadata={"kind": result.kind},
    )
    return ProductSchema.model_validate(result.model_dump())


@router.get("", response_model=list[ProductSchema])
async def list_products(
    uow: UnitOfWork = Depends(get_uow),
) -> list[ProductSchema]:
    """List all products."""
    service = ProductsService(uow)
    result = await service.list_products()
    return [ProductSchema.model_validate(item.model_dump()) for item in result]


@router.get("/{productId}", response_model=ProductSchema)
async def get_product(
    product_id: UUID = Path(..., alias="productId"),
    uow: UnitOfWork = Depends(get_uow),
) -> ProductSchema:
    """Get a product by ID."""
    service = ProductsService(uow)
    try:
        result = await service.get_product(product_id)
        return ProductSchema.model_validate(result.model_dump())
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.patch("/{productId}", response_model=ProductSchema)
async def update_product(
    payload: ProductUpdateSchema,
    product_id: UUID = Path(..., alias="productId"),
    uow: UnitOfWork = Depends(get_uow),
) -> ProductSchema:
    """Update a product."""
    service = ProductsService(uow)
    try:
        result = await service.update_product(
            product_id,
            ServiceProductUpdateDto.model_validate(payload.model_dump()),
        )
        await audit_event(
            uow,
            action="products.update",
            entity_type="product",
            entity_id=str(product_id),
            summary=f"Updated product {result.name}",
            metadata={"updated_fields": list(payload.model_dump(exclude_unset=True))},
        )
        return ProductSchema.model_validate(result.model_dump())
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/{productId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID = Path(..., alias="productId"),
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    """Delete a product."""
    service = ProductsService(uow)
    try:
        await service.delete_product(product_id)
        await audit_event(
            uow,
            action="products.delete",
            entity_type="product",
            entity_id=str(product_id),
            summary=f"Deleted product {product_id}",
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

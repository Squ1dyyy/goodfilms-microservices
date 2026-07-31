from fastapi import APIRouter, Depends, status

from movie.app.api.v1.dependencies import CountryFullDep, verify_admin_role
from movie.app.schemas.country import (
    CountrySchema,
    CreateCountrySchema,
    UpdateCountrySchema,
)

router = APIRouter(prefix="/countries", tags=["country"])
admin_router = APIRouter(prefix="/admin/countries", tags=["country-admin"])


@router.get("")
async def get_all_countries(country_service: CountryFullDep) -> list[CountrySchema]:
    return await country_service.get_countries()


@admin_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin_role)],
)
async def create_country(
    data: CreateCountrySchema,
    country_service: CountryFullDep,
) -> None:
    await country_service.create_country(data.name)


@admin_router.patch(
    "/{country_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin_role)],
)
async def patch_country(
    country_id: int,
    data: UpdateCountrySchema,
    country_service: CountryFullDep,
) -> None:
    await country_service.patch_country(country_id, data.name)


@admin_router.delete(
    "/{country_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_admin_role)],
)
async def delete_country(
    country_id: int,
    country_service: CountryFullDep,
) -> None:
    await country_service.delete_country(country_id)

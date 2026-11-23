from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_current_user
from src.modules.units.dependencies import get_units_service
from src.modules.units.schemas import UnitCreate, UnitResponse, UnitUpdate
from src.modules.units.service import UnitsService
from src.modules.users.models import User

router = APIRouter(prefix="/units", tags=["Units"])


@router.get("/", response_model=list[UnitResponse], status_code=status.HTTP_200_OK)
def get_units(
    service: UnitsService = Depends(get_units_service),
    current_user: User = Depends(get_current_user),
):
    return service.list_units()


@router.get("/{unit_id}", response_model=UnitResponse, status_code=status.HTTP_200_OK)
def get_unit(
    unit_id: int,
    service: UnitsService = Depends(get_units_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_unit(unit_id)


@router.post("/", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
    unit_data: UnitCreate,
    service: UnitsService = Depends(get_units_service),
    current_user: User = Depends(get_current_user),
):
    return service.create_unit(unit_data, current_user)


@router.patch("/{unit_id}", response_model=UnitResponse, status_code=status.HTTP_200_OK)
def update_unit(
    unit_id: int,
    unit_data: UnitUpdate,
    service: UnitsService = Depends(get_units_service),
    current_user: User = Depends(get_current_user),
):
    return service.update_unit(unit_id, unit_data, current_user)


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
    unit_id: int,
    service: UnitsService = Depends(get_units_service),
    current_user: User = Depends(get_current_user),
):
    service.delete_unit(unit_id, current_user)
    return None

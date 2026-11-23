from fastapi import APIRouter, Depends, File, UploadFile, status

from src.bulk.parser import template_response
from src.core.dependencies import get_current_user
from src.core.pagination import Pagination
from src.core.schemas import BulkImportResult
from src.modules.providers.dependencies import get_providers_service
from src.modules.providers.schemas import (
    ProviderContactCreate,
    ProviderContactResponse,
    ProviderContactUpdate,
    ProviderCreate,
    ProviderDeleteResponse,
    ProviderResponse,
    ProviderUpdate,
)
from src.modules.providers.service import (
    BULK_CONTACT_EXAMPLES,
    BULK_CONTACT_HEADERS,
    BULK_PROVIDER_EXAMPLES,
    BULK_PROVIDER_HEADERS,
    ProvidersService,
)
from src.modules.users.models import User

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.post(
    "/",
    response_model=ProviderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo proveedor",
)
def create_provider(
    provider_data: ProviderCreate,
    service: ProvidersService = Depends(get_providers_service),
    current_user: User = Depends(get_current_user),
):
    return service.create(provider_data, current_user)


@router.get(
    "/",
    response_model=list[ProviderResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los proveedores",
)
def get_all_providers(
    pagination: Pagination,
    service: ProvidersService = Depends(get_providers_service),
    current_user: User = Depends(get_current_user),
):
    return service.list(pagination.skip, pagination.limit)


@router.get(
    "/{provider_id}",
    response_model=ProviderResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener proveedor por ID con sus contactos",
)
def get_provider(
    provider_id: int,
    service: ProvidersService = Depends(get_providers_service),
    current_user: User = Depends(get_current_user),
):
    return service.get(provider_id)


@router.patch(
    "/{provider_id}",
    response_model=ProviderResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar proveedor parcialmente",
)
def update_provider(
    provider_id: int,
    provider_data: ProviderUpdate,
    service: ProvidersService = Depends(get_providers_service),
    current_user: User = Depends(get_current_user),
):
    return service.update(provider_id, provider_data, current_user)


@router.delete(
    "/{provider_id}",
    response_model=ProviderDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar proveedor (soft delete)",
)
def delete_provider(
    provider_id: int,
    service: ProvidersService = Depends(get_providers_service),
    current_user: User = Depends(get_current_user),
):
    return service.delete(provider_id, current_user)


@router.post(
    "/{provider_id}/contacts/",
    response_model=ProviderContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar contacto a un proveedor",
)
def create_contact(
    provider_id: int,
    contact_data: ProviderContactCreate,
    service: ProvidersService = Depends(get_providers_service),
    current_user: User = Depends(get_current_user),
):
    return service.create_contact(provider_id, contact_data, current_user)


@router.patch(
    "/{provider_id}/contacts/{contact_id}",
    response_model=ProviderContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar contacto de un proveedor",
)
def update_contact(
    provider_id: int,
    contact_id: int,
    contact_data: ProviderContactUpdate,
    service: ProvidersService = Depends(get_providers_service),
    current_user: User = Depends(get_current_user),
):
    return service.update_contact(provider_id, contact_id, contact_data, current_user)


@router.delete(
    "/{provider_id}/contacts/{contact_id}",
    response_model=ProviderDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar contacto de un proveedor (soft delete)",
)
def delete_contact(
    provider_id: int,
    contact_id: int,
    service: ProvidersService = Depends(get_providers_service),
    current_user: User = Depends(get_current_user),
):
    return service.delete_contact(provider_id, contact_id, current_user)


@router.post(
    "/bulk/import",
    response_model=BulkImportResult,
    status_code=status.HTTP_200_OK,
    summary="Cargar proveedores por archivo Excel/CSV",
)
def bulk_import_providers(
    file: UploadFile = File(...),
    service: ProvidersService = Depends(get_providers_service),
    current_user: User = Depends(get_current_user),
):
    return service.bulk_import_providers(file, current_user)


@router.get(
    "/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de proveedores",
)
def bulk_providers_template():
    return template_response(
        "plantilla_proveedores.xlsx", BULK_PROVIDER_HEADERS, BULK_PROVIDER_EXAMPLES
    )


@router.post(
    "/contacts/bulk/import",
    response_model=BulkImportResult,
    status_code=status.HTTP_200_OK,
    summary="Cargar contactos de proveedores por archivo Excel/CSV",
)
def bulk_import_provider_contacts(
    file: UploadFile = File(...),
    service: ProvidersService = Depends(get_providers_service),
    current_user: User = Depends(get_current_user),
):
    return service.bulk_import_contacts(file, current_user)


@router.get(
    "/contacts/bulk/template",
    status_code=status.HTTP_200_OK,
    summary="Descargar plantilla de contactos de proveedores",
)
def bulk_provider_contacts_template():
    return template_response(
        "plantilla_contactos_proveedores.xlsx",
        BULK_CONTACT_HEADERS,
        BULK_CONTACT_EXAMPLES,
    )

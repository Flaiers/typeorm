import asyncio
from functools import wraps
from uuid import UUID

import typer

from examples.service import ApplicationService
from examples.usecase.database import context_session
from examples.usecase.dto import (
    ApplicationCreate,
    ApplicationFilter,
    ApplicationRead,
)


class Typer(typer.Typer):

    def async_command(self, *args, **kwargs):
        def decorator(async_func):
            @wraps(async_func)
            def sync_func(*_args, **_kwargs):  # noqa: WPS430
                return asyncio.run(async_func(*_args, **_kwargs))

            self.command(*args, **kwargs)(sync_func)
            return async_func

        return decorator


app = Typer()


@app.async_command()
async def read_applications() -> None:
    dto = ApplicationFilter(
        phone='+78005553535',
        email='user@example.com',
    )
    async with context_session() as session:
        application_service = ApplicationService(session)
        applications = await application_service.find(dto)
        typer.echo([
            ApplicationRead.from_orm(application)
            for application in applications
        ])


@app.async_command()
async def read_application(application_id: UUID) -> None:
    async with context_session() as session:
        application_service = ApplicationService(session)
        application = await application_service.find_one_or_fail(application_id)
        typer.echo(ApplicationRead.from_orm(application))


@app.async_command()
async def create_application() -> None:
    dto = ApplicationCreate(
        phone='+78005553535',
        email='user@example.com',
        text='Your service is excellent!',
    )
    async with context_session() as session:
        application_service = ApplicationService(session)
        application = await application_service.create(dto)
        typer.echo(ApplicationRead.from_orm(application))


@app.async_command()
async def delete_application(application_id: UUID) -> None:
    async with context_session() as session:
        application_service = ApplicationService(session)
        application = await application_service.delete(application_id)
        typer.echo(ApplicationRead.from_orm(application))


if __name__ == '__main__':
    app()

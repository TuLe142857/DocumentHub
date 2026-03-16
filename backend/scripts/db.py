from typing import Annotated

from sqlalchemy.orm import Session
import typer

db_cli = typer.Typer(help="database cli")


@db_cli.command(name="inspect", short_help="Inspect ORM")
def inspect():
    from sqlalchemy.schema import CreateTable

    from app.models import ORMBase

    for table in ORMBase.metadata.sorted_tables:
        typer.echo(CreateTable(table))


@db_cli.command(name="test", help="Test database")
def test():
    from app.crud.user import CRUDUser
    from app.dependencies import get_db_engine
    from app.models import ORMBase

    engine = get_db_engine()
    with Session(engine) as session:
        crud = CRUDUser(session)
        res = crud.list()
        print(type(res))
        print(res[0])


@db_cli.command(name="drop", help="drop all tables")
def drop_database():
    from app.dependencies import get_db_engine
    from app.models import ORMBase

    ORMBase.metadata.drop_all(get_db_engine())


@db_cli.command(name="create", help="create all tables")
def create_database():
    from app.dependencies import get_db_engine
    from app.models import ORMBase

    ORMBase.metadata.create_all(get_db_engine())


@db_cli.command(name="seed", help="Seed database")
def seed_database(
    default_password: Annotated[
        str, typer.Option(help="default password")
    ] = "password123",
    drop: Annotated[bool, typer.Option(help="drop all tables before seeding")] = True,
):
    from sqlalchemy.exc import IntegrityError

    from app.dependencies import get_db_engine
    from app.models import Category, ORMBase, Role, User, UserProfile

    engine = get_db_engine()

    if drop:
        typer.secho("Dropping all tables", fg=typer.colors.BLUE)
        ORMBase.metadata.drop_all(engine)

        typer.secho("Creating all tables", fg=typer.colors.BLUE)
        ORMBase.metadata.create_all(engine)

    typer.secho("Seeding database", fg=typer.colors.BLUE)
    with Session(engine) as session:
        try:
            """
                    GENERATE NORMAL USER & ADMIN USER
            """
            role_user = Role.get_or_create("USER", session)
            role_admin = Role.get_or_create("ADMIN", session)

            typer.echo("Create user and admin")
            admin = User(
                email="admin@mail.com",
                username="admin",
                role=role_admin,
                profile=UserProfile(),
            )

            user = User(
                email="user@mail.com",
                username="username",
                role=role_user,
                profile=UserProfile(),
            )

            admin.set_password(default_password)
            user.set_password(default_password)

            session.add(admin)
            session.add(user)

            """
                    GENERATE CATEGORY
            """
            typer.echo("Create category")
            categories = ["Science", "Computer", "Programming"]
            for category_name in categories:
                session.add(Category(name=category_name))

            typer.secho("Commit", fg=typer.colors.BLUE)
            session.commit()
        except IntegrityError:
            typer.secho(
                "Some thing went wrong, rollback all things", fg=typer.colors.RED
            )

            session.rollback()

        typer.secho("Finish", fg=typer.colors.BLUE)

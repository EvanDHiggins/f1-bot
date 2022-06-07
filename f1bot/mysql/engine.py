import os

from typing import Callable, TypeVar

import sqlalchemy as sql # type: ignore
import sqlalchemy.engine as sqlengine


MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']

ergast_engine = sql.create_engine(f"mysql+mysqldb://evanhiggins:{MYSQL_PASSWORD}@localhost/ergast")

T = TypeVar('T')

def with_conn(engine: sqlengine.Engine) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Passes a mysql DB connection to the decorated function.

    func will be called with an additional argument which is a context-managed 
    sqlengine.Connection instance for the database specified by engine.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            with engine.connect() as conn:
                return func(conn, *args, **kwargs)
        return wrapper
    return decorator

with_ergast = with_conn(ergast_engine)

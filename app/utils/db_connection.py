import os
from contextlib import contextmanager
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import classes

MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

Base = declarative_base()

engine = create_engine(DATABASE_URL)


class InputTable(Base):
    __tablename__ = "input_table"
    metadata = MetaData()

    type = Table(__tablename__, metadata, autoload_with=engine).c.type
    sector = Table(__tablename__, metadata, autoload_with=engine).c.sector
    net_usable_area = Table(
        __tablename__, metadata, autoload_with=engine
    ).c.net_usable_area
    net_area = Table(__tablename__, metadata, autoload_with=engine).c.net_area
    n_rooms = Table(__tablename__, metadata, autoload_with=engine).c.n_rooms
    n_bathroom = Table(
        __tablename__, metadata, autoload_with=engine
    ).c.n_bathroom
    latitude = Table(__tablename__, metadata, autoload_with=engine).c.latitude
    longitude = Table(
        __tablename__, metadata, autoload_with=engine
    ).c.longitude
    price = Table(__tablename__, metadata, autoload_with=engine).c.price


@contextmanager
def get_db_session():
    """
    Gets a database session and closes it after use.

    Raises:
        e: an exception

    Yields:
        sessionmaker: the database session
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    except Exception as e:
        raise e
    finally:
        session.close()


def fetch_data_as_dataframe() -> pd.DataFrame:
    """
    Fetch data from the database and convert it to a Pandas DataFrame.

    Returns:
        pd.DataFrame: the data from the database as a Pandas DataFrame
    """
    with get_db_session() as session:
        query = session.query(InputTable)
        results = query.all()

        data = [classes.InputColumns(**row.__dict__) for row in results]

        df = pd.DataFrame([item.model_dump() for item in data])
        return df


def write_inference_from_model_to_db(prediction: list):
    """
    Write the inference results to the database in the field 'price'

    Args:
        prediction (list): the predictions
    """
    with get_db_session() as session:
        for i, pred in enumerate(prediction):
            row = session.query(InputTable).get(i + 1)
            row.price = pred
        session.commit()

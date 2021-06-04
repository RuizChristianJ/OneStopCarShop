from scraper import SelectionEnum, WebDriverWrapper
import rds_config
import pymysql
import pandas as pd
from sqlalchemy import *


def lambda_handler(*args, **kwargs):

    connection_string = f'mysql+pymysql://{rds_config.db_username}:{rds_config.db_password}@{rds_config.db_endpoint}:3306/{rds_config.db_name}'
    db = create_engine(connection_string).connect()

    driver = WebDriverWrapper()
    makes = driver.get_make_id(SelectionEnum.allMakes)
    makes_df = pd.DataFrame({'make_name': makes.keys(), 'carguru_make_id': makes.values()})
    makes_df.index.name = 'make_id'

    df = pd.read_sql_table('Makes', db)
    df = df.set_index('make_id')

    table_status = ''

    if makes_df.equals(df) is False:
        makes_df.to_sql(name='Makes', con=db, if_exists='replace')
        table_status = 'Makes table updated'
    else:
        table_status = 'Makes table up to date'

    return table_status

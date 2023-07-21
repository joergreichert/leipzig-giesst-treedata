from sqlalchemy import text
import logging
from shapely.wkt import dumps
import pandas

logger = logging.getLogger(__name__)


def upload_radolan_data(engine, radolan_data):
    radolan_data = radolan_data.rename(columns={'MYFLD': 'value'})
    radolan_data['measured_at'] = pandas.to_datetime(radolan_data['measured_at'])
    # radolan_data['geometry'] = dumps(radolan_data['geometry'], rounding_precision=5)
    radolan_data.to_postgis('radolan_temp', engine, if_exists='replace', index=False)
    with engine.connect() as conn:
        conn.execute(text('''
            INSERT INTO "public".radolan_data(geom_id, value, measured_at) 
            SELECT radolan_geometry.id, radolan_temp.value, radolan_temp.measured_at 
            FROM radolan_geometry JOIN radolan_temp 
            ON ST_WithIn(radolan_geometry.centroid, radolan_temp.geometry)       
        '''))


def purge_data_older_than_time_limit_days(engine, time_limit_days):
    with engine.connect() as conn:
        conn.execute(text(f'''
            DELETE FROM radolan_data 
            WHERE measured_at < NOW() - INTERVAL '{time_limit_days} days'
        '''))


def purge_duplicates(engine):
    with engine.connect() as conn:
        conn.execute(text('''
            DELETE FROM radolan_data AS a USING radolan_data AS b 
            WHERE a.id < b.id AND a.geom_id = b.geom_id 
            AND a.measured_at = b.measured_at
        '''))

from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


def upload_radolan_data(engine, radolan_data):
    radolan_data.to_postgis('radolan_temp', engine, if_exists='replace', index=False)
    with engine.connect() as conn:
        result = conn.execute(text('INSERT INTO radolan_data (geom_id, value, measured_at)'
                        'SELECT radolan_geometry.id, radolan_temp.value, radolan_temp.measured_at '
                        'FROM radolan_geometry JOIN radolan_temp ON ST_WithIn(radolan_geometry.centroid, '
                        'radolan_temp.geometry);'))
        logger.info(result)

from datetime import datetime
from datetime import timedelta
import logging
import psycopg2
import psycopg2.extras
from sqlalchemy import text

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# get all grid cells, get data for last 30 days for each grid cell,
# generate a list for each grid cell
# as we don't store "0" events, those need to be generated,
# afterwards trees are updated and a geojson is being created

def get_weather_data_grid_cells(engine, time_limit_days):
    with engine.connect() as conn:
        result = conn.execute(text(f'''
            SELECT 
                radolan_geometry.id, 
                ST_AsGeoJSON(radolan_geometry.geometry), 
                ARRAY_AGG(radolan_data.measured_at) AS measured_at, 
                ARRAY_AGG(radolan_data.value) AS value 
            FROM radolan_geometry 
            JOIN radolan_data ON radolan_geometry.id = radolan_data.geom_id 
            WHERE radolan_data.measured_at > NOW() - INTERVAL '{time_limit_days} days' 
            GROUP BY radolan_geometry.id, radolan_geometry.geometry
        '''))
        return result.fetchall()


def get_sorted_cleaned_grid(grid, time_limit_days):
    clean = []
    for cell in grid:
        end_date = datetime.now() + timedelta(days=-1)
        end_date = end_date.replace(hour=23, minute=50, second=0, microsecond=0)
        start_date = datetime.now() + timedelta(days=-time_limit_days)
        start_date = start_date.replace(hour=0, minute=50, second=0, microsecond=0)
        clean_data = []
        while start_date <= end_date:
            found = False
            for dateindex, date in enumerate(cell[2]):
                if start_date == date:
                    found = True
                    clean_data.append(cell[3][dateindex])
                    # TODO: Add the algorithm that calculates the actually absorbed amount of water (upper & lower threshold)
            if not found:
                clean_data.append(0)
            start_date += timedelta(hours=1)
        clean.append(clean_data)
    return clean


def get_sorted_cleaned_grid_cells(cleaned_grid):
    cells = []
    for cellindex, cell in enumerate(cleaned_grid):
        cells.append([
            cleaned_grid[cellindex],
            sum(cleaned_grid[cellindex]),
            cell[1]
        ])
    return cells


def update_statistics_db(filelist, engine, time_limit_days, last_received):
    if len(filelist) > 0:
        end_date = datetime.now() + timedelta(days=-1)
        end_date = end_date.replace(hour=23, minute=50, second=0, microsecond=0)
        start_date = datetime.now() + timedelta(days=-time_limit_days)
        start_date = start_date.replace(hour=0, minute=50, second=0, microsecond=0)
        datetime_format = "%Y-%m-%d %H:%M:%S"
        with engine.connect() as conn:
            conn.execute(text(f'''
                UPDATE radolan_harvester SET 
                    collection_date = '{last_received.strftime(datetime_format)}', 
                    start_date = '{start_date.strftime(datetime_format)}', 
                    end_date = '{end_date.strftime(datetime_format)}' 
                WHERE id = 1
            '''))


def update_tree_radolan_days(engine, values):
    logging.info("updating trees 🌳")
    try:
        with engine.connect() as conn:
            conn.begin()
            psycopg2.extras.execute_batch(
                conn,
                text('''
                    UPDATE trees SET radolan_days = %s, radolan_sum = %s 
                    WHERE ST_CoveredBy(geom, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
                '''),
                values
            )
            conn.commit()
    except:
        logging.error("❌Could not update radolan days")

    # update all the trees we have missed with the first round :(
    logging.info("updating sad trees 🌳")
    try:
        with engine.connect() as conn:
            conn.begin()
            psycopg2.extras.execute_batch(
                conn,
                text('''
                    UPDATE trees SET radolan_days = %s, radolan_sum = %s 
                    WHERE trees.radolan_sum IS NULL 
                    AND ST_CoveredBy(geom, 
                        ST_Buffer(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), 0.00005)
                    )
                '''),
                values
            )
            conn.commit()
    except:
        logging.error("❌Could not update radolan days")

from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


def create_radolan_schema(engine):
    with engine.connect() as conn:
        conn.begin()
        conn.execute(text('CREATE SEQUENCE IF NOT EXISTS radolan_geometry_id_seq'))
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS "public"."radolan_geometry" (
                "id" int4 NOT NULL DEFAULT nextval('radolan_geometry_id_seq'::regclass),
                "geometry" geometry,
                "centroid" geometry,
                PRIMARY KEY ("id")
            );
        '''))
        conn.execute(text('CREATE SEQUENCE IF NOT EXISTS radolan_data_id_seq'))
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS "public"."radolan_data" (
                "id" int4 NOT NULL DEFAULT nextval('radolan_data_id_seq'::regclass),
                "measured_at" timestamp,
                "value" int2,
                "geom_id" int2,
                PRIMARY KEY ("id")
            );
        '''))
        conn.commit()


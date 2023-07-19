from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


def create_radolan_schema(engine):
    with engine.connect() as conn:
        conn.execute(text('CREATE SEQUENCE IF NOT EXISTS radolan_geometry_id_seq'))
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS "public"."radolan_geometry" (
                "id" int4 NOT NULL DEFAULT nextval('radolan_geometry_id_seq'::regclass),
                "geometry" geometry,
                "centroid" geometry,
                PRIMARY KEY ("id")
            );
        '''))
        count = conn.execute(text('SELECT count(*) FROM public.radolan_geometry WHERE id = \'9047\'')).scalar()
        logger.info(f" *** found: {count}")
        if count == 0:
            result = conn.execute(text('''
                INSERT INTO public.radolan_geometry("id", "geometry", "centroid") 
                VALUES ('9047','0106000020E61000000100000001030000000100000005000000B13385CE6BCC28400E10CCD1E3AB49406C26DF6C73D328400EF3E505D8AB4940FB05BB61DBD22840BD8C62B9A5A94940CF6BEC12D5CB2840BDA94885B1A94940B13385CE6BCC28400E10CCD1E3AB4940','0101000020E6100000EC2FF2EEA3CF2840C7D44FCEC4AA4940');
            '''))
            logger.info(result)
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



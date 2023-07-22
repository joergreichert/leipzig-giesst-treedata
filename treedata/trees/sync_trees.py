from sqlalchemy import text


def create_trees_table(engine):
    with engine.connect() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS "public"."trees" (
                "id" text NOT NULL,
                "lat" text,
                "lng" text,
                "artdtsch" text,
                "artbot" text,
                "gattungdeutsch" text,
                "gattung" text,
                "standort_nr" text,
                "strname" text,
                "haus_nr" text,
                "pflanzjahr" text,
                "stammdurch" text,
                "kronedurch" text,
                "baumhoehe" text,
                "bezirk" text,
                "geom" geometry,
                "zuletztakt" timestamp,
                "adopted" text,
                "watered" text,
                "radolan_sum" int4,
                "radolan_days" _int4,
                PRIMARY KEY ("id")
            );        
        '''))


def delete_removed_trees(engine, original_tree_table, tmp_tree_table):
    with engine.connect() as conn:
        conn.execute(text(f'''
            DELETE FROM public."{original_tree_table}" WHERE standort_nr IN (
                SELECT A."standort_nr" FROM public."{original_tree_table}" AS A
                WHERE A."standort_nr" NOT IN (
                    SELECT B."standort_nr" FROM public."{tmp_tree_table}" AS B
                ) 
                AND A."standort_nr" not like 'osm_%'
            )        
        '''))


def insert_added_trees(engine, original_tree_table, tmp_tree_table):
    with engine.connect() as conn:
        conn.execute(text(f'''
            INSERT INTO public."{original_tree_table}" ("standort_nr")
            SELECT standort_nr FROM public."{tmp_tree_table}" AS B
            WHERE B."standort_nr" NOT IN (
                SELECT "standort_nr" FROM public."{original_tree_table}" AS A
            )        
        '''))


def updated_trees(engine, original_tree_table, tmp_tree_table):
    with engine.connect() as conn:
        conn.execute(text(f'''
            UPDATE public."{original_tree_table}" AS A
               SET ("lat", "lng", "artdtsch", "artbot", "gattungdeutsch", "gattung", "standort_nr", "strname", 
                    "haus_nr", "pflanzjahr", "stammdurch", "kronedurch", "baumhoehe", "bezirk", "geom", "zuletztakt") = 
                  (
                      ( 
                        SELECT B."lat", B."lng", B."artdtsch", B."artbot", B."gattungdeutsch", B."gattung", 
                               B."standort_nr", B."strname", B."haus_nr", B."pflanzjahr", B."stammdurch", 
                               B."kronedurch", B."baumhoehe", B."bezirk", B."geom", B."zuletztakt" 
                        FROM FROM public."{tmp_tree_table}" AS B 
                        WHERE A."standort_nr" = B."standort_nr" LIMIT 1
                      )
                  )
                WHERE A."standort_nr" not like 'osm_%'        
        '''))


def sync_trees(engine, original_tree_table, tmp_tree_table):
    create_trees_table(engine)
    delete_removed_trees(engine, original_tree_table, tmp_tree_table)
    insert_added_trees(engine, original_tree_table, tmp_tree_table)
    updated_trees(engine, original_tree_table, tmp_tree_table)
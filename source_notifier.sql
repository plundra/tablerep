CREATE OR REPLACE FUNCTION tablerep_notifier ()
RETURNS trigger AS $$
DECLARE
    old_key text DEFAULT '';
    new_key text DEFAULT '';
BEGIN
    CASE TG_OP
        WHEN 'UPDATE' THEN
            old_key = OLD.id;
            new_key = OLD.id;
        WHEN 'INSERT' THEN
            new_key = NEW.id;
        WHEN 'DELETE' THEN
            old_key = OLD.id;
    END CASE;

    PERFORM pg_notify('tablerep',
                      format('%s:%s:%s:%s:%s',
                             TG_OP,
                             TG_TABLE_SCHEMA,
                             TG_TABLE_NAME,
                             new_key,
                             old_key
                      )
            );

    RETURN NULL;

EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Error in tabelrep_notifier, %: %', SQLSTATE, SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION biz_a_cust_pruner ()
RETURNS trigger AS $$
BEGIN
    RAISE NOTICE 'Deleting % from business_a.customers', NEW.id;
    DELETE FROM business_a.customers WHERE id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

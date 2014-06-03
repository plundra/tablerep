CREATE TRIGGER tablerep_customers_change
AFTER INSERT OR UPDATE ON business_a.customers
FOR EACH ROW EXECUTE PROCEDURE tablerep_notifier();

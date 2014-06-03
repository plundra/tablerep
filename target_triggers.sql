CREATE TRIGGER biz_a_cust_prune_trigger
BEFORE INSERT ON business_a.customers
FOR EACH ROW EXECUTE PROCEDURE  biz_a_cust_pruner();

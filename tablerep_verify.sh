#!/usr/bin/env bash
# Example script on how to verify the two tables are in-sync

SOURCE_DSN="service=biz-a-prod"
TARGET_DSN="service=biz-b-prod"

SOURCE_QUERY="COPY (
SELECT id, firstname, lastname, email, country_id
FROM business_a.customers
JOIN countries USING (country)
ORDER BY id
) TO STDOUT;"

TARGET_QUERY="COPY (
SELECT * FROM business_a.customers
ORDER BY id
) TO STDOUT;"

diff -u0 <(psql -Xc "$SOURCE_QUERY" "$SOURCE_DSN") \
         <(psql -Xc "$TARGET_QUERY" "$TARGET_DSN")

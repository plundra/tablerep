#!/usr/bin/env python
import psycopg2
import select
import re
import logging
from cStringIO import StringIO

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger("tablerep")

SOURCE_DSN = "service=biz-a-prod"
TARGET_DSN = "service=biz-b-prod"

SOURCE_COPY = """COPY (
SELECT id, firstname, lastname, email, country_id
FROM business_a.customers
JOIN countries USING ON (country)
WHERE id = %s
) TO STDOUT;"""

TARGET_COPY = """COPY business_a.customers (
id, firstname, lastname, email, country_id
) FROM STDIN;"""

# XXX Assumes integer key
PAYLOAD_REGEXP = re.compile(
    r"^(?P<TG_OP>\w+):(?P<TG_TABLE_SCHEMA>\w+):(?P<TG_TABLE_NAME>\w+):" \
    r"(?P<NEW_KEY>\d*):(?P<OLD_KEY>\d*)$")

with psycopg2.connect(SOURCE_DSN) as source_conn, \
     psycopg2.connect(TARGET_DSN) as target_conn:

    source_conn.autocommit = True
    target_conn.autocommit = True

    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    source_cursor.execute("LISTEN tablerep;")
    #target_cursor.execute("SET ROLE plundra_super;") ## When testing

    while select.select([source_conn], [], []):
        source_conn.poll()
        while source_conn.notifies:
            # Order matters, INSERT->UPDATE->DELETE on same pk, start from the back
            notify = source_conn.notifies.pop(0)

            payload_match = PAYLOAD_REGEXP.match(notify.payload)

            if not payload_match:
                _log.warning("Unknown payload: %r", notify.payload)
                continue

            payload = payload_match.groupdict()

            if payload["TG_OP"] not in ("INSERT", "UPDATE"):
                _log.info("Ignorning %(TG_OP)s", payload)
                continue

            if payload["TG_OP"] == "UPDATE" and payload["NEW_KEY"] != payload["OLD_KEY"]:
                _log.error("Unhandled PK change: %(OLD_KEY)s -> %(NEW_KEY)s", payload)
                continue

            # XXX: Again, assumes integer key
            try:
                key = int(payload["NEW_KEY"])
            except ValueError:
                _log.error("Unexpected (non-numeric) key: %(NEW_KEY)s", payload)
                continue

        _log.info("%(TG_OP)s for PK %(NEW_KEY)s", payload)

        copy_buf = StringIO()
        source_cursor.copy_expert(source_cursor.mogrify(SOURCE_COPY, (key,)), copy_buf)
        copy_buf.seek(0)
        target_cursor.copy_expert(TARGET_COPY, copy_buf)

#!/bin/bash

WORKING_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

. $WORKING_DIR/config

$SQLPLUS -S $DB_USER/$DB_PASS@$TNS/$SERVICE_NAME <<EOF
SELECT TABLESPACE_NAME,SUM(BYTES)/1024/1024/1024 "FREE SPACE(GB)" FROM DBA_FREE_SPACE GROUP BY TABLESPACE_NAME;

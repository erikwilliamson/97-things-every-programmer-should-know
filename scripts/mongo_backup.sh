#!/usr/bin/env bash

set -e
SCRIPT_NAME=$(basename $0)
SCRIPT_DIR=$(dirname $0)
source ${SCRIPT_DIR}/common.sh

BASE_DIR=${SCRIPT_DIR}/..
LOCAL_MONGO_BACKUP_DIR=${BASE_DIR}/mongo_backups

echo "Enter the database pasword: "
read -s DB_PASSWORD


PRODUCTION_URI="${PROTOCOL}://${USERNAME}:${DB_PASSWORD}@${PRODUCTION_HOST}:${PRODUCTION_PORT}"


function get_collection_names() {
  COLLECTIONS=$(${MONGO_SH} --authenticationDatabase admin ${PRODUCTION_URI}/${DATABASE_NAME} --eval "printjson(db.getCollectionNames())" --quiet --json=canonical | egrep -ve "\[|\]" | cut -d "'" -f 2)
  echo "${COLLECTIONS}"
}

COLLECTION_NAMES=$(get_collection_names)

echo "${COLLECTION_NAMES}" | while read -r COLLECTION_NAME; do
  log "INFO" "${SCRIPT_NAME}" "Exporting ${COLLECTION_NAME}"
  ${MONGO_EXPORT} --authenticationDatabase=admin --db=${DATABASE_NAME} --uri ${PRODUCTION_URI} --collection ${COLLECTION_NAME}
done

${MONGO_DUMP} --uri ${PRODUCTION_URI} --out ${LOCAL_MONGO_BACKUP_DIR}

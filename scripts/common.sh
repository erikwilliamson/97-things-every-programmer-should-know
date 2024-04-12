E_OK=0
E_USAGE=1

HOMEBREW_BIN="/opt/homebrew/bin"

MONGO_EXPORT="${HOMEBREW_BIN}/mongoexport"
MONGO_SH="${HOMEBREW_BIN}/mongosh"
MONGO_DUMP="${HOMEBREW_BIN}/mongodump"

PROTOCOL="mongodb"
USERNAME="mongo"
DATABASE_NAME=wj

LOCAL_HOST="localhost"
LOCAL_PORT="27017"
LOCAL_URI="${PROTOCOL}://${LOCAL_HOST}:${LOCAL_PORT}"

DEVELOPMENT_HOST="containers-us-west-116.railway.app"
DEVELOPMENT_PORT="5553"
#DEVELOPMENT_URI="${PROTOCOL}://${USERNAME}:${DEVELOPMENT_PASSWORD}@${DEVELOPMENT_HOST}:${DEVELOPMENT_PORT}"

PRODUCTION_HOST="containers-us-west-56.railway.app"
PRODUCTION_PORT="6017"
#PRODUCTION_URI="${PROTOCOL}://${USERNAME}:${PRODUCTION_PASSWORD}@${PRODUCTION_HOST}:${PRODUCTION_PORT}"

function get_mongo_uri {
  ENVIRONMENT=${1-UNKNOWN}
  case "${ENVIRONMENT}" in
    "development") echo "${DEVELOPMENT_URI}"
                   ;;
    "production") echo "${PRODUCTION_URI}"
                  ;;
    "local") echo "${LOCAL_URI}"
             ;;
    *) echo "UNKNOWN"
       ;;
  esac
}

function get_timestamp {
  date +"%Y-%m-%dT%H:%M:%S"
}

function log {
  LEVEL=${1-UNKNOWN}
  LOG_PREFIX=${2-UNKNOWN}
  MESSAGE=${3-UNKNOWN}
  echo "$(get_timestamp) : ${LOG_PREFIX} : ${LEVEL} : ${MESSAGE}"
}

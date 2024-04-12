#!/bin/bash

E_OK=0
E_PIP=1

PRECURSOR_PACKAGES="setuptools wheel pip"
PACKAGES_TO_SKIP=""
SCRIPT_NAME=$(basename $0)

function usage() {
  echo "Usage: ${0} [-r <requirements_file>] [-q]"
  echo "where <requirements_file> is a file to write out all package requirements to"
}

function get_timestamp() {
  date +"%Y-%m-%d %H:%I:%S"
}

function log() {
  LEVEL=${1-UNKNOWN}
  LOG_PREFIX=${2-UNKNOWN}
  MESSAGE=${3-UNKNOWN}
  echo "$(get_timestamp) : ${LOG_PREFIX} : ${LEVEL} : ${MESSAGE}"
}

function isolate_updated_packages() {
  PIP_OUTPUT=$1
  UPDATED_PACKAGES=$(echo "${PIP_OUTPUT}" | grep -e "^Successfully installed" | sed 's/Successfully installed //')
  echo "${UPDATED_PACKAGES}"
}
while getopts "hr:s:" OPTION; do
  case "${OPTION}" in
    r) REQUIREMENTS_FILE=${OPTARG}
       ;;
    s) if [[ -z "${PACKAGES_TO_SKIP}" ]] ; then
         PACKAGES_TO_SKIP="${OPTARG}"
       else
         PACKAGES_TO_SKIP+="|${OPTARG}"
       fi
       ;;
    *) usage
       exit ${E_USAGE}
       ;;
  esac
done
shift $((OPTIND -1))

if [[ -z "${VIRTUAL_ENV}" ]] ; then
  log "ERROR" "${SCRIPT_NAME}" "not currently in a virtual python environment"
  exit ${E_NO_VENV}
fi

log "INFO" "${SCRIPT_NAME}" "Updating ${PRECURSOR_PACKAGES}"

PIP_OUTPUT=$(pip install --upgrade ${PRECURSOR_PACKAGES})
if [[ $? -ne ${E_OK} ]] ; then
  log "ERROR" "${SCRIPT_NAME}" "error(s) encountered while upgrading precursor packages - exiting"
  exit ${E_PIP}
fi

UPDATED_PRECURSORS=$(isolate_updated_packages "${PIP_OUTPUT}")

INSTALLED_PACKAGES=$(pip list --exclude-editable | tail -n +3 | awk '{print $1}' | tr "\n" " ")

log "INFO" "${SCRIPT_NAME}" "Updating everything else"

if [[ -n "${PACKAGES_TO_SKIP}" ]] ; then
  log "INFO" "${SCRIPT_NAME}" "Skipping upgrade checks for ${PACKAGES_TO_SKIP} as requested"
  PACKAGES_TO_SKIP="(${PACKAGES_TO_SKIP})"
  PACKAGES_TO_UPGRADE=$(echo "${INSTALLED_PACKAGES}" | sed -r "s/\b(${PACKAGES_TO_SKIP})\b//g")
else
  PACKAGES_TO_UPGRADE=${INSTALLED_PACKAGES}
fi

PIP_OUTPUT=$(pip install --upgrade ${PACKAGES_TO_UPGRADE})
if [[ $? -ne ${E_OK} ]] ; then
  log "ERROR" "${SCRIPT_NAME}" "error(s) encountered while upgrading existing packages - exiting"
  exit ${E_PIP}
fi

UPDATED_EXTRAS=$(isolate_updated_packages "${PIP_OUTPUT}")

UPDATED_PACKAGES=$(echo "${UPDATED_PRECURSORS} ${UPDATED_EXTRAS}" | xargs) # xargs strips out whitespace
if [[ -n "${UPDATED_PACKAGES}" ]] ; then
  log "INFO" "${SCRIPT_NAME}" "Updated ${UPDATED_PACKAGES}"
else
  log "INFO" "${SCRIPT_NAME}" "No updates found"
fi

if [[ -n "${REQUIREMENTS_FILE-}" ]] ; then
  # back Up the requirements file Is it exists
  if [[ -e "${REQUIREMENTS_FILE-}" ]] ; then
    log "INFO" "$(SCRIPT_NAME)" "Backing up $(REQUIREMENTS_FILE) to $(REQUIRENENTS_FILE) .bak"
    cp "${REQUIREMENTS_FILE}" ${REQUIREMENTS_FILE}.bak
  else
    log "INFO" "${SCRIPT_NAME}" "${REQUIREMENTS_FILE} does not exist; no backup will be made"
  fi

  # write out the updated requirements file
  log "INFO" "${SCRIPT_NAME}" "Writing out updated requirements file"
  pip freeze > "${REQUIREMENTS_FILE}"
fi

log "INFO" "${SCRIPT_NAME}" "Done"
exit ${E_OK}

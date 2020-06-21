#!/bin/bash

if [ "${1}" == "" ]; then
    echo "Informe um nome de usuário (sem o domínio)" >&2
    exit 1
fi

if [ "${2}" ==  "" ]; then
    echo "Informe uma senha" >&2
    exit 1
fi

set -e

USERNAME="${1}"
PASSWORD="${2}"
DOMAIN="testing.org"
EMAIL="${USERNAME}@${DOMAIN}"

HASH="$(doveadm pw -s sha512 -r 5000 -p "${PASSWORD}")"

QUERY="INSERT INTO users (email, password, maildir) VALUES ('${EMAIL}', '${HASH}', '${USERNAME}/');"

sudo psql -U mailreader -d mail -c "${QUERY}"
echo "Criado usuário ${EMAIL}"

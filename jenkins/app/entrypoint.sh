#!/bin/bash

################################################################################
# Estre trecho do script instala o NodeJS através do NVM e uma dependência que #
# possibilita a execução dos testes em navegadores (headless) usando o QUnit.  #
################################################################################

if [[ ! -f "${JENKINS_HOME}/.customrc" ]]; then
    echo ">>> Creating ~/.customrc"
    touch "${JENKINS_HOME}/.customrc"
    echo -e '# Load Custom here\nsource ~/.customrc\n' > "${JENKINS_HOME}/.bashrc"
    cat /etc/skel/.bashrc >> "${JENKINS_HOME}/.bashrc"
fi


if [[ ! -f "${JENKINS_HOME}/.nvm/.nvm.sh" ]]; then
    echo ">>> Installing NVM"
    mkdir -p "${JENKINS_HOME}/.nvm"
    git clone https://github.com/nvm-sh/nvm.git "${JENKINS_HOME}/.nvm"

    echo 'export NVM_DIR="$HOME/.nvm"' >> "${JENKINS_HOME}/.customrc"
    echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm' >> "${JENKINS_HOME}/.customrc"
    echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion' >> "${JENKINS_HOME}/.customrc"

    source "${JENKINS_HOME}/.bashrc"
fi


if [[ "$(nvm current)" == "none" ]]; then
    echo ">>> Installing NODEJS LTS and Node QUnit Puppeteer Plugin"
    nvm install --lts

    # Para os testes automatizados no Jenkins, usaremos o plugin do QUnit
    # que usa uma instância do headless do Chromium.
    # - https://www.npmjs.com/package/node-qunit-puppeteer
    # EX:
    # npx node-qunit-puppeteer ./lists/static/tests/tests.html  30000 "--allow-file-access-from-files --no-sandbox"
    npm install -g node-qunit-puppeteer
fi

###############################
# Fim da instalação do NodeJS #
###############################


# Iniciando o Jenkins
exec /usr/bin/java \
        -Djava.awt.headless=true \
        -jar /usr/share/jenkins/jenkins.war \
        --webroot=/var/cache/jenkins/war \
        --httpPort=8080

# Chamada realizada em "/etc/init.d/jenkins" para iniciar o servidor
# /usr/bin/daemon \
#     --name=jenkins \
#     --inherit \
#     --env=JENKINS_HOME=/var/lib/jenkins \
#     --output=/var/log/jenkins/jenkins.log \
#     --pidfile=/var/run/jenkins/jenkins.pid \
#     --running \
#         /bin/su \
#             -l jenkins \
#             --shell=/bin/bash \
#             -c /usr/bin/daemon \
#             --name=jenkins \
#             --inherit \
#             --env=JENKINS_HOME=/var/lib/jenkins \
#             --output=/var/log/jenkins/jenkins.log \
#             --pidfile=/var/run/jenkins/jenkins.pid \
#             --
#             /usr/bin/java \
#                 -Djava.awt.headless=true \
#                 -jar /usr/share/jenkins/jenkins.war \
#                 --webroot=/var/cache/jenkins/war \
#                 --httpPort=8080

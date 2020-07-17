#!/bin/bash

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
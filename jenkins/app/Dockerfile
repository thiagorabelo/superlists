FROM ubuntu:18.04

ENV JENKINS_HOME=/var/lib/jenkins

RUN apt-get update && apt-get install -y wget gnupg nano openjdk-11-jdk \
    && wget -q -O- https://pkg.jenkins.io/debian-stable/jenkins.io.key | apt-key add - \
    && echo "deb https://pkg.jenkins.io/debian-stable binary/" | tee /etc/apt/sources.list.d/jenkins.list \
    && apt-get update \
    && apt-get install -y jenkins firefox python3-venv xvfb build-essential libssl-dev libffi-dev git libxss1 \
    && wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz \
    && tar xvzf geckodriver-v0.26.0-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./entrypoint.sh /entrypoint.sh

VOLUME [ "/var/lib/jenkins" ]

USER jenkins

# No entrypoint há configuração do NodeJS para testes em navegador headless
ENTRYPOINT [ "/entrypoint.sh" ]

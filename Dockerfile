FROM python:latest
RUN apt-get update && \
    apt-get install -y wget gnupg unzip firefox-esr && \
    rm -rf /var/lib/apt/lists/*
RUN GECKO_DRIVER_VERSION=$(curl -sS https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep 'tag_name' | cut -d\" -f4) && \
    wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/$GECKO_DRIVER_VERSION/geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ && \
    rm /tmp/geckodriver.tar.gz
RUN pip install selenium beautifulsoup4 lxml
COPY . /app
WORKDIR /app
CMD ["python", "main.py"]
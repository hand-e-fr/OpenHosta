ARG BASE_DISTRO=debian:latest
ARG PYTHON_VERSION=3.9

FROM ${BASE_DISTRO}

RUN if cat /etc/*release | grep -q -i "debian\|ubuntu"; then \
      apt-get update && apt-get install -y \
      python${PYTHON_VERSION} \
      python3-pip \
    && apt-get clean; \
    elif cat /etc/*release | grep -q -i "fedora"; then \
      dnf install -y python${PYTHON_VERSION/\./} \
                    python3-pip && dnf clean all; \
    fi

WORKDIR /usr/src/app

COPY . .
RUN python3 -m pip install --no-cache-dir .[pydantic]

CMD ["python3", "test.py"]

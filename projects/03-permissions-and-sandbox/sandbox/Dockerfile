# A disposable sandbox image for running an agent's commands.
# Dependencies are installed at build time, so the task can run with the network off.
FROM python:3.12-slim

RUN useradd --create-home --uid 1000 agent
WORKDIR /work
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

USER agent
CMD ["python", "-m", "pytest", "-q"]

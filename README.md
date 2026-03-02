# IoT Deployment Methods Portfolio

This repository showcases a deployment-focused IoT simulation built as part of an IoT Software Engineering project. The main artifact is a **Digital Twin Smart HVAC Simulation** that models how a connected device, a messaging layer, and a cloud-side digital twin interact in a real IoT deployment.

## Featured Project

The core project lives in [digital-twin-sim](C:/Users/Jehosua%20Joya/Desktop/iot-deployment-methods/digital-twin-sim). It simulates a smart air conditioner without requiring physical hardware.

The system includes:

- A **physical device simulator** written in Python that behaves like an air conditioner.
- An **MQTT broker** that carries telemetry and remote commands.
- A **digital twin service** written in Python that mirrors the device state, estimates energy cost, and detects basic maintenance issues.
- A **Docker Compose** setup that deploys the full system as a small distributed environment.

## Why This Project Matters

This repository is intended to demonstrate practical skills that are directly relevant to IoT deployment and backend engineering:

- Containerizing independent services with Docker
- Orchestrating multi-service systems with Docker Compose
- Implementing publish/subscribe communication with MQTT
- Designing a digital twin pattern for remote monitoring and control
- Separating device-side logic from cloud-side analytics
- Building a reproducible, hardware-free simulation for testing and demonstration

## Repository Layout

```text
iot-deployment-methods/
|-- README.md
|-- OVERVIEW.md
`-- digital-twin-sim/
    |-- docker-compose.yml
    |-- mosquitto.conf
    |-- physical_device/
    |   |-- device.py
    |   `-- Dockerfile
    `-- digital_twin/
        |-- twin.py
        `-- Dockerfile
```

## Quick Start

From the repository root:

```bash
cd digital-twin-sim
docker compose up --build
```

In another terminal, send commands to the simulated HVAC unit:

```bash
docker exec -it digital-twin-mqtt mosquitto_pub -t "home/ac/cmd" -m "ON"
docker exec -it digital-twin-mqtt mosquitto_pub -t "home/ac/cmd" -m "20.5"
docker exec -it digital-twin-mqtt mosquitto_pub -t "home/ac/cmd" -m "OFF"
```

## What a Visitor Should Notice

- The project is not just a script; it is a small **distributed system**.
- The design models a realistic IoT workflow: device, network protocol, cloud logic, and monitoring.
- The digital twin keeps a synchronized software representation of a physical asset, which is a common industrial IoT pattern.

## Documentation

- Portfolio-level project summary: [OVERVIEW.md](C:/Users/Jehosua%20Joya/Desktop/iot-deployment-methods/OVERVIEW.md)
- Project run guide: [digital-twin-sim/README.md](C:/Users/Jehosua%20Joya/Desktop/iot-deployment-methods/digital-twin-sim/README.md)

## Status

This repository currently contains a working simulation environment for demonstrating IoT deployment concepts. It is designed to be easy to review, run locally, and extend with additional features such as dashboards, persistence, or more advanced predictive maintenance logic.

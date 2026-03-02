# Project Overview

## Summary

This repository contains a simple but realistic IoT deployment simulation centered on a **Digital Twin Smart HVAC System**. The goal is to demonstrate how an IoT solution can be structured and deployed even when physical hardware is not available.

Instead of using a real air conditioner, the project uses Docker containers to represent the main layers of an IoT system:

- A simulated edge device
- A communication broker
- A cloud-side digital twin

This makes the repository suitable for academic work, portfolio review, and technical discussion around deployment-oriented IoT engineering.

## Architecture

The implementation in [digital-twin-sim](C:/Users/Jehosua%20Joya/Desktop/iot-deployment-methods/digital-twin-sim) is built around three services:

1. **Physical Device Simulator**
   The Python service in [device.py](C:/Users/Jehosua%20Joya/Desktop/iot-deployment-methods/digital-twin-sim/physical_device/device.py) acts like a smart air conditioner. It simulates thermal behavior, power draw, and compressor runtime. It listens for MQTT commands and publishes telemetry at a fixed interval.

2. **MQTT Broker**
   The Mosquitto broker routes messages between services. It provides the publish/subscribe communication layer used by many real IoT systems.

3. **Digital Twin**
   The Python service in [twin.py](C:/Users/Jehosua%20Joya/Desktop/iot-deployment-methods/digital-twin-sim/digital_twin/twin.py) subscribes to telemetry, maintains the latest known state of the HVAC unit, estimates energy cost, tracks online/offline status, and raises a simple maintenance warning when cooling performance is poor.

## Data Flow

The system uses bidirectional MQTT communication:

- Commands are published to `home/ac/cmd`
- Telemetry is published to `home/ac/telemetry`

Typical flow:

1. A user sends `ON`, `OFF`, or a temperature value.
2. The device simulator updates its internal state.
3. The device publishes updated telemetry.
4. The digital twin receives that telemetry and updates its shadow model.
5. The twin prints its current view of the asset, including derived analytics.

## What It Demonstrates

This project is useful as a portfolio piece because it demonstrates several practical software engineering skills in one compact system:

- **IoT messaging** through MQTT topics and pub/sub design
- **Containerization** of independent services with Docker
- **Orchestration** with Docker Compose
- **System decomposition** into device-side and cloud-side responsibilities
- **State synchronization** between a simulated asset and a software twin
- **Basic operational logic** such as retry behavior, heartbeat monitoring, and alerting

## Why It Fits IoT Deployment Engineering

Many IoT projects focus only on the device code. This one goes further by modeling how the full deployment works:

- The device runs as one service.
- The communication infrastructure runs as another.
- The cloud-side monitoring and analytics run separately.

That separation reflects how production IoT systems are actually deployed and managed. The project therefore highlights not only programming skills, but also deployment thinking: service boundaries, runtime coordination, reproducibility, and scalability.

## Best Entry Point for Reviewers

If someone is reviewing this repository for portfolio purposes, the best way to understand it is:

1. Read [README.md](C:/Users/Jehosua%20Joya/Desktop/iot-deployment-methods/README.md) for the high-level context.
2. Read [digital-twin-sim/README.md](C:/Users/Jehosua%20Joya/Desktop/iot-deployment-methods/digital-twin-sim/README.md) for setup and usage.
3. Inspect [docker-compose.yml](C:/Users/Jehosua%20Joya/Desktop/iot-deployment-methods/digital-twin-sim/docker-compose.yml) to see how the services are deployed together.
4. Inspect [device.py](C:/Users/Jehosua%20Joya/Desktop/iot-deployment-methods/digital-twin-sim/physical_device/device.py) and [twin.py](C:/Users/Jehosua%20Joya/Desktop/iot-deployment-methods/digital-twin-sim/digital_twin/twin.py) to review the application logic.

## Extension Ideas

This repository can be expanded in several directions:

- Add a web dashboard for live visualization
- Persist telemetry to a database
- Simulate multiple devices instead of one HVAC unit
- Add automated tests for message handling and state transitions
- Add CI/CD workflows to demonstrate deployment automation

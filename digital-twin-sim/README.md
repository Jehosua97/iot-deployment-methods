# Digital Twin HVAC Simulation

This project simulates a smart HVAC unit and its cloud-side digital twin using Docker and MQTT. It is structured as a small IoT deployment exercise: a containerized physical device publishes telemetry, an MQTT broker carries commands and state updates, and a digital twin maintains a synchronized model of the asset.

## Structure

```text
digital-twin-sim/
|-- docker-compose.yml
|-- mosquitto.conf
|-- physical_device/
|   |-- device.py
|   `-- Dockerfile
`-- digital_twin/
    |-- twin.py
    `-- Dockerfile
```

## What the simulation does

- `physical_device/device.py` simulates an air conditioner with temperature drift, cooling behavior, and power draw.
- `digital_twin/twin.py` tracks the latest device state, keeps the last known heartbeat, estimates hourly energy cost, and raises a simple maintenance warning if cooling is unexpectedly slow.
- `mosquitto.conf` enables anonymous local MQTT access for a self-contained development environment.

## Run the stack

From the repository root:

```bash
cd digital-twin-sim
docker compose up --build
```

If you are using the legacy plugin naming, `docker-compose up --build` also works.

## Send commands

In another terminal:

```bash
docker exec -it digital-twin-mqtt mosquitto_pub -t "home/ac/cmd" -m "ON"
docker exec -it digital-twin-mqtt mosquitto_pub -t "home/ac/cmd" -m "20.5"
docker exec -it digital-twin-mqtt mosquitto_pub -t "home/ac/cmd" -m "OFF"
```

The accepted commands are:

- `ON`
- `OFF`
- Any numeric target temperature in Celsius, such as `21` or `23.5`

## Why this qualifies as a digital twin

- The data flow is bi-directional: commands go to the device, telemetry returns to the twin.
- The twin keeps a last known state even if the device stops sending updates.
- Device-side behavior and cloud-side logic are separated so the twin can host analytics independently of the simulated hardware.

## Reference alignment

The design reflects the themes in the provided background papers: protocol-driven IoT communication, container-based orchestration for distributed systems, and deployment-oriented separation of services.

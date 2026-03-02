import json
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("MQTT_HOST", "mqtt-broker")
BROKER_PORT = int(os.getenv("MQTT_PORT", "1883"))
COMMAND_TOPIC = "home/ac/cmd"
TELEMETRY_TOPIC = "home/ac/telemetry"
DEVICE_ID = "ac-unit-001"
AMBIENT_TEMP_C = float(os.getenv("AMBIENT_TEMP_C", "29.0"))
PUBLISH_INTERVAL_SECONDS = float(os.getenv("PUBLISH_INTERVAL_SECONDS", "2"))
COOLING_GAIN = float(os.getenv("COOLING_GAIN", "0.18"))
BASE_ACTIVE_POWER_W = float(os.getenv("BASE_ACTIVE_POWER_W", "850"))
STANDBY_POWER_W = float(os.getenv("STANDBY_POWER_W", "12"))

state = {
    "current_temp_c": 25.0,
    "target_temp_c": 22.0,
    "power_on": False,
    "power_draw_w": STANDBY_POWER_W,
    "compressor_runtime_s": 0.0,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp_temp(value: float) -> float:
    return max(16.0, min(35.0, value))


def apply_physics() -> None:
    if state["power_on"]:
        state["compressor_runtime_s"] += PUBLISH_INTERVAL_SECONDS
        error = state["current_temp_c"] - state["target_temp_c"]
        if error > 0:
            state["current_temp_c"] -= error * COOLING_GAIN
        else:
            state["current_temp_c"] += 0.02
        state["current_temp_c"] += random.uniform(-0.08, 0.05)
    else:
        drift = (AMBIENT_TEMP_C - state["current_temp_c"]) * 0.04
        state["current_temp_c"] += drift + random.uniform(-0.02, 0.06)

    state["current_temp_c"] = clamp_temp(state["current_temp_c"])

    if state["power_on"]:
        delta = max(0.0, state["current_temp_c"] - state["target_temp_c"])
        state["power_draw_w"] = BASE_ACTIVE_POWER_W + (delta * 60.0)
    else:
        state["power_draw_w"] = STANDBY_POWER_W


def publish_telemetry(client: mqtt.Client) -> None:
    payload = {
        "device_id": DEVICE_ID,
        "timestamp": now_iso(),
        "current_temp_c": round(state["current_temp_c"], 2),
        "target_temp_c": round(state["target_temp_c"], 2),
        "power_on": state["power_on"],
        "power_draw_w": round(state["power_draw_w"], 1),
        "compressor_runtime_s": round(state["compressor_runtime_s"], 1),
    }
    client.publish(TELEMETRY_TOPIC, json.dumps(payload), qos=1)
    print(
        "[PHYSICAL DEVICE] Sent telemetry: "
        f"temp={payload['current_temp_c']}C, "
        f"target={payload['target_temp_c']}C, "
        f"power_on={payload['power_on']}, "
        f"draw={payload['power_draw_w']}W"
    )


def handle_command(raw_payload: str) -> None:
    command = raw_payload.strip()
    upper_command = command.upper()

    if upper_command == "ON":
        state["power_on"] = True
    elif upper_command == "OFF":
        state["power_on"] = False
    else:
        requested_temp = float(command)
        state["target_temp_c"] = clamp_temp(requested_temp)

    print(
        "[PHYSICAL DEVICE] Applied command: "
        f"power_on={state['power_on']}, target={state['target_temp_c']}C"
    )


def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties) -> None:
    reason_value = getattr(reason_code, "value", reason_code)
    if reason_value == 0:
        client.subscribe(COMMAND_TOPIC, qos=1)
        print(f"[PHYSICAL DEVICE] Connected to broker at {BROKER_HOST}:{BROKER_PORT}")
    else:
        print(f"[PHYSICAL DEVICE] MQTT connect failed with reason code {reason_code}")


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
    try:
        handle_command(msg.payload.decode("utf-8"))
    except ValueError:
        print(f"[PHYSICAL DEVICE] Ignored invalid command: {msg.payload!r}")


def connect_with_retry(client: mqtt.Client) -> None:
    while True:
        try:
            client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
            return
        except OSError as exc:
            print(f"[PHYSICAL DEVICE] Broker unavailable ({exc}). Retrying in 2s.")
            time.sleep(2)


def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=DEVICE_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=10)

    connect_with_retry(client)
    client.loop_start()

    while True:
        apply_physics()
        publish_telemetry(client)
        time.sleep(PUBLISH_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()

import json
import os
import time
from collections import deque

import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("MQTT_HOST", "mqtt-broker")
BROKER_PORT = int(os.getenv("MQTT_PORT", "1883"))
TELEMETRY_TOPIC = "home/ac/telemetry"
ENERGY_PRICE_PER_KWH = float(os.getenv("ENERGY_PRICE_PER_KWH", "0.18"))
OFFLINE_TIMEOUT_SECONDS = int(os.getenv("OFFLINE_TIMEOUT_SECONDS", "8"))

twin_state = {
    "device_id": None,
    "actual_temp_c": None,
    "target_temp_c": None,
    "power_on": False,
    "power_draw_w": 0.0,
    "predicted_hourly_cost_usd": 0.0,
    "cooling_rate_c_per_min": None,
    "last_seen": None,
    "last_seen_epoch": None,
    "status": "Offline",
    "maintenance_alert": None,
}

telemetry_history = deque(maxlen=8)


def calculate_cooling_rate(current_temp_c: float, now_epoch: float):
    telemetry_history.append((now_epoch, current_temp_c))
    if len(telemetry_history) < 2:
        return None

    first_epoch, first_temp = telemetry_history[0]
    elapsed_minutes = (now_epoch - first_epoch) / 60.0
    if elapsed_minutes <= 0:
        return None

    return (first_temp - current_temp_c) / elapsed_minutes


def evaluate_alert() -> str | None:
    temp_gap = None
    if twin_state["actual_temp_c"] is not None and twin_state["target_temp_c"] is not None:
        temp_gap = twin_state["actual_temp_c"] - twin_state["target_temp_c"]

    if not twin_state["power_on"]:
        return None

    if temp_gap is not None and temp_gap > 2.5:
        rate = twin_state["cooling_rate_c_per_min"]
        if rate is not None and rate < 0.20:
            return "Cooling slower than expected; inspect airflow or refrigerant."

    return None


def print_state() -> None:
    temp = twin_state["actual_temp_c"]
    target = twin_state["target_temp_c"]
    draw = twin_state["power_draw_w"]
    rate = twin_state["cooling_rate_c_per_min"]
    rate_text = f"{rate:.2f} C/min" if rate is not None else "n/a"
    summary = (
        "[DIGITAL TWIN] "
        f"device={twin_state['device_id']} | "
        f"status={twin_state['status']} | "
        f"temp={temp}C | "
        f"target={target}C | "
        f"power_on={twin_state['power_on']} | "
        f"draw={draw}W | "
        f"cost=${twin_state['predicted_hourly_cost_usd']:.2f}/h | "
        f"cooling_rate={rate_text}"
    )
    if twin_state["maintenance_alert"]:
        summary += f" | alert={twin_state['maintenance_alert']}"
    print(summary)


def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties) -> None:
    reason_value = getattr(reason_code, "value", reason_code)
    if reason_value == 0:
        client.subscribe(TELEMETRY_TOPIC, qos=1)
        print(f"[DIGITAL TWIN] Connected to broker at {BROKER_HOST}:{BROKER_PORT}")
    else:
        print(f"[DIGITAL TWIN] MQTT connect failed with reason code {reason_code}")


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        print(f"[DIGITAL TWIN] Ignored malformed telemetry: {msg.payload!r}")
        return

    now_epoch = time.time()
    twin_state["device_id"] = payload.get("device_id")
    twin_state["actual_temp_c"] = float(payload["current_temp_c"])
    twin_state["target_temp_c"] = float(payload["target_temp_c"])
    twin_state["power_on"] = bool(payload["power_on"])
    twin_state["power_draw_w"] = float(payload["power_draw_w"])
    twin_state["predicted_hourly_cost_usd"] = (
        twin_state["power_draw_w"] / 1000.0
    ) * ENERGY_PRICE_PER_KWH
    twin_state["cooling_rate_c_per_min"] = calculate_cooling_rate(
        twin_state["actual_temp_c"], now_epoch
    )
    twin_state["last_seen"] = payload.get("timestamp")
    twin_state["last_seen_epoch"] = now_epoch
    twin_state["status"] = "Online"
    twin_state["maintenance_alert"] = evaluate_alert()
    print_state()


def mark_offline_if_stale() -> None:
    last_seen_epoch = twin_state["last_seen_epoch"]
    if last_seen_epoch is None:
        return

    if (time.time() - last_seen_epoch) > OFFLINE_TIMEOUT_SECONDS:
        if twin_state["status"] != "Offline":
            twin_state["status"] = "Offline"
            print("[DIGITAL TWIN] Telemetry heartbeat is stale. Device marked Offline.")


def connect_with_retry(client: mqtt.Client) -> None:
    while True:
        try:
            client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
            return
        except OSError as exc:
            print(f"[DIGITAL TWIN] Broker unavailable ({exc}). Retrying in 2s.")
            time.sleep(2)


def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ac-digital-twin")
    client.on_connect = on_connect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=10)

    connect_with_retry(client)
    client.loop_start()

    print("[DIGITAL TWIN] Service started. Waiting for telemetry...")

    while True:
        mark_offline_if_stale()
        time.sleep(1)


if __name__ == "__main__":
    main()

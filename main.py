import os, requests, csv, datetime as dt, time, pathlib, zoneinfo

TOKEN   = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")
TZ      = zoneinfo.ZoneInfo("Europe/Riga")

URL_SEND    = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
URL_UPDATES = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
URL_ANSWER  = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
LOG_PATH    = pathlib.Path(__file__).with_name("stretch_log.csv")


REMINDER_INTERVAL = 60

def log(event):
    LOG_PATH.parent.mkdir(exist_ok=True)
    with LOG_PATH.open("a", newline="") as f:
        csv.writer(f).writerow([dt.datetime.now(tz=TZ).isoformat(timespec="seconds"), event])

def send_reminder():
    kb = {"inline_keyboard": [[
        {"text": "✅ Done", "callback_data": "done"},
        {"text": "🚫 Skip", "callback_data": "skip"}]]}
    try:
        r = requests.post(URL_SEND,
                          json={"chat_id": CHAT_ID,
                                "text": "🧘‍♂️ Time to stand up and stretch for 2 minutes!",
                                "reply_markup": kb},
                          timeout=10)
        r.raise_for_status()
        print("SEND OK", flush=True)
        log("prompt")
    except Exception as e:
        print("SEND FAIL:", e, flush=True)

def poll(offset):
    params = {"timeout": 60}
    if offset is not None:
        params["offset"] = offset
    try:
        r = requests.get(URL_UPDATES, params=params, timeout=70)
        r.raise_for_status()
        res = r.json().get("result", [])
        for upd in res:
            offset = upd["update_id"] + 1
            cq = upd.get("callback_query")
            if cq:
                requests.post(URL_ANSWER,
                              json={"callback_query_id": cq["id"]},
                              timeout=10)
                log(cq["data"])
        return offset
    except Exception as e:
        print("POLL FAIL:", e, flush=True)
        return offset

def main():
    offset = None
    if not LOG_PATH.exists():
        LOG_PATH.write_text("")

    last_reminder_time = dt.datetime.now(tz=TZ).replace(hour=0, minute=0, second=0, microsecond=0)

    while True:
        now = dt.datetime.now(tz=TZ)
        print(f"DEBUG time={now.strftime('%H:%M:%S')}, last_reminder={last_reminder_time.strftime('%H:%M:%S')}", flush=True)

        time_since_last_reminder = (now - last_reminder_time).total_seconds() / 60
        in_active_hours = 9 <= now.hour < 23

        if in_active_hours and time_since_last_reminder >= REMINDER_INTERVAL:
            print(f"Sending reminder, {time_since_last_reminder:.1f} minutes since last one", flush=True)
            if send_reminder():
                last_reminder_time = now

        offset = poll(offset)

        time.sleep(5)

if __name__ == "__main__":
    main()
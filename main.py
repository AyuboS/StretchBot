import os, requests, csv, datetime as dt, time, pathlib

TOKEN   = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

URL_SEND    = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
URL_UPDATES = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
URL_ANSWER  = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
LOG_PATH    = pathlib.Path(__file__).with_name("stretch_log.csv")

def log(event):
    with LOG_PATH.open("a", newline="") as f:
        csv.writer(f).writerow([dt.datetime.now().isoformat(timespec="seconds"), event])

def send_reminder():
    kb = {"inline_keyboard": [[
        {"text": "✅ Done", "callback_data": "done"},
        {"text": "🚫 Skip", "callback_data": "skip"}]]}
    requests.post(URL_SEND,
                  json={"chat_id": CHAT_ID,
                        "text": "🧘‍♂️ Time to stand up and stretch for 2 minutes!",
                        "reply_markup": kb},
                  timeout=10)
    log("prompt")

def poll(offset):
    params = {"timeout": 0}
    if offset is not None:
        params["offset"] = offset
    res = requests.get(URL_UPDATES, params=params, timeout=10).json().get("result", [])
    for upd in res:
        offset = upd["update_id"] + 1
        cq = upd.get("callback_query")
        if cq:
            requests.post(URL_ANSWER,
                          json={"callback_query_id": cq["id"]},
                          timeout=10)
            log(cq["data"])
    return offset

def main():
    if not LOG_PATH.exists():
        LOG_PATH.write_text("")
    while True:
        now = dt.datetime.now()
        if 9 <= now.hour < 20:
            send_reminder()
            end = time.time() + 3600
            while time.time() < end:
                offset = poll(None)
                time.sleep(5)
        else:
            offset = poll(None)
            time.sleep(30)

if __name__ == "__main__":
    main()
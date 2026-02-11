#!/usr/bin/env python3
import flask, serial, time, re, hashlib, logging, threading
from logging.handlers import TimedRotatingFileHandler
from flask_limiter import Limiter
from collections import defaultdict

SERIAL_PORT, BAUD, TIMEOUT = "/dev/serial0", 115200, 10
GSM7_TABLE = "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x00\x00\x00\x00\x00 !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà"
GSM7 = {c: i for i, c in enumerate(GSM7_TABLE) if c != '\x00'}
ser, ser_lock, provider = None, threading.Lock(), "unknown"
app = flask.Flask(__name__)
dedup, recipient_hits = {}, defaultdict(list)
day_count, day_start = [0], [time.time()]

# Load config files
keys = {l.split()[1]: l.split()[0] for l in open("keys.dic") if len(l.split()) == 2}
swiss = [l.strip() for l in open("swiss.dic") if l.strip().isdigit()]
blacklist = [l.strip() for l in open("blacklist.dic") if l.strip()]

# Logging
handler = TimedRotatingFileHandler("sms.log", when="D", interval=1, backupCount=1)
handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
log = logging.getLogger("sms"); log.addHandler(handler); log.setLevel(logging.INFO)

# Rate limiter (per-key)
limiter = Limiter(key_func=lambda: flask.request.args.get("key", ""), app=app)
send_limit = limiter.limit("7/minute;1000/day")

def modem_cmd(cmd, wait=1):
    with ser_lock:
        ser.reset_input_buffer()
        ser.write(f"{cmd}\r\n".encode()); time.sleep(wait)
        return ser.read(ser.in_waiting).decode(errors="ignore")

def get_signal():
    m = re.search(r"\+CSQ:\s*(\d+)", modem_cmd("AT+CSQ", 0.5))
    return int(m.group(1)) if m else -1

def gsm_encode(msg):
    return bytes(GSM7[c] for c in msg)

def send_sms(to, msg):
    with ser_lock:
        ser.write(b'\x1b'); time.sleep(0.1)  # ESC to cancel any pending
        ser.reset_input_buffer()
        ser.write(b'AT+CMGF=1\r\n'); time.sleep(0.3)
        ser.write(b'AT+CSCS="GSM"\r\n'); time.sleep(0.3)
        ser.reset_input_buffer()
        ser.write(f'AT+CMGS="{to}"\r\n'.encode()); time.sleep(0.5)
        ser.write(gsm_encode(msg) + b'\x1a'); time.sleep(3)
        res = ser.read(ser.in_waiting).decode(errors="ignore")
        return "OK" in res or "+CMGS" in res

def normalize(num):
    num = re.sub(r"[\s\-\(\)]", "", num)
    for prefix in swiss:
        if num.startswith("0" + prefix[1:]): return "+41" + num[1:]
        if num.startswith(prefix): return "+41" + num
    return num if num.startswith("+") else None

def is_blacklisted(num):
    return any(num.startswith(b) or num.lstrip("+").startswith(b) for b in blacklist)

def check_recipient_limit(num):
    now, hits = time.time(), recipient_hits[num]
    recipient_hits[num] = [t for t in hits if now - t < 86400]
    day_hits = recipient_hits[num]
    min_hits = [t for t in day_hits if now - t < 60]
    if len(min_hits) >= 7 or len(day_hits) >= 40: return False
    recipient_hits[num].append(now)
    return True

def check_global_limit():
    if time.time() - day_start[0] > 86400: day_count[0], day_start[0] = 0, time.time()
    if day_count[0] >= 5000: return False
    day_count[0] += 1
    return True

@app.route("/up")
def up(): return "OK", 200

@app.route("/send")
@send_limit
def send():
    key, to, msg = flask.request.args.get("key"), flask.request.args.get("to"), flask.request.args.get("msg", "")
    if not key or key not in keys: return "unauthorized", 401
    if not to: return "missing recipient", 400
    to = normalize(to)
    if not to or not re.match(r"^\+\d{8,15}$", to): return "invalid number format", 400
    if is_blacklisted(to): return "number blacklisted", 403
    if len(msg) > 70: return "message too long (max 70)", 400
    if not msg: return "empty message", 400
    if not all(c in GSM7 for c in msg): return "invalid characters (no emojis)", 400
    dedup_key = hashlib.md5(f"{to}{msg}".encode()).hexdigest()
    if dedup_key in dedup and time.time() - dedup[dedup_key] < 60: return "duplicate", 429
    if not check_recipient_limit(to): return "recipient limit exceeded", 429
    if not check_global_limit(): return "global limit exceeded", 429
    dedup[dedup_key] = time.time()
    dedup.update({k: v for k, v in dedup.items() if time.time() - v < 60})  # Cleanup
    signal = get_signal()
    if not send_sms(to, msg):
        log.info(f"FAIL {keys[key]} {to} [{provider}/{signal}] {msg[:20]}...")
        return "send failed", 500
    log.info(f"OK {keys[key]} {to} [{provider}/{signal}] {msg[:20]}...")
    return "sent", 200

def init_modem():
    global ser, provider
    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=TIMEOUT)
    ser.write(b'\x1b'); time.sleep(0.1)  # ESC to cancel any pending
    ser.reset_input_buffer()
    if "OK" not in modem_cmd("AT"):
        return False
    m = re.search(r'\+COPS:\s*\d+,\d+,"([^"]+)"', modem_cmd("AT+COPS?", 0.5))
    provider = m.group(1) if m else "unknown"
    return True

if __name__ == "__main__":
    if not init_modem(): print("Modem not responding"); exit(1)
    print("Modem OK, starting server..."); app.run(host="0.0.0.0", port=8080)

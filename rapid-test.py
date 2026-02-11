#!/usr/bin/env python3

import sys, os, requests, hashlib, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv


load_dotenv()

if len(sys.argv) != 3:
    print("Usage: rapid-test.py <count> <phone>"); sys.exit(1)

count, phone = int(sys.argv[1]), sys.argv[2]
key = os.getenv("TEST_KEY")
if not key: print("TEST_KEY not set in .env"); sys.exit(1)
url = "https://sms.problem.li/send"

def send(i):
    h = hashlib.md5(f"{time.time()}{i}".encode()).hexdigest()[:6]
    msg = f"test{i} {h}"
    r = requests.get(url, params={"key": key, "to": phone, "msg": msg}, timeout=30)
    return i, r.status_code, r.text, msg

print(f"Firing {count} parallel requests to {phone}...")
start = time.time()
with ThreadPoolExecutor(max_workers=count) as ex:
    futures = [ex.submit(send, i) for i in range(1, count + 1)]
    for f in as_completed(futures):
        i, code, text, msg = f.result()
        print(f"  [{i}] {code}: {text} ({msg})")

print(f"Done in {time.time() - start:.1f}s")

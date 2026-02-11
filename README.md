# sms

*just send sms*

<img src="./sms.svg" style="zoom:25%;" />

  

### Usage

```bash
curl "https://sms.problem.li/send?key=YOUR_KEY&to=0791234567&msg=Hello"
curl "https://sms.problem.li/up"  # Health check
```



## Rate Limits

  - Per key: 100/min, 1000/day
  - Per recipient: 5/min, 50/day
  - Global: 5000/day



## Architecture

  Internet → Caddy (443/HTTPS) → Flask (8080) → Serial → 4G HAT → SMS
                  ↑
          sms.problem.li → CNAME → sms-problemli.duckdns.org → Pi IP



## Deployment

On Raspberry Pi 4:

1. mount the 4G HAT

   > [!TIP]
   >
   > test with 
   >
   > ```bash
   > minicom -D /dev/ttyUSB2 -b 115200
   > ```

2. clone code

   ```bash
   cd /opt
   sudo git clone <repo> sms
   cd sms
   ```

3. add at least one api key

   ```bash
   cp keys.dic.example keys.dic
   key=$(python3 -c "import secrets; print(secrets.token_hex(32))")
   echo "problemli $key">>keys.dic
   ```

4. add duckdns token to .env

   ```bash
   echo "DUCK_TOKEN=xxxxx">>.env
   ```

5. run setup

   ```bash
   ./setup/setup.sh
   ```

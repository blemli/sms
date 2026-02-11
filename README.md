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
  - Roaming is blocked



## Architecture

  Internet → Caddy (443/HTTPS) → Flask (8080) → Serial → [SIM7600E-H 4G HAT](https://www.waveshare.com/wiki/SIM7600E-H_4G_HAT)  → SMS
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

2. set project 

   ```bash
   PROJECT=$(hostname)
   ```

3. create Installation directory

   ```bash
   sudo mkdir /opt/$PROJECT && sudo chown -c pi /opt/$PROJECT
   ```

4. clone code

   ```bash
   sudo apt install git
   cd /opt
   sudo git clone https://github.com/blemli/sms $PROJECT
   cd $PROJECT
   ```

5. add at least one api key

   ```bash
   cp keys.dic.example keys.dic
   key=$(python3 -c "import secrets; print(secrets.token_hex(32))")
   op item create $key
   echo "problemli $key">>keys.dic
   ```

   > [!IMPORTANT]
   >
   > Make sure to add every key to 1password

6. add duckdns token to .env

   ```bash
   sudo apt install vim
   echo "DUCK_TOKEN=608f514e-ca03-4839-8135-3e58c661e608">>.env
   ```

7. run setup

   ```bash
   ./setup/setup.sh
   ```





## Maintenance

### SIM7600 Cheat Sheet

If the hat makes problems you can debug directly with:

minicom -D /dev/serial0

| Command            | Description                              | Expected Response           |
| ------------------ | ---------------------------------------- | --------------------------- |
| `AT`               | Basic test                               | `OK`                        |
| `AT+CPIN?`         | SIM status                               | `READY`                     |
| `AT+CSQ`           | Signal strength                          | 10-31 good, 99 = none       |
| `AT+CREG?`         | Network registration                     | `0,1` or `0,5` = registered |
| `AT+COPS?`         | Carrier name                             | e.g. `spusu`                |
| `AT+CMGF=1`        | Set SMS text mode                        | `OK`                        |
| `AT+CMGS="+41..."` | Send SMS, then type msg, end with Ctrl+Z | `+CMGS: <id>`               |

  Exit minicom: Ctrl+A then X

### Update

```bash
setup/update.sh
```


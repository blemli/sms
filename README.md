# sms

*just send sms*

<img src="./sms.svg" style="zoom:25%;" />

  

### Usage

```bash
curl -L "https://sms.problem.li/send?key=YOUR_KEY&to=0791234567&msg=Hello"
curl -L "https://sms.problem.li/up"  # Health check
```



## Limits

  - Per key: 100/min, 1000/day
  - Per recipient: 5/min, 50/day
  - Global: 5000/day
  - Roaming is blocked
  - max 70 Characters per Message



## Architecture

  Internet → Caddy (443/HTTPS) → Flask (8080) → Serial → [SIM7600E-H 4G HAT](https://www.waveshare.com/wiki/SIM7600E-H_4G_HAT)  → SMS
                  ↑
          sms.problem.li → CNAME → sms-problemli.duckdns.org → Pi IP



## Deployment

On Raspberry Pi 4:

1. mount the 4G HAT

2. set project 

   ```bash
   PROJECT=$(hostname)
   ```

3. create Installation directory

   ```bash
   sudo mkdir /opt/$PROJECT && sudo chown -cR pi /opt/$PROJECT
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
   echo "DUCK_TOKEN=xxxx">>.env
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

### Update Code

```bash
setup/update.sh
```

### Add API-Key

```bash
name=xyz
key=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "$name $key">>keys.dic
sudo service sms restart
```

> [!IMPORTANT]
>
> make sure to save the key in 1password and send it only via [kpaste](kpaste.infomaniak.ch)


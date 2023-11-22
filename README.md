# Jerrita's utils

This repo contains some scripts that I use.

Feel free to use them if you need.


## Tools

### ddns.py
This script is used to update my homelab ip, which will use `cip.cc` to get real IPv4 address and use `netifaces` to get IPv6 address.

requirements:
```bash
pip install netifaces requests
```

envs:
- `CF_API_TOKEN`：Cloudflare API Token
- `DOMAIN`：要更新的域名
- `ZONE`：域名所在的区域 ID
- `NIC_NAME`：用于获取 IPv6 地址的网卡名称（例如 en0）

You can register a service with systemd also. An example can  be found under `svc/`, and use `journalctl -u ddns` to get the log.
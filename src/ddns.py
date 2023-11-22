import requests
import netifaces
from dns import message as dns_message

import datetime
import base64
import os


class CloudflareDNS:
    def __init__(self, api_token):
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }

    def update_record(self, zone, domain, rtype, record):
        zone_id = self._get_zone_id(zone)
        record_id = self._get_record_id(zone_id, domain, rtype)
        data = {
            'type': rtype,
            'name': domain,
            'content': record
        }
        response = requests.put(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}',
                                headers=self.headers, json=data)
        return response.json()

    def _get_zone_id(self, domain):
        response = requests.get(f'https://api.cloudflare.com/client/v4/zones?name={domain}', headers=self.headers)
        zone_id = response.json()['result'][0]['id']
        return zone_id

    def _get_record_id(self, zone_id, domain, record_type):
        response = requests.get(
            f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type={record_type}&name={domain}',
            headers=self.headers)
        record_id = response.json()['result'][0]['id']
        return record_id


class DnsClient:
    def __init__(self, dns_server):
        self.dns_server = dns_server

    def resolve_dns(self, domain, rtype) -> str:
        doh_url = f'https://{self.dns_server}/dns-query'
        message = dns_message.make_query(domain, rtype)
        dns_req = base64.b64encode(message.to_wire()).decode("UTF8").rstrip("=")
        response = requests.get(doh_url + "?dns=" + dns_req,
                                headers={"Content-type": "application/dns-message"})
        res = []
        for answer in dns_message.from_wire(response.content).answer:
            dns = answer.to_text().split()
            res.append({"Query": dns[0], "TTL": dns[1], "RR": dns[3], "Answer": dns[4]})
        return res[0]['Answer']

    @classmethod
    def get_ipv4_from_internet(cls):
        response = requests.get('https://cip.cc',
                                headers={
                                    "User-Agent": "curl/7.88.1"
                                })
        lines = response.text.split('\n')
        for line in lines:
            if 'IP' in line:
                ip = line.split(':')[1].strip()
                return ip
        return None

    @classmethod
    def get_ipv4_from_interface(cls, nic):
        details = netifaces.ifaddresses(nic)
        for i in details[netifaces.AF_INET]:
            return i['addr']

    @classmethod
    def get_ipv6_from_interface(cls, nic):
        details = netifaces.ifaddresses(nic)
        for i in details[netifaces.AF_INET6]:
            if i['addr'].startswith('240e'):
                return i['addr']


if __name__ == '__main__':
    token = os.environ['CF_API_TOKEN']
    domain = os.environ['DOMAIN']
    zone = os.environ['ZONE']
    nic_name = os.environ['NIC_NAME']

    print('[+] Time:', datetime.datetime.now())
    dc = DnsClient('dns.alidns.com')
    cf = CloudflareDNS(token)

    # IPv4 from interface
    old = dc.resolve_dns(domain, 'A')
    now = dc.get_ipv4_from_internet()
    print(f'[{"+" if old != now else "-"}] IPv4: {old} => {now}')
    if old != now:
        cf.update_record(zone, domain, 'A', now)
        print('[+] IPv4 Updated.')
    else:
        print('[-] No need to update.')

    # IPv6 from interface
    now = dc.get_ipv6_from_interface(nic_name)
    if not now:
        print('[-] Failed to detect ipv6 address. Skip.')
    else:
        old = dc.resolve_dns(domain, 'AAAA')
        print(f'[{"+" if old != now else "-"}] IPv6: {old} => {now}')
        if old != now:
            print('[+] Updating...')
            cf.update_record(zone, domain, 'AAAA', now)
            print('[+] IPv6 Updated.')
        else:
            print('[-] No need to update.')

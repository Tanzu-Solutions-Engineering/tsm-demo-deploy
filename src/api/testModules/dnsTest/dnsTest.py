from ..testInterface import TestInterface
import sys
import subprocess
import logging


class dnsTest(TestInterface):


    def __init__(self):
        self.__description__ = 'This test validates name resolution'

    
    def test_parameters(self):

        return (
            ("VC_HOST","FQDN of vCenter Server"),
            ("VC_IP","IP address of vCenter Server"),
            ("DNS_SERVERS","List of DNS Servers")
        )
    

    def test_start(self, params: dict):

        try:

            vc_host = params['VC_HOST']
            vc_ip = params['VC_IP']
            dns_servers = params['DNS_SERVERS']
        
        except KeyError as ke:
            logging.error(f'Input parameters not correct or missing: {ke}')
            self.test_return(self.FAILURE, f'Input parameters {ke} not correct or missing.')
            return False


        try:
            for d in dns_servers:
                output = subprocess.check_output(['nslookup', vc_host, str(d)], universal_newlines=True)
                res = dict(map(str.strip, sub.split(':', 1)) for sub in output.split('\n') if ':' in sub)
                if vc_ip != res['Address']:
                    #raise ValueError(CRED + "\t ERROR - The Hostname, " + vc_host + " does not resolve to the IP " + vc_ip + CEND)
                    self.test_return(self.FAILURE, f'The Hostname, {vc_host} does not resolve to the IP {vc_ip}')
                    return False

        except subprocess.CalledProcessError as err:
            #raise ValueError("ERROR - The vCenter FQDN is not resolving")
            self.test_return(self.FAILURE, f'The vCenter FQDN is not resolving using DNS server {d}')
            return False

        self.test_return(self.SUCCESS, f'The Hostname, {vc_host} resolves to the IP {vc_ip} using all DNS servers')
        return True




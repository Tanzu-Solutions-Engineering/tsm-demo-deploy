from ..testInterface import TestInterface
import sys
import subprocess
import logging


class sshTest(TestInterface):


    def __init__(self):
        self.__description__ = 'This test validates if SSH is running on a host and if you are able to login'

    
    def test_parameters(self):

        return (
            ("HOST","SSH host"),
            ("USER","SSH username"),
            ("PASSWORD","SSH password")
        )
    

    def test_start(self, params: dict):

        try:

            host = params['HOST']
            user = params['USER']
            password = params['PASSWORD']
        
        except KeyError as ke:
            logging.error(f'Input parameters not correct or missing: {ke}')
            self.test_return(self.FAILURE, f'Input parameters {ke} not correct or missing.')
            return False


        proc = subprocess.Popen(f'./testModules/sshTest/sshTest.expect {host} {user} {password}',  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

        while True:
            if proc.poll() != None:
                break

            if( self.__test_stop__ == True):
                proc.kill()
                break

            msg = proc.stdout.readline()
            msg = msg.decode("utf-8")
            #print(msg, end="")

        ret_code = proc.returncode

        if ret_code == 0:
            self.test_return(self.SUCCESS, f'SSH session to {host} succeeded')
            return True
        elif ret_code == 1:
            self.test_return(self.FAILURE, f'SSH is disabled or {host} is unreachable')
        elif ret_code == 2:
            self.test_return(self.FAILURE, f'Username or Password for {host} is incorrect')
        else:
            self.test_return(self.FAILURE, 'Unknown Failure')

        return False






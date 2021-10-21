from ..testInterface import TestInterface
import sys
import subprocess, os
import logging


class tsmCluster(TestInterface):


    def __init__(self):
        self.__description__ = 'This test validates if SSH is running on a host and if you are able to login'

    
    def test_parameters(self):

        return (
            ("AWS_ACCESS_KEY_ID","AWS_ACCESS_KEY_ID"),
            ("AWS_SECRET_ACCESS_KEY","AWS_SECRET_ACCESS_KEY"),
            ("AWS_SESSION_TOKEN","AWS_SESSION_TOKEN"),
            ("TSM_CLUSTER_NAME","TSM Cluster Name"),
            ("TSM_API_SERVER","TSM API Server"),
            ("TSM_API_KEY","TSM API Key"),
            ("ACTION","Options are ADD or REMOVE")

        )
    

    def test_start(self, params: dict):

        try:

            #aws_access_key_id = params['AWS_ACCESS_KEY_ID']
            #aws_secret_access_key = params['AWS_SECRET_ACCESS_KEY']
            #aws_session_token = params['AWS_SESSION_TOKEN']
            tsm_cluster_name = params['TSM_CLUSTER_NAME']
            tsm_api_server = params['TSM_API_SERVER']
            tsm_api_key = params['TSM_API_KEY']
            action = params['ACTION']
            
        
        except KeyError as ke:
            logging.error(f'Input parameters not correct or missing: {ke}')
            self.test_return(self.FAILURE, f'Input parameters {ke} not correct or missing.')
            return False

        if( action == 'ADD'):
            action = 'add'
        else:
            action = 'remove'


        env = os.environ.copy()

        try:

            env_vars = params['ENV_VARIABLES']

            if type(env_vars) == list:
                for item in env_vars:
                    for env_key,env_value in item.items():
                        env[env_key] = env_value

        except KeyError as ke:
            pass



        #env["AWS_ACCESS_KEY_ID"] = aws_access_key_id
        #env["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key
        #env["AWS_SESSION_TOKEN"] = aws_session_token
        env["TSM_API_SERVER"] = tsm_api_server
        env["TSM_API_KEY"] = tsm_api_key


        proc = subprocess.Popen(f'cd testModules/tsmCluster; python3 tsmClusterctl.py {action} {tsm_cluster_name} 2>&1',  env=env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

        #proc = subprocess.Popen(f'terraform plan -var=\"cluster_name={eks_cluster_name}\" 2>&1',  env=env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

        #print(f'terraform workspace new {eks_cluster_name}; terraform workspace select {eks_cluster_name}; terraform plan -var="cluster_name={eks_cluster_name}"')

        while True:
            if proc.poll() != None:
                break

            if( self.__test_stop__ == True):
                proc.kill()
                break

            
            proc.stdout.flush()
            msg = proc.stdout.read(1)
            msg = msg.decode("utf-8")
            print(msg, end="", flush=True)

        ret_code = proc.returncode

        if ret_code == 0:
            if action == 'add':
                self.test_return(self.SUCCESS, f'Added cluster {tsm_cluster_name} to TSM')
            else:
                self.test_return(self.SUCCESS, f'Removed cluster {tsm_cluster_name} from TSM')
            return True
        elif ret_code == 1:
            self.test_return(self.FAILURE, f'')
        elif ret_code == 2:
            self.test_return(self.FAILURE, f'')
        else:
            self.test_return(self.FAILURE, '')

        return False






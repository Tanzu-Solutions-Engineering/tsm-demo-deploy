from ..testInterface import TestInterface
import sys
import subprocess, os
import logging


class eks(TestInterface):


    def __init__(self):
        self.__description__ = 'This test validates if SSH is running on a host and if you are able to login'

    
    def test_parameters(self):

        return (
            ("AWS_ACCESS_KEY_ID","AWS_ACCESS_KEY_ID"),
            ("AWS_SECRET_ACCESS_KEY","AWS_SECRET_ACCESS_KEY"),
            ("AWS_SESSION_TOKEN","AWS_SESSION_TOKEN (OPTIONAL)"),
            ("EKS_CLUSTER_NAME","EKS Cluster Name"),
            ("EKS_NUM_NODES","Number of Worker Nodes"),
            ("EKS_NODE_SIZE","Size of Each Node"),
            ("EKS_K8S_VERSION","Kubernetes Version"),
            ("AWS_REGION","AWS Region"),
            ("ACTION","Options are CREATE or DESTROY")

        )
    

    def test_start(self, params: dict):

        try:

            aws_access_key_id = params['AWS_ACCESS_KEY_ID']
            aws_secret_access_key = params['AWS_SECRET_ACCESS_KEY']
            eks_cluster_name = params['EKS_CLUSTER_NAME']
            eks_num_nodes = params['EKS_NUM_NODES']
            eks_node_size = params['EKS_NODE_SIZE']
            eks_k8s_version = params['EKS_K8S_VERSION']
            aws_region = params['AWS_REGION']
            action = params['ACTION']
            
        
        except KeyError as ke:
            logging.error(f'Input parameters not correct or missing: {ke}')
            self.test_return(self.FAILURE, f'Input parameters {ke} not correct or missing.')
            return False

        try:

            aws_session_token = params['AWS_SESSION_TOKEN']

        except KeyError as ke:
            aws_session_token = None


        if( action == 'CREATE'):
            action = 'apply'
        else:
            action = 'destroy'

        env = os.environ.copy()

        env["AWS_ACCESS_KEY_ID"] = aws_access_key_id
        env["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key

        if aws_session_token != None:
            env["AWS_SESSION_TOKEN"] = aws_session_token
        
        env["eks_cluster_name"] = eks_cluster_name

        if action == 'apply':
            proc = subprocess.Popen(f'cd testModules/eks; terraform workspace new {eks_cluster_name}; terraform workspace select {eks_cluster_name} 2>&1; terraform {action} -var="cluster_name={eks_cluster_name}" -var="num_nodes={eks_num_nodes}" -var="node_size={eks_node_size}" -var="k8s_version={eks_k8s_version}" -var="region={aws_region}" -auto-approve 2>&1; aws eks --region $(terraform output -raw region) update-kubeconfig --name $(terraform output -raw cluster_name) --alias {eks_cluster_name} 2>&1',  env=env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        else:
            proc = subprocess.Popen(f'cd testModules/eks; terraform workspace new {eks_cluster_name}; terraform workspace select {eks_cluster_name} 2>&1; terraform {action} -var="cluster_name={eks_cluster_name}" -var="num_nodes={eks_num_nodes}" -var="node_size={eks_node_size}" -var="k8s_version={eks_k8s_version}" -var="region={aws_region}" -auto-approve 2>&1',  env=env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

        #proc = subprocess.Popen(f'terraform plan -var=\"cluster_name={eks_cluster_name}\" 2>&1',  env=env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

        #print(f'terraform workspace new {eks_cluster_name}; terraform workspace select {eks_cluster_name}; terraform plan -var="cluster_name={eks_cluster_name}"')

        while True:
            if proc.poll() != None:
                break

            if( self.__test_stop__ == True):
                proc.kill()
                break

            msg = proc.stdout.readline()
            msg = msg.decode("utf-8")
            print(msg, end="")

        ret_code = proc.returncode

        if ret_code == 0:
            self.test_return(self.SUCCESS, f'EKS cluster {action} for cluster {eks_cluster_name} succeeded')
            return True
        elif ret_code == 1:
            self.test_return(self.FAILURE, f'SSH is disabled or is unreachable')
        elif ret_code == 2:
            self.test_return(self.FAILURE, f'Username or Password for is incorrect')
        else:
            self.test_return(self.FAILURE, 'Unknown Failure')

        return False






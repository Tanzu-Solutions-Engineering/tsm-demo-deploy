from ..testInterface import TestInterface
import sys
import subprocess, os
import logging


class aks(TestInterface):


    def __init__(self):
        self.__description__ = 'This test validates if SSH is running on a host and if you are able to login'

    
    def test_parameters(self):

        return (
            ("AZURE_APP_ID","Azure App ID"),
            ("AZURE_PASSWORD","Azure Password"),
            ("AKS_CLUSTER_NAME","AKS Cluster Name"),
            ("AKS_NUM_NODES","Number of Worker Nodes"),
            ("AKS_NODE_SIZE","Size of Each Node"),
            ("AKS_K8S_VERSION","Kubernetes Version"),
            ("AZURE_REGION","Azure Region"),
            ("ACTION","Options are CREATE or DESTROY")

        )
    

    def test_start(self, params: dict):

        try:

            azure_app_id = params['AZURE_APP_ID']
            azure_password = params['AZURE_PASSWORD']
            aks_cluster_name = params['AKS_CLUSTER_NAME']
            aks_num_nodes = params['AKS_NUM_NODES']
            aks_node_size = params['AKS_NODE_SIZE']
            aks_k8s_version = params['AKS_K8S_VERSION']
            azure_region = params['AZURE_REGION']
            action = params['ACTION']
            
        
        except KeyError as ke:
            logging.error(f'Input parameters not correct or missing: {ke}')
            self.test_return(self.FAILURE, f'Input parameters {ke} not correct or missing.')
            return False

        if( action == 'CREATE'):
            action = 'apply'
        else:
            action = 'destroy'

        env = os.environ.copy()


        if action == 'apply':
            proc = subprocess.Popen(f'cd testModules/aks; terraform workspace new {aks_cluster_name}; terraform workspace select {aks_cluster_name} 2>&1; terraform {action} -var="appId={azure_app_id}" -var="password={azure_password}" -var="cluster_name={aks_cluster_name}" -var="num_nodes={aks_num_nodes}" -var="node_size={aks_node_size}" -var="k8s_version={aks_k8s_version}" -var="region={azure_region}" -auto-approve 2>&1; az aks get-credentials --resource-group $(terraform output -raw resource_group_name) --name $(terraform output -raw kubernetes_cluster_name) --overwrite-existing 2>&1',  env=env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        else:
            proc = subprocess.Popen(f'cd testModules/aks; terraform workspace new {aks_cluster_name}; terraform workspace select {aks_cluster_name} 2>&1; terraform {action} -var="appId={azure_app_id}" -var="password={azure_password}" -var="cluster_name={aks_cluster_name}" -var="num_nodes={aks_num_nodes}" -var="node_size={aks_node_size}" -var="k8s_version={aks_k8s_version}" -var="region={azure_region}" -auto-approve 2>&1',  env=env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )


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
            self.test_return(self.SUCCESS, f'AKS cluster {action} for cluster {aks_cluster_name} succeeded')
            return True
        else:
            self.test_return(self.FAILURE, 'Error')

        return False






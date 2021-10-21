import requests
from requests_toolbelt import MultipartEncoder
import subprocess, os, time


class ApiError(Exception):
    pass
class ClusterExistsError(Exception):
    pass
class ClusterNotExistsError(Exception):
    pass

class TSM():

    __api_fqdn = None
    __api_url = None
    __api_token = None
    __access_token = None
    __requests_session = None

    def __init__(self, api_fqdn: str, api_token: str) -> None:
        
        self.__api_fqdn = api_fqdn
        self.__api_token = api_token

        self.__api_url = f'https://{api_fqdn}'
        self.__requests_session = requests.Session()

        self.__get_access_token()



    def __get_access_token(self) -> None:

        multipart_data = MultipartEncoder(
            fields={
                    'refresh_token': f'{self.__api_token}'
                }
            )

        resp_token = self.__requests_session.post('https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize', headers={'Content-Type': multipart_data.content_type, 'authority': 'console.cloud.vmware.com', 'pragma': 'no-cache', 'cache-control': 'no-cache', 'accept': 'application/json, text/plain, */*'},data=multipart_data)

        if resp_token.status_code == 200:

            resp_json = resp_token.json()

            try: 
                self.__access_token = resp_json['access_token']
            except KeyError as ke:
                self.__access_token = None
                return

            self.__requests_session.headers.update({'csp-auth-token': self.__access_token})

            #print(self.__access_token)

        else:

            self.__access_token = None




    def __get_registration_url(self) -> str:

        resp_url = self.__requests_session.get(self.__api_url + '/tsm/v1alpha1/clusters/onboard-url')

        if resp_url.status_code == 200:

            resp_json = resp_url.json()

            try:
                reg_url = resp_json['url']
            except KeyError as ke:
                raise ApiError('Registration url not returned from __get_regisration_url API call')

            return reg_url

        else:

            resp_json = resp_url.json()

            try:
                resp_err = resp_json['error']
            except KeyError as ke:
                raise ApiError(f'API error: {resp_url.text}')

            raise ApiError(f'API error: {resp_err}')



    def __apply_reg_url(self, cluster_name: str, reg_url: str) -> bool:

        msg = ''
        my_env = os.environ.copy()

        proc = subprocess.Popen(f'kubectl --context {cluster_name} apply -f {reg_url} 2>&1',  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env )


        while True:

            if proc.stdout.readable():
                msgbytes = proc.stdout.readline()
                msg += msgbytes.decode("utf-8")
                #print(msg, end="")

            
            if proc.poll() != None:
                break

            #msg = proc.stdout.readline()
            #msg = msg.decode("utf-8")
            #print(msg, end="")

        ret_code = proc.returncode

        if ret_code == 0:
            return True
        else:
            raise ApiError(f'Kubectl Error during __apply_reg_url: {msg}')




    def __add_cluster_spec(self, cluster_name: str) -> str:

        j_data = f'{{"displayName":"{cluster_name}","description":"","tags":[],"labels":[],"namespaceExclusions":[],"autoInstallServiceMesh":true,"enableNamespaceExclusions":true}}'


        resp_token = self.__requests_session.put(self.__api_url + f'/tsm/v1alpha1/clusters/{cluster_name}', headers={'Content-Type': 'application/json'}, data=j_data)

        if resp_token.status_code == 200:

            resp_json = resp_token.json()

            try:
                token = resp_json['token']
            except KeyError as ke:
                raise ApiError('Token not returned from __add_cluster_spec API call')

            return token

        else:

            resp_json = resp_token.json()

            try:
                resp_err = resp_json['error']
            except KeyError as ke:
                raise ApiError(f'API error: {resp_token.text}')

            raise ApiError(f'API error: {resp_err}')        


    def __tsm_connect(self, cluster_name: str, token: str) -> bool:

        msg = ''
        my_env = os.environ.copy()

        proc = subprocess.Popen(f'kubectl --context {cluster_name} -n vmware-system-tsm create secret generic cluster-token --from-literal=token={token} 2>&1',  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env )


        while True:

            if proc.stdout.readable():
                msgbytes = proc.stdout.readline()
                msg += msgbytes.decode("utf-8")
                #print(msg, end="")

            
            if proc.poll() != None:
                break


        ret_code = proc.returncode

        if ret_code == 0:
            return True
        else:
            raise ApiError(f'Kubectl Error during __tsm_connect: {msg}')



    def __delete_cluster(self, cluster_name: str) -> str:

        resp_url = self.__requests_session.delete(self.__api_url + f'/tsm/v1alpha1/clusters/{cluster_name}')

        if resp_url.status_code == 202:

            resp_json = resp_url.json()

            try:
                job_id = resp_json['id']
            except KeyError as ke:
                raise ApiError('Job id not returned from __delete_cluster API call')

            return job_id

        else:

            resp_json = resp_url.json()

            try:
                resp_err = resp_json['error']
            except KeyError as ke:
                raise ApiError(f'API error: {resp_url.text}')

            raise ApiError(f'API error: {resp_err}')




    def __get_job_status(self, job_id: str) -> dict:

        resp_url = self.__requests_session.get(self.__api_url + f'/tsm/v1alpha1/jobs/{job_id}')

        if resp_url.status_code == 200:

            resp_json = resp_url.json()

            return resp_json

            #try:
            #    job_id = resp_json['id']
            #except KeyError as ke:
            #    raise ApiError('Job id not returned from __delete_cluster API call')
            #
            #return job_id

        else:

            resp_json = resp_url.json()

            try:
                resp_err = resp_json['error']
            except KeyError as ke:
                raise ApiError(f'API error: {resp_url.text}')

            raise ApiError(f'API error: {resp_err}')


    def __get_deletion_url(self, job_id: str) -> str:

        resp_url = self.__requests_session.get(self.__api_url + f'/tsm/v1alpha1/jobs/{job_id}/download')

        if resp_url.status_code == 200:

            resp_json = resp_url.json()

            try:
                del_url = resp_json['url']
            except KeyError as ke:
                raise ApiError('Registration url not returned from __get_regisration_url API call')

            return del_url

        else:

            resp_json = resp_url.json()

            try:
                resp_err = resp_json['error']
            except KeyError as ke:
                raise ApiError(f'API error: {resp_url.text}')

            raise ApiError(f'API error: {resp_err}')


    def __apply_del_url(self, cluster_name: str, del_url: str) -> bool:

        msg = ''
        my_env = os.environ.copy()

        proc = subprocess.Popen(f'kubectl --context {cluster_name} delete -f {del_url} 2>&1',  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env )


        while True:

            if proc.stdout.readable():
                msgbytes = proc.stdout.readline()
                msg += msgbytes.decode("utf-8")
                #print(msg, end="")

            
            if proc.poll() != None:
                break

            #msg = proc.stdout.readline()
            #msg = msg.decode("utf-8")
            #print(msg, end="")

        ret_code = proc.returncode

        if ret_code == 0:
            return True
        else:
            raise ApiError(f'Kubectl Error during __apply_reg_url: {msg}')




    def get_cluster_details(self, cluster_name: str ) -> dict:


        resp = self.__requests_session.get(self.__api_url + f'/tsm/v1alpha1/clusters/{cluster_name}')

        if resp.status_code == 200:

            resp_json = resp.json()

            return resp_json

        else:

            resp_json = resp.json()

            try:
                resp_err = resp_json['error']
            except KeyError as ke:
                raise ApiError(f'API error: {resp.text}')

            raise ApiError(f'API error: {resp_err}')



    def add_cluster(self, cluster_name: str ) -> bool:

        cluster_details = None

        try:

            cluster_details = self.get_cluster_details(cluster_name)

            if cluster_details != None:
                raise ClusterExistsError(f'Cluster with name: {cluster_name} already exists')

        except ApiError as ae:
            pass


        try:
            


            reg_url = self.__get_registration_url()

            self.__apply_reg_url( cluster_name, reg_url)
            #time.sleep(2)  
            token = self.__add_cluster_spec(cluster_name)
            #time.sleep(2)
            self.__tsm_connect(cluster_name, token)       

        except ApiError as ae:
            raise Exception(f'Error adding cluster to TSM: {ae}')


        while True:

            try:

                self.get_cluster_details(cluster_name)
                break

            except ApiError as ae:
                time.sleep(1)
                continue



    def delete_cluster(self, cluster_name: str ) -> bool:

        cluster_details = None

        try:

            cluster_details = self.get_cluster_details(cluster_name)

        except ApiError as ae:
            raise ClusterNotExistsError(f'Cluster with name: {cluster_name} does not exist')


        try:
            
            job_id = self.__delete_cluster(cluster_name)

            while True:
                status = self.__get_job_status(job_id)

                if status['state'] == 'Completed':
                    break

                time.sleep(2)

            del_url = self.__get_deletion_url(job_id)

            print(del_url)

            self.__apply_del_url(cluster_name, del_url)


        except ApiError as ae:
            raise Exception(f'Error deleting cluster to TSM: {ae}')





    def test(self) -> None:

        try:

            url = self.__get_registration_url()
            self.__apply_reg_url('eks1', url)

        except ApiError as ae:
            print(f'Error: {ae}')


        
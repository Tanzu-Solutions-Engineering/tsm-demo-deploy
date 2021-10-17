import argparse
import requests
import yaml
import json
from time import sleep
from websocket import create_connection
import threading


APISERVER = 'http://localhost:5050'
WSSERVER = 'ws://localhost:5050'

# Define ANSI Colors
CRED = '\033[91m'
CEND = '\033[0m'
CGRN = '\033[92m'

_g_new_test_flag = True

def list_all_tests(arg_results):

    try:

        resp_tests = requests.get(APISERVER + '/list_tests')

        if resp_tests.status_code == 200:

            json_tests = resp_tests.json()
            print('\nAvailable tests:')
            num = 1

            for test in json_tests['tests']:

                print(f'\t{num} {test}')
                num+=1

                # Let's retrieve and print out parameters for this test if -p is selected
                if arg_results.p == True:
                    
                    resp_parameters = requests.get(APISERVER + f'/{test}/test_parameters')

                    if resp_parameters.status_code == 200:

                        json_parameters = resp_parameters.json()

                        for parameter in json_parameters['parameters']:

                            parameter_name = parameter['name']
                            parameter_description = parameter['description']

                            print(f'\t\t{parameter_name} - {parameter_description}')

                    else:
                        print(f'\t\tInternal Error - {resp_parameters.status_code} returned when calling /{test}/test_parameters ')
            
            print()

        else:
            print(f'Internal Error - {resp_tests.status_code} returned when calling /list_tests ')

    except requests.exceptions.RequestException:
        print('Internal Error - Connection to backend API server failed. Please verify that the API server is running.')




def run_tests(arg_results):

    global _g_new_test_flag
    
    try:
        cfg_yaml = yaml.load( open(arg_results.yaml), Loader=yaml.Loader )
    except FileNotFoundError:
        print(f'ERROR: {arg_results.yaml} not found')
        return
    except Exception as e:
        print(f'ERROR: {e}')
        return

    try:

        try: 
            tests = cfg_yaml['TESTS']
        except KeyError as ke:
            tests = cfg_yaml['TASKS']

        counter = 1

        # enumerate all tests and start executing
        for test in tests:

            # check whether test object is a dict or str...if dict then extract test_name, test_cfg 
            if type(test) == dict:
                for test_name,test_cfg in test.items():
                    pass
            else:
                test_name = test
                test_cfg  = test


            if test_cfg in cfg_yaml:
                test_parameters = cfg_yaml[test_cfg]
            elif type(test) == dict and test_cfg not in cfg_yaml:
                print(f'ERROR: test parameters {test_cfg} not found')
                return;
            else:
                test_parameters = {}

            print(f'\n{counter}-Running {test_name}...')

            resp_start = requests.post(APISERVER + f'/{test_name}/test_start', data=json.dumps(test_parameters))
            
            if resp_start.status_code == 200:
                while True:
                    sleep(0.5)
                    resp_status = requests.get(APISERVER + f'/{test_name}/test_status')

                    if resp_status.status_code == 200:
                        json_status = resp_status.json()

                        if json_status['status'] == 'RUNNING':
                            continue
                        elif json_status['status'] == 'SUCCESS':
                            msg = json_status['message']
                            print(CGRN+f'\n\t SUCCESS - {msg}' + CEND)
                            _g_new_test_flag = True
                            break
                        elif json_status['status'] == 'FAILURE':
                            msg = json_status['message']
                            print(CRED+f'\n\t FAILURE - {msg}' + CEND)
                            _g_new_test_flag = True
                            break

                    elif resp_start.status_code == 404:
                        print(CRED+f'ERROR: test {test_name} not found' + CEND)
                        break

            elif resp_start.status_code == 404:
                print(CRED+f'ERROR: test {test_name} not found' + CEND)


            counter+=1

    except KeyError as ke:
        print(f'ERROR: missing key {ke} in {arg_results.yaml}')
        return


def wsThread(ws):
    
    global _g_new_test_flag

    try:
        while True:
            msg =  ws.recv()

            if _g_new_test_flag == True:
                print('\t', end='', flush=True)
                _g_new_test_flag = False                

            if msg == '\n':
                print(msg, end='', flush=True)
                print('\t', end='', flush=True)
            else:
                print(msg, end='', flush=True)
            #print('\t' + msg, end='', flush=True)
            
    except Exception:
        pass


def main():

    parser = argparse.ArgumentParser(description='testctl.py is a modular suite to run tests/tasks.')
    #parser.add_argument('--version', action='version',version='%(prog)s v0.01')
    parser.add_argument('-r','--run', action='store', dest='yaml', help='Run tests/tasks specified in yaml file')
    parser.add_argument('-l','--list', action='store_true', default=False, help='List available tests/tasks')
    parser.add_argument('-p', action='store_true', default=False, help='Include parameter details when using -l')
    arg_results = parser.parse_args()

    try:
        ws = create_connection(WSSERVER + '/msgs')
    except ConnectionRefusedError:
        print('Error connecting to API Server...please verify API server is running')
        return

    x = threading.Thread(target=wsThread, args=(ws,))
    x.start()

    try:

        # list all tests
        if arg_results.list == True:
            list_all_tests(arg_results)

        # run tests
        if arg_results.yaml != None:
            run_tests(arg_results)
            print("\n*********************************************\n* All tasks were run. Validation Complete. *\n*********************************************")

        ws.close()
        print(" ")
        x.join()

    except Exception as e:
        print(type(e))
        print(e)





if __name__ == 'testctl' or __name__ == '__main__':
    main()
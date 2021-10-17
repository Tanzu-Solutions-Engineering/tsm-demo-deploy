from flask import Flask, redirect, url_for, request, Response
from flask_sockets import Sockets
import json
import logging
import sys
import threading

from testModuleManager import *
from testModules.baseTestInterface import *

# Globals
_g_app = Flask(__name__)
_g_sockets = Sockets(_g_app)
_g_ws_list = list()
_g_test_instances = dict()

_g_pipe_name = './stdout.pipe'


@_g_sockets.route('/msgs')
def echo_socket(ws):
    
    _g_ws_list.append(ws)

    try:

        while not ws.closed:
            message = ws.receive()
            ws.send(message)

    except:
        logging.info("WebSocket closed")
        _g_ws_list.remove(ws)




@_g_app.route('/<testModule>/test_start',methods = ['POST'])
def test_start(testModule):

    if request.method == 'POST':

        tmm = testModuleManager('testModules')

        try:

            test_module = tmm.get_test(testModule)
                
            test_instance = eval(f'test_module.{testModule}()')
            param = json.loads(request.data)
            
            test_instance.__run__(param)
            
            _g_test_instances[testModule] = test_instance

        except TestNotFound as tnf:
            logging.error(str(tnf))
            return Response(content_type='application/json', status=404)


        status, progress, message = test_instance.test_status()

        res = {
            "status": status,
            "progress": progress,
            "message": message
        }


        return Response(content_type='application/json', response=json.dumps(res), status=200)



@_g_app.route('/<testModule>/test_status',methods = ['GET'])
def test_status(testModule):

    if request.method == 'GET':

        tmm = testModuleManager('testModules')

        try:

            # Check to see if the test module exists...if not this will raise TestNotFound
            tmm.get_test(testModule)       
            test_instance = _g_test_instances[testModule]
            status, progress, message = test_instance.test_status()

            res = {
                "status": status,
                "progress": progress,
                "message": message
            }


        except KeyError as ke:
            logging.error(str(ke))

            res = {
                "status": BaseTestInterface.__test_status__,
                "progress": 0,
                "message": f"Test {ke} not running"
            }

            return Response(content_type='application/json', response=json.dumps(res), status=200)

        except TestNotFound as tnf:
            logging.error(str(tnf))
            return Response(content_type='application/json', status=404)



        return Response(content_type='application/json', response=json.dumps(res), status=200)


        
@_g_app.route('/<testModule>/test_parameters',methods = ['GET'])
def test_parameters(testModule):

    if request.method == 'GET':

        tmm = testModuleManager('testModules')

        try:

            test_module = tmm.get_test(testModule)
            test_instance = eval(f'test_module.{testModule}()')
            params = test_instance.test_parameters()

            param_list = []

            for param in params:

                param_dict = dict()

                param_dict['name'] = param[0]
                param_dict['description'] = param[1]

                param_list.append(param_dict)

            res = {
                "parameters": param_list
            }

        except TestNotFound as tnf:
            logging.error(str(tnf))
            return Response(content_type='application/json', status=404)
        except TypeError:
            logging.error('Error in parameters for ' + f'{testModule}: ' + '{0}'.format(params))
            return Response(content_type='application/json', status=500)


        return Response(content_type='application/json', response=json.dumps(res), status=200)



@_g_app.route('/list_tests',methods = ['GET'])
def list_tests():

    if request.method == 'GET':
        tmm = testModuleManager('testModules')
        tests = tmm.list_tests()

        test_list = []

        for test in tests:

            test_list.append(test)

        res = {
            "tests": test_list
        }

        return Response(content_type='application/json', response=json.dumps(res), status=200)




def web_socket_output( wsList: list ):

    stdout_pipe = open(_g_pipe_name, 'r')

    while True:


        message = stdout_pipe.read(1)

        for ws in wsList:
            ws.send(message)



def main():

    
    #print(__name__)
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d]    %(message)s', datefmt='%Y-%m-%d:%H:%M:%S',level=logging.DEBUG)
    logging.info('Started')

    if not os.path.exists(_g_pipe_name):
        os.mkfifo(_g_pipe_name, 0o600)

    wsThread = threading.Thread(target=web_socket_output, args=(_g_ws_list,))
    wsThread.start()

    

    sys.stdout = open(_g_pipe_name, mode='w', buffering=1)
    
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5050), _g_app, handler_class=WebSocketHandler)
    server.serve_forever()
    

    logging.info('Finished')



if __name__ == 'apiserver' or __name__ == '__main__':
    main()
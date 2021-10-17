import importlib
import os
import logging

class TestNotFound(Exception):
    pass


class testModuleManager:

    def __init__(self, modulePath: str ):
        self._mPath = modulePath

    def list_tests(self):
        
        tests = os.listdir(self._mPath)

        test_list = list()

        for item in tests:
            if os.path.isdir(f'{self._mPath}/{item}'):

                if item != '__pycache__':
                    test_list.append(item)

        return(test_list)



    def get_test(self, testName: str ):

        try:
           test = importlib.import_module(f'.{testName}', f'{self._mPath}.{testName}' )
           importlib.reload( test )
        except ModuleNotFoundError as mnfe:
            logging.error(str(mnfe))
            raise TestNotFound(f'Test {testName} does not exist!')

        return(test)



        



    


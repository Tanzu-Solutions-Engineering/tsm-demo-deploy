import abc
import threading

class BaseTestInterface(abc.ABC):

    NOTRUNNING  = 'NOT_RUNNING'
    RUNNING     = 'RUNNING'
    SUCCESS     = 'SUCCESS'
    FAILURE     = 'FAILURE'

    __test_status__     = NOTRUNNING
    __test_message__    =  ''
    __test_stop__       = False
    __test_progress__   = 0

    __description__     = ''

    def __run__(self, params: dict):
        #print("run called", params)
        self.__test_status__ = self.RUNNING
        self.__test_message__ = ''
        self.__test_stop__ = False
        self.__test_progress__ = 0

        x = threading.Thread(target=self.test_start, args=(params,))
        x.start()


    @abc.abstractmethod
    def test_parameters( self ) -> list:
        pass


    @abc.abstractmethod
    def test_start( self, params: dict ) -> bool:
        pass


    def test_return( self, result: str, message: str):
        self.__test_status__ = result
        self.__test_message__ = message
        self.__test_progress__ = 100


    def test_stop( self ):
        self.__test_stop__ = True
        

    def test_status( self ):
        return self.__test_status__, self.__test_progress__, self.__test_message__
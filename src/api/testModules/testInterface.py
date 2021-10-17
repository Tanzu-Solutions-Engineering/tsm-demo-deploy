from .baseTestInterface import BaseTestInterface
import abc


class TestInterface(BaseTestInterface, abc.ABC):


    def test_parameters( self ) -> list:
        return ()

    @abc.abstractmethod
    def test_start( self, params: dict ) -> bool:
        pass
    



import abc


class ABAgent(abc.ABC):
    @abc.abstractmethod
    def act(self, observation):
        pass



    
from abc import ABC, abstractmethod

class IProcessor(ABC):

    @abstractmethod
    def process_notification(self, document):
        pass
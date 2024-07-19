from abc import ABC, abstractmethod

class IProcessor(ABC):

    @abstractmethod
    def process_scheduled_job(self, document):
        pass
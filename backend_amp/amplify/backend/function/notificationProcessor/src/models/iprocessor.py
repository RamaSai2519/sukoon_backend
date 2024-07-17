from abc import ABC, abstractmethod

class IProcessor(ABC):

    @abstractmethod
    def process_document(self, document):
        pass
class ProcessorsFactory:
   """ProcessorsFactory: dispatches documentProcessor based on document type"""

   def __init__(self):
       self._processors_store = {}


   def register_processor(self, documentType, processor):
       self._processors_store[documentType] = processor


   def get_handler(self, documentType, record):
       documentProcessor = self._processors_store.get(documentType)
       if not documentProcessor:
           raise ValueError(
               f"Handler for DocumentType '{documentType}' not found."
           )
       return documentProcessor(record)
class ProcessorsFactory:
   """ProcessorsFactory: dispatches notification_processor based on document type"""

   def __init__(self):
       self._processors_store = {}


   def register_processor(self, notification_type, processor):
       self._processors_store[notification_type] = processor


   def get_handler(self, notification_type, record):
       notification_processor = self._processors_store.get(notification_type)
       if not notification_processor:
           raise ValueError(
               f"Handler for notification_type '{notification_type}' not found."
           )
       return notification_processor(record)
class ProcessorsFactory:
   """ProcessorsFactory: dispatches job_processor based on job type"""

   def __init__(self):
       self._processors_store = {}


   def register_processor(self, job_type, processor):
       self._processors_store[job_type] = processor

   def get_handler(self, job_type, job):
       job_processor = self._processors_store.get(job_type)
       if not job_processor:
           raise ValueError(
               f"Handler for job_type '{job_type}' not found."
           )
       return job_processor(job)
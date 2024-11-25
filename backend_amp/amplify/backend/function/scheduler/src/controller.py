import os
import sys
import time
from inspect import getsourcefile
from models.processor_factory import ProcessorsFactory


current_path = os.path.abspath(getsourcefile(lambda: 0))
current_dir = os.path.dirname(current_path)
parent_dir = current_dir[: current_dir.rfind(os.path.sep)]
sys.path.insert(0, parent_dir)


from models.call_job_handler import CallJobHandler

def setup_factory() -> ProcessorsFactory:
    processors_factory = ProcessorsFactory()

    processors_factory.register_processor("CALL", CallJobHandler)
    return processors_factory


def process(job):
    try:
        start = time.perf_counter()
        factory = setup_factory()
        job_type = job.get("scheduledJobType")
        handler = factory.get_handler(job_type, job)
        
        print("scheduled_job_processor**", handler)
        print(handler.__class__)

        response = handler.process_scheduled_job()
        finish = time.perf_counter()
        total_time_taken = round(finish - start, 2) * 1000
        print(f"total_time_taken: {total_time_taken}")

    except Exception as error:
       print(
           f"Unhandled exception in scheduled job processor => {error}"
       )
       response = f"{repr(error)}"
    return response
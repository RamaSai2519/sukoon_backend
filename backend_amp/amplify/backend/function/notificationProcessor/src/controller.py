import time
import os
import sys
from inspect import getsourcefile
from models.processor_factory import ProcessorsFactory
from http import HTTPStatus


current_path = os.path.abspath(getsourcefile(lambda: 0))
current_dir = os.path.dirname(current_path)
parent_dir = current_dir[: current_dir.rfind(os.path.sep)]
sys.path.insert(0, parent_dir)


from models.whatsapp_notification import WhatsappNotification

def setup_factory():
    processors_factory = ProcessorsFactory()
    processors_factory.register_processor("WHATSAPP", WhatsappNotification)
    return processors_factory


def process(record):
    try:
        start = time.perf_counter()
        factory = setup_factory()
        
        if record == "TEST_ACTION":
           return {
               "statusCode": HTTPStatus.OK.value,
               "contentType": "application/json",
               "body": {"msg": "SUCCESS"},
           }
        
        notification_type = record["notificationJobType"]["S"]
        print("notification_type**", notification_type)
        handler = factory.get_handler(notification_type, record)
        print("notification_processor**", handler)
        print(handler.__class__)

        response = handler.process_notification()
        print(f"response: {response}")
        finish = time.perf_counter()
        total_time_taken = round(finish - start, 2) * 1000  # in millisecond
        print(f"response: {response}")
        print(f"total_time_taken: {total_time_taken}")


        # if isinstance(response, tuple):
        #     notificationProcessor.update_notification(
        #         notificationId, response_meta=response[1], status=response[0]
        #     )

        #     if str(response[0]).upper() == "FAILED":
        #         raise Exception(response[1])


        # elif isinstance(response, str):
        #     notificationProcessor.update_notification(
        #         notificationId, response_meta=response, status=response
        #     )

        #     if str(response).upper() == "FAILED":
        #         raise Exception(response)

    except Exception as error:
       print(
           f"Unhandled exception in notification processor => {error}"
       )
       response = f"{repr(error)}"


    return response
import sys
import os
import time
from models.interfaces import BytePlusTokenInput as Input, Output
from models.constants import OutputStatus
sys.path.append(os.path.join(os.path.dirname(__file__), '../byteplus_token'))

import AccessToken



class Compute:
    def __init__(self,input: Input) -> None:
        self.input = input

    def compute(self):
        
        app_id="6696518f721f7801754f4629"
        app_key="99f57abffd824c778195cc3805c5c1b6"

        token = AccessToken.AccessToken(app_id, app_key, self.input.room_id, self.input.user_id)
        token.add_privilege(AccessToken.PrivSubscribeStream, 0)
        token.add_privilege(AccessToken.PrivPublishStream, int(time.time()) + 3600)
        token.expire_time(int(time.time()) + 3600)

        s = token.serialize()
        t = AccessToken.parse(s)

        print(t.verify(app_key))


        return Output(
            output_details= {"token": s},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully fetched game config"
        )

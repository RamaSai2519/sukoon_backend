
import awsgi
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from services.controller import *

app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(QuizGameService, '/actions/quiz_game')
api.add_resource(CouponRewardService, '/actions/coupon_reward')
api.add_resource(GameConfigService, '/actions/game_config')
api.add_resource(ScoreUpdaterService, '/actions/score_update')
api.add_resource(CalculateWinnerService, '/actions/calculate_winner')
api.add_resource(UserReferralService, '/actions/user_referral')
api.add_resource(SendOTPService, '/actions/send_otp')
api.add_resource(ValidateOTPService, '/actions/validate_otp')
api.add_resource(GameHistoryService, '/actions/game_history')
api.add_resource(CardGameService, '/actions/card_game')
api.add_resource(BytePlusTokenService, '/actions/byte_plus_token')
api.add_resource(FetchShortsService, '/actions/fetch_shorts')
api.add_resource(WhatsappMessageService, '/actions/send_whatsapp')
api.add_resource(WhatsappWebhookService, '/actions/webhooks')
api.add_resource(PushNotificationService, '/actions/push')
api.add_resource(FCMTokenService, '/actions/update_fcm_token')

def handler(event, context):
    print(event)
    return awsgi.response(app, event, context)

if __name__ == '__main__':    
    app.run(debug= True,port=8080)

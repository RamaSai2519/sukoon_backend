
import awsgi
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from services.controller import *
from configs import CONFIG as Config
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = Config.JWT_REFRESH_TOKEN_EXPIRES

api = Api(app)
JWTManager(app)
CORS(app, supports_credentials=True)

# Users Routes
api.add_resource(UserService, '/actions/user')
api.add_resource(SlotsService, '/actions/slots')
api.add_resource(ExpertService, '/actions/expert')
api.add_resource(ApplicantService, '/actions/applicant')

# Events Routes
api.add_resource(ListEventsService, '/actions/list_events')
api.add_resource(UpsertEventsService, '/actions/upsert_event')
api.add_resource(ListEventUsersService, '/actions/list_event_users')
api.add_resource(CreateEventUserService, '/actions/create_event_user')

# Scheduled Jobs Routes
api.add_resource(CreateScheduledJobsService, '/actions/create_scheduled_job')
api.add_resource(UpdateScheduledJobsService, '/actions/update_scheduled_job')


api.add_resource(CreatePaymentOrderService, '/actions/create_payment_order')
api.add_resource(CashfreeWebhookService, '/actions/cashfree_webhook')
api.add_resource(CalculateWinnerService, '/actions/calculate_winner')
api.add_resource(WhatsappMessageService, '/actions/send_whatsapp')
api.add_resource(BytePlusTokenService, '/actions/byte_plus_token')
api.add_resource(CouponRewardService, '/actions/coupon_reward')
api.add_resource(UserReferralService, '/actions/user_referral')
api.add_resource(ScoreUpdaterService, '/actions/score_update')
api.add_resource(FCMTokenService, '/actions/update_fcm_token')
api.add_resource(ValidateOTPService, '/actions/validate_otp')
api.add_resource(GameHistoryService, '/actions/game_history')
api.add_resource(WhatsappWebhookService, '/actions/webhooks')
api.add_resource(UpdateEventService, '/actions/update_event')
api.add_resource(FetchShortsService, '/actions/fetch_shorts')
api.add_resource(GameConfigService, '/actions/game_config')
api.add_resource(PushNotificationService, '/actions/push')
api.add_resource(QuizGameService, '/actions/quiz_game')
api.add_resource(CardGameService, '/actions/card_game')
api.add_resource(SendOTPService, '/actions/send_otp')

# Admin Routes
# - Auth
api.add_resource(AdminAuthService, '/actions/admin_auth')
# - Services
api.add_resource(AdminFCMService, '/actions/save_fcm_token')
# - Stats
api.add_resource(DashboardStatsService, '/actions/dashboard_stats')


def handler(event, context):
    print(event)
    return awsgi.response(app, event, context)


if __name__ == '__main__':
    app.run(debug=True, port=8080)

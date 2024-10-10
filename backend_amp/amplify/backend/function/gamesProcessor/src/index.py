
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


# Call Routes
api.add_resource(CallService, '/actions/call')
api.add_resource(CallWebhookService, '/actions/call_webhook')

# Users Routes
api.add_resource(ClubService, '/actions/club')
api.add_resource(UserService, '/actions/user')
api.add_resource(SlotsService, '/actions/slots')
api.add_resource(ExpertService, '/actions/expert')
api.add_resource(ApplicantService, '/actions/applicant')
api.add_resource(UserReferralService, '/actions/user_referrals')

# Events Routes
api.add_resource(ListEventsService, '/actions/list_events')
api.add_resource(UpsertEventsService, '/actions/upsert_event')
api.add_resource(ListEventUsersService, '/actions/list_event_users')
api.add_resource(CreateEventUserService, '/actions/create_event_user')

# Scheduled Jobs Routes
api.add_resource(CreateScheduledJobsService, '/actions/create_scheduled_job')
api.add_resource(UpdateScheduledJobsService, '/actions/update_scheduled_job')

# Mark7 Routes
api.add_resource(InvokeMarkService, '/actions/invoke_mark')
api.add_resource(UpdateExpertScoresService, '/actions/expert_scores')

# Cashfree Routes
api.add_resource(CashfreeWebhookService, '/actions/cashfree_webhook')
api.add_resource(CreatePaymentOrderService, '/actions/create_payment_order')

# WhatsApp Routes
api.add_resource(WhatsappWebhookService, '/actions/webhooks')
api.add_resource(WhatsappMessageService, '/actions/send_whatsapp')

# OTP Routes
api.add_resource(SendOTPService, '/actions/send_otp')
api.add_resource(ValidateOTPService, '/actions/validate_otp')

# Admin Routes
# - Auth
api.add_resource(AdminAuthService, '/actions/admin_auth')
api.add_resource(VerifyUserService, '/actions/verify_user')
# - Data
api.add_resource(LogsService, '/actions/logs')
api.add_resource(LeadsService, '/actions/leads')
api.add_resource(RemarkService, '/actions/remarks')
api.add_resource(WhatsappHistoryService, '/actions/wa_history')
api.add_resource(EngagementDataService, '/actions/user_engagement')
# - Content
api.add_resource(ChatService, '/actions/chat')
api.add_resource(PhotoService, '/actions/photos')
api.add_resource(ContentService, '/actions/content')
# - Services
api.add_resource(UploadService, '/actions/upload')
api.add_resource(TimingService, '/actions/timings')
api.add_resource(CategoryService, '/actions/categories')
api.add_resource(AdminFCMService, '/actions/save_fcm_token')
api.add_resource(AdminWhatsappService, '/actions/wa_options')
api.add_resource(AdminSchedulesService, '/actions/schedules')
# - Stats
api.add_resource(DashboardStatsService, '/actions/dashboard_stats')

# Push Notification Routes
api.add_resource(PushNotificationService, '/actions/push')
api.add_resource(FCMTokenService, '/actions/update_fcm_token')
api.add_resource(BytePlusTokenService, '/actions/byte_plus_token')

# Game Routes (deprecated)
api.add_resource(QuizGameService, '/actions/quiz_game')
api.add_resource(CardGameService, '/actions/card_game')
api.add_resource(GameConfigService, '/actions/game_config')
api.add_resource(GameHistoryService, '/actions/game_history')
api.add_resource(ScoreUpdaterService, '/actions/score_update')
api.add_resource(CouponRewardService, '/actions/coupon_reward')
api.add_resource(CalculateWinnerService, '/actions/calculate_winner')


def handler(event, context):
    print(event)
    return awsgi.response(app, event, context)


if __name__ == '__main__':
    app.run(debug=True, port=8080)

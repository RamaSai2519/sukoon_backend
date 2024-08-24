from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class GetGameConfigInput:
    game_type: str


@dataclass
class UpdateGameConfigInput:
    game_type: str
    game_config: dict


@dataclass
class QuizGameInput:
    user_id: str
    question_to_show: str
    level: int
    category: Optional[str] = field(default='culture')


@dataclass
class CouponRewardInput:
    user_id: str


@dataclass
class UserReferralInput:
    city: str
    name: str
    referral_code: str
    phone_number: str


@dataclass
class SendOTPInput:
    phone_number: str


@dataclass
class ValidateOTPInput:
    otp: str
    phone_number: str


@dataclass
class CardGameInput:
    cards_to_show: int
    level: int


@dataclass
class ScoreUpdaterInput:
    user_id: str
    level: int
    user_score: int
    saarthi_score: int
    saarthi_id: str
    game_type: str


@dataclass
class CalculateWinnerInput:
    user_id: str
    saarthi_id: str
    game_type: str


@dataclass
class UpdateGamePlayInput:
    user_id: str
    user_score: int
    saarthi_score: int
    saarthi_id: str
    game_type: str
    total_time: str
    reward_amount: int


@dataclass
class GetGamePlayInput:
    user_id: str


@dataclass
class BytePlusTokenInput:
    user_id: str
    room_id: str


@dataclass
class BytePlusTokenInput:
    user_id: str
    room_id: str


@dataclass
class FetchShortsInput:
    user_id: str
    fetchedTill: Optional[List[dict]] = field(default_factory=list)


@dataclass
class WhtasappMessageInput:
    phone_number: str
    parameters: dict
    template_name: str
    user_id: Optional[str] = field(default_factory=lambda: "")
    request_meta: str = field(default_factory=lambda: "")


@dataclass
class GetWhatsappWebhookInput:
    hub_mode: str
    hub_challenge: int
    hub_verify_token: str


@dataclass
class WhatsappWebhookEventInput:
    object: str
    entry: dict


@dataclass
class PushNotificationInput:
    title: str
    body: str
    user_id: str
    fcm_token: str


@dataclass
class UpdateFCMTokenInput:
    user_id: str
    fcm_token: str


@dataclass
class ScheduledJobInput:
    job_type: str = field(default_factory=lambda: "")
    job_time: str = field(default_factory=lambda: "")
    status: str = field(default_factory=lambda: "")
    request_meta: str = field(default_factory=lambda: "")
    action: str = field(default_factory=lambda: "")
    scheduled_job_id: str = field(default_factory=lambda: "")


@dataclass
class GetUserInput:
    mobile_number: str


@dataclass
class CreateNonRegisteredUserInput:
    mobile_number: str


@dataclass
class UpsertRegisteredUserInput:
    first_name: str
    gender: str
    last_name: str
    date_of_birth: str
    mobile_number: str


@dataclass
class CreatePaymentOrderInput:
    user_id: str
    order_amount: float
    event_id: str = field(default_factory=lambda: "")


@dataclass
class CashfreeWebhookEventInput:
    data: dict
    type: str
    event_time: str


@dataclass
class EventInput:
    name: Optional[str] = None
    slug: Optional[str] = None
    repeat: Optional[str] = None
    subTitle: Optional[str] = None
    hostedBy: Optional[str] = None
    category: Optional[str] = None
    imageUrl: Optional[str] = None
    mainTitle: Optional[str] = None
    eventType: Optional[str] = None
    prizeMoney: Optional[int] = None
    isAlways: Optional[bool] = False
    meetingLink: Optional[str] = None
    description: Optional[str] = None
    guestSpeaker: Optional[str] = None
    validUpto: Optional[datetime] = None
    isPremiumUserOnly: Optional[bool] = None
    maxVisitorsAllowed: Optional[int] = None
    startEventDate: Optional[datetime] = None
    registrationAllowedTill: Optional[str] = None


@dataclass
class GetEventsInput:
    page: Optional[int] = 1
    limit: Optional[int] = 10
    slug: Optional[str] = None
    fromToday: Optional[str] = "false"
    isHomePage: Optional[str] = "false"


@dataclass
class EventUserInput:
    phone: str
    name: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = None
    dob: Optional[datetime] = None
    eventName: Optional[str] = None
    advSeenOn: Optional[str] = None


@dataclass
class GetEventUsersInput:
    page: Optional[int] = None
    size: Optional[int] = None
    slug: Optional[str] = None


@dataclass
class Output:
    output_status: str
    output_message: str
    output_details: dict

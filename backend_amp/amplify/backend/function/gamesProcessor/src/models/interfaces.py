from bson import ObjectId
from typing import Optional
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Expert:
    phoneNumber: str
    _id: Optional[str] = None
    otp: Optional[str] = None
    name: Optional[str] = None
    flow: Optional[int] = None
    type: Optional[str] = None
    video: Optional[str] = None
    score: Optional[int] = None
    score: Optional[int] = None
    topics: Optional[str] = None
    status: Optional[str] = None
    active: Optional[bool] = None
    profile: Optional[str] = None
    isBusy: Optional[bool] = None
    tonality: Optional[int] = None
    fcmToken: Optional[str] = None
    timeSpent: Optional[int] = None
    languages: Optional[str] = None
    timeSplit: Optional[int] = None
    isDeleted: Optional[bool] = None
    probability: Optional[int] = None
    description: Optional[str] = None
    total_score: Optional[int] = None
    displayScore: Optional[str] = None
    repeat_score: Optional[int] = None
    isGamesPlay: Optional[bool] = None
    daysLoggedIn: Optional[int] = None
    calls_share: Optional[float] = None
    userSentiment: Optional[int] = None
    closingGreeting: Optional[int] = None
    openingGreeting: Optional[int] = None
    expiresOtp: Optional[datetime] = None
    createdDate: Optional[datetime] = None
    categories: Optional[List[str]] = None
    profileCompleted: Optional[bool] = None


@dataclass
class GetSlotsInput:
    duration: int
    expert: str
    datetime: str


@dataclass
class GetTimingsInput:
    expert: str


@dataclass
class GetWaHistoryInput:
    type: str
    page: Optional[int] = 0
    size: Optional[int] = 0


@dataclass
class GetEngagementDataInput:
    page: Optional[int] = 0
    size: Optional[int] = 0


@dataclass
class GetClubInterestsInput:
    page: Optional[int] = 0
    size: Optional[int] = 0


@dataclass
class GetErrorLogsInput:
    callId: str


@dataclass
class CreateClubInterestInput:
    user_id: str
    isInterested: Optional[bool] = False


@dataclass
class ClubInterest:
    user_id: str
    isInterested: Optional[bool] = False
    createdAt: datetime = field(default_factory=datetime.now)
    updatedAt: datetime = field(default_factory=datetime.now)

    _id: Optional[str] = None


@dataclass
class UpsertEngagementDataInput:
    key: str
    field: str
    value: str


@dataclass
class PhotosInput:
    page: int
    query: str
    per_page: int


@dataclass
class WaOptionsInput:
    type: str


@dataclass
class GetLeadsInput:
    page: Optional[int] = 0
    size: Optional[int] = 0
    data: Optional[bool] = False
    sort_order: Optional[int] = None
    sort_field: Optional[str] = None
    filter_field: Optional[str] = None
    filter_value: Optional[str] = None


@dataclass
class GetCallsInput:
    dest: str
    page: Optional[int] = 0
    size: Optional[int] = 0
    internal: Optional[str] = ""
    callId: Optional[str] = None
    filter_field: Optional[str] = None
    filter_value: Optional[str] = None


@dataclass
class GetExpertsInput:
    internal: Optional[str] = ""
    expert_id: Optional[str] = None
    phoneNumber: Optional[str] = None
    schedule_status: Optional[str] = None


@dataclass
class GetContentPostsInput:
    page: Optional[int] = 0
    size: Optional[int] = 0


@dataclass
class GetGameConfigInput:
    game_type: str


@dataclass
class ChatInput:
    prompt: str


@dataclass
class ContentPhoto:
    url: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Content:
    response: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class SaveContentInput:
    content: Content
    photo: ContentPhoto


@dataclass
class WASlackNotifierInput:
    name: str
    body: str
    from_number: str


@dataclass
class Call:
    type: Optional[str] = None
    callId: Optional[str] = None
    status: Optional[str] = None
    _id: Optional[ObjectId] = None
    duration: Optional[str] = None
    user: Optional[ObjectId] = None
    expert: Optional[ObjectId] = None
    scheduledId: Optional[str] = None
    failedReason: Optional[str] = None
    recording_url: Optional[str] = None
    user_requested: Optional[bool] = None
    transferDuration: Optional[str] = None
    conversationScore: Optional[int] = None
    initiatedTime: Optional[datetime] = None


@dataclass
class WebhookInput:
    call_uuid: str
    call_time: str
    call_date: str
    call_status: str
    agent_number: str
    call_duration: str
    called_number: str
    call_direction: str
    customer_number: str
    callrecordingurl: str
    call_transfer_status: str
    call_transfer_duration: str


@dataclass
class TimingsRow:
    key: str
    value: str
    field: str


@dataclass
class SaveRemarkInput:
    key: str
    value: str


@dataclass
class UpdateTimingsInput:
    expertId: str
    row: TimingsRow


@dataclass
class SaveFCMTokenInput:
    token: str


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
class GetReferralsInput:
    userId: Optional[str] = None
    refCode: Optional[str] = None


@dataclass
class GetReferralsInput:
    userId: Optional[str] = None
    refCode: Optional[str] = None


@dataclass
class SendOTPInput:
    phone_number: str


@dataclass
class ValidateOTPInput:
    otp: str
    user_type: str
    phone_number: str
    internal: Optional[str] = ""
    call_status: Optional[str] = None


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
    request_meta: str = field(default_factory=lambda: "")
    user_id: Optional[str] = field(default_factory=lambda: "")


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
    body: str
    title: str
    token: str
    type_: str
    user_id: str
    image_url: str
    sarathi_id: str
    priority: Optional[str] = field(default="high")
    sound: Optional[str] = field(default="longbell")
    action: str = field(default_factory=lambda: "")
    app_type: str = field(default_factory=lambda: "expert")


@dataclass
class UpdateFCMTokenInput:
    user_id: str
    fcm_token: str


@dataclass
class ScheduledJobInput:
    user_requested: Optional[bool] = None
    action: str = field(default_factory=lambda: "")
    status: str = field(default_factory=lambda: "")
    job_type: str = field(default_factory=lambda: "")
    job_time: str = field(default_factory=lambda: "")
    request_meta: str = field(default_factory=lambda: "")
    scheduled_job_id: str = field(default_factory=lambda: "")


@dataclass
class GetUsersInput:
    size: Optional[int] = None
    page: Optional[int] = None
    internal: Optional[str] = ""
    user_id: Optional[str] = None
    call_status: Optional[str] = None
    phoneNumber: Optional[str] = None


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
class Event:
    name: Optional[str] = None
    slug: Optional[str] = None
    repeat: Optional[str] = None
    passcode: Optional[str] = None
    subTitle: Optional[str] = None
    hostedBy: Optional[str] = None
    category: Optional[str] = None
    imageUrl: Optional[str] = None
    mainTitle: Optional[str] = None
    eventType: Optional[str] = None
    meeting_id: Optional[str] = None
    prizeMoney: Optional[int] = None
    isAlways: Optional[bool] = False
    meetingLink: Optional[str] = None
    description: Optional[str] = None
    guestSpeaker: Optional[str] = None
    validUpto: Optional[datetime] = None
    isPremiumUserOnly: Optional[bool] = None
    maxVisitorsAllowed: Optional[int] = None
    startEventDate: Optional[datetime] = None
    registrationAllowedTill: Optional[datetime] = None


@dataclass
class ContributeEvent:
    slug: Optional[str] = None
    name: Optional[str] = None
    image: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    stipend: Optional[str] = None
    isPaid: Optional[bool] = False
    highlights: Optional[str] = None
    isDeleted: Optional[bool] = None
    phoneNumber: Optional[str] = None
    description: Optional[str] = None
    locationType: Optional[str] = None
    validUpto: Optional[datetime] = None
    startDate: Optional[datetime] = None
    

@dataclass
class GetEventsInput:
    page: Optional[int] = 0
    size: Optional[int] = 0
    slug: Optional[str] = None
    events_type: Optional[str] = None
    fromToday: Optional[str] = "false"
    isHomePage: Optional[str] = "false"
    filter_field: Optional[str] = None
    filter_value: Optional[str] = None


@dataclass
class EventUserInput:
    source: str
    phoneNumber: str
    name: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    dob: Optional[datetime] = None
    eventName: Optional[str] = None
    advSeenOn: Optional[str] = None
    isUserPaid: Optional[bool] = None


@dataclass
class GetEventUsersInput:
    page: Optional[int] = None
    size: Optional[int] = None
    slug: Optional[str] = None
    filter_field: Optional[str] = None
    filter_value: Optional[str] = None


@dataclass
class PhoneConfigInput:
    user_id: str
    model: Optional[str] = None
    serial: Optional[str] = None
    location: Optional[str] = None
    metadata: Optional[dict] = None
    user_type: Optional[str] = None
    installedApps: Optional[list] = None


@dataclass
class PhoneConfig:
    user_id: str
    _id: Optional[str] = None
    model: Optional[str] = None
    serial: Optional[str] = None
    location: Optional[str] = None
    metadata: Optional[dict] = None
    user_type: Optional[str] = None
    installedApps: Optional[list] = None
    createdDate: datetime = field(default_factory=datetime.now)


@dataclass
class User:
    createdDate: datetime = field(default_factory=datetime.now)

    name: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    refCode: Optional[str] = None
    active: Optional[bool] = None
    isBusy: Optional[bool] = None
    _id: Optional[ObjectId] = None
    refSource: Optional[str] = None
    isBlocked: Optional[bool] = None
    isPaidUser: Optional[bool] = None
    wa_opt_out: Optional[bool] = None
    phoneNumber: Optional[str] = None
    expert: Optional[ObjectId] = None
    numberOfGames: Optional[int] = None
    numberOfCalls: Optional[int] = None
    birthDate: Optional[datetime] = None
    customerPersona: Optional[dict] = None
    profileCompleted: Optional[bool] = None


@dataclass
class EventUser:
    phoneNumber: str = None
    createdAt: datetime = field(default_factory=datetime.now)
    updatedAt: datetime = field(default_factory=datetime.now)

    name: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = None
    dob: Optional[datetime] = None
    _id: Optional[ObjectId] = None
    eventName: Optional[str] = None
    advSeenOn: Optional[str] = None
    userId: Optional[ObjectId] = None
    isUserPaid: Optional[bool] = None


@dataclass
class ApplicantInput:
    phoneNumber: str
    name: str = field(default_factory=lambda: '')
    email: str = field(default_factory=lambda: '')
    skills: str = field(default_factory=lambda: '')
    gender: str = field(default_factory=lambda: '')
    formType: str = field(default_factory=lambda: '')
    languages: list = field(default_factory=lambda: [])
    dateOfBirth: str = field(default_factory=lambda: '')
    workingHours: list = field(default_factory=lambda: [])
    createdDate: datetime = field(default_factory=datetime.now)

    _id: Optional[str] = None


@dataclass
class GetApplicantsInput:
    formType: str
    page: Optional[int] = 0
    size: Optional[int] = 0


@dataclass
class CategoriesInput:
    name: Optional[str] = None
    action: Optional[str] = None


@dataclass
class Category:
    name: str
    active: bool = True
    createdDate: datetime = field(default_factory=datetime.now)
    lastModifiedBy: Optional[str] = None


@dataclass
class UpdateScoresInput:
    expert_id: str
    expert_number: str


@dataclass
class AverageScores:
    flow: Optional[int] = 0
    timeSplit: Optional[int] = 0
    timeSpent: Optional[int] = 0
    probability: Optional[int] = 0
    userSentiment: Optional[int] = 0
    closingGreeting: Optional[int] = 0
    openingGreeting: Optional[int] = 0


@dataclass
class AverageScoresObject:
    message: str
    average_scores: AverageScores
    score: Optional[int] = 0


@dataclass
class GetUserCountsInput:
    test: Optional[str] = None


@dataclass
class UserMeta:
    user: ObjectId
    source: Optional[str] = ""
    remarks: Optional[str] = ""
    context: Optional[str] = ""
    userStatus: Optional[str] = ""


@dataclass
class RecommendExpertInput:
    user_id: str


@dataclass
class UploadInput:
    file_name: str
    file_type: str


@dataclass
class GetScheduledJobsInput:
    limit: Optional[int] = None
    nextToken: Optional[str] = None


@dataclass
class Output:
    output_status: str
    output_message: str
    output_details: dict


# Admin Interfaces
@dataclass
class AdminAuthInput:
    action: str
    name: Optional[str] = None
    password: Optional[str] = None
    phoneNumber: Optional[str] = None


@dataclass
class Admin:
    password: str
    phoneNumber: str
    createdDate: datetime = field(default_factory=datetime.now)

    _id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class DashboardStatsInput:
    item: str
    internal: Optional[str] = ""


@dataclass
class CallInput:
    user_id: str
    expert_id: str
    scheduledId: Optional[str] = None
    user_requested: Optional[bool] = None
    type_: str = field(default_factory=lambda: 'call')


@dataclass
class AdminWaInput:
    action: str
    inputs: Optional[dict] = None
    eventId: Optional[str] = None
    usersType: Optional[str] = None
    messageId: Optional[str] = None
    templateId: Optional[str] = None
    cities: Optional[List[str]] = None

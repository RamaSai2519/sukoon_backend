from variables import *
from openai import AzureOpenAI
from pymongo import MongoClient

user_document = None
expert_document = None

client = MongoClient(MONGO_KEY)

main_lambda_url = MAIN_LAMBDA_URL

db = client["test"]
calls_collection = db["calls"]
users_collection = db["users"]
experts_collection = db["experts"]
fcm_tokens_collection = db["fcm_tokens"]
errorlog_collection = db["errorlogs"]
timings_collection = db["timings"]
callsmeta_collection = db["callsmeta"]
schedules_collection = db["schedules"]


# Initialize the OpenAI client with the API key
# client = OpenAI(api_key="sk-proj-aKKDe91pGa2k6HMxYksiT3BlbkFJfijdRZELYUustkm8biLd")

# Configure the generative AI with the API key
# genai.configure(api_key=os.getenv("GEMNAI_KEY"))

# # Initialize the generative model
# model = genai.GenerativeModel("gemini-pro")

open_ai_client = AzureOpenAI(
    azure_endpoint="https://sukoon-chat.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2023-03-15-preview",
    api_key="13c72289e9704b4ca63f683df19a7afe",
    api_version="2023-03-15-preview"
)

import os
import re
import json
import requests
from notify import notify
from json_extractor import extract_json
from txthelper import download_txt_file
from download_audio import download_audio
from config import DEEPGRAM_API_KEY, open_ai_client as client


class CallProcessor:
    def __init__(self, document, user, expert, persona, user_calls):
        self.document = document
        self.user = user
        self.expert = expert
        self.persona = persona
        self.user_calls = user_calls
        self.audio_filename = f"/tmp/{document['callId']}.mp3"
        self.transcript_url = f"https://sukoontest.s3.ap-south-1.amazonaws.com/{document['callId']}.txt"
        self.guidelines_url = 'https://sukoon-media.s3.ap-south-1.amazonaws.com/guidelines.txt'

    def fetch_guidelines(self):
        return download_txt_file(self.guidelines_url)

    def fetch_transcript(self):
        return download_txt_file(self.transcript_url)

    def download_audio_and_transcribe(self):
        download_audio(self.document, self.audio_filename)
        print(f"Downloaded audio for call ID: {self.document['callId']} to {self.audio_filename}")

        url = 'https://api.deepgram.com/v1/listen?model=whisper-large&diarize=true&punctuate=true&utterances=true'
        headers = {
            'Authorization': f'Token {DEEPGRAM_API_KEY}',
            'Content-Type': 'audio/mp3'
        }

        with open(self.audio_filename, 'rb') as audio_file:
            response = requests.post(url, headers=headers, data=audio_file)

        if response.status_code != 200:
            print(f"Error: {response.text}")
            return None

        try:
            response_json = response.json()
            utterances = response_json.get('results', {}).get('utterances', [])
            transcriptions = "\n".join(
                [f"[Speaker:{utt['speaker']}] {utt['transcript']}" for utt in utterances])
            return transcriptions
        except json.JSONDecodeError as e:
            print(f"Error parsing response: {e}")
            return None

    def process_transcription(self):
        transcript = self.fetch_transcript()
        if not transcript:
            try:
                transcript = self.download_audio_and_transcribe()
                os.remove(self.audio_filename)
            except Exception as e:
                os.remove(self.audio_filename)
                error_message = f"An error occurred processing the call ({self.document['callId']}): {str(e)} while transcribing the audio"
                notify(error_message)
                print(error_message)
                return None
        return transcript

    def chat_with_model(self, message_history, user_input):
        message_history.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model="gpt-4-turbo", messages=message_history)
        assistant_response = response.choices[0].message.content
        message_history.append(
            {"role": "assistant", "content": assistant_response})
        return assistant_response

    def process_call_recording(self):
        print(f"Starting process for call ID: {self.document['callId']}")
        guidelines = self.fetch_guidelines()
        transcript = self.process_transcription()
        if not transcript:
            return (None, None, None, None, None, None, None, None)

        system_message = {"role": "system",
                          "content": "You are a helpful assistant."}
        message_history = [system_message]

        self.chat_with_model(message_history, f"I'll give you a call transcript between the user {self.user} and the sarathi {self.expert}. You have to correctly identify which Speaker is the User and which Speaker is the Sarathi (Generally Sarathi will be the one who ask the User questions about their routine and how they are doing. Also you can identify which speaker is Sarathi by their name). The user and sarathi connected via a website called 'Sukoon.Love', a platform for people to have conversations and seek guidance from Sarathis. Analyze the transcript and answer the questions I ask accordingly.")
        self.chat_with_model(message_history, f"{transcript} \nThis is the transcript for the call")

        self.chat_with_model(message_history, """Analyze the transcript and flag any instances of inappropriate language or behavior. Detect any offensive language, insults, harassment, discrimination,religious or any other form of inappropriate communication. Just say "All good" if nothing is wrong or give a summary of flagged content if found anything wrong, with the confidence score between 0 to 1. Please be strict in analysing and give correct data only""")
        summary = message_history[-1]['content']

        if "All good" not in summary:
            print(f"Inappropriate content found for call ID: {self.document['callId']}")
            return (None, None, None, None, None, None, None, None)

        self.chat_with_model(
            message_history, "Calculate probability of the user calling back only on the basis of the transcript given to you. Give the reason also.")
        user_callback = message_history[-1]['content']

        self.chat_with_model(
            message_history, "Summarize the transcript, with the confidence score between 0 to 1.")
        summary = message_history[-1]['content']

        self.chat_with_model(
            message_history, "Give me feedback for the sarathi.")
        saarthi_feedback = message_history[-1]['content']

        self.chat_with_model(message_history, f"This is the guidelines {guidelines}. Remember this")
        self.chat_with_model(
            message_history, """Please analyze the call transcript based on the given parameters. Opening Greeting(_/10)- Evaluate if the guidelines are followed. Time split between Saarthi and User(_/15) - Evaluate if the guidelines are followed. User Sentiment(_/20) - Evaluate the sentiment of the user based on the transcript. Flow Of Conversation(_/15) - Evaluate if the guidelines are followed. Time Spent on Call(_/10) - If time spent is more than 15 minutes, its good. Use the transcript provided initially for this. Probability of the User Calling Back(_/20) - The User should explicitly state that they would call back or the user and sarathi should mutually decide for a future date for the call for a higher score. Also mention the instance. Closing Greeting(_/10) - Evaluate if the guidelines are followed. Find the section relating to the parameters in the guidelines before you give a score. Higher score if the guidelines are followed. With the confidence score between 0 to 1. Give me the output in a json format like this: {"openingGreeting": 0,"timeSplit": 0,"userSentiment": 0,"flow": 0,"timeSpent": 0,"probability": 0,"closingGreeting": 0, "explanation": ""}""")
        conversation_score_details = extract_json(
            message_history[-1]['content'])

        self.chat_with_model(
            message_history, "Give me a total score out of 100. Only return the score in response.")
        conversation_score = int(re.findall(r"\b(?:\d{2}|100)\b", message_history[-1]['content'])[0]) / 20

        topics = download_txt_file('https://sukoon-media.s3.ap-south-1.amazonaws.com/topics.txt')
        self.chat_with_model(message_history, f"Identify the topics they are talking about from the {topics}. Give me the output in a json format like this: {{\"topic\": \"\", \"sub_topic\": \"\"}}")
        topics = extract_json(message_history[-1]['content'])

        if self.persona != "None":
            self.chat_with_model(message_history, f"This is the user persona derived from previous call transcripts of the user. User Persona: {self.persona} Remember this and answer the next question accordingly. with the confidence score between 0 to 1")

        self.chat_with_model(
            message_history, """Context: Generate a user persona from the transcript provided above. Remember which speaker was the user and use only that speaker lines from the transcript to generate this persona. The persona should encompass demographics, psychographics, and personality traits based on the conversation. Specify the reason also for every field. Update the persona provided above, update only the field which you are sure about. a. User Demographics: 1. Gender: 2. Ethnicity: 3. Education: 4. Marital Status Choose one(Single/Married/Widow/Widower/Divorced/Unmarried): 5. Income: 6. Living Status Choose one(Stays alone/Stays with spouse only/Stays with spouse and kids/Stays with kids (no spouse)/Has parents staying with them ): 7. Medical History: 8. Location/City: 9. Comfort with Technology: 10. Standard of Living: 11. Family Members: 12. Work Status Choose One(Retired/Active Working/Part-Time/Projects) 13. Last Company Worked For: 14. Language Preference: 15. Physical State Of Being: b. User Psychographics: 1. Needs: 2. Values: 3. Pain Points/ Challenges: 4. Motivators: c. User Personality: Choose one(Sanguine/Choleric/Melancholic/Phlegmatic) with the confidence score between 0 to 1, Please be strict in analysing and give correct data only Give me the output in a json format like this: {demographics: { gender: "", ethnicity: "", education: "", maritalStatus: "", income: "", livingStatus: "", medicalHistory: "", location: "", techComfort: "", standardOfLiving: "", familyMembers: "", workStatus: "", lastCompany: "", languagePreference: "", physicalState: "" }, psychographics: { needs: "", values: "", painPoints: "", motivators: "" }, personality: ""}""")
        customer_persona = extract_json(message_history[-1]['content'])

        return (transcript, summary, conversation_score, conversation_score_details, saarthi_feedback, customer_persona, user_callback, topics)
            


def process_call_recording(document, user, expert, persona, user_calls):
    processor = CallProcessor(document, user, expert, persona, user_calls)
    return processor.process_call_recording()

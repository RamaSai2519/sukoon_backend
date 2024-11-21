import json
from bson import ObjectId
from typing import List, Dict
from shared.models.common import Common
from shared.db.users import get_user_collection
from shared.db.experts import get_experts_collections
from shared.models.constants import extract_json_function_str
from shared.models.interfaces import RecommendExpertInput as Input, User


class Prompt:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.users_collection = get_user_collection()
        self.experts_collection = get_experts_collections()

    def get_user_persona(self):
        query = {"_id": ObjectId(self.input.user_id)}
        user = self.users_collection.find_one(query)
        user = Common.clean_dict(user, User)
        user = User(**user)
        persona = user.customerPersona
        if isinstance(persona, dict) and persona.get("demographics"):
            persona["_id"] = str(user._id)
            persona["name"] = user.name
            return persona
        return None

    def get_experts_personas(self) -> List[Dict]:
        query = {'type': {'$ne': 'internal'}}
        experts = list(self.experts_collection.find(query))
        personas = []
        for e in experts:
            persona = e.get('persona', {})
            if isinstance(persona, str):
                persona = {}
            if persona.get('demographics'):
                e['persona']['_id'] = str(e['_id'])
                e['persona']['name'] = e['name']
                personas.append(e['persona'])
        return personas

    def format_persona_dict(self, persona: dict, indent_level: int = 0) -> str:
        indent = "  " * indent_level
        persona_str = ""

        for key, value in persona.items():
            formatted_key = ''.join(
                [' ' + char if char.isupper() else char for char in key]).strip().capitalize()
            if isinstance(value, dict):
                persona_str += f"{indent}**{formatted_key}:**\n"
                persona_str += self.format_persona_dict(
                    value, indent_level + 1)
            else:
                persona_str += f"{indent}- {formatted_key}: {value}\n"

        return persona_str

    def get_json_prompt(self, prompt: str, output_doc: dict) -> str:
        prompt += "\nGive me the output in a json format like this, don't change the keys:"
        prompt += json.dumps(output_doc, indent=4)
        prompt += "\nand make sure I will be able to store your response as a json object using the following function by not placing colons and double quotes inside the values:"
        prompt += extract_json_function_str
        return prompt

    def personas_prompt(self) -> str:
        experts_personas = self.get_experts_personas()
        user_persona = self.get_user_persona()
        if not user_persona:
            return None

        user_persona_str = "**User Persona:**\n"
        user_persona_str += self.format_persona_dict(user_persona)

        experts_personas_str = "**Available Expert Personas:**\n"
        for idx, expert in enumerate(experts_personas, 1):
            experts_personas_str += f"{idx}. **{expert.get('name')}**:\n"
            experts_personas_str += self.format_persona_dict(expert)

        description = "Analyze the user persona and the available Sarathi (expert) personas, and select the expert who is best suited to connect with the user based on their demographics, psychographics, needs, values, and personality traits."

        prompt = "{user_persona}\n{experts_personas}\n**Task:**\n{description}"
        prompt = prompt.format(
            user_persona=user_persona_str,
            experts_personas=experts_personas_str,
            description=description
        )
        example_output = {"expert_id": "expert_id", "confidence": "0 to 1",
                          "explanation": "reason for selecting the expert"}
        prompt = self.get_json_prompt(prompt, example_output)
        return prompt

import requests
from shared.models.common import Common
from shared.configs import CONFIG as config
from shared.models.constants import OutputStatus
from shared.db.content import get_blogposts_collection
from shared.models.interfaces import BlogPostInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.blogposts_collection = get_blogposts_collection()

    def generate_missing_fields(self, title: str, body: str):
        payload = {
            "prompt": f"Generate the description, meta description (for use in meta tag of the webpage) and tags (for use in SEO) for the following blog: {title} \n {body}",
            "context": "blog",
            "phoneNumber": "1234567890"
        }
        url = config.URL + '/actions/chat'
        response = requests.post(url, json=payload)
        data = response.json().get('output_details', {})

        return {
            "description": data.get('description'),
            "meta_description": data.get('meta_description'),
            "tags": data.get('tags')
        }

    def compute(self) -> Output:
        new_data = self.input.__dict__

        if not new_data.get("description") or not new_data.get("meta_description") or not new_data.get("tags"):
            generated_data = self.generate_missing_fields(
                title=new_data.get("title"),
                body=new_data.get("content_html")
            )

            new_data["description"] = new_data.get("description") or generated_data.get("description")
            new_data["meta_description"] = new_data.get("meta_description") or generated_data.get("meta_description")
            new_data["tags"] = new_data.get("tags") or generated_data.get("tags")

        if self.input.number_of_words:
            est_read_time = round(self.input.number_of_words / 200)
            new_data["estimated_read_time"] = est_read_time

        query = {"title": new_data.get("title")}
        blogpost = self.blogposts_collection.find_one_and_update(
            filter=query,
            update={"$set": new_data},
            upsert=True,
            return_document=True
        )

        return Output(
            output_details=Common.jsonify(blogpost),
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully upserted blogpost"
        )

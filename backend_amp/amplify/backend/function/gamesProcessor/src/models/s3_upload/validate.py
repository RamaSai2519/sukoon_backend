class Validator():
    def __init__(self, input) -> None:
        self.input = input
        self.ALLOWED_MIME_TYPES = [
            "image/jpeg", "image/pipeg", "image/png", "application/octet-stream",
            "image/svg+xml", "video/mp4", "video/webm", "video/quicktime",
            "video/x-matroska"
        ]

    def file_filter(self, mimetype) -> bool:
        return mimetype in self.ALLOWED_MIME_TYPES

    def validate_input(self):
        if 'file' not in self.input:
            return False, "No file part"

        if self.input['file'].filename == '':
            return False, "No selected file"

        if not self.file_filter(self.input['file'].mimetype):
            return False, "Invalid file type"

        return True, ""

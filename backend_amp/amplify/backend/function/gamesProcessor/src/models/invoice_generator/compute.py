from pyppeteer import launch
from models.common import Common
from models.constants import OutputStatus
from models.interfaces import InvoiceData as Input, Output
from models.invoice_generator.htmlTemplate import htmlTemplate


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.bucket_name = "sukoon-media"
        self.client = Common.get_s3_client()

    async def generate_pdf(self, html_content, output_path):
        browser = await launch()
        page = await browser.newPage()
        await page.setContent(html_content, waitUntil='networkidle0')
        await page.pdf({'path': output_path, 'format': 'A4', 'printBackground': True})
        await browser.close()

    async def upload_to_s3(self, file_path: str, file_name: str) -> str:
        endpoint_url = self.client.meta.endpoint_url
        file_url = f"{endpoint_url}/{self.bucket_name}/invoices/{file_name}"
        metadata = {"fieldName": "pdf_file"}

        with open(file_path, "rb") as file:
            file = file.read()
            self.client.upload_fileobj(
                file,
                self.bucket_name,
                file_name,
                ExtraArgs={
                    "Metadata": metadata,
                    "ACL": "public-read",
                    "ContentType": "application/pdf"
                }
            )

        return file_url

    async def compute(self) -> Output:
        html_content = htmlTemplate(self.input)
        file_name = f"{self.input.userId}-{self.input.invoiceNumber}.pdf"
        output_path = f"/tmp/{file_name}"
        await self.generate_pdf(html_content, output_path)
        file_url = await self.upload_to_s3(output_path, file_name)

        return Output(
            output_details={"file_url": file_url},
            output_status=OutputStatus.SUCCESS,
            output_message="Successfully generated Invoice PDF"
        )

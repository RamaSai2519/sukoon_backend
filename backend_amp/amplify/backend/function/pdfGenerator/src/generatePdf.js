const puppeteer = require('puppeteer-core');
const chromium = require('chrome-aws-lambda');
const AWS = require('aws-sdk');

const s3 = new AWS.S3();

async function generatePDF(htmlContent) {
    let browser = null;

    try {
        browser = await puppeteer.launch({
            args: chromium.args, // Only needed for AWS Lambda
            executablePath: await chromium.executablePath(), // Replace with your Chromium path if not using Lambda
            headless: chromium.headless,
        });

        const page = await browser.newPage();

        // Set the content of the page to your HTML
        await page.setContent(htmlContent, { waitUntil: 'networkidle0' });

        // Generate the PDF
        const pdfBuffer = await page.pdf({
            format: 'A4',
            printBackground: true,
        });

        return pdfBuffer;
    } catch (error) {
        console.error('Error generating PDF:', error);
        throw error;
    } finally {
        if (browser !== null) {
            await browser.close();
        }
    }
}

async function uploadPDFToS3(pdfBuffer, bucketName, key) {
    const params = {
        Bucket: bucketName,
        Key: key,
        Body: pdfBuffer,
        ContentType: 'application/pdf',
    };

    try {
        await s3.upload(params).promise();
        console.log(`PDF successfully uploaded to ${bucketName}/${key}`);
    } catch (error) {
        console.error('Error uploading PDF to S3:', error);
        throw error;
    }
}

// Export the functions
module.exports = {
    generatePDF,
    uploadPDFToS3,
};

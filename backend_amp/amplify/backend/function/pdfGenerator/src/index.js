const { generatePDF, uploadPDFToS3 } = require('./generatePdf');


/**
 * @type {import('@types/aws-lambda').APIGatewayProxyHandler}
 */
exports.handler = async (event) => {
    console.log(`EVENT: ${JSON.stringify(event)}`);
    const pdfBuffer = await generatePDF(htmlContent);

        // Define S3 parameters
        const bucketName = 'sukoon-media';
        const key = 'invoicePdf/output.pdf';

        // Upload the PDF to S3
        await uploadPDFToS3(pdfBuffer, bucketName, key);
    return {
        statusCode: 200,
    //  Uncomment below to enable CORS requests
    //  headers: {
    //      "Access-Control-Allow-Origin": "*",
    //      "Access-Control-Allow-Headers": "*"
    //  },
        body: JSON.stringify('Hello from Lambda!'),
    };
};

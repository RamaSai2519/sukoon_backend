const { generatePDF, uploadPDFToS3 } = require('./generatePdf');

const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Test</title>
    <!-- Tailwind CSS CDN -->
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 text-gray-800">
    <div class="max-w-xl mx-auto p-4 bg-white shadow-lg rounded-lg">
        <h1 class="text-2xl font-bold text-blue-500">Tailwind CSS PDF</h1>
        <p class="mt-2 text-lg">
            This is a sample PDF generated using Puppeteer with Tailwind CSS for styling. 
            The following are some of the features of Tailwind CSS:
        </p>
        <ul class="list-disc list-inside mt-4">
            <li>Utility-first CSS framework</li>
            <li>Responsive design</li>
            <li>Highly customizable</li>
        </ul>
        <p class="mt-4">
            Tailwind CSS is a utility-first CSS framework packed with classes like <code>flex</code>, 
            <code>pt-4</code>, <code>text-center</code>, and <code>rotate-90</code> that can be composed to build any design, directly in your markup.
        </p>
        <footer class="mt-6 text-right">
            <p class="text-sm text-gray-500">Generated on: <span id="date"></span></p>
        </footer>
    </div>
</body>
</html>
`;

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

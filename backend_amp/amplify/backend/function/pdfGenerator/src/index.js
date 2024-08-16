/* Amplify Params - DO NOT EDIT
	ENV
	REGION
	STORAGE_GETPAZADMIN_BUCKETNAME
Amplify Params - DO NOT EDIT */
const chromium = require("@sparticuz/chromium");
const puppeteer = require("puppeteer-core");
const AWS = require("aws-sdk");
const fs = require("fs");

const BUCKET_NAME = process.env.STORAGE_GETPAZADMIN_BUCKETNAME;
const s3bucket = new AWS.S3();

async function uploadToS3(uploadFileName, s3BucketPath) {
  const readStream = fs.createReadStream(uploadFileName);

  const params = {
    Bucket: BUCKET_NAME,
    Key: s3BucketPath,
    Body: readStream
  };

  return new Promise((resolve, reject) => {
    s3bucket.upload(params, function(err, data) {
      readStream.destroy();

      if (err) {
        return reject(err);
      }
      console.log(`${uploadFileName} has been uploaded!`);
      return resolve(data);
    });
  });
}

const generatePdf = async (template, identifier, format, scale) => {
    const decodedTemplate = Buffer.from(template, "base64").toString();
    const browser = await puppeteer.launch({
      args: chromium.args,
      defaultViewport: chromium.defaultViewport,
      executablePath: await chromium.executablePath(),
      headless: chromium.headless
    });
    const page = await browser.newPage();
    await page.setContent(decodedTemplate);
    await page.pdf({ path: `/tmp/${identifier}.pdf`, format: format, printBackground: true, scale: scale, preferCSSPageSize: true });
    await browser.close();
}

exports.handler = async (event, context) => {
    const response = { statusCode: 201, error: null }
    console.log(`EVENT: ${JSON.stringify(event)}`);

    try {
        context.callbackWaitsForEmptyEventLoop = false;
        console.log(event);
        const { id, template, destination, format="a4", scale=1 } = event;
        const identifier = id;
        await generatePdf(template, identifier, format, scale);
        await uploadToS3(`/tmp/${identifier}.pdf`, destination);
    } catch (error) {
        response.statusCode = 400;
        response.error = error;
        console.log(error);
    }

    console.log(`Response: ${JSON.stringify(response)}`);
    return response;
};

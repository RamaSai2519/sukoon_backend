from models.interfaces import InvoiceData as Input


def htmlTemplate(data: Input) -> str:
    return f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invoice</title>
    <!-- Tailwind CSS CDN -->
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>

<body class="bg-gray-100 p-5 font-sans">

    <div class="bg-white p-8 max-w-3xl mx-auto shadow-lg rounded-lg">
        <img class="w-48 h-48 mb-6 mx-auto" src="https://sukoon-media.s3.ap-south-1.amazonaws.com/logo/app-logo.png" alt="Company Logo">

        <div class="flex justify-between items-start mb-8">
            <div>
                <h1 class="text-2xl font-bold mb-2">TAX INVOICE</h1>
                <p class="text-sm mb-1">Invoice #{data.invoiceNumber}</p>
                <p class="text-sm mb-1">Date: {data.createdDate}</p>
                <p class="text-sm mb-1">Due Date: {data.createdDate}</p>
            </div>
            <div class="text-right">
                <p class="text-sm mb-1">Three Dots & Dash Pvt. Ltd.</p>
                <p class="text-sm mb-1">Karnataka, India</p>
                <p class="text-sm">GSTIN: 29AAKCT7222N1ZO</p>
            </div>
        </div>

        <div class="mb-8">
        <p class="text-sm mb-1"><strong>Bill To:</strong> {data.customerFullName}</p>
            <p class="text-sm mb-1">GSTIN: 29AAKCT7222N1ZO</p>
            <p class="text-sm"><strong>Place Of Supply:</strong> Karnataka (29)</p>
        </div>

        <table class="w-full border-collapse mb-8">
            <thead>
                <tr class="bg-gray-200 text-left">
                    <th class="px-4 py-2 border-b">#</th>
                    <th class="px-4 py-2 border-b">Item Description</th>
                    <th class="px-4 py-2 border-b">HSN/SAC</th>
                    <th class="px-4 py-2 border-b">Qty</th>
                    <th class="px-4 py-2 border-b">Rate</th>
                    <th class="px-4 py-2 border-b">CGST</th>
                    <th class="px-4 py-2 border-b">SGST</th>
                    <th class="px-4 py-2 border-b">Amount</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="px-4 py-2 border-b">1</td>
                    <td class="px-4 py-2 border-b">{data.itemDescription}</td>
                    <td class="px-4 py-2 border-b">999594</td>
                    <td class="px-4 py-2 border-b">1.00</td>
                    <td class="px-4 py-2 border-b">{data.rate}</td>
                    <td class="px-4 py-2 border-b">{data.cgst}</td>
                    <td class="px-4 py-2 border-b">{data.sgst}</td>
                    <td class="px-4 py-2 border-b">{data.amount}</td>
                </tr>
            </tbody>
        </table>

        <div class="text-right">
            <p class="text-sm mb-1"><strong>Sub Total:</strong> ₹{data.rate}</p>
            <p class="text-sm mb-1"><strong>CGST (9%):</strong> ₹{data.cgst}</p>
            <p class="text-sm mb-1"><strong>SGST (9%):</strong> ₹{data.sgst}</p>
            <hr class="my-4 border-t border-gray-300">
            <p class="text-lg font-bold"><strong>Total: ₹{data.amount}</strong></p>
               <hr class="my-4 border-t border-gray-300">
              <p class="text-lg font-bold">Payment Made:₹{data.amount}</p>
              <hr class="my-4 border-t border-gray-300">
              <p class="text-lg font-bold"><strong>Balance Due: (-) ₹0</strong></p>
        </div>

        <p class="mt-8 text-center">Thank you for becoming part of Sukoon family.</p>
    </div>

</body>

</html>
"""

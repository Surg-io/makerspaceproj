export async function SheetsConnectionError(res,err) {
    return res.status(500).send({"Success":"False","Message":`Error in Connecting to Sheets: ${err}`});
}
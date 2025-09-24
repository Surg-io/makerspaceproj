export async function SheetsConnectionError(res,err) {
    return res.status(500).send({"Success": 0 ,"Message":`Error in Connecting to Sheets: ${err}`});
}

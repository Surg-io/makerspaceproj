export async function SheetsConnectionError(res,err) {
    return res.status(500).send("Error in Connecting to Sheets: " + err);
}
import { SheetsConnectionError } from "./Responses.js";
export async function SheetsGet(res,sheets, spreadsheetId, range) {
    try{
       const result = await sheets.spreadsheets.values.get({ //'Get' request using sheet resource to retrieve the values specified by range from the spreadsheet 
        spreadsheetId,
        range,
    });
      console.log("Retrieving Values...");
      return result;
    }catch(err)
    {
      SheetsConnectionError(res,err); //This will send response. 
      return null; //Allows index.js to know this failed.
    }
}

export async function SheetsUpdate(res,sheets, spreadsheetId, range, resource) {
     try {
          const result = await sheets.spreadsheets.values.update({ //Update Cells Call
            spreadsheetId,
            range,
            valueInputOption: 'USER_ENTERED', //Value Input Option. What 'mode' the data is inserted
            resource,
            });
          console.log(`Cells cleared.`);
          return result;
        } catch (err) {
          SheetsConnectionError(res,err);
          return null;
        }
}

export async function SheetsAppend(res,sheets, spreadsheetId, range,resource) {
    try {
      const result = await sheets.spreadsheets.values.append({ //Append Cells
        spreadsheetId,
        range,
        valueInputOption: 'USER_ENTERED', //What 'mode' the data is inserted
        resource,
        });
      console.log(`Sheet Appended`);
      return result;
    } catch (err) {
     SheetsConnectionError(res,err);
     return null;
    }
}

export async function SheetsBatchGet(res,sheets, spreadsheetId, range) {
    try{
     const result = await sheets.spreadsheets.values.batchGet({ //'Get' request using sheet resource to retrieve the values specified by range from the spreadsheet 
        spreadsheetId,
        ranges:range,
    });
    console.log("Checking IDs...");
    //console.log(result);
    return result;
  }
  catch(err)
  {
     SheetsConnectionError(res,err); //Send Error, if there is one.
     return null;
  }
}
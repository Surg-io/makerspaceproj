import express from "express"; //Express utility
import dotenv from 'dotenv'; //Allows use of .env variables, w/ config
import bodyParser from "body-parser"; //Parses body of Requests.
import compression from "compression";
import { SheetsConnectionError } from "./Responses.js";
import {google} from "googleapis"; //Allows for use of Google API's
import { GoogleAuth } from "google-auth-library";

dotenv.config();//Use with dotenv to use .env vars

const app = express();
const port = 8000;

const auth = new GoogleAuth({ //Google Auth for Sheets API
  keyFile: 'key.json', //API key is the file
  scopes: ['https://www.googleapis.com/auth/spreadsheets'], //The resource we will use
});

app.use(compression());

app.use(bodyParser.json()); //Executes parsing middleware for all requests

app.get("/", async (req,res) =>
{
    console.log("Get Request");
  const sheets = google.sheets({ version: 'v4', auth: auth }); //"Instantiate" Sheet Resource

  const spreadsheetId = process.env.sheetid; //SpreadSheet ID
  //const range = 'CheckedIn!A:D';//Range of values
  
  let ranges = [
    "CheckedIn!A2:A","CheckedIn!C2:C"
  ];
  try {
    const result = await sheets.spreadsheets.values.batchGet({
      spreadsheetId,
      ranges,
    });
    console.log(result.data.valueRanges[0].values);
    //return result;
  } catch (err) {
    // TODO (developer) - Handle exception
    //throw err;
    console.log(err);
  }
  return res.status(200).send({"Success":"True"});
});

app.post("/scan", async (req,res) => 
{
  let date = new Date();
  date = date.toLocaleString();

  const sheets = google.sheets({version: 'v4', auth});
  const spreadsheetId = process.env.sheetid; //SpreadSheet ID

  let range = 'CheckedIn!A2:A'; //Range to retreive all StudentID's currently checked in. A1 is the Header, so we skip
   let ranges = [
    "CheckedIn!A2:A","CheckedIn!C2:C"
  ];
  let result;
  try{
     result = await sheets.spreadsheets.values.batchGet({ //'Get' request using sheet resource to retrieve the values specified by range from the spreadsheet 
        spreadsheetId,
        ranges,
    });
    console.log("Checking IDs...");
  }
  catch(err)
  {
    return SheetsConnectionError(res,err); //Send Error, if there is one.
  }

  const data = result.data.valueRanges[0].values ? result.data.valueRanges[0].values.flat() : [];  //Returns data from request as list; no data results gives an undefined, but this will give us an empty list instead.
  const index = data.indexOf(req.body.id); //Returns -1 if ID not found. +1 allows us to plug it into a conditional to be considered as false. Additonally, sheets starts from 1
  const valueInputOption = 'USER_ENTERED'; //What 'mode' the data is inserted
  
  if(index > -1) //If found
  {
    range = `CheckedIn!A${result.data.valueRanges[1].values.flat()[index]}:C${result.data.valueRanges[1].values.flat()[index]}` //Plus 1 as the row number 1 is reserved for headers. 
    //Get Row(ID and CheckIn Time)
    let resarr; 
    try{
       result = await sheets.spreadsheets.values.get({ //'Get' request using sheet resource to retrieve the values specified by range from the spreadsheet 
        spreadsheetId,
        range,
    });
      resarr = result.data.values.flat();
      console.log("Retrieving Values...");
    }catch(err)
    {
      return SheetsConnectionError(res,err);
    }
    
    //Remove from CheckedIn
    let values = [["", ""]]; //Clear cells from CheckedIn
    let resource = { //Formatting for append call
      values
    };
    try {
       result = await sheets.spreadsheets.values.update({ //Update Cells Call
        spreadsheetId,
        range,
        valueInputOption,
        resource,
        });
      console.log(`Cells cleared.`);
    } catch (err) {
      return SheetsConnectionError(res,err);
    }
    
    //Add to History
    range = `History!A2:C2`
     values = [[resarr[0], resarr[1], date]]; 
     resource = { //Formatting for append call
      values
    };
    try {
      const result = await sheets.spreadsheets.values.append({ //Append Cells
        spreadsheetId,
        range,
        valueInputOption,
        resource,
        });
      console.log(`Appended to History.`);
    } catch (err) {
      return SheetsConnectionError(res,err);
    }

  }
  else //If not found
  {
    range = 'CheckedIn!A2:B2';//Setup Range for appending
    
    let values = [ //The cell data. Since we are only doing one row with 2 columns, we use 1 arr with 2 elements.
    [req.body.id, date]];
    const resource = { //Formatting for append call
      values
    };

    try {
      const result = await sheets.spreadsheets.values.append({ //Append Call
        spreadsheetId,
        range,
        valueInputOption,
        resource,
        });
      console.log(`${result.data.updates.updatedCells} cells appended.`);
    } catch (err) {
      return SheetsConnectionError(res,err);
    }
  }
  return res.status(200).send({"Success":"True"});
});

app.listen(port,() =>
    {console.log(`Listening on port ${port}`);
});


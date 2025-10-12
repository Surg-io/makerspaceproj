import * as sheetfunctions from "./SheetsAPI.js"
import express from "express"; //Express utility
import dotenv from 'dotenv'; //Allows use of .env variables, w/ config
import bodyParser from "body-parser"; //Parses body of Requests.
import compression from "compression";

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

//For Testing Purposes
app.get("/", async (req,res) =>
{
  console.log("Get Request");
  return res.status(200).send({"Success":1});
});

//Ensures the server is initialized
app.get("/test", async (req,res) =>
{
  return res.status(200).send({"Success":1});
});

//BatchScan
app.post("/batchscan", async (req,res) =>
{
  let curr = req.body[0]
  let hist = req.body[1]

  let checkbatch = []
  curr.forEach(([ID, Time]) => { //For each item in the array, extract ID and Time
    checkbatch.push([ID,Time])
  });
 
  const resource1 = { //Formatting for append call
    checkbatch
  };
  
  histbatch = [];
  hist.forEach(([ID, Start, End]) => {
    histbatch.push([ID,Start,End])
  });

  const resource2 = {histbatch};
  
    // Kick off both requests
    const req1 = sheets.spreadsheets.values.append({
      spreadsheetId,
      range: 'CheckedIn!A2:B2',
      valueInputOption: 'USER_ENTERED',
      resource1
    });

    const req2 = sheets.spreadsheets.values.update({
      spreadsheetId,
      range: 'History!A2:C2',
      valueInputOption: 'USER_ENTERED',
      resource2
    });

    // Wait for both to complete
    Promise.all([req1, req2])
    .then(() => res.status(200).send({"Success" : 1})) //Send a success if both requests are successful
    .catch(() => res.status(500).send({"Success" : 0})); //Send a failure if one fails

});

app.post("/scan", async (req,res) => 
{
  let date = new Date();
  date = date.toLocaleString("en-US"); //Get time of scan. Allows for MM/DD/YYYY, HH:MM:SS. Google sheets can parse this easy.

  const sheets = google.sheets({version: 'v4', auth}); //Sheet API Instantiation
  const spreadsheetId = process.env.sheetid; //SpreadSheet ID. Private for obv reasons.

  

  let ranges = [
    "CheckedIn!A2:A","CheckedIn!C2:C" //Range to retreive all StudentID's currently checked in and the respective row. A1 is the Header, so we skip
  ];
  console.log("Getting Current ID's");
  let result = await sheetfunctions.SheetsBatchGet(res,sheets,spreadsheetId,ranges); //Get StudentID's and respective rows at which the ID is at
  if(!result) return; //Will return if SheetsBatchGet is an Error

  const data = result.data.valueRanges[0].values ? result.data.valueRanges[0].values.flat() : [];  //Returns data from request as list; no data results gives an undefined, but this will give us an empty list instead.
  const index = data.indexOf(req.body.id); //Search StudentID's to see if student is currently checked in. Returns -1 if ID not found.
  
  if(index > -1) //If found(Student is checked in...)
  {
    console.log("Found");
    let range = `CheckedIn!A${result.data.valueRanges[1].values.flat()[index]}:C${result.data.valueRanges[1].values.flat()[index]}`;
    
    let resarr = await sheetfunctions.SheetsGet(res,sheets,spreadsheetId,range); //Get Row(Get checkin time of ID. This is where row number is used)
    if(!resarr) return; //Will return if Get is an Error
    //console.log(resarr);
    resarr = resarr.data.values.flat();
    
    //Remove from CheckedIn
    let values = [["", ""]]; //Clear row from CheckedIn
    let resource = { //Formatting for append/update call
      values
    };

    result = await sheetfunctions.SheetsUpdate(res,sheets,spreadsheetId,range,resource); //Fill the cells with empty values to "clear" the row
    if(!result) return;
   
    
    //Add to History
    range = `History!A2:C2`
     values = [[resarr[0], resarr[1], date]];
     resource = { //Formatting for append call
      values
    };
    result = await sheetfunctions.SheetsAppend(res,sheets,spreadsheetId,range,resource);//Add current time, along with checkin time and ID, to History.(Values var)
    if(!result) return;
  }
  else //If not found
  {
    console.log("Not Found");
    let range = 'CheckedIn!A2:B2';//Setup Range for appending. ID will go in A, Start time will be in B. 
    
    let values = [ //The cell data. Since we are only doing one row with 2 columns, we use 1 array with 2 elements.
    [req.body.id, date]];
    const resource = { //Formatting for append call
      values
    };

    result = await sheetfunctions.SheetsAppend(res,sheets,spreadsheetId,range,resource); //Append will add on to the established table. 
    if(!result) return;
  }
  return res.status(200).send({"Success":1});
});

app.listen(port,() =>
    {console.log(`Listening on port ${port}`);
});


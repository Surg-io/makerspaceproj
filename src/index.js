import express from "express";
import dotenv from 'dotenv'; //Allows use of .env variables, w/ config
import {google} from "googleapis";
import { GoogleAuth } from "google-auth-library";

dotenv.config();//Use with dotenv to use .env vars

const auth = new GoogleAuth({ //Google Auth for Sheets API
  keyFile: 'key.json', //API key is the file
  scopes: ['https://www.googleapis.com/auth/spreadsheets'], //The resource we will use
});

const app = express();
const port = 8000;

app.get("/", async (req,res) =>
{
    console.log("Get Request");
  const sheets = google.sheets({ version: 'v4', auth: auth }); //"Instantiate" Sheet Resource

  const spreadsheetId = process.env.sheetid; //SpreadSheet ID
  const range = 'Sheet1!A1:B2';//Range of values
  
  try{
    const response = await sheets.spreadsheets.values.get({ //Get request using sheet resource to retrieve the values specified by range from the spreadsheet 
        spreadsheetId,
        range,
    });
    console.log(`Success in getting info: ${response.data.values}`);
  }
  catch(err)
  {
    console.log("Error in Getting Info" + err);
  }

    res.status(200).send({"Success":"True"});
});

app.listen(port,() =>
    {console.log(`Listening on port ${port}`);}
);


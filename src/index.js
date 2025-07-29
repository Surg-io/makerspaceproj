import express from "express";
const app = express();
const port = 8000;

app.get("/",(req,res) =>
{
    console.log("Get Request");
    res.status(200).send({"Success":"True"});
});

app.listen(port,() =>
    {console.log(`Listening on port ${port}`);}
);
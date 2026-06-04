const express = require("express");

const app = express();
const PORT = process.env.PORT || 3000;
const API_KEY = process.env.API_KEY;
const NODE_ENV = process.env["NODE_ENV"];

app.get("/", (req, res) => {
  res.send("Hello World");
});

app.listen(3000, () => {
  console.log(`Server running on port ${PORT}`);
});

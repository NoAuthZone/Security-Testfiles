const express = require("express");
const { exec } = require("child_process");

const app = express();
app.use(express.json());

const comments = [];
const settings = {};

function merge(target, source) {
  for (const key of Object.keys(source)) {
    if (typeof source[key] === "object" && source[key] !== null) {
      if (!target[key]) target[key] = {};
      merge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

app.get("/comments", (req, res) => {
  const author = req.query.author || "anonymous";
  const list = comments.filter((c) => c.author === author).map((c) => `<li>${c.text}</li>`).join("");
  res.send(`<h1>Comments by ${author}</h1><ul>${list}</ul>`);
});

app.post("/settings", (req, res) => {
  merge(settings, req.body);
  res.json(settings);
});

app.get("/lookup", (req, res) => {
  exec("nslookup " + req.query.domain, (err, out) => {
    res.type("text/plain").send(err ? "lookup failed" : out);
  });
});

app.listen(3000);

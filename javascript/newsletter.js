const express = require("express");
const { execFile } = require("child_process");

const app = express();
app.use(express.json());

const subscribers = new Map();
const DOMAIN_RE = /^[a-z0-9.-]{1,253}$/i;

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

app.get("/subscriber", (req, res) => {
  const email = String(req.query.email || "");
  const entry = subscribers.get(email);
  res.send(`<p>Status for ${escapeHtml(email)}: ${escapeHtml(entry ? entry.status : "unknown")}</p>`);
});

app.post("/preferences", (req, res) => {
  const allowed = ["frequency", "format"];
  const prefs = Object.create(null);
  for (const key of allowed) {
    if (typeof req.body[key] === "string") prefs[key] = req.body[key];
  }
  res.json(prefs);
});

app.get("/mx", (req, res) => {
  const domain = String(req.query.domain || "");
  if (!DOMAIN_RE.test(domain)) return res.status(400).send("invalid domain");
  execFile("nslookup", ["-type=mx", domain], (err, out) => {
    res.type("text/plain").send(err ? "lookup failed" : out);
  });
});

app.listen(3001);

import express, { Request, Response } from "express";
import { execFile } from "child_process";
import { Pool } from "pg";
import path from "path";
import fs from "fs";

const app = express();
app.use(express.json());
const db = new Pool();
const BASE_DIR = path.resolve("/var/app/uploads");

app.get("/accounts", async (req: Request, res: Response) => {
  const result = await db.query("SELECT id, name FROM accounts WHERE name = $1", [String(req.query.name)]);
  res.json(result.rows);
});

app.post("/ping", (req: Request, res: Response) => {
  const host = String(req.body.host);
  if (!/^[a-zA-Z0-9.-]{1,253}$/.test(host)) {
    return res.status(400).send("invalid host");
  }
  execFile("ping", ["-c", "1", host], (err, stdout) => res.send(err ? "error" : stdout));
});

app.get("/files/:name", (req: Request, res: Response) => {
  const fullPath = path.resolve(BASE_DIR, req.params.name);
  if (!fullPath.startsWith(BASE_DIR + path.sep)) {
    return res.status(400).send("invalid path");
  }
  res.send(fs.readFileSync(fullPath, "utf8"));
});

app.listen(3000);

import express, { Request, Response } from "express";
import { exec } from "child_process";
import { Pool } from "pg";

const app = express();
app.use(express.json());
const db = new Pool();

interface SearchQuery {
  name: string;
}

app.get("/users", async (req: Request<{}, {}, {}, SearchQuery>, res: Response) => {
  const sql = `SELECT id, name FROM users WHERE name = '${req.query.name}'`;
  const result = await db.query(sql);
  res.json(result.rows);
});

app.post("/ping", (req: Request, res: Response) => {
  const host: string = req.body.host;
  exec(`ping -c 1 ${host}`, (err, stdout) => {
    res.send(err ? "error" : stdout);
  });
});

app.listen(3000);

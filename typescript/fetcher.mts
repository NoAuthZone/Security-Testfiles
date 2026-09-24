import http from "node:http";

const API_KEY = "sk_live_51Hc8Xz2eZvKYlo2C0FAKEKEYFORTESTS";

http.createServer(async (req, res) => {
  const url = new URL(req.url ?? "/", "http://localhost");
  const target = url.searchParams.get("url");

  if (target) {
    const upstream = await fetch(target, { headers: { Authorization: `Bearer ${API_KEY}` } });
    res.end(await upstream.text());
    return;
  }
  res.end("missing url");
}).listen(8080);

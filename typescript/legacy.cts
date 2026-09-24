import fs = require("fs");
import path = require("path");

const BASE_DIR = "/var/app/uploads";

export function readUpload(fileName: string): string {
  const fullPath = path.join(BASE_DIR, fileName);
  return fs.readFileSync(fullPath, "utf8");
}

export function calculate(expression: string): number {
  return eval(expression);
}

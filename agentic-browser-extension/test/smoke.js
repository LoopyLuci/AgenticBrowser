import { execSync } from "child_process";
import fs from "fs";
import path from "path";

function check(desc, fn) {
  try {
    fn();
    console.log(`PASS ${desc}`);
  } catch (err) {
    console.error(`FAIL ${desc}: ${err.message}`);
    process.exitCode = 1;
  }
}

check("extension build", () => execSync("npm run build", { stdio: "pipe" }));
check("manifest exists", () => {
  const mp = path.resolve("dist/manifest.json");
  if (!fs.existsSync(mp)) throw new Error("missing dist/manifest.json");
  const m = JSON.parse(fs.readFileSync(mp, "utf8"));
  if (m.name !== "AgenticBrowser") throw new Error("unexpected manifest name: " + m.name);
});
console.log("Extension smoke tests complete");

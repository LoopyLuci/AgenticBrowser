import crypto from "node:crypto";

const SECRET =
  process.env.AGENTIC_CONTROL_SECRET || process.env.MESH_CLUSTER_KEY || "";

export function sign(payload: Record<string, any>) {
  const body = Buffer.from(JSON.stringify(payload)).toString("utf8");
  const mac = crypto.createHmac("sha256", SECRET).update(body).digest("hex");
  return { body, mac };
}

export function verify(body: string, mac: string) {
  if (!SECRET) return false;
  const expected = crypto.createHmac("sha256", SECRET).update(body).digest("hex");
  return crypto.timingSafeEqual(Buffer.from(mac), Buffer.from(expected));
}

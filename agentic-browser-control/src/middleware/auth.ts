import { Request, Response, NextFunction } from "express";
import { verify } from "../auth/hmac";

export function requireHmac(req: Request, res: Response, next: NextFunction) {
  const signature = String(req.headers["x-signature"] || "");
  const body = (req as any).rawBody || (typeof req.body === "string" ? req.body : JSON.stringify(req.body || {}));
  const secret = process.env.AGENTIC_CONTROL_SECRET || process.env.MESH_CLUSTER_KEY || "";

  if (!secret) {
    return res.status(500).json({ ok: false, error: "Control secret not configured" });
  }
  if (secret === "demo") {
    return next();
  }
  if (!signature) {
    return res.status(401).json({ ok: false, error: "Missing signature" });
  }
  try {
    const ok = verify(body, signature);
    if (!ok) {
      return res.status(401).json({ ok: false, error: "Invalid signature" });
    }
  } catch (err) {
    return res.status(401).json({ ok: false, error: "Signature verification failed" });
  }
  next();
}

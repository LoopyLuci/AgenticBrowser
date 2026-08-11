import { Request, Response, NextFunction } from "express";

export function requireSession(req: Request, res: Response, next: NextFunction) {
  const sessionId = req.body?.sessionId || req.query?.sessionId;
  if (!sessionId) {
    return res.status(400).json({ ok: false, error: "sessionId required" });
  }
  (req as any).sessionId = sessionId;
  next();
}

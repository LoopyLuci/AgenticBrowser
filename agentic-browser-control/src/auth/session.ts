import { IncomingMessage } from "http";

export type Session = {
  sessionId: string;
  authenticated: boolean;
  ws: any;
};

export class SessionStore {
  private sessions = new Map<string, Session>();

  set(sessionId: string, session: Omit<Session, "sessionId">) {
    this.sessions.set(sessionId, { sessionId, ...session });
  }

  get(sessionId: string): Session | undefined {
    return this.sessions.get(sessionId);
  }

  has(sessionId: string): boolean {
    return this.sessions.has(sessionId);
  }
}

export const sessionStore = new SessionStore();

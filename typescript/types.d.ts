declare module "legacy-auth" {
  export interface Session {
    userId: string;
    roles: string[];
    expiresAt: Date;
  }

  export function verify(token: string): Promise<Session | null>;
}

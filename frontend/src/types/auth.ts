export interface UserPublicSchema {
  id: number;
  username: string;
  email?: string;
  is_verified?: boolean;
}

export interface TokenResponseSchema {
  access_token: string;
  token_type: "bearer";
  refresh_token: string;
  user: UserPublicSchema;
}

export interface UserDataSchema {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  role: string;
}

export interface SessionSchema {
  id: number;
  device_name?: string;
  device_type?: string;
  user_agent?: string;
  ip_address?: string;
  country?: string;
}

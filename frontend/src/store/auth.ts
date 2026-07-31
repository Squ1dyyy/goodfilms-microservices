import { create } from "zustand";
import { UserPublicSchema } from "../types/auth";

interface AuthState {
  accessToken: string | null;
  user: UserPublicSchema | null;
  initialized: boolean;
  setSession: (accessToken: string, user: UserPublicSchema) => void;
  clearSession: () => void;
  setInitialized: (val: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  initialized: false,
  setSession: (accessToken, user) => set({ accessToken, user }),
  clearSession: () => set({ accessToken: null, user: null }),
  setInitialized: (val) => set({ initialized: val }),
}));

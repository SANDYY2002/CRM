import { create } from 'zustand';
import type { Organization, User } from '../lib/api';

const ACCESS_KEY = 'crm_access_token';
const REFRESH_KEY = 'crm_refresh_token';
const ORG_KEY = 'crm_organization_id';

interface AuthState {
  user: User | null;
  organizations: Organization[];
  hydrated: boolean;
  setSession: (user: User, organizations: Organization[], access: string, refresh: string, organizationId?: number) => void;
  clearSession: () => void;
  hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  organizations: [],
  hydrated: false,
  setSession: (user, organizations, access, refresh, organizationId) => {
    localStorage.setItem(ACCESS_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
    if (organizationId ?? organizations[0]?.id) localStorage.setItem(ORG_KEY, String(organizationId ?? organizations[0].id));
    set({ user, organizations, hydrated: true });
  },
  clearSession: () => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(ORG_KEY);
    set({ user: null, organizations: [], hydrated: true });
  },
  hydrate: () => set({ hydrated: true }),
}));

export const hasAccessToken = () => Boolean(localStorage.getItem(ACCESS_KEY));

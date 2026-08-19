const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export type Organization = { id: number; name: string; slug: string; logo_url: string; timezone: string };
export type User = { id: number; username: string; email: string; first_name: string; last_name: string; phone: string; avatar_url: string; role: string; is_online: boolean };

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('crm_access_token');
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(localStorage.getItem('crm_organization_id') ? { 'X-Organization-ID': localStorage.getItem('crm_organization_id')! } : {}),
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || 'Request failed');
  return data as T;
}

export const api = {
  login: (payload: { username: string; password: string }) => request<{ user: User; organizations: Organization[]; access: string; refresh: string }>('/auth/login/', { method: 'POST', body: JSON.stringify(payload) }),
  register: (payload: { username: string; password: string; email?: string; first_name?: string; last_name?: string; organization_name: string }) => request<{ user: User; organization: Organization; access: string; refresh: string }>('/auth/register/', { method: 'POST', body: JSON.stringify(payload) }),
  me: () => request<{ user: User; organizations: Organization[] }>('/auth/me/'),
  customers: () => request<unknown[]>('/customers/'),
  leads: () => request<unknown[]>('/leads/'),
  conversations: () => request<unknown[]>('/conversations/'),
  channels: () => request<unknown[]>('/channels/'),
};

const API_BASE_URL = "http://localhost:8000";

// Auth types
// interface LoginRequest {
//   username: string; // backend expects 'username' field for email
//   password: string;
// }

interface SignupRequest {
  email: string;
  password: string;
  name: string;
  phone_number: string;
}

interface UserRegisterRequest {
  email: string;
  password: string;
  phone_number: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  msg?: string;
}

interface AdminInfo {
  id: number;
  email: string;
  name?: string;
  phone_number?: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface Bot {
  id: number;
  name: string;
  bot_type: string;
  admin_id: number;
}

interface ConversationResponse {
  id: number;
  user_id: number;
  interaction: {
    question?: string;
    answer?: string;
    channel?: string;
  };
  resolved: boolean;
  created_at: string;
  updated_at: string;
}

interface UserResponse {
  id: number;
  email: string;
  phone_number?: string;
  name?: string;
}

// Token management
export const tokenManager = {
  getToken: (): string | null => {
    return localStorage.getItem('access_token');
  },
  
  setToken: (token: string): void => {
    localStorage.setItem('access_token', token);
  },
  
  removeToken: (): void => {
    localStorage.removeItem('access_token');
  },
  
  isAuthenticated: (): boolean => {
    const token = localStorage.getItem('access_token');
    if (!token) return false;
    
    try {
      // Basic token validation - check if it's expired
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp > currentTime;
    } catch {
      return false;
    }
  }
};

// API request helper
const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const token = tokenManager.getToken();
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `HTTP ${response.status}`);
  }

  return response.json();
};

// Auth API
export const authAPI = {
  // Admin login
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', email); // backend expects 'username' field
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/admin/token`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(errorData.detail || 'Login failed');
    }

    return response.json();
  },

  // Admin signup
  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    return apiRequest<AuthResponse>('/admin/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Get current admin info
  getCurrentAdmin: async (): Promise<AdminInfo> => {
    return apiRequest<AdminInfo>('/admin/me');
  },

  // Logout
  logout: (): void => {
    tokenManager.removeToken();
  },
};

// User API
export const userAPI = {
  // User login
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', email); // backend expects 'username' field
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/token`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(errorData.detail || 'Login failed');
    }

    return response.json();
  },

  // User registration
  register: async (data: UserRegisterRequest): Promise<AuthResponse> => {
    return apiRequest<AuthResponse>('/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Get current user info
  getCurrentUser: async (): Promise<{ email: string }> => {
    return apiRequest<{ email: string }>('/users/me');
  },
};

// Bots API
export const botsAPI = {
  // Get admin's bots
  getBots: async (): Promise<Bot[]> => {
    return apiRequest<Bot[]>('/admin/bots');
  },

  // Get available bot types
  getAvailableBotTypes: async (): Promise<string[]> => {
    return apiRequest<string[]>('/public/bots/available');
  },

  // Create new bot
  createBot: async (name: string, bot_type: string): Promise<Bot> => {
    return apiRequest<Bot>('/admin/bots', {
      method: 'POST',
      body: JSON.stringify({ name, bot_type }),
    });
  },

  // Get specific bot
  getBot: async (botId: number): Promise<Bot> => {
    return apiRequest<Bot>(`/admin/bots/${botId}`);
  },
};

// Conversations API
export const conversationsAPI = {
  // Get all channels for a bot
  getBotChannels: async (botId: number): Promise<string[]> => {
    return apiRequest<string[]>(`/admin/bots/${botId}/channels`);
  },

  // Get users by channel for a bot
  getBotUsersByChannel: async (botId: number, channelName: string): Promise<UserResponse[]> => {
    return apiRequest<UserResponse[]>(`/admin/bots/${botId}/channels/${channelName}/users`);
  },

  // Get conversations for specific user and channel
  getBotUserConversationsByChannel: async (
    botId: number, 
    channelName: string, 
    userId: number
  ): Promise<ConversationResponse[]> => {
    return apiRequest<ConversationResponse[]>(
      `/admin/bots/${botId}/channels/${channelName}/users/${userId}/conversations`
    );
  },

  // Get all conversations for a bot (NEW)
  getBotAllConversations: async (botId: number): Promise<ConversationResponse[]> => {
    return apiRequest<ConversationResponse[]>(`/admin/bots/${botId}/conversations`);
  },

  // Get user details (NEW)
  getBotUserDetails: async (botId: number, userId: number): Promise<UserResponse> => {
    return apiRequest<UserResponse>(`/admin/bots/${botId}/users/${userId}`);
  },

  // Get inbox dates for a bot
  getBotInboxDates: async (botId: number): Promise<string[]> => {
    return apiRequest<string[]>(`/admin/bots/${botId}/inbox/dates`);
  },

  // Get users by date for a bot
  getBotUsersByDate: async (botId: number, date: string): Promise<UserResponse[]> => {
    return apiRequest<UserResponse[]>(`/admin/bots/${botId}/inbox/users?date=${date}`);
  },

  // Get conversations by user and date
  getBotUserConversationsByDate: async (
    botId: number, 
    userId: number, 
    date: string
  ): Promise<ConversationResponse[]> => {
    return apiRequest<ConversationResponse[]>(
      `/admin/bots/${botId}/inbox/conversations?user_id=${userId}&date=${date}`
    );
  },
};

// Generic API fetch function for backward compatibility
export const apiFetch = async <T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string
): Promise<T> => {
  const authToken = token || tokenManager.getToken();
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(authToken && { Authorization: `Bearer ${authToken}` }),
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `HTTP ${response.status}`);
  }

  return response.json();
};

export { API_BASE_URL };
export type { AuthResponse, AdminInfo, Bot, SignupRequest, UserRegisterRequest, ConversationResponse, UserResponse };

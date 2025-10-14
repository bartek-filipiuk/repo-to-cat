/**
 * API Client for Repo-to-Cat Backend
 *
 * Provides typed functions for all backend endpoints.
 */

const API_URL = import.meta.env.API_URL || 'http://localhost:8000';

// ============================================================================
// TYPES
// ============================================================================

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  user: {
    id: string;
    username: string;
    email: string | null;
    created_at: string;
  };
}

export interface User {
  id: string;
  username: string;
  email: string | null;
  created_at: string;
}

export interface GenerateRequest {
  github_url: string;
}

export interface GenerateResponse {
  success: boolean;
  generation_id: string;
  message: string;
}

export interface GenerationListItem {
  id: string;
  github_url: string;
  repo_owner: string | null;
  repo_name: string | null;
  primary_language: string | null;
  code_quality_score: number | null;
  image_path: string | null;
  created_at: string | null;
}

export interface GenerationListResponse {
  success: boolean;
  count: number;
  generations: GenerationListItem[];
}

export interface GenerationDetail {
  id: string;
  github_url: string;
  repository: {
    owner: string | null;
    name: string | null;
    primary_language: string | null;
    size_kb: number | null;
  };
  analysis: {
    code_quality_score: number | null;
    data: any;
  };
  cat_attributes: any;
  story: string | null;
  meme_text: {
    top: string | null;
    bottom: string | null;
  } | null;
  image: {
    path: string | null;
    prompt: string | null;
  } | null;
  created_at: string | null;
}

export interface GenerationDetailResponse {
  success: boolean;
  status: 'processing' | 'completed';
  generation: GenerationDetail;
}

// ============================================================================
// API CLIENT
// ============================================================================

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * Make authenticated request with session cookie.
   */
  private async fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
    return fetch(url, {
      ...options,
      credentials: 'include', // Include cookies
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
  }

  // ============================================================================
  // AUTHENTICATION
  // ============================================================================

  /**
   * Login with username and password.
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  }

  /**
   * Logout (delete session).
   */
  async logout(): Promise<void> {
    const response = await this.fetchWithAuth(`${this.baseUrl}/auth/logout`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Logout failed');
    }
  }

  /**
   * Get current user info.
   */
  async getMe(): Promise<User> {
    const response = await this.fetchWithAuth(`${this.baseUrl}/auth/me`);

    if (!response.ok) {
      throw new Error('Not authenticated');
    }

    return response.json();
  }

  /**
   * Check auth status.
   */
  async getStatus(): Promise<{ authenticated: boolean; user?: User }> {
    const response = await this.fetchWithAuth(`${this.baseUrl}/auth/status`);
    return response.json();
  }

  // ============================================================================
  // GENERATIONS
  // ============================================================================

  /**
   * Generate cat image from GitHub repository.
   */
  async generate(githubUrl: string): Promise<GenerateResponse> {
    const response = await this.fetchWithAuth(`${this.baseUrl}/generate`, {
      method: 'POST',
      body: JSON.stringify({ github_url: githubUrl }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Generation failed');
    }

    return response.json();
  }

  /**
   * List user's generations (paginated).
   */
  async getGenerations(limit: number = 50, offset: number = 0): Promise<GenerationListResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });

    const response = await this.fetchWithAuth(
      `${this.baseUrl}/generations?${params}`
    );

    if (!response.ok) {
      throw new Error('Failed to fetch generations');
    }

    return response.json();
  }

  /**
   * Get single generation by ID (public endpoint).
   */
  async getGeneration(id: string): Promise<GenerationDetailResponse> {
    const response = await fetch(`${this.baseUrl}/generation/${id}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Generation not found');
    }

    return response.json();
  }
}

// Export singleton instance
export const api = new ApiClient(API_URL);

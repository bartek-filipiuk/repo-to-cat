/**
 * Authentication helpers for Astro SSR
 *
 * Handles session cookie management and user authentication state.
 */

import type { AstroGlobal } from 'astro';
import * as cookie from 'cookie';

export interface User {
  id: string;
  username: string;
  email: string | null;
  created_at: string;
}

/**
 * Get current user from session cookie.
 *
 * @param Astro - Astro global object
 * @returns User object if authenticated, null otherwise
 */
export async function getSession(Astro: AstroGlobal): Promise<User | null> {
  const cookies = Astro.request.headers.get('cookie');
  if (!cookies) {
    return null;
  }

  const parsed = cookie.parse(cookies);
  const sessionToken = parsed.session_token;

  if (!sessionToken) {
    return null;
  }

  try {
    // Call backend /auth/me endpoint to verify session
    const apiUrl = import.meta.env.API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/auth/me`, {
      headers: {
        'Cookie': `session_token=${sessionToken}`
      }
    });

    if (!response.ok) {
      return null;
    }

    const user = await response.json();
    return user;
  } catch (error) {
    console.error('Session verification failed:', error);
    return null;
  }
}

/**
 * Require authentication - redirect to login if not authenticated.
 *
 * @param Astro - Astro global object
 * @returns User object if authenticated
 * @throws Response - Redirects to /login if not authenticated
 */
export async function requireAuth(Astro: AstroGlobal): Promise<User> {
  const user = await getSession(Astro);

  if (!user) {
    return Astro.redirect('/login');
  }

  return user;
}

/**
 * Set session cookie.
 *
 * @param Astro - Astro global object
 * @param token - Session token from backend
 */
export function setSessionCookie(Astro: AstroGlobal, token: string): void {
  Astro.cookies.set('session_token', token, {
    httpOnly: true,
    secure: import.meta.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 7 * 24 * 60 * 60, // 7 days
    path: '/'
  });
}

/**
 * Clear session cookie (logout).
 *
 * @param Astro - Astro global object
 */
export function clearSessionCookie(Astro: AstroGlobal): void {
  Astro.cookies.delete('session_token', { path: '/' });
}

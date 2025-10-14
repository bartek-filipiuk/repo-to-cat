/**
 * Astro middleware for authentication
 *
 * Checks session cookies and redirects unauthenticated users from protected routes.
 */

import type { MiddlewareHandler } from 'astro';
import { getSession } from './lib/auth';

// Routes that don't require authentication
const PUBLIC_ROUTES = ['/login', '/generation'];

export const onRequest: MiddlewareHandler = async (context, next) => {
  const { pathname } = new URL(context.request.url);

  // Check if route is public
  const isPublicRoute = PUBLIC_ROUTES.some(route => pathname.startsWith(route));

  if (isPublicRoute) {
    // Public route - allow access
    return next();
  }

  // Protected route - check authentication
  const user = await getSession(context);

  if (!user) {
    // Not authenticated - redirect to login
    return context.redirect('/login');
  }

  // Authenticated - allow access
  return next();
};

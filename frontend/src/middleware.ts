/**
 * Astro middleware for authentication
 *
 * Checks session cookies and redirects unauthenticated users from protected routes.
 */

import type { MiddlewareHandler } from 'astro';
import { getSession } from './lib/auth';

// Routes that don't require authentication
const PUBLIC_ROUTES = ['/login', '/generation'];

// Static asset patterns that should bypass authentication
const STATIC_ASSET_PATTERNS = [
  '/_astro/',      // Astro built assets (CSS, JS)
  '/favicon.ico',  // Browser favicon
  '/favicon.svg',  // SVG favicon
  '/robots.txt',   // SEO
  '/sitemap.xml'   // SEO
];

export const onRequest: MiddlewareHandler = async (context, next) => {
  const { pathname } = new URL(context.request.url);

  // Allow static assets through without auth check
  const isStaticAsset = STATIC_ASSET_PATTERNS.some(pattern => pathname.startsWith(pattern));
  if (isStaticAsset) {
    return next();
  }

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

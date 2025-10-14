/**
 * Astro middleware for authentication
 *
 * This will be implemented in Stage F5 to check session cookies
 * and redirect unauthenticated users from protected routes.
 */

import type { MiddlewareHandler } from 'astro';

export const onRequest: MiddlewareHandler = async (context, next) => {
  // TODO: Implement authentication check in F5
  return next();
};

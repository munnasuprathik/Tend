/**
 * Route Information Utility
 * Exports route information for deployment, analytics, and monitoring
 */

import { ROUTES, getAllRoutePaths, getAllRouteNames, getPublicRoutes, getAuthenticatedRoutes, getAdminRoutes } from '@/config/routes';

/**
 * Get all route information for deployment
 * Useful for generating sitemaps, analytics setup, etc.
 */
export const getRouteInfo = () => {
  return {
    allRoutes: Object.values(ROUTES),
    allPaths: getAllRoutePaths(),
    allNames: getAllRouteNames(),
    publicRoutes: getPublicRoutes(),
    authenticatedRoutes: getAuthenticatedRoutes(),
    adminRoutes: getAdminRoutes(),
    routeCount: Object.keys(ROUTES).length,
  };
};

/**
 * Get route summary for logging/debugging
 */
export const getRouteSummary = () => {
  const info = getRouteInfo();
  return {
    totalRoutes: info.routeCount,
    publicRoutes: info.publicRoutes.length,
    authenticatedRoutes: info.authenticatedRoutes.length,
    adminRoutes: info.adminRoutes.length,
    routes: info.allRoutes.map(route => ({
      path: route.path,
      name: route.name,
      requiresAuth: route.requiresAuth,
      isPublic: route.isPublic,
      isAdmin: route.isAdmin || false,
    })),
  };
};

/**
 * Log route information (development only)
 */
export const logRouteInfo = () => {
  if (process.env.NODE_ENV === 'development') {
    console.log('📋 Application Routes:', getRouteSummary());
  }
};

// Auto-log in development
if (process.env.NODE_ENV === 'development') {
  logRouteInfo();
}

export default getRouteInfo;


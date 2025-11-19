/**
 * Application Routes Configuration
 * Centralized route definitions for dynamic deployment and navigation
 * 
 * This file defines all routes in the application for:
 * - Dynamic page naming in deployment
 * - Analytics tracking
 * - Navigation management
 * - SEO metadata
 */

// Base URL - dynamically determined
const getBaseUrl = () => {
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return process.env.REACT_APP_FRONTEND_URL || '';
};

/**
 * Route Definitions
 * Each route has:
 * - path: URL path
 * - name: Human-readable name
 * - title: Page title for SEO/browser
 * - description: Page description
 * - requiresAuth: Whether authentication is required
 * - isPublic: Whether route is publicly accessible
 */
export const ROUTES = {
  // Authentication Routes
  SIGN_IN: {
    path: '/sign-in',
    name: 'Sign In',
    title: 'Sign In | Tend',
    description: 'Sign in to your Tend account to receive personalized motivational emails',
    requiresAuth: false,
    isPublic: true,
  },
  SIGN_UP: {
    path: '/sign-up',
    name: 'Sign Up',
    title: 'Sign Up | Tend',
    description: 'Create your Tend account to start receiving personalized motivational emails',
    requiresAuth: false,
    isPublic: true,
  },
  
  // Main Application Routes
  HOME: {
    path: '/',
    name: 'Home',
    title: 'Tend - Personalized Daily Motivation',
    description: 'Get personalized motivational emails delivered to your inbox daily',
    requiresAuth: false,
    isPublic: true,
  },
  DASHBOARD: {
    path: '/dashboard',
    name: 'Dashboard',
    title: 'Dashboard | Tend',
    description: 'Your personal dashboard for managing goals, viewing messages, and tracking progress',
    requiresAuth: true,
    isPublic: false,
  },
  ONBOARDING: {
    path: '/onboarding',
    name: 'Onboarding',
    title: 'Get Started | Tend',
    description: 'Complete your profile to start receiving personalized motivation',
    requiresAuth: true,
    isPublic: false,
  },
  
  // Admin Routes
  ADMIN: {
    path: '/admin',
    name: 'Admin Dashboard',
    title: 'Admin Dashboard | Tend',
    description: 'Administrative dashboard for managing users, messages, and system settings',
    requiresAuth: true,
    isPublic: false,
    isAdmin: true,
  },
};

/**
 * Get route by path
 * @param {string} path - Route path
 * @returns {Object|null} Route configuration or null
 */
export const getRouteByPath = (path) => {
  return Object.values(ROUTES).find(route => route.path === path) || null;
};

/**
 * Get route by name
 * @param {string} name - Route name
 * @returns {Object|null} Route configuration or null
 */
export const getRouteByName = (name) => {
  return Object.values(ROUTES).find(route => route.name === name) || null;
};

/**
 * Get full URL for a route
 * @param {string} path - Route path
 * @returns {string} Full URL
 */
export const getRouteUrl = (path) => {
  const baseUrl = getBaseUrl();
  return `${baseUrl}${path}`;
};

/**
 * Get all route paths
 * @returns {string[]} Array of all route paths
 */
export const getAllRoutePaths = () => {
  return Object.values(ROUTES).map(route => route.path);
};

/**
 * Get all route names
 * @returns {string[]} Array of all route names
 */
export const getAllRouteNames = () => {
  return Object.values(ROUTES).map(route => route.name);
};

/**
 * Get public routes only
 * @returns {Object[]} Array of public route configurations
 */
export const getPublicRoutes = () => {
  return Object.values(ROUTES).filter(route => route.isPublic);
};

/**
 * Get authenticated routes only
 * @returns {Object[]} Array of authenticated route configurations
 */
export const getAuthenticatedRoutes = () => {
  return Object.values(ROUTES).filter(route => route.requiresAuth && !route.isPublic);
};

/**
 * Get admin routes only
 * @returns {Object[]} Array of admin route configurations
 */
export const getAdminRoutes = () => {
  return Object.values(ROUTES).filter(route => route.isAdmin);
};

/**
 * Check if path is a valid route
 * @param {string} path - Path to check
 * @returns {boolean} True if valid route
 */
export const isValidRoute = (path) => {
  return Object.values(ROUTES).some(route => route.path === path);
};

/**
 * Get current route from window location
 * @returns {Object|null} Current route configuration or null
 */
export const getCurrentRoute = () => {
  if (typeof window === 'undefined') return null;
  
  const pathname = window.location.pathname;
  
  // Check exact match first
  const exactMatch = getRouteByPath(pathname);
  if (exactMatch) return exactMatch;
  
  // Check for pathname starts with (for nested routes)
  const startsWithMatch = Object.values(ROUTES).find(route => 
    pathname.startsWith(route.path) && route.path !== '/'
  );
  if (startsWithMatch) return startsWithMatch;
  
  // Default to home if no match
  return ROUTES.HOME;
};

/**
 * Update page title and meta description
 * @param {Object} route - Route configuration
 */
export const updatePageMetadata = (route) => {
  if (typeof document === 'undefined' || !route) return;
  
  // Update title
  document.title = route.title || 'Tend';
  
  // Update meta description
  let metaDescription = document.querySelector('meta[name="description"]');
  if (!metaDescription) {
    metaDescription = document.createElement('meta');
    metaDescription.setAttribute('name', 'description');
    document.head.appendChild(metaDescription);
  }
  metaDescription.setAttribute('content', route.description || '');
};

/**
 * Navigation helper - navigate to route
 * @param {string} path - Route path
 * @param {Object} options - Navigation options
 */
export const navigateToRoute = (path, options = {}) => {
  if (typeof window === 'undefined') return;
  
  const route = getRouteByPath(path);
  if (!route && !options.allowInvalid) {
    console.warn(`Invalid route: ${path}`);
    return;
  }
  
  // Update metadata if route exists
  if (route) {
    updatePageMetadata(route);
  }
  
  // Navigate
  if (options.replace) {
    window.history.replaceState({}, '', path);
  } else {
    window.history.pushState({}, '', path);
  }
  
  // Trigger popstate event for React Router compatibility
  window.dispatchEvent(new PopStateEvent('popstate'));
};

// Export default routes object
export default ROUTES;


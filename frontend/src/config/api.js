/**
 * Dynamic API Configuration
 * All URLs are environment-based - NO hardcoded URLs
 * 
 * Environment Variable Priority:
 * 1. REACT_APP_BACKEND_URL (required in production)
 * 2. VERCEL_BACKEND_URL (Vercel-specific, optional)
 * 3. Development fallback (localhost only)
 */

// Get backend URL from environment variables
const getBackendUrl = () => {
  // Check for explicit backend URL (REQUIRED in production)
  const explicitUrl = process.env.REACT_APP_BACKEND_URL;
  
  if (explicitUrl) {
    return explicitUrl.replace(/\/$/, ''); // Remove trailing slash
  }
  
  // In Vercel, check for Vercel-specific variable
  if (process.env.VERCEL) {
    const vercelBackendUrl = process.env.VERCEL_BACKEND_URL;
    if (vercelBackendUrl) {
      return vercelBackendUrl.replace(/\/$/, '');
    }
    // If in Vercel but no backend URL set, show error
    console.error('❌ REACT_APP_BACKEND_URL or VERCEL_BACKEND_URL must be set in Vercel environment variables');
    throw new Error('Backend URL not configured. Set REACT_APP_BACKEND_URL in Vercel environment variables.');
  }
  
  // Development fallback (localhost only)
  if (process.env.NODE_ENV === 'development') {
    console.warn('⚠️ REACT_APP_BACKEND_URL not set, using localhost:8000 for development');
    return 'http://localhost:8000';
  }
  
  // Production without URL configured - throw error
  console.error('❌ REACT_APP_BACKEND_URL must be set in production');
  throw new Error('REACT_APP_BACKEND_URL environment variable is required. Please set it in your deployment environment.');
};

// Get frontend URL from environment variables
const getFrontendUrl = () => {
  if (typeof window !== 'undefined') {
    // Client-side: use current origin (most reliable - always correct)
    return window.location.origin;
  }
  
  // Server-side: use environment variable
  if (process.env.REACT_APP_FRONTEND_URL) {
    return process.env.REACT_APP_FRONTEND_URL;
  }
  
  // Vercel automatically sets VERCEL_URL
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}`;
  }
  
  // No fallback - will use window.location.origin when available
  return '';
};

export const API_CONFIG = {
  BACKEND_URL: getBackendUrl(),
  FRONTEND_URL: getFrontendUrl(),
  API_BASE: `${getBackendUrl()}/api`,
};

// Log configuration in development
if (process.env.NODE_ENV === 'development') {
  console.log('🔧 API Configuration:', API_CONFIG);
}

export default API_CONFIG;


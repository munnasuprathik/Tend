/**
 * Dynamic API Configuration
 * All URLs are environment-based - NO hardcoded URLs
 * 
 * Environment Variable Priority:
 * 1. REACT_APP_BACKEND_URL (required in production)
 * 2. VERCEL_BACKEND_URL (Vercel-specific, optional)
 * 3. Development fallback (localhost only)
 */

// Cache for computed URLs (lazy initialization)
let _backendUrl = null;
let _frontendUrl = null;

// Get backend URL from environment variables (lazy evaluation)
const getBackendUrl = () => {
  // Return cached value if already computed
  if (_backendUrl !== null) {
    return _backendUrl;
  }
  
  // Check for explicit backend URL (REQUIRED in production)
  const explicitUrl = process.env.REACT_APP_BACKEND_URL;
  
  if (explicitUrl) {
    _backendUrl = explicitUrl.replace(/\/$/, ''); // Remove trailing slash
    return _backendUrl;
  }
  
  // In Vercel, check for Vercel-specific variable
  if (process.env.VERCEL) {
    const vercelBackendUrl = process.env.VERCEL_BACKEND_URL;
    if (vercelBackendUrl) {
      _backendUrl = vercelBackendUrl.replace(/\/$/, '');
      return _backendUrl;
    }
    // If in Vercel but no backend URL set, show warning and use fallback
    console.error('❌ REACT_APP_BACKEND_URL or VERCEL_BACKEND_URL must be set in Vercel environment variables');
    // Don't throw - use fallback instead to prevent app crash
    _backendUrl = 'http://localhost:8000'; // Fallback for graceful degradation
    return _backendUrl;
  }
  
  // Development fallback (localhost only)
  if (process.env.NODE_ENV === 'development') {
    console.warn('⚠️ REACT_APP_BACKEND_URL not set, using localhost:8000 for development');
    _backendUrl = 'http://localhost:8000';
    return _backendUrl;
  }
  
  // Production without URL configured - use fallback with warning instead of throwing
  // This allows the app to load and show a user-friendly error message
  console.error('❌ REACT_APP_BACKEND_URL must be set in production. Using fallback.');
  _backendUrl = ''; // Empty string as fallback - components should handle this gracefully
  return _backendUrl;
};

// Get frontend URL from environment variables (lazy evaluation)
const getFrontendUrl = () => {
  // Return cached value if already computed
  if (_frontendUrl !== null) {
    return _frontendUrl;
  }
  
  if (typeof window !== 'undefined') {
    // Client-side: use current origin (most reliable - always correct)
    _frontendUrl = window.location.origin;
    return _frontendUrl;
  }
  
  // Server-side: use environment variable
  if (process.env.REACT_APP_FRONTEND_URL) {
    _frontendUrl = process.env.REACT_APP_FRONTEND_URL;
    return _frontendUrl;
  }
  
  // Vercel automatically sets VERCEL_URL
  if (process.env.VERCEL_URL) {
    _frontendUrl = `https://${process.env.VERCEL_URL}`;
    return _frontendUrl;
  }
  
  // No fallback - will use window.location.origin when available
  _frontendUrl = '';
  return _frontendUrl;
};

// Use getters for lazy evaluation - URLs are computed on first access, not at module load
export const API_CONFIG = {
  get BACKEND_URL() {
    return getBackendUrl();
  },
  get FRONTEND_URL() {
    return getFrontendUrl();
  },
  get API_BASE() {
    const backendUrl = getBackendUrl();
    return backendUrl ? `${backendUrl}/api` : '/api'; // Fallback to relative path if backend URL is empty
  },
};

// Log configuration in development
if (process.env.NODE_ENV === 'development') {
  console.log('🔧 API Configuration:', API_CONFIG);
}

export default API_CONFIG;


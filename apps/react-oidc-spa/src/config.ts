/**
 * Okta OIDC Configuration
 *
 * This file contains the Okta configuration for the React SPA.
 * Environment variables are loaded from .env file.
 */

export interface OktaConfig {
  clientId: string;
  issuer: string;
  redirectUri: string;
  scopes: string[];
  pkce: boolean;
  disableHttpsCheck: boolean;
}

const CLIENT_ID = process.env.REACT_APP_OKTA_CLIENT_ID;
const ISSUER = process.env.REACT_APP_OKTA_ISSUER;
const REDIRECT_URI = process.env.REACT_APP_REDIRECT_URI || window.location.origin + '/login/callback';
const SCOPES = process.env.REACT_APP_SCOPES || 'openid profile email';

// Validate required environment variables
if (!CLIENT_ID) {
  throw new Error('REACT_APP_OKTA_CLIENT_ID is required in .env file');
}

if (!ISSUER) {
  throw new Error('REACT_APP_OKTA_ISSUER is required in .env file');
}

export const oktaConfig: OktaConfig = {
  clientId: CLIENT_ID,
  issuer: ISSUER,
  redirectUri: REDIRECT_URI,
  scopes: SCOPES.split(' '),
  pkce: true, // Always use PKCE for SPAs (security best practice)
  disableHttpsCheck: process.env.NODE_ENV === 'development' // Only for local dev
};

// API configuration
export const apiConfig = {
  baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8080'
};

// Token storage configuration
export const tokenManagerConfig = {
  autoRenew: true, // Automatically refresh tokens before expiry
  storage: 'sessionStorage' as const, // Use sessionStorage for security
  expireEarlySeconds: 300, // Renew tokens 5 minutes before expiration
  storageKey: 'okta-token-storage'
};

export default oktaConfig;

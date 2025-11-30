/**
 * Okta Authentication Configuration
 *
 * Initializes the OktaAuth client with PKCE and token management settings.
 * This module is imported by App.tsx to wrap the application with Okta security.
 */

import { OktaAuth } from '@okta/okta-auth-js';
import { oktaConfig, tokenManagerConfig } from './config';

/**
 * Initialize Okta Auth SDK
 *
 * Configuration:
 * - Authorization Code Flow with PKCE (secure for SPAs)
 * - Automatic token renewal
 * - SessionStorage for tokens (cleared on tab close)
 */
export const oktaAuth = new OktaAuth({
  issuer: oktaConfig.issuer,
  clientId: oktaConfig.clientId,
  redirectUri: oktaConfig.redirectUri,
  scopes: oktaConfig.scopes,
  pkce: oktaConfig.pkce,
  disableHttpsCheck: oktaConfig.disableHttpsCheck,
  tokenManager: {
    autoRenew: tokenManagerConfig.autoRenew,
    storage: tokenManagerConfig.storage,
    expireEarlySeconds: tokenManagerConfig.expireEarlySeconds,
    storageKey: tokenManagerConfig.storageKey
  },
  // Additional security settings
  responseType: 'code', // Authorization Code Flow
  cookies: {
    secure: process.env.NODE_ENV === 'production' // Secure cookies in production
  }
});

/**
 * Token renewal event listener
 *
 * Logs when tokens are automatically renewed (helpful for debugging)
 */
oktaAuth.tokenManager.on('renewed', (key, newToken, oldToken) => {
  console.log(`Token renewed: ${key}`);
});

/**
 * Token error event listener
 *
 * Handles token renewal failures by redirecting to login
 */
oktaAuth.tokenManager.on('error', (error) => {
  console.error('Token Manager Error:', error);
  // If token renewal fails, redirect to login
  if (error.name === 'OAuthError' || error.name === 'AuthSdkError') {
    oktaAuth.signInWithRedirect();
  }
});

export default oktaAuth;

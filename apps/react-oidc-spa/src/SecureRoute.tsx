/**
 * Secure Route Component
 *
 * Wraps protected components and ensures user is authenticated.
 * If not authenticated, triggers Okta login flow.
 */

import React, { useEffect } from 'react';
import { useOktaAuth } from '@okta/okta-react';
import { toRelativeUrl } from '@okta/okta-auth-js';

interface SecureRouteProps {
  children: React.ReactNode;
}

const SecureRoute: React.FC<SecureRouteProps> = ({ children }) => {
  const { oktaAuth, authState } = useOktaAuth();

  useEffect(() => {
    if (!authState) {
      return;
    }

    // If user is not authenticated, redirect to Okta login
    if (!authState.isAuthenticated) {
      const originalUri = toRelativeUrl(window.location.href, window.location.origin);
      oktaAuth.setOriginalUri(originalUri);
      oktaAuth.signInWithRedirect();
    }
  }, [authState, oktaAuth]);

  // Show loading while checking authentication state
  if (!authState || authState.isPending) {
    return (
      <div style={styles.loading}>
        <div style={styles.spinner}></div>
        <p style={styles.loadingText}>Loading...</p>
      </div>
    );
  }

  // If authenticated, render protected content
  if (authState.isAuthenticated) {
    return <>{children}</>;
  }

  // While redirecting to login
  return (
    <div style={styles.loading}>
      <p style={styles.loadingText}>Redirecting to login...</p>
    </div>
  );
};

const styles = {
  loading: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    color: '#ffffff'
  },
  spinner: {
    border: '4px solid rgba(255, 255, 255, 0.3)',
    borderTop: '4px solid #ffffff',
    borderRadius: '50%',
    width: '50px',
    height: '50px',
    animation: 'spin 1s linear infinite'
  },
  loadingText: {
    marginTop: '20px',
    fontSize: '18px'
  }
};

export default SecureRoute;

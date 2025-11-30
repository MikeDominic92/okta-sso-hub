/**
 * Main Application Component
 *
 * Sets up routing and Okta security context for the application.
 * All routes are protected except the login page.
 */

import React from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { Security, LoginCallback } from '@okta/okta-react';
import { toRelativeUrl } from '@okta/okta-auth-js';
import oktaAuth from './OktaAuth';
import Login from './Login';
import Dashboard from './Dashboard';
import SecureRoute from './SecureRoute';

const App: React.FC = () => {
  const navigate = useNavigate();

  /**
   * Custom authentication required handler
   * Redirects unauthenticated users to login page
   */
  const customAuthHandler = () => {
    navigate('/login');
  };

  /**
   * Restore original URI after authentication
   * Okta SDK stores the original URI and restores it after login
   */
  const restoreOriginalUri = async (_oktaAuth: any, originalUri: string) => {
    navigate(toRelativeUrl(originalUri || '/', window.location.origin), { replace: true });
  };

  return (
    <Security
      oktaAuth={oktaAuth}
      onAuthRequired={customAuthHandler}
      restoreOriginalUri={restoreOriginalUri}
    >
      <Routes>
        {/* Public route - Login page */}
        <Route path="/login" element={<Login />} />

        {/* Okta callback route - handles authorization code exchange */}
        <Route path="/login/callback" element={<LoginCallback />} />

        {/* Protected route - Dashboard (requires authentication) */}
        <Route path="/" element={<SecureRoute><Dashboard /></SecureRoute>} />
        <Route path="/dashboard" element={<SecureRoute><Dashboard /></SecureRoute>} />
      </Routes>
    </Security>
  );
};

export default App;

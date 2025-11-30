/**
 * Login Component
 *
 * Landing page with Okta login button.
 * Initiates Authorization Code Flow with PKCE when user clicks "Login".
 */

import React, { useEffect } from 'react';
import { useOktaAuth } from '@okta/okta-react';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const { oktaAuth, authState } = useOktaAuth();
  const navigate = useNavigate();

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (authState?.isAuthenticated) {
      navigate('/dashboard');
    }
  }, [authState, navigate]);

  /**
   * Handle login button click
   * Redirects to Okta authorization endpoint with PKCE challenge
   */
  const handleLogin = async () => {
    try {
      await oktaAuth.signInWithRedirect({
        originalUri: '/dashboard'
      });
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <svg style={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <h1 style={styles.title}>Okta SSO Hub</h1>
          <p style={styles.subtitle}>React SPA with OIDC Integration</p>
        </div>

        <div style={styles.content}>
          <h2 style={styles.welcomeTitle}>Welcome!</h2>
          <p style={styles.description}>
            This is a demonstration of OpenID Connect (OIDC) authentication
            using Okta as the Identity Provider.
          </p>

          <div style={styles.features}>
            <div style={styles.feature}>
              <span style={styles.checkmark}>✓</span>
              <span>Authorization Code Flow with PKCE</span>
            </div>
            <div style={styles.feature}>
              <span style={styles.checkmark}>✓</span>
              <span>Automatic Token Refresh</span>
            </div>
            <div style={styles.feature}>
              <span style={styles.checkmark}>✓</span>
              <span>Multi-Factor Authentication</span>
            </div>
            <div style={styles.feature}>
              <span style={styles.checkmark}>✓</span>
              <span>Secure Session Management</span>
            </div>
          </div>

          <button style={styles.button} onClick={handleLogin}>
            <svg style={styles.buttonIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
            Login with Okta
          </button>

          <div style={styles.techStack}>
            <p style={styles.techTitle}>Technology Stack:</p>
            <div style={styles.badges}>
              <span style={styles.badge}>React 18</span>
              <span style={styles.badge}>TypeScript</span>
              <span style={styles.badge}>Okta Auth SDK</span>
              <span style={styles.badge}>OAuth 2.0</span>
            </div>
          </div>
        </div>

        <div style={styles.footer}>
          <p style={styles.footerText}>
            IAM Portfolio Project | Built by Michael Dominic
          </p>
          <a
            href="https://github.com/MikeDominic92/okta-sso-hub"
            target="_blank"
            rel="noopener noreferrer"
            style={styles.link}
          >
            View on GitHub →
          </a>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    padding: '20px'
  },
  card: {
    background: 'rgba(255, 255, 255, 0.95)',
    borderRadius: '16px',
    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
    maxWidth: '500px',
    width: '100%',
    overflow: 'hidden'
  },
  header: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: '#ffffff',
    padding: '40px 30px',
    textAlign: 'center' as const
  },
  icon: {
    width: '60px',
    height: '60px',
    margin: '0 auto 20px'
  },
  title: {
    margin: '0 0 10px 0',
    fontSize: '32px',
    fontWeight: '700'
  },
  subtitle: {
    margin: '0',
    fontSize: '16px',
    opacity: 0.9
  },
  content: {
    padding: '40px 30px'
  },
  welcomeTitle: {
    margin: '0 0 15px 0',
    fontSize: '24px',
    color: '#333333'
  },
  description: {
    margin: '0 0 30px 0',
    fontSize: '16px',
    lineHeight: '1.6',
    color: '#666666'
  },
  features: {
    marginBottom: '30px'
  },
  feature: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '12px',
    fontSize: '15px',
    color: '#555555'
  },
  checkmark: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '24px',
    height: '24px',
    borderRadius: '50%',
    background: '#4caf50',
    color: '#ffffff',
    fontSize: '14px',
    marginRight: '12px',
    fontWeight: '700'
  },
  button: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    padding: '16px 24px',
    fontSize: '18px',
    fontWeight: '600',
    color: '#ffffff',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
    marginBottom: '30px'
  },
  buttonIcon: {
    width: '24px',
    height: '24px',
    marginRight: '10px'
  },
  techStack: {
    borderTop: '1px solid #e0e0e0',
    paddingTop: '25px'
  },
  techTitle: {
    margin: '0 0 12px 0',
    fontSize: '14px',
    color: '#888888',
    fontWeight: '600'
  },
  badges: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '8px'
  },
  badge: {
    display: 'inline-block',
    padding: '6px 12px',
    fontSize: '13px',
    background: '#f0f0f0',
    color: '#555555',
    borderRadius: '4px',
    fontWeight: '500'
  },
  footer: {
    background: '#f8f8f8',
    padding: '20px 30px',
    textAlign: 'center' as const,
    borderTop: '1px solid #e0e0e0'
  },
  footerText: {
    margin: '0 0 8px 0',
    fontSize: '14px',
    color: '#666666'
  },
  link: {
    color: '#667eea',
    textDecoration: 'none',
    fontSize: '14px',
    fontWeight: '600'
  }
};

export default Login;

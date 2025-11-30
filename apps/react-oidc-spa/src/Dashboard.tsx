/**
 * Dashboard Component
 *
 * Protected page that displays user information and demonstrates API calls.
 * Only accessible to authenticated users.
 */

import React, { useState, useEffect } from 'react';
import { useOktaAuth } from '@okta/okta-react';
import { apiConfig } from './config';

interface UserInfo {
  sub?: string;
  name?: string;
  email?: string;
  preferred_username?: string;
  given_name?: string;
  family_name?: string;
  locale?: string;
  zoneinfo?: string;
  updated_at?: number;
}

interface ApiData {
  message?: string;
  timestamp?: string;
  user?: string;
  error?: string;
}

const Dashboard: React.FC = () => {
  const { oktaAuth, authState } = useOktaAuth();
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [apiData, setApiData] = useState<ApiData | null>(null);
  const [apiLoading, setApiLoading] = useState(false);
  const [showTokens, setShowTokens] = useState(false);
  const [tokens, setTokens] = useState<any>(null);

  // Fetch user information on component mount
  useEffect(() => {
    if (authState?.isAuthenticated) {
      fetchUserInfo();
      loadTokens();
    }
  }, [authState]);

  /**
   * Fetch user information from Okta UserInfo endpoint
   */
  const fetchUserInfo = async () => {
    try {
      const user = await oktaAuth.getUser();
      setUserInfo(user);
    } catch (error) {
      console.error('Error fetching user info:', error);
    }
  };

  /**
   * Load tokens from token manager
   */
  const loadTokens = async () => {
    try {
      const accessToken = await oktaAuth.tokenManager.get('accessToken');
      const idToken = await oktaAuth.tokenManager.get('idToken');
      setTokens({
        accessToken,
        idToken
      });
    } catch (error) {
      console.error('Error loading tokens:', error);
    }
  };

  /**
   * Call protected API endpoint
   */
  const callProtectedApi = async () => {
    setApiLoading(true);
    setApiData(null);

    try {
      const accessToken = authState?.accessToken?.accessToken;

      if (!accessToken) {
        throw new Error('No access token available');
      }

      const response = await fetch(`${apiConfig.baseUrl}/api/protected`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setApiData(data);
    } catch (error: any) {
      console.error('API call error:', error);
      setApiData({ error: error.message || 'Failed to call API' });
    } finally {
      setApiLoading(false);
    }
  };

  /**
   * Handle logout
   */
  const handleLogout = async () => {
    try {
      await oktaAuth.signOut({
        postLogoutRedirectUri: window.location.origin
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  /**
   * Format timestamp
   */
  const formatTimestamp = (timestamp?: number) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp * 1000).toLocaleString();
  };

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        {/* Header */}
        <div style={styles.header}>
          <div>
            <h1 style={styles.title}>Dashboard</h1>
            <p style={styles.subtitle}>You are securely authenticated with Okta</p>
          </div>
          <button style={styles.logoutButton} onClick={handleLogout}>
            Logout
          </button>
        </div>

        {/* User Info Card */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>User Information</h2>
          {userInfo ? (
            <div style={styles.infoGrid}>
              <div style={styles.infoItem}>
                <span style={styles.label}>Name:</span>
                <span style={styles.value}>{userInfo.name || 'N/A'}</span>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.label}>Email:</span>
                <span style={styles.value}>{userInfo.email || 'N/A'}</span>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.label}>Username:</span>
                <span style={styles.value}>{userInfo.preferred_username || 'N/A'}</span>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.label}>Subject (ID):</span>
                <span style={styles.value}>{userInfo.sub || 'N/A'}</span>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.label}>Given Name:</span>
                <span style={styles.value}>{userInfo.given_name || 'N/A'}</span>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.label}>Family Name:</span>
                <span style={styles.value}>{userInfo.family_name || 'N/A'}</span>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.label}>Locale:</span>
                <span style={styles.value}>{userInfo.locale || 'N/A'}</span>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.label}>Last Updated:</span>
                <span style={styles.value}>{formatTimestamp(userInfo.updated_at)}</span>
              </div>
            </div>
          ) : (
            <p style={styles.loading}>Loading user information...</p>
          )}
        </div>

        {/* API Testing Card */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Protected API Access</h2>
          <p style={styles.cardDescription}>
            Test calling a protected API endpoint using your access token.
          </p>

          <button
            style={styles.apiButton}
            onClick={callProtectedApi}
            disabled={apiLoading}
          >
            {apiLoading ? 'Calling API...' : 'Call Protected API'}
          </button>

          {apiData && (
            <div style={apiData.error ? styles.errorBox : styles.successBox}>
              <pre style={styles.pre}>
                {JSON.stringify(apiData, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Tokens Card */}
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <h2 style={styles.cardTitle}>Security Tokens</h2>
            <button
              style={styles.toggleButton}
              onClick={() => setShowTokens(!showTokens)}
            >
              {showTokens ? 'Hide Tokens' : 'Show Tokens'}
            </button>
          </div>

          {showTokens && tokens && (
            <div>
              <div style={styles.tokenSection}>
                <h3 style={styles.tokenTitle}>ID Token (Authentication)</h3>
                <div style={styles.tokenInfo}>
                  <p><strong>Expires:</strong> {new Date(tokens.idToken?.expiresAt * 1000).toLocaleString()}</p>
                  <p><strong>Scopes:</strong> {tokens.idToken?.scopes?.join(', ') || 'N/A'}</p>
                </div>
                <details style={styles.details}>
                  <summary style={styles.summary}>View ID Token Claims</summary>
                  <pre style={styles.tokenPre}>
                    {JSON.stringify(tokens.idToken?.claims, null, 2)}
                  </pre>
                </details>
                <details style={styles.details}>
                  <summary style={styles.summary}>View Raw ID Token</summary>
                  <pre style={styles.tokenPre}>
                    {tokens.idToken?.idToken}
                  </pre>
                </details>
              </div>

              <div style={styles.tokenSection}>
                <h3 style={styles.tokenTitle}>Access Token (Authorization)</h3>
                <div style={styles.tokenInfo}>
                  <p><strong>Expires:</strong> {new Date(tokens.accessToken?.expiresAt * 1000).toLocaleString()}</p>
                  <p><strong>Scopes:</strong> {tokens.accessToken?.scopes?.join(', ') || 'N/A'}</p>
                </div>
                <details style={styles.details}>
                  <summary style={styles.summary}>View Access Token Claims</summary>
                  <pre style={styles.tokenPre}>
                    {JSON.stringify(tokens.accessToken?.claims, null, 2)}
                  </pre>
                </details>
                <details style={styles.details}>
                  <summary style={styles.summary}>View Raw Access Token</summary>
                  <pre style={styles.tokenPre}>
                    {tokens.accessToken?.accessToken}
                  </pre>
                </details>
              </div>
            </div>
          )}
        </div>

        {/* Authentication Status */}
        <div style={styles.statusCard}>
          <h3 style={styles.statusTitle}>Authentication Status</h3>
          <div style={styles.statusGrid}>
            <div style={styles.statusItem}>
              <span style={styles.statusLabel}>Authenticated:</span>
              <span style={styles.statusValue}>
                {authState?.isAuthenticated ? (
                  <span style={styles.statusSuccess}>✓ Yes</span>
                ) : (
                  <span style={styles.statusError}>✗ No</span>
                )}
              </span>
            </div>
            <div style={styles.statusItem}>
              <span style={styles.statusLabel}>Auth State:</span>
              <span style={styles.statusValue}>
                {authState?.isPending ? 'Pending' : 'Ready'}
              </span>
            </div>
            <div style={styles.statusItem}>
              <span style={styles.statusLabel}>Token Auto-Renew:</span>
              <span style={styles.statusValue}>
                <span style={styles.statusSuccess}>✓ Enabled</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    padding: '20px'
  },
  content: {
    maxWidth: '1200px',
    margin: '0 auto'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px',
    padding: '20px',
    background: 'rgba(255, 255, 255, 0.95)',
    borderRadius: '12px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)'
  },
  title: {
    margin: '0',
    fontSize: '32px',
    color: '#333333',
    fontWeight: '700'
  },
  subtitle: {
    margin: '5px 0 0 0',
    fontSize: '16px',
    color: '#666666'
  },
  logoutButton: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#ffffff',
    background: '#dc3545',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'background 0.2s'
  },
  card: {
    background: 'rgba(255, 255, 255, 0.95)',
    borderRadius: '12px',
    padding: '30px',
    marginBottom: '20px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)'
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px'
  },
  cardTitle: {
    margin: '0 0 20px 0',
    fontSize: '24px',
    color: '#333333',
    fontWeight: '600'
  },
  cardDescription: {
    margin: '0 0 20px 0',
    color: '#666666',
    fontSize: '15px'
  },
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '16px'
  },
  infoItem: {
    display: 'flex',
    flexDirection: 'column' as const
  },
  label: {
    fontSize: '13px',
    color: '#888888',
    fontWeight: '600',
    marginBottom: '4px'
  },
  value: {
    fontSize: '16px',
    color: '#333333',
    wordBreak: 'break-all' as const
  },
  loading: {
    color: '#666666',
    fontStyle: 'italic' as const
  },
  apiButton: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#ffffff',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    marginBottom: '20px'
  },
  successBox: {
    background: '#d4edda',
    border: '1px solid #c3e6cb',
    borderRadius: '8px',
    padding: '15px'
  },
  errorBox: {
    background: '#f8d7da',
    border: '1px solid #f5c6cb',
    borderRadius: '8px',
    padding: '15px'
  },
  pre: {
    margin: '0',
    fontSize: '14px',
    fontFamily: 'monospace',
    whiteSpace: 'pre-wrap' as const,
    wordBreak: 'break-all' as const
  },
  toggleButton: {
    padding: '8px 16px',
    fontSize: '14px',
    fontWeight: '600',
    color: '#667eea',
    background: '#ffffff',
    border: '2px solid #667eea',
    borderRadius: '6px',
    cursor: 'pointer'
  },
  tokenSection: {
    marginBottom: '25px',
    padding: '20px',
    background: '#f8f9fa',
    borderRadius: '8px'
  },
  tokenTitle: {
    margin: '0 0 15px 0',
    fontSize: '18px',
    color: '#333333',
    fontWeight: '600'
  },
  tokenInfo: {
    marginBottom: '15px',
    fontSize: '14px',
    color: '#555555'
  },
  details: {
    marginTop: '10px'
  },
  summary: {
    cursor: 'pointer',
    fontWeight: '600' as const,
    color: '#667eea',
    marginBottom: '10px'
  },
  tokenPre: {
    background: '#ffffff',
    padding: '15px',
    borderRadius: '6px',
    fontSize: '12px',
    fontFamily: 'monospace',
    whiteSpace: 'pre-wrap' as const,
    wordBreak: 'break-all' as const,
    maxHeight: '300px',
    overflow: 'auto' as const,
    marginTop: '10px'
  },
  statusCard: {
    background: 'rgba(255, 255, 255, 0.95)',
    borderRadius: '12px',
    padding: '25px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)'
  },
  statusTitle: {
    margin: '0 0 20px 0',
    fontSize: '20px',
    color: '#333333',
    fontWeight: '600'
  },
  statusGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '16px'
  },
  statusItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px',
    background: '#f8f9fa',
    borderRadius: '6px'
  },
  statusLabel: {
    fontSize: '14px',
    color: '#666666',
    fontWeight: '600'
  },
  statusValue: {
    fontSize: '14px',
    color: '#333333'
  },
  statusSuccess: {
    color: '#28a745',
    fontWeight: '600' as const
  },
  statusError: {
    color: '#dc3545',
    fontWeight: '600' as const
  }
};

export default Dashboard;

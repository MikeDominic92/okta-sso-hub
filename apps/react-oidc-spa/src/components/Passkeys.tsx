/**
 * Passkeys Management Component
 *
 * Provides UI for FIDO2/WebAuthn passkey management:
 * - Browser compatibility detection
 * - Passkey registration (create new credentials)
 * - View registered passkeys
 * - Delete passkeys
 * - Status indicators and error handling
 */

import React, { useState, useEffect } from 'react';
import { useOktaAuth } from '@okta/okta-react';
import { useNavigate } from 'react-router-dom';
import {
  isWebAuthnSupported,
  isPlatformAuthenticatorAvailable,
  createCredential,
  generateChallenge,
  getStoredPasskeys,
  savePasskey,
  removePasskey,
  StoredPasskey,
  RegistrationOptions,
} from '../utils/webauthn';

const Passkeys: React.FC = () => {
  const { authState, oktaAuth } = useOktaAuth();
  const navigate = useNavigate();

  // State management
  const [passkeys, setPasskeys] = useState<StoredPasskey[]>([]);
  const [isSupported, setIsSupported] = useState(false);
  const [isPlatformAvailable, setIsPlatformAvailable] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [passkeyName, setPasskeyName] = useState('');
  const [authenticatorType, setAuthenticatorType] = useState<'platform' | 'cross-platform'>('platform');

  // Load passkeys and check browser support on mount
  useEffect(() => {
    checkSupport();
    loadPasskeys();
  }, []);

  /**
   * Check WebAuthn browser support
   */
  const checkSupport = async () => {
    const supported = isWebAuthnSupported();
    setIsSupported(supported);

    if (supported) {
      const platformAvailable = await isPlatformAuthenticatorAvailable();
      setIsPlatformAvailable(platformAvailable);
    }
  };

  /**
   * Load registered passkeys from localStorage
   */
  const loadPasskeys = () => {
    const stored = getStoredPasskeys();
    setPasskeys(stored);
  };

  /**
   * Register a new passkey
   */
  const handleRegisterPasskey = async () => {
    if (!passkeyName.trim()) {
      setError('Please enter a name for your passkey');
      return;
    }

    setIsRegistering(true);
    setError(null);
    setSuccess(null);

    try {
      // Get user info from Okta
      const userInfo = await oktaAuth.getUser();
      const userId = userInfo.sub || 'user-' + Date.now();
      const userName = userInfo.email || userInfo.preferred_username || 'user';
      const displayName = userInfo.name || userName;

      // Generate challenge (in production, this should come from your server)
      const challenge = generateChallenge();

      // Prepare registration options
      const options: RegistrationOptions = {
        challenge,
        userId: btoa(userId).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, ''),
        userName,
        userDisplayName: displayName,
        rpName: 'Okta SSO Hub',
        rpId: window.location.hostname,
        timeout: 60000,
        attestation: 'none',
        authenticatorSelection: {
          authenticatorAttachment: authenticatorType,
          requireResidentKey: true,
          residentKey: 'required',
          userVerification: 'preferred',
        },
        excludeCredentials: passkeys.map(pk => ({
          id: pk.credentialId,
          type: 'public-key' as const,
        })),
      };

      // Create credential
      const credential = await createCredential(options);

      // Save to localStorage (in production, save to server)
      const newPasskey: StoredPasskey = {
        id: `pk-${Date.now()}`,
        credentialId: credential.id,
        name: passkeyName.trim(),
        createdAt: new Date().toISOString(),
        authenticatorType,
      };

      savePasskey(newPasskey);
      loadPasskeys();

      setSuccess(`Passkey "${passkeyName}" registered successfully!`);
      setPasskeyName('');

      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
    } catch (err: any) {
      console.error('Registration error:', err);
      setError(err.message || 'Failed to register passkey');
    } finally {
      setIsRegistering(false);
    }
  };

  /**
   * Delete a passkey
   */
  const handleDeletePasskey = (credentialId: string, name: string) => {
    if (window.confirm(`Are you sure you want to delete the passkey "${name}"?`)) {
      try {
        removePasskey(credentialId);
        loadPasskeys();
        setSuccess(`Passkey "${name}" deleted successfully`);
        setTimeout(() => setSuccess(null), 3000);
      } catch (err: any) {
        setError(err.message || 'Failed to delete passkey');
      }
    }
  };

  /**
   * Format date for display
   */
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  /**
   * Get authenticator type label
   */
  const getAuthenticatorLabel = (type?: 'platform' | 'cross-platform') => {
    if (type === 'platform') return 'Platform (Touch ID, Windows Hello, etc.)';
    if (type === 'cross-platform') return 'Security Key (YubiKey, etc.)';
    return 'Unknown';
  };

  // Show unsupported message if WebAuthn is not available
  if (!isSupported) {
    return (
      <div style={styles.container}>
        <div style={styles.content}>
          <button style={styles.backButton} onClick={() => navigate('/dashboard')}>
            ← Back to Dashboard
          </button>

          <div style={styles.header}>
            <h1 style={styles.title}>Passkey Management</h1>
            <p style={styles.subtitle}>Passwordless Authentication with FIDO2/WebAuthn</p>
          </div>

          <div style={styles.errorCard}>
            <h2 style={styles.cardTitle}>Browser Not Supported</h2>
            <p style={styles.errorText}>
              Your browser does not support WebAuthn/FIDO2 passkeys. Please use a modern browser like:
            </p>
            <ul style={styles.browserList}>
              <li>Chrome/Edge 90+</li>
              <li>Firefox 90+</li>
              <li>Safari 14+</li>
              <li>Opera 76+</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <button style={styles.backButton} onClick={() => navigate('/dashboard')}>
          ← Back to Dashboard
        </button>

        {/* Header */}
        <div style={styles.header}>
          <div>
            <h1 style={styles.title}>Passkey Management</h1>
            <p style={styles.subtitle}>Passwordless Authentication with FIDO2/WebAuthn</p>
          </div>
        </div>

        {/* Success Message */}
        {success && (
          <div style={styles.successAlert}>
            <strong>Success!</strong> {success}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div style={styles.errorAlert}>
            <strong>Error!</strong> {error}
          </div>
        )}

        {/* Browser Support Status */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Browser Compatibility</h2>
          <div style={styles.statusGrid}>
            <div style={styles.statusItem}>
              <span style={styles.statusLabel}>WebAuthn Support:</span>
              <span style={styles.statusSuccess}>✓ Supported</span>
            </div>
            <div style={styles.statusItem}>
              <span style={styles.statusLabel}>Platform Authenticator:</span>
              <span style={isPlatformAvailable ? styles.statusSuccess : styles.statusWarning}>
                {isPlatformAvailable ? '✓ Available' : '⚠ Not Available'}
              </span>
            </div>
            <div style={styles.statusItem}>
              <span style={styles.statusLabel}>Security Keys:</span>
              <span style={styles.statusSuccess}>✓ Supported</span>
            </div>
          </div>
          <p style={styles.infoText}>
            {isPlatformAvailable
              ? 'Your device supports built-in authenticators (Touch ID, Windows Hello, etc.) and external security keys.'
              : 'Your device supports external security keys. Built-in authenticators are not available on this device.'}
          </p>
        </div>

        {/* Register New Passkey */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Register New Passkey</h2>
          <p style={styles.cardDescription}>
            Create a new passkey for passwordless authentication. Passkeys are more secure than passwords
            and resistant to phishing attacks.
          </p>

          <div style={styles.formGroup}>
            <label style={styles.label} htmlFor="passkeyName">
              Passkey Name
            </label>
            <input
              id="passkeyName"
              type="text"
              style={styles.input}
              placeholder="e.g., My MacBook Touch ID, YubiKey 5"
              value={passkeyName}
              onChange={(e) => setPasskeyName(e.target.value)}
              disabled={isRegistering}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Authenticator Type</label>
            <div style={styles.radioGroup}>
              <label style={styles.radioLabel}>
                <input
                  type="radio"
                  value="platform"
                  checked={authenticatorType === 'platform'}
                  onChange={(e) => setAuthenticatorType(e.target.value as 'platform')}
                  disabled={isRegistering || !isPlatformAvailable}
                  style={styles.radio}
                />
                Platform Authenticator (Touch ID, Windows Hello, etc.)
                {!isPlatformAvailable && (
                  <span style={styles.disabledText}> - Not available on this device</span>
                )}
              </label>
              <label style={styles.radioLabel}>
                <input
                  type="radio"
                  value="cross-platform"
                  checked={authenticatorType === 'cross-platform'}
                  onChange={(e) => setAuthenticatorType(e.target.value as 'cross-platform')}
                  disabled={isRegistering}
                  style={styles.radio}
                />
                Security Key (YubiKey, etc.)
              </label>
            </div>
          </div>

          <button
            style={isRegistering ? styles.buttonDisabled : styles.button}
            onClick={handleRegisterPasskey}
            disabled={isRegistering}
          >
            {isRegistering ? 'Registering...' : 'Register Passkey'}
          </button>
        </div>

        {/* Registered Passkeys */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Your Passkeys ({passkeys.length})</h2>

          {passkeys.length === 0 ? (
            <div style={styles.emptyState}>
              <p style={styles.emptyText}>No passkeys registered yet.</p>
              <p style={styles.emptySubtext}>
                Register your first passkey above to enable passwordless authentication.
              </p>
            </div>
          ) : (
            <div style={styles.passkeyList}>
              {passkeys.map((passkey) => (
                <div key={passkey.id} style={styles.passkeyItem}>
                  <div style={styles.passkeyInfo}>
                    <div style={styles.passkeyName}>{passkey.name}</div>
                    <div style={styles.passkeyMeta}>
                      <span style={styles.metaItem}>
                        Type: {getAuthenticatorLabel(passkey.authenticatorType)}
                      </span>
                      <span style={styles.metaItem}>
                        Created: {formatDate(passkey.createdAt)}
                      </span>
                      {passkey.lastUsed && (
                        <span style={styles.metaItem}>
                          Last used: {formatDate(passkey.lastUsed)}
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    style={styles.deleteButton}
                    onClick={() => handleDeletePasskey(passkey.credentialId, passkey.name)}
                    title="Delete passkey"
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Information */}
        <div style={styles.infoCard}>
          <h3 style={styles.infoTitle}>About Passkeys</h3>
          <div style={styles.infoContent}>
            <p>
              <strong>What are passkeys?</strong> Passkeys are a passwordless authentication method that uses
              FIDO2/WebAuthn technology. They provide a more secure and convenient alternative to traditional passwords.
            </p>
            <p>
              <strong>Why use passkeys?</strong>
            </p>
            <ul style={styles.infoList}>
              <li>More secure than passwords - resistant to phishing and credential stuffing</li>
              <li>More convenient - no need to remember complex passwords</li>
              <li>Faster authentication - authenticate with biometrics or security key</li>
              <li>Privacy-preserving - your biometric data never leaves your device</li>
              <li>Industry standard - supported by major platforms (Apple, Google, Microsoft)</li>
            </ul>
            <p>
              <strong>Note:</strong> This demo stores passkeys in browser localStorage for demonstration purposes.
              In a production environment, passkeys should be registered with your Okta tenant for full SSO integration.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    padding: '20px',
    backgroundColor: '#f5f5f5',
  },
  content: {
    maxWidth: '1000px',
    margin: '0 auto',
  },
  backButton: {
    marginBottom: '20px',
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: '600' as const,
    color: '#667eea',
    background: '#ffffff',
    border: '2px solid #667eea',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px',
    padding: '20px',
    background: 'rgba(255, 255, 255, 0.95)',
    borderRadius: '12px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
  },
  title: {
    margin: '0',
    fontSize: '32px',
    color: '#333333',
    fontWeight: '700' as const,
  },
  subtitle: {
    margin: '5px 0 0 0',
    fontSize: '16px',
    color: '#666666',
  },
  card: {
    background: 'rgba(255, 255, 255, 0.95)',
    borderRadius: '12px',
    padding: '30px',
    marginBottom: '20px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
  },
  cardTitle: {
    margin: '0 0 20px 0',
    fontSize: '24px',
    color: '#333333',
    fontWeight: '600' as const,
  },
  cardDescription: {
    margin: '0 0 20px 0',
    color: '#666666',
    fontSize: '15px',
    lineHeight: '1.5',
  },
  statusGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '16px',
    marginBottom: '15px',
  },
  statusItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px',
    background: '#f8f9fa',
    borderRadius: '6px',
  },
  statusLabel: {
    fontSize: '14px',
    color: '#666666',
    fontWeight: '600' as const,
  },
  statusSuccess: {
    color: '#28a745',
    fontWeight: '600' as const,
    fontSize: '14px',
  },
  statusWarning: {
    color: '#ffc107',
    fontWeight: '600' as const,
    fontSize: '14px',
  },
  infoText: {
    margin: '0',
    fontSize: '14px',
    color: '#666666',
    lineHeight: '1.5',
  },
  formGroup: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontSize: '14px',
    fontWeight: '600' as const,
    color: '#333333',
  },
  input: {
    width: '100%',
    padding: '12px',
    fontSize: '16px',
    border: '2px solid #e0e0e0',
    borderRadius: '8px',
    boxSizing: 'border-box' as const,
    transition: 'border-color 0.2s',
  },
  radioGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
  },
  radioLabel: {
    display: 'flex',
    alignItems: 'center',
    fontSize: '14px',
    color: '#333333',
    cursor: 'pointer',
  },
  radio: {
    marginRight: '8px',
    cursor: 'pointer',
  },
  disabledText: {
    color: '#999999',
    fontStyle: 'italic' as const,
  },
  button: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '600' as const,
    color: '#ffffff',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'transform 0.2s',
  },
  buttonDisabled: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '600' as const,
    color: '#ffffff',
    background: '#cccccc',
    border: 'none',
    borderRadius: '8px',
    cursor: 'not-allowed',
  },
  emptyState: {
    textAlign: 'center' as const,
    padding: '40px 20px',
  },
  emptyText: {
    margin: '0 0 10px 0',
    fontSize: '18px',
    color: '#666666',
    fontWeight: '600' as const,
  },
  emptySubtext: {
    margin: '0',
    fontSize: '14px',
    color: '#999999',
  },
  passkeyList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
  },
  passkeyItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px',
    background: '#f8f9fa',
    borderRadius: '8px',
    border: '1px solid #e0e0e0',
  },
  passkeyInfo: {
    flex: '1',
  },
  passkeyName: {
    fontSize: '16px',
    fontWeight: '600' as const,
    color: '#333333',
    marginBottom: '8px',
  },
  passkeyMeta: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '4px',
  },
  metaItem: {
    fontSize: '13px',
    color: '#666666',
  },
  deleteButton: {
    padding: '8px 16px',
    fontSize: '14px',
    fontWeight: '600' as const,
    color: '#ffffff',
    background: '#dc3545',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
  successAlert: {
    padding: '15px 20px',
    marginBottom: '20px',
    background: '#d4edda',
    border: '1px solid #c3e6cb',
    borderRadius: '8px',
    color: '#155724',
    fontSize: '14px',
  },
  errorAlert: {
    padding: '15px 20px',
    marginBottom: '20px',
    background: '#f8d7da',
    border: '1px solid #f5c6cb',
    borderRadius: '8px',
    color: '#721c24',
    fontSize: '14px',
  },
  errorCard: {
    background: '#fff3cd',
    border: '2px solid #ffc107',
    borderRadius: '12px',
    padding: '30px',
    marginBottom: '20px',
  },
  errorText: {
    margin: '0 0 15px 0',
    fontSize: '15px',
    color: '#856404',
  },
  browserList: {
    margin: '10px 0',
    paddingLeft: '20px',
    color: '#856404',
  },
  infoCard: {
    background: 'rgba(102, 126, 234, 0.1)',
    border: '2px solid #667eea',
    borderRadius: '12px',
    padding: '25px',
    marginBottom: '20px',
  },
  infoTitle: {
    margin: '0 0 15px 0',
    fontSize: '20px',
    color: '#667eea',
    fontWeight: '600' as const,
  },
  infoContent: {
    fontSize: '14px',
    color: '#333333',
    lineHeight: '1.6',
  },
  infoList: {
    margin: '10px 0',
    paddingLeft: '20px',
  },
};

export default Passkeys;

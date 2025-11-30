/**
 * WebAuthn API Wrapper Utilities
 *
 * Provides functions for FIDO2/WebAuthn credential management:
 * - Passkey registration (createCredential)
 * - Passkey authentication (getCredential)
 * - Browser compatibility detection
 * - Error handling and user-friendly messages
 */

/**
 * Base64URL encoding/decoding utilities
 * WebAuthn requires base64url format (no padding, URL-safe characters)
 */
export const base64url = {
  /**
   * Encode ArrayBuffer to base64url string
   */
  encode(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary)
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
  },

  /**
   * Decode base64url string to ArrayBuffer
   */
  decode(base64url: string): ArrayBuffer {
    // Add padding if needed
    const base64 = base64url
      .replace(/-/g, '+')
      .replace(/_/g, '/');
    const padding = '='.repeat((4 - (base64.length % 4)) % 4);
    const binary = atob(base64 + padding);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }
};

/**
 * Check if WebAuthn is supported in the current browser
 */
export const isWebAuthnSupported = (): boolean => {
  return !!(
    window.PublicKeyCredential &&
    navigator.credentials &&
    navigator.credentials.create &&
    navigator.credentials.get
  );
};

/**
 * Check if platform authenticator (Touch ID, Windows Hello, etc.) is available
 */
export const isPlatformAuthenticatorAvailable = async (): Promise<boolean> => {
  if (!isWebAuthnSupported()) {
    return false;
  }

  try {
    return await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
  } catch (error) {
    console.error('Error checking platform authenticator:', error);
    return false;
  }
};

/**
 * Registration options for creating a new passkey
 */
export interface RegistrationOptions {
  challenge: string;
  userId: string;
  userName: string;
  userDisplayName: string;
  rpName?: string;
  rpId?: string;
  timeout?: number;
  attestation?: AttestationConveyancePreference;
  authenticatorSelection?: {
    authenticatorAttachment?: AuthenticatorAttachment;
    requireResidentKey?: boolean;
    residentKey?: ResidentKeyRequirement;
    userVerification?: UserVerificationRequirement;
  };
  excludeCredentials?: Array<{
    id: string;
    type: 'public-key';
  }>;
}

/**
 * Authentication options for verifying with existing passkey
 */
export interface AuthenticationOptions {
  challenge: string;
  rpId?: string;
  timeout?: number;
  userVerification?: UserVerificationRequirement;
  allowCredentials?: Array<{
    id: string;
    type: 'public-key';
  }>;
}

/**
 * Credential response from registration
 */
export interface CredentialResponse {
  id: string;
  rawId: string;
  type: string;
  response: {
    clientDataJSON: string;
    attestationObject: string;
    transports?: string[];
  };
}

/**
 * Credential response from authentication
 */
export interface AuthenticationResponse {
  id: string;
  rawId: string;
  type: string;
  response: {
    clientDataJSON: string;
    authenticatorData: string;
    signature: string;
    userHandle?: string;
  };
}

/**
 * Create a new WebAuthn credential (passkey registration)
 *
 * @param options - Registration options including challenge and user info
 * @returns Credential response to send to server for verification
 */
export const createCredential = async (
  options: RegistrationOptions
): Promise<CredentialResponse> => {
  if (!isWebAuthnSupported()) {
    throw new Error('WebAuthn is not supported in this browser');
  }

  try {
    // Convert challenge and user ID from base64url to ArrayBuffer
    const challengeBuffer = base64url.decode(options.challenge);
    const userIdBuffer = base64url.decode(options.userId);

    // Build PublicKeyCredentialCreationOptions
    const publicKeyOptions: PublicKeyCredentialCreationOptions = {
      challenge: challengeBuffer,
      rp: {
        name: options.rpName || window.location.hostname,
        id: options.rpId || window.location.hostname,
      },
      user: {
        id: userIdBuffer,
        name: options.userName,
        displayName: options.userDisplayName,
      },
      pubKeyCredParams: [
        { alg: -7, type: 'public-key' },  // ES256 (ECDSA with SHA-256)
        { alg: -257, type: 'public-key' }, // RS256 (RSASSA-PKCS1-v1_5 with SHA-256)
      ],
      timeout: options.timeout || 60000, // 60 seconds
      attestation: options.attestation || 'none',
      authenticatorSelection: {
        authenticatorAttachment: options.authenticatorSelection?.authenticatorAttachment,
        requireResidentKey: options.authenticatorSelection?.requireResidentKey ?? false,
        residentKey: options.authenticatorSelection?.residentKey || 'preferred',
        userVerification: options.authenticatorSelection?.userVerification || 'preferred',
      },
      excludeCredentials: options.excludeCredentials?.map(cred => ({
        id: base64url.decode(cred.id),
        type: 'public-key' as const,
      })),
    };

    // Create credential
    const credential = await navigator.credentials.create({
      publicKey: publicKeyOptions,
    }) as PublicKeyCredential | null;

    if (!credential) {
      throw new Error('Failed to create credential');
    }

    const response = credential.response as AuthenticatorAttestationResponse;

    // Convert response to base64url format for server
    return {
      id: credential.id,
      rawId: base64url.encode(credential.rawId),
      type: credential.type,
      response: {
        clientDataJSON: base64url.encode(response.clientDataJSON),
        attestationObject: base64url.encode(response.attestationObject),
        transports: response.getTransports ? response.getTransports() : undefined,
      },
    };
  } catch (error: any) {
    console.error('WebAuthn registration error:', error);
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Get existing credential (passkey authentication)
 *
 * @param options - Authentication options including challenge
 * @returns Authentication response to send to server for verification
 */
export const getCredential = async (
  options: AuthenticationOptions
): Promise<AuthenticationResponse> => {
  if (!isWebAuthnSupported()) {
    throw new Error('WebAuthn is not supported in this browser');
  }

  try {
    // Convert challenge from base64url to ArrayBuffer
    const challengeBuffer = base64url.decode(options.challenge);

    // Build PublicKeyCredentialRequestOptions
    const publicKeyOptions: PublicKeyCredentialRequestOptions = {
      challenge: challengeBuffer,
      rpId: options.rpId || window.location.hostname,
      timeout: options.timeout || 60000, // 60 seconds
      userVerification: options.userVerification || 'preferred',
      allowCredentials: options.allowCredentials?.map(cred => ({
        id: base64url.decode(cred.id),
        type: 'public-key' as const,
      })),
    };

    // Get credential
    const credential = await navigator.credentials.get({
      publicKey: publicKeyOptions,
    }) as PublicKeyCredential | null;

    if (!credential) {
      throw new Error('Failed to get credential');
    }

    const response = credential.response as AuthenticatorAssertionResponse;

    // Convert response to base64url format for server
    return {
      id: credential.id,
      rawId: base64url.encode(credential.rawId),
      type: credential.type,
      response: {
        clientDataJSON: base64url.encode(response.clientDataJSON),
        authenticatorData: base64url.encode(response.authenticatorData),
        signature: base64url.encode(response.signature),
        userHandle: response.userHandle ? base64url.encode(response.userHandle) : undefined,
      },
    };
  } catch (error: any) {
    console.error('WebAuthn authentication error:', error);
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Convert WebAuthn error to user-friendly message
 */
const getErrorMessage = (error: any): string => {
  if (error.name === 'NotAllowedError') {
    return 'Operation cancelled or not allowed. Please try again.';
  }
  if (error.name === 'InvalidStateError') {
    return 'This passkey is already registered.';
  }
  if (error.name === 'NotSupportedError') {
    return 'Your device does not support this operation.';
  }
  if (error.name === 'SecurityError') {
    return 'Security error. Make sure you are using HTTPS.';
  }
  if (error.name === 'AbortError') {
    return 'Operation was aborted.';
  }
  if (error.name === 'ConstraintError') {
    return 'No authenticator matches the requirements.';
  }
  if (error.name === 'UnknownError') {
    return 'An unknown error occurred. Please try again.';
  }

  return error.message || 'An error occurred during the operation.';
};

/**
 * Generate a random challenge for WebAuthn operations
 * In production, this should come from your server
 */
export const generateChallenge = (): string => {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return base64url.encode(array.buffer);
};

/**
 * Storage key for passkeys in localStorage
 */
const PASSKEYS_STORAGE_KEY = 'okta_passkeys';

/**
 * Stored passkey information
 */
export interface StoredPasskey {
  id: string;
  credentialId: string;
  name: string;
  createdAt: string;
  lastUsed?: string;
  authenticatorType?: 'platform' | 'cross-platform';
}

/**
 * Get stored passkeys from localStorage
 */
export const getStoredPasskeys = (): StoredPasskey[] => {
  try {
    const stored = localStorage.getItem(PASSKEYS_STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Error reading stored passkeys:', error);
    return [];
  }
};

/**
 * Save passkey to localStorage
 */
export const savePasskey = (passkey: StoredPasskey): void => {
  try {
    const passkeys = getStoredPasskeys();
    passkeys.push(passkey);
    localStorage.setItem(PASSKEYS_STORAGE_KEY, JSON.stringify(passkeys));
  } catch (error) {
    console.error('Error saving passkey:', error);
    throw new Error('Failed to save passkey');
  }
};

/**
 * Remove passkey from localStorage
 */
export const removePasskey = (credentialId: string): void => {
  try {
    const passkeys = getStoredPasskeys();
    const filtered = passkeys.filter(pk => pk.credentialId !== credentialId);
    localStorage.setItem(PASSKEYS_STORAGE_KEY, JSON.stringify(filtered));
  } catch (error) {
    console.error('Error removing passkey:', error);
    throw new Error('Failed to remove passkey');
  }
};

/**
 * Update last used timestamp for a passkey
 */
export const updatePasskeyLastUsed = (credentialId: string): void => {
  try {
    const passkeys = getStoredPasskeys();
    const passkey = passkeys.find(pk => pk.credentialId === credentialId);
    if (passkey) {
      passkey.lastUsed = new Date().toISOString();
      localStorage.setItem(PASSKEYS_STORAGE_KEY, JSON.stringify(passkeys));
    }
  } catch (error) {
    console.error('Error updating passkey:', error);
  }
};

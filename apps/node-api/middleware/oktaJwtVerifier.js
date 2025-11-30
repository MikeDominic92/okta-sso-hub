/**
 * Okta JWT Verifier Middleware
 *
 * Validates JWT access tokens from Okta.
 * Verifies signature, issuer, audience, and expiration.
 */

const OktaJwtVerifier = require('@okta/jwt-verifier');

const oktaJwtVerifier = new OktaJwtVerifier({
  issuer: process.env.OKTA_ISSUER,
  clientId: process.env.OKTA_CLIENT_ID,
  assertClaims: {
    aud: process.env.OKTA_AUDIENCE || 'api://default',
    cid: process.env.OKTA_CLIENT_ID
  }
});

/**
 * JWT Verification Middleware
 *
 * Extracts Bearer token from Authorization header,
 * verifies it with Okta, and attaches claims to req.user.
 */
async function verifyToken(req, res, next) {
  try {
    // Extract authorization header
    const authHeader = req.headers.authorization;

    if (!authHeader) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'No authorization header provided'
      });
    }

    // Check Bearer token format
    const match = authHeader.match(/Bearer (.+)/);

    if (!match) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid authorization header format. Expected: Bearer <token>'
      });
    }

    const accessToken = match[1];

    // Verify JWT token
    // This validates:
    // - Signature (cryptographic verification)
    // - Issuer (iss claim matches OKTA_ISSUER)
    // - Audience (aud claim matches OKTA_AUDIENCE)
    // - Client ID (cid claim matches OKTA_CLIENT_ID)
    // - Expiration (exp claim is in the future)
    // - Not Before (nbf claim, if present)
    const jwt = await oktaJwtVerifier.verifyAccessToken(
      accessToken,
      process.env.OKTA_AUDIENCE || 'api://default'
    );

    // Attach user claims to request object
    req.user = jwt.claims;
    req.jwt = jwt;

    // Log successful verification (development only)
    if (process.env.NODE_ENV === 'development') {
      console.log(`✓ JWT verified for user: ${jwt.claims.sub}`);
      console.log(`  Scopes: ${jwt.claims.scp ? jwt.claims.scp.join(', ') : 'none'}`);
    }

    next();
  } catch (error) {
    console.error('JWT Verification Error:', error.message);

    // Provide specific error messages
    let message = 'Invalid or expired token';

    if (error.message.includes('expired')) {
      message = 'Token has expired';
    } else if (error.message.includes('issuer')) {
      message = 'Token issuer is invalid';
    } else if (error.message.includes('audience')) {
      message = 'Token audience is invalid';
    } else if (error.message.includes('signature')) {
      message = 'Token signature verification failed';
    }

    return res.status(401).json({
      error: 'Unauthorized',
      message: message,
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
}

/**
 * Scope Verification Middleware Factory
 *
 * Creates middleware that checks for specific scopes in the JWT.
 *
 * @param {string|string[]} requiredScopes - Scope(s) required to access endpoint
 * @returns {Function} Express middleware function
 */
function requireScope(requiredScopes) {
  const scopes = Array.isArray(requiredScopes) ? requiredScopes : [requiredScopes];

  return (req, res, next) => {
    const userScopes = req.user?.scp || [];

    const hasRequiredScope = scopes.some(scope => userScopes.includes(scope));

    if (!hasRequiredScope) {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'Insufficient scope to access this resource',
        requiredScopes: scopes,
        userScopes: userScopes
      });
    }

    next();
  };
}

/**
 * Claims Verification Middleware Factory
 *
 * Creates middleware that checks for specific claims in the JWT.
 *
 * @param {Object} requiredClaims - Claims and values required
 * @returns {Function} Express middleware function
 */
function requireClaims(requiredClaims) {
  return (req, res, next) => {
    for (const [claim, expectedValue] of Object.entries(requiredClaims)) {
      const actualValue = req.user?.[claim];

      if (actualValue !== expectedValue) {
        return res.status(403).json({
          error: 'Forbidden',
          message: `Required claim '${claim}' not met`,
          expected: expectedValue,
          actual: actualValue
        });
      }
    }

    next();
  };
}

module.exports = verifyToken;
module.exports.requireScope = requireScope;
module.exports.requireClaims = requireClaims;

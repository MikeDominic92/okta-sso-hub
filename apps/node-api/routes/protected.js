/**
 * Protected API Routes
 *
 * All routes require valid JWT authentication.
 * Demonstrates scope-based and claims-based authorization.
 */

const express = require('express');
const router = express.Router();
const { requireScope, requireClaims } = require('../middleware/oktaJwtVerifier');

/**
 * GET /api/protected
 *
 * Basic protected endpoint - requires any valid JWT token
 */
router.get('/protected', (req, res) => {
  res.json({
    message: 'Access granted to protected resource',
    timestamp: new Date().toISOString(),
    user: {
      sub: req.user.sub,
      email: req.user.email || req.user.preferred_username,
      name: req.user.name,
      scopes: req.user.scp || []
    }
  });
});

/**
 * GET /api/userinfo
 *
 * Returns user information from JWT claims
 */
router.get('/userinfo', (req, res) => {
  res.json({
    sub: req.user.sub,
    email: req.user.email,
    name: req.user.name,
    preferred_username: req.user.preferred_username,
    given_name: req.user.given_name,
    family_name: req.user.family_name,
    locale: req.user.locale,
    zoneinfo: req.user.zoneinfo,
    updated_at: req.user.updated_at,
    email_verified: req.user.email_verified
  });
});

/**
 * GET /api/scope-test
 *
 * Demonstrates scope-based authorization
 * Requires 'profile' scope in access token
 */
router.get('/scope-test', requireScope('profile'), (req, res) => {
  res.json({
    message: 'Scope-based authorization successful',
    requiredScope: 'profile',
    userScopes: req.user.scp || [],
    timestamp: new Date().toISOString()
  });
});

/**
 * GET /api/admin
 *
 * Demonstrates claims-based authorization
 * Requires specific claim value (example: admin role)
 *
 * Note: This is an example. You would need to configure
 * custom claims in your Okta authorization server.
 */
router.get('/admin', (req, res) => {
  // Example: Check if user has admin role (custom claim)
  const userGroups = req.user.groups || [];

  if (!userGroups.includes('Administrators')) {
    return res.status(403).json({
      error: 'Forbidden',
      message: 'Admin access required',
      userGroups: userGroups
    });
  }

  res.json({
    message: 'Admin access granted',
    user: req.user.sub,
    groups: userGroups,
    timestamp: new Date().toISOString()
  });
});

/**
 * GET /api/token-info
 *
 * Returns detailed information about the JWT token
 * (for debugging and educational purposes)
 */
router.get('/token-info', (req, res) => {
  const jwt = req.jwt;

  res.json({
    header: jwt.header,
    claims: jwt.claims,
    expiresAt: new Date(jwt.claims.exp * 1000).toISOString(),
    issuedAt: new Date(jwt.claims.iat * 1000).toISOString(),
    issuer: jwt.claims.iss,
    audience: jwt.claims.aud,
    subject: jwt.claims.sub,
    scopes: jwt.claims.scp || [],
    clientId: jwt.claims.cid,
    timeUntilExpiration: `${jwt.claims.exp - Math.floor(Date.now() / 1000)} seconds`
  });
});

/**
 * POST /api/echo
 *
 * Echo endpoint for testing POST requests with authentication
 */
router.post('/echo', (req, res) => {
  res.json({
    message: 'Echo endpoint',
    receivedBody: req.body,
    user: req.user.sub,
    timestamp: new Date().toISOString()
  });
});

/**
 * GET /api/data
 *
 * Example endpoint that would return application-specific data
 */
router.get('/data', (req, res) => {
  // In a real application, you would query a database here
  const mockData = [
    { id: 1, name: 'Item 1', description: 'First item' },
    { id: 2, name: 'Item 2', description: 'Second item' },
    { id: 3, name: 'Item 3', description: 'Third item' }
  ];

  res.json({
    data: mockData,
    user: req.user.sub,
    timestamp: new Date().toISOString()
  });
});

module.exports = router;

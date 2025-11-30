/**
 * Node.js Protected API Server
 *
 * RESTful API with Okta JWT token verification.
 * Demonstrates scope-based authorization and secure API design.
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const oktaJwtVerifier = require('./middleware/oktaJwtVerifier');
const protectedRoutes = require('./routes/protected');

const app = express();
const PORT = process.env.PORT || 8080;

// Security middleware
app.use(helmet());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});

app.use('/api/', limiter);

// CORS configuration
const allowedOrigins = process.env.ALLOWED_ORIGINS
  ? process.env.ALLOWED_ORIGINS.split(',')
  : ['http://localhost:3000'];

app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (like mobile apps or curl requests)
    if (!origin) return callback(null, true);

    if (allowedOrigins.indexOf(origin) === -1) {
      const msg = 'The CORS policy for this site does not allow access from the specified Origin.';
      return callback(new Error(msg), false);
    }
    return callback(null, true);
  },
  credentials: true
}));

// Body parser
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging middleware (development)
if (process.env.NODE_ENV === 'development') {
  app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
    next();
  });
}

// Public routes
app.get('/', (req, res) => {
  res.json({
    message: 'Okta SSO Hub - Protected API',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      protected: '/api/protected (requires authentication)',
      userInfo: '/api/userinfo (requires authentication)',
      scopeTest: '/api/scope-test (requires specific scope)'
    },
    documentation: 'https://github.com/MikeDominic92/okta-sso-hub'
  });
});

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Protected routes (require JWT authentication)
app.use('/api', oktaJwtVerifier, protectedRoutes);

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.method} ${req.path} not found`,
    timestamp: new Date().toISOString()
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);

  if (err.name === 'UnauthorizedError' || err.message.includes('JWT')) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid or expired token',
      timestamp: new Date().toISOString()
    });
  }

  res.status(err.status || 500).json({
    error: err.name || 'Internal Server Error',
    message: err.message || 'An unexpected error occurred',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log('\n========================================');
  console.log('🚀 Okta SSO Hub - Protected API Server');
  console.log('========================================');
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`Server running on: http://localhost:${PORT}`);
  console.log(`Okta Issuer: ${process.env.OKTA_ISSUER}`);
  console.log(`Allowed Origins: ${allowedOrigins.join(', ')}`);
  console.log('========================================\n');
  console.log('Endpoints:');
  console.log(`  GET  /               - API information`);
  console.log(`  GET  /health         - Health check`);
  console.log(`  GET  /api/protected  - Protected endpoint (requires JWT)`);
  console.log(`  GET  /api/userinfo   - User information from token`);
  console.log(`  GET  /api/scope-test - Scope-based authorization test`);
  console.log('\n');
});

module.exports = app;

# SCIM 2.0 Server

System for Cross-domain Identity Management (SCIM) server for automated provisioning from Okta.

## Features

- SCIM 2.0 compliant endpoints
- User CRUD operations
- Group management
- SQLite database for user storage
- Bearer token authentication

## Setup

```bash
pip install -r requirements.txt
python scim_server.py
```

Runs on: `http://localhost:5001`

## Configuration

See [SCIM Provisioning Guide](../docs/SCIM_PROVISIONING.md) for complete setup instructions.

---

**Built with:** Flask • SCIM 2.0 • SQLite

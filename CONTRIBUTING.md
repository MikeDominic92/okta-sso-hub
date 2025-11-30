# Contributing to Okta SSO Hub

Thank you for your interest in contributing to Okta SSO Hub! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/MikeDominic92/okta-sso-hub/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Node/Python version, etc.)
   - Screenshots if applicable

### Suggesting Enhancements

1. Check existing [Issues](https://github.com/MikeDominic92/okta-sso-hub/issues) and [Pull Requests](https://github.com/MikeDominic92/okta-sso-hub/pulls)
2. Create an issue describing:
   - Use case and motivation
   - Proposed solution
   - Alternative solutions considered
   - Impact on existing functionality

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/MikeDominic92/okta-sso-hub.git
   cd okta-sso-hub
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clear, commented code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Python tests
   pytest tests/

   # Node.js tests
   cd apps/node-api && npm test

   # React tests
   cd apps/react-oidc-spa && npm test
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting, etc.)
   - `refactor:` - Code refactoring
   - `test:` - Adding or updating tests
   - `chore:` - Maintenance tasks

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template
   - Link related issues

## Development Setup

### Prerequisites

- Node.js 18.x or higher
- Python 3.9 or higher
- Okta Developer Account
- Git

### Local Development

1. **Clone and install dependencies**
   ```bash
   git clone https://github.com/MikeDominic92/okta-sso-hub.git
   cd okta-sso-hub

   # React app
   cd apps/react-oidc-spa
   npm install

   # Node API
   cd ../node-api
   npm install

   # Flask app
   cd ../flask-saml-sp
   pip install -r requirements.txt

   # Python automation
   cd ../../automation/python
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   - Copy `.env.example` files to `.env` in each directory
   - Update with your Okta developer credentials

3. **Run applications**
   - Follow Quick Start guides in each app's README

## Code Style

### Python
- Follow [PEP 8](https://pep8.org/)
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable names

### JavaScript/TypeScript
- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use ESLint and Prettier
- Prefer `const` over `let`
- Use TypeScript for type safety

### Documentation
- Use Markdown for documentation
- Keep line length under 100 characters
- Include code examples
- Update README when adding features

## Testing Guidelines

### Unit Tests
- Write tests for all new functions
- Aim for >80% code coverage
- Use descriptive test names
- Test edge cases and error handling

### Integration Tests
- Test complete user flows
- Verify Okta integration works end-to-end
- Test authentication and authorization

### Test Structure
```python
# Python example
def test_create_user_success():
    """Test successful user creation with valid data."""
    # Arrange
    user_data = {...}

    # Act
    result = create_user(user_data)

    # Assert
    assert result.status == 'ACTIVE'
```

## Documentation

When adding features, update:
- [ ] README.md - If changing setup or adding apps
- [ ] Relevant docs/ files - For Okta configuration changes
- [ ] Code comments - For complex logic
- [ ] CHANGELOG.md - For version changes

## Release Process

1. Update version in `package.json` files
2. Update CHANGELOG.md with changes
3. Create Git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub release with notes

## Questions?

- Open an issue for discussion
- Check existing documentation in `docs/`
- Review closed issues and PRs for similar questions

## Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Release notes
- GitHub contributors page

Thank you for contributing to Okta SSO Hub!

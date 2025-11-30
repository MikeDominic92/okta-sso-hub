"""
Flask SAML Service Provider

Demonstrates SAML 2.0 SSO integration with Okta as Identity Provider.
Implements SSO, SLO, and attribute mapping.
"""

import os
import json
from flask import Flask, request, redirect, session, render_template_string, url_for
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key_change_in_production')

# SAML settings path
SAML_PATH = os.path.join(os.path.dirname(__file__), 'saml')


def init_saml_auth(req):
    """
    Initialize SAML authentication object

    Args:
        req: Dictionary with request data

    Returns:
        OneLogin_Saml2_Auth instance
    """
    auth = OneLogin_Saml2_Auth(req, custom_base_path=SAML_PATH)
    return auth


def prepare_flask_request(request):
    """
    Prepare Flask request for SAML library

    Args:
        request: Flask request object

    Returns:
        Dictionary with request data formatted for python3-saml
    """
    # Extract host and port
    url_data = request.url.split('://', 1)
    scheme = url_data[0]
    host = url_data[1].split('/', 1)[0]

    return {
        'https': 'on' if scheme == 'https' else 'off',
        'http_host': host,
        'script_name': request.path,
        'server_port': request.environ.get('SERVER_PORT', '5000'),
        'get_data': request.args.copy(),
        'post_data': request.form.copy(),
        'query_string': request.query_string.decode('utf-8')
    }


@app.route('/')
def index():
    """Landing page - shows login button or user info if authenticated"""
    if 'samlUserdata' in session:
        # User is authenticated
        attributes = session['samlUserdata']
        name_id = session.get('samlNameId', 'Unknown')

        return render_template_string(DASHBOARD_TEMPLATE,
                                     name_id=name_id,
                                     attributes=attributes)
    else:
        # User not authenticated - show login page
        return render_template_string(LOGIN_TEMPLATE)


@app.route('/login')
def saml_login():
    """Initiate SAML SSO login flow"""
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)

    # Redirect to Okta for authentication
    return redirect(auth.login())


@app.route('/saml/acs', methods=['POST'])
def saml_acs():
    """
    Assertion Consumer Service (ACS)

    Receives SAML response from Okta after successful authentication.
    Validates assertion and creates session.
    """
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)

    # Process SAML response
    auth.process_response()
    errors = auth.get_errors()

    if errors:
        error_reason = auth.get_last_error_reason()
        return render_template_string(ERROR_TEMPLATE,
                                     errors=errors,
                                     error_reason=error_reason), 400

    # Check if user is authenticated
    if not auth.is_authenticated():
        return render_template_string(ERROR_TEMPLATE,
                                     errors=['Not authenticated'],
                                     error_reason='Authentication failed'), 401

    # Store user data in session
    session['samlUserdata'] = auth.get_attributes()
    session['samlNameId'] = auth.get_nameid()
    session['samlNameIdFormat'] = auth.get_nameid_format()
    session['samlNameIdNameQualifier'] = auth.get_nameid_nq()
    session['samlNameIdSPNameQualifier'] = auth.get_nameid_spnq()
    session['samlSessionIndex'] = auth.get_session_index()

    # Redirect to original URL or dashboard
    self_url = OneLogin_Saml2_Utils.get_self_url(req)
    if 'RelayState' in request.form and self_url != request.form['RelayState']:
        return redirect(auth.redirect_to(request.form['RelayState']))

    return redirect(url_for('index'))


@app.route('/saml/metadata')
def saml_metadata():
    """
    Generate and return SP metadata XML

    This endpoint provides SAML metadata for the Service Provider
    which can be uploaded to Okta or used for manual configuration.
    """
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if errors:
        return render_template_string(ERROR_TEMPLATE,
                                     errors=errors,
                                     error_reason='Invalid SP metadata'), 500

    return metadata, 200, {'Content-Type': 'text/xml'}


@app.route('/saml/sls', methods=['GET', 'POST'])
def saml_sls():
    """
    Single Logout Service (SLS)

    Handles logout requests from Okta (IdP-initiated logout)
    and logout responses (SP-initiated logout).
    """
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)

    # Process SLO request/response
    url = auth.process_slo(delete_session_cb=lambda: session.clear())
    errors = auth.get_errors()

    if errors:
        error_reason = auth.get_last_error_reason()
        return render_template_string(ERROR_TEMPLATE,
                                     errors=errors,
                                     error_reason=error_reason), 400

    if url:
        return redirect(url)

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """
    Initiate SP-initiated logout

    Logs out from local session and sends SLO request to Okta.
    """
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)

    # Get session data for SLO
    name_id = session.get('samlNameId')
    session_index = session.get('samlSessionIndex')
    name_id_format = session.get('samlNameIdFormat')
    name_id_nq = session.get('samlNameIdNameQualifier')
    name_id_spnq = session.get('samlNameIdSPNameQualifier')

    # Clear local session
    session.clear()

    # Send SLO request to Okta
    return redirect(auth.logout(
        name_id=name_id,
        session_index=session_index,
        nq=name_id_nq,
        name_id_format=name_id_format,
        spnq=name_id_spnq
    ))


@app.route('/attributes')
def attributes():
    """Display raw SAML attributes from session"""
    if 'samlUserdata' not in session:
        return redirect(url_for('index'))

    attributes = session.get('samlUserdata', {})
    name_id = session.get('samlNameId', 'Unknown')

    return render_template_string(ATTRIBUTES_TEMPLATE,
                                 name_id=name_id,
                                 attributes=json.dumps(attributes, indent=2))


# HTML Templates (inline for simplicity)

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask SAML SP - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 { font-size: 32px; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .content { padding: 40px 30px; }
        .content h2 { margin-bottom: 15px; color: #333; }
        .content p { color: #666; margin-bottom: 30px; line-height: 1.6; }
        .features { margin-bottom: 30px; }
        .feature {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            color: #555;
        }
        .check {
            width: 24px;
            height: 24px;
            background: #4caf50;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            font-weight: bold;
        }
        .button {
            display: block;
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        .button:hover { transform: translateY(-2px); }
        .footer {
            background: #f8f8f8;
            padding: 20px 30px;
            text-align: center;
            border-top: 1px solid #e0e0e0;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h1>🔐 Flask SAML SP</h1>
            <p>SAML 2.0 Service Provider</p>
        </div>
        <div class="content">
            <h2>Welcome!</h2>
            <p>This application demonstrates SAML 2.0 Single Sign-On integration with Okta as the Identity Provider.</p>
            <div class="features">
                <div class="feature">
                    <span class="check">✓</span>
                    <span>SAML 2.0 SSO (Single Sign-On)</span>
                </div>
                <div class="feature">
                    <span class="check">✓</span>
                    <span>SLO (Single Logout)</span>
                </div>
                <div class="feature">
                    <span class="check">✓</span>
                    <span>Attribute Mapping from Okta</span>
                </div>
                <div class="feature">
                    <span class="check">✓</span>
                    <span>SP Metadata Generation</span>
                </div>
            </div>
            <a href="/login" class="button">Login with Okta SAML</a>
        </div>
        <div class="footer">
            <p>IAM Portfolio Project | Built with Flask + python3-saml</p>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Flask SAML SP</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: white;
            border-radius: 12px;
            padding: 20px 30px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { color: #333; }
        .header p { color: #666; margin-top: 5px; }
        .logout-btn {
            padding: 12px 24px;
            background: #dc3545;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .card h2 { margin-bottom: 20px; color: #333; }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
        }
        .info-item {
            padding: 12px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        .label {
            font-size: 13px;
            color: #888;
            font-weight: 600;
            display: block;
            margin-bottom: 4px;
        }
        .value {
            font-size: 16px;
            color: #333;
            word-break: break-all;
        }
        .badge {
            display: inline-block;
            padding: 6px 12px;
            background: #4caf50;
            color: white;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 600;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>Dashboard</h1>
                <p>You are authenticated via SAML 2.0</p>
            </div>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>

        <div class="card">
            <h2>User Information</h2>
            <div class="info-grid">
                <div class="info-item">
                    <span class="label">NameID (Subject):</span>
                    <span class="value">{{ name_id }}</span>
                </div>
                {% for key, values in attributes.items() %}
                <div class="info-item">
                    <span class="label">{{ key }}:</span>
                    <span class="value">{{ values[0] if values else 'N/A' }}</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="card">
            <h2>SAML Attributes</h2>
            <p style="margin-bottom: 15px; color: #666;">
                These attributes were received from Okta in the SAML assertion:
            </p>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                <span class="badge">firstName: {{ attributes.get('firstName', ['N/A'])[0] }}</span>
                <span class="badge">lastName: {{ attributes.get('lastName', ['N/A'])[0] }}</span>
                <span class="badge">email: {{ attributes.get('email', ['N/A'])[0] }}</span>
            </div>
            <p style="margin-top: 20px;">
                <a href="/attributes" style="color: #667eea; text-decoration: none; font-weight: 600;">
                    View Raw Attributes →
                </a>
            </p>
        </div>
    </div>
</body>
</html>
"""

ATTRIBUTES_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SAML Attributes - Flask SAML SP</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .card h1 { margin-bottom: 20px; color: #333; }
        pre {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.6;
        }
        .back-btn {
            display: inline-block;
            margin-top: 20px;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>Raw SAML Attributes</h1>
            <p style="margin-bottom: 20px; color: #666;">
                <strong>NameID:</strong> {{ name_id }}
            </p>
            <pre>{{ attributes }}</pre>
            <a href="/" class="back-btn">← Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

ERROR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Error - Flask SAML SP</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 40px;
            max-width: 600px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #dc3545; margin-bottom: 20px; }
        .error-box {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        pre {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
        }
        .back-btn {
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>⚠️ SAML Error</h1>
        <div class="error-box">
            <strong>Error Reason:</strong><br>
            {{ error_reason }}
        </div>
        {% if errors %}
        <p><strong>Error Details:</strong></p>
        <pre>{{ errors }}</pre>
        {% endif %}
        <a href="/" class="back-btn">← Back to Home</a>
    </div>
</body>
</html>
"""


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

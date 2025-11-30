# Cost Analysis

Complete cost breakdown for the Okta SSO Hub portfolio project.

## Total Cost: $0/month

This project is 100% free using Okta's developer tier and open-source tools.

## Okta Developer Tier

### Included Features

| Feature | Free Tier Limit | Cost |
|---------|----------------|------|
| **Monthly Active Users (MAU)** | 1,000 | $0 |
| **Applications** | Unlimited | $0 |
| **SAML 2.0** | ✅ Included | $0 |
| **OIDC/OAuth 2.0** | ✅ Included | $0 |
| **SCIM 2.0** | ✅ Included | $0 |
| **Multi-Factor Auth** | ✅ Included | $0 |
| **Okta Verify** | ✅ Included | $0 |
| **Email MFA** | ✅ Included | $0 |
| **SMS MFA** | Limited credits | $0* |
| **API Calls** | 500/minute | $0 |
| **Universal Directory** | ✅ Included | $0 |
| **Groups** | Unlimited | $0 |
| **Okta Workflows** | 10 active flows | $0 |
| **ThreatInsight** | Basic | $0 |
| **API Access Management** | 1 auth server | $0 |
| **Custom Domains** | ❌ Not included | N/A |
| **Support** | Community forums | $0 |

**Total Monthly Cost:** **$0**

*SMS MFA requires Twilio integration or Okta telephony credits (limited free tier).

### What You Get

For a portfolio/demo project with <100 test users:

✅ **Full Enterprise Features:**
- All authentication protocols (SAML, OIDC, SCIM)
- Multi-factor authentication
- Adaptive authentication policies
- API automation capabilities
- Workflow automation (limited)

✅ **No Expiration:**
- Developer account never expires
- No credit card required
- No trial period limitations

✅ **Production-Grade:**
- Same platform used by enterprises
- Real Okta infrastructure
- Suitable for demonstrations to employers

### Limitations

**Free Tier Restrictions:**

1. **Monthly Active Users:** 1,000 limit
   - Impact: None for portfolio (expected <100 users)
   - Workaround: Not needed

2. **SMS Credits:** Limited free SMS
   - Impact: ~50 free SMS per month
   - Workaround: Use Email or Okta Verify instead

3. **API Rate Limits:** 500 requests/minute
   - Impact: Sufficient for demos and automation scripts
   - Workaround: Implement exponential backoff

4. **Workflows:** 10 active flows
   - Impact: Enough for demo workflows
   - Workaround: Deactivate unused flows

5. **Custom Domains:** Not available
   - Impact: Uses `dev-12345678.okta.com` domain
   - Workaround: Acceptable for portfolio

6. **Support:** Community-only
   - Impact: No direct support tickets
   - Workaround: Developer forums are active

**Not a Limitation for This Project:**
- Single authorization server (we only need one)
- No advanced admin roles (developer is admin)
- No lifecycle management hooks (can use API instead)

## Infrastructure Costs

### Development Environment

All applications run locally on your machine - no hosting costs:

| Component | Hosting | Cost |
|-----------|---------|------|
| React SPA | localhost:3000 | $0 |
| Flask SAML App | localhost:5000 | $0 |
| Node.js API | localhost:8080 | $0 |
| SCIM Server | localhost:5001 | $0 |
| Database (SQLite) | Local file | $0 |

**Total Infrastructure Cost:** **$0**

### Production Deployment (Optional)

If deploying to production for live demo:

| Service | Option | Free Tier | Cost |
|---------|--------|-----------|------|
| **Frontend Hosting** | Vercel | ✅ Yes | $0 |
| | Netlify | ✅ Yes | $0 |
| | GitHub Pages | ✅ Yes | $0 |
| **Backend Hosting** | Heroku | ✅ 1000 hrs/mo | $0 |
| | Railway | ✅ 500 hrs/mo | $0 |
| | Render | ✅ 750 hrs/mo | $0 |
| **Database** | PostgreSQL (Heroku) | ✅ 10k rows | $0 |
| | MongoDB Atlas | ✅ 512 MB | $0 |
| **SSL Certificate** | Let's Encrypt | ✅ Yes | $0 |
| **Domain** | Freenom (.tk/.ml) | ✅ Yes | $0 |
| | Your existing domain | ✅ If owned | $0 |

**Production Hosting:** **$0** (using free tiers)

## Software & Tools

All tools are free and open-source:

| Tool | Purpose | License | Cost |
|------|---------|---------|------|
| **Node.js** | JavaScript runtime | MIT | $0 |
| **Python** | Backend language | PSF | $0 |
| **React** | Frontend framework | MIT | $0 |
| **Flask** | Python web framework | BSD | $0 |
| **Express** | Node.js framework | MIT | $0 |
| **TypeScript** | Type-safe JavaScript | Apache 2.0 | $0 |
| **Git** | Version control | GPL | $0 |
| **VS Code** | Code editor | MIT | $0 |
| **Postman** | API testing | Free tier | $0 |
| **GitHub** | Code hosting | Free (public repos) | $0 |

**Total Software Cost:** **$0**

## Okta SDKs & Libraries

All Okta SDKs are free and open-source:

| SDK | NPM/PyPI Package | License | Cost |
|-----|------------------|---------|------|
| Okta React SDK | @okta/okta-react | Apache 2.0 | $0 |
| Okta Auth JS | @okta/okta-auth-js | Apache 2.0 | $0 |
| Okta JWT Verifier (Node) | @okta/jwt-verifier | Apache 2.0 | $0 |
| Okta Python SDK | okta-sdk-python | Apache 2.0 | $0 |
| Python SAML | python3-saml | MIT | $0 |

**Total SDK Cost:** **$0**

## Certification Costs

### Okta Certified Professional

| Item | Cost |
|------|------|
| **Study Materials** | Free (Okta website) |
| **Practice Exams** | Free (Okta training) |
| **Certification Exam** | $150 |
| **Renewal** | $50/year |

**Note:** Certification is optional but recommended for career advancement.

## Time Investment

Estimated time to build complete project:

| Phase | Hours | Hourly Value* | Opportunity Cost |
|-------|-------|---------------|------------------|
| Setup & Configuration | 8 | $50 | $400 |
| React App Development | 12 | $50 | $600 |
| Flask App Development | 10 | $50 | $500 |
| Node.js API Development | 8 | $50 | $400 |
| SCIM Server Development | 10 | $50 | $500 |
| Automation Scripts | 8 | $50 | $400 |
| Documentation | 12 | $50 | $600 |
| Testing & Debugging | 8 | $50 | $400 |
| **Total** | **76 hours** | - | **$3,800** |

*Estimated value for mid-level developer time.

**ROI Consideration:**
- Portfolio projects demonstrate skills to employers
- Can lead to higher salary offers ($10k-$20k increase)
- One job offer covers time investment 3-5x over

## Comparison: Okta vs Alternatives

| Provider | Free Tier | Protocols | Cost for 1000 MAU |
|----------|-----------|-----------|-------------------|
| **Okta (Developer)** | 1,000 MAU | SAML, OIDC, SCIM | **$0** |
| Auth0 | 7,000 MAU* | SAML*, OIDC, SCIM* | $0 (limited features) |
| Azure AD | 50,000 objects | SAML, OIDC, SCIM | $6/user/month** |
| Keycloak | Unlimited | SAML, OIDC | Self-hosted (infra cost) |
| AWS Cognito | 50,000 MAU | OIDC, SAML* | $0.0055/MAU = $5.50 |
| Google Identity | Varies | OIDC, SAML* | Varies |

*Some features limited or require paid tier
**Azure AD Free has many restrictions; Premium P1 needed for full features

**Winner for Portfolio:** Okta (best features for $0)

## Annual Cost Projection

### Year 1
- Okta Developer: $0
- Local development: $0
- GitHub hosting: $0
- **Total:** **$0**

### Year 2-3
- Same as Year 1: $0
- Optional: Okta Certification renewal: $50/year

### Scaling Costs (If Project Grows)

**If exceeding 1,000 MAU:**

Okta pricing (for reference):
- Workforce Identity Cloud: ~$2-$8/user/month
- Customer Identity Cloud: ~$0.03-$0.15/MAU

**For portfolio:** Unlikely to exceed free tier limits.

## Hidden Costs

### None! But Consider:

1. **Internet Connection:** Required (you already have this)
2. **Computer:** Any modern laptop works (you already have this)
3. **Phone:** For MFA testing with Okta Verify (you already have this)
4. **Time:** 76 hours (see time investment above)

## Value Delivered

### What You Get for $0:

✅ **Technical Skills:**
- SAML 2.0 expertise
- OIDC/OAuth 2.0 mastery
- SCIM provisioning knowledge
- API automation experience
- Modern web development (React, Node, Python)

✅ **Portfolio Assets:**
- GitHub repository
- Live demo applications
- Comprehensive documentation
- Code samples for interviews

✅ **Certification Preparation:**
- Hands-on Okta experience
- Real-world configuration practice
- Troubleshooting skills

✅ **Career Benefits:**
- Demonstrates initiative
- Shows enterprise IAM knowledge
- Practical proof of skills
- Talking points for interviews

**Estimated Value:** $3,800-$5,000 in equivalent training

## Cost Optimization Tips

### Stay Within Free Tier

1. **Monitor MAU:**
   - Delete inactive test users
   - Use <100 users for demos
   - Don't share publicly (prevents random signups)

2. **Optimize API Calls:**
   - Cache responses when possible
   - Use pagination effectively
   - Implement exponential backoff

3. **MFA Strategy:**
   - Prefer Email and Okta Verify (free)
   - Limit SMS usage (costs after free credits)
   - Use TOTP authenticators (free)

4. **Workflow Limits:**
   - Keep only 10 flows active
   - Deactivate unused flows
   - Combine related logic

### If Upgrading Later

**Not needed for portfolio**, but if scaling:

- Start with Workforce Identity ($2/user/month)
- Only pay for active users
- Monthly billing (no annual commitment)
- Cancel anytime

## Summary

| Category | Cost |
|----------|------|
| Okta Developer Tier | **$0** |
| Infrastructure (Local Dev) | **$0** |
| Software & Tools | **$0** |
| SDKs & Libraries | **$0** |
| Hosting (Optional Production) | **$0** (free tiers) |
| **Grand Total** | **$0/month** |

**Certification (Optional):** $150 one-time + $50/year renewal

---

**Bottom Line:** This entire IAM portfolio project costs nothing to build and maintain, while providing thousands of dollars in career value. The only investment is your time, which pays dividends in job opportunities and skill development.

## Questions?

**"Is the free tier really unlimited time-wise?"**
Yes! Okta developer accounts never expire.

**"Will I hit rate limits?"**
Unlikely. 500 requests/minute is more than enough for demos and automation scripts.

**"Can I use this in job interviews?"**
Absolutely! This is a production-ready demo showcasing enterprise IAM skills.

**"What if I need more than 1,000 MAU?"**
For a portfolio project, you won't. If building a real product, upgrade to paid tier.

## Next Steps

- [Set Up Okta Account](OKTA_SETUP.md) - Still $0!
- [Review Security Practices](SECURITY.md)
- [Start Building Apps](../apps/)

---

**Cost Analysis Complete!** Build enterprise-grade IAM skills without spending a dime.

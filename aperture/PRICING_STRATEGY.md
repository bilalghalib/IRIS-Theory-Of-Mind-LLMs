# Pricing Strategy & Rationale

## Recommended Pricing Tiers

### Free Tier - "Get Started"
**$0/month**
- 1,000 assessments/month
- 2 users tracked
- Basic constructs (3 pre-built)
- Community support
- 7-day data retention

**Why this works:**
- Low enough for indie hackers to try
- High enough to validate product-market fit
- Limits prevent abuse
- Forces upgrade at scale

### Starter - "Ship Faster"
**$29/month** (or $290/year - save 17%)
- 5,000 assessments/month
- 100 users tracked
- All pre-built constructs
- Custom constructs (up to 3)
- Email support
- 30-day data retention

**Target:** Solo developers, small startups
**Rationale:** Lower entry point than $49, more attractive

### Pro - "Scale Smart"
**$99/month** (or $990/year - save 17%)
- 25,000 assessments/month
- 1,000 users tracked
- Unlimited custom constructs
- Pattern discovery
- Weekly insights emails
- Priority email support
- 90-day data retention
- Webhooks (10/month)

**Target:** Growing startups, product teams
**Rationale:** Sweet spot for product-market fit companies

### Business - "Grow Confident"
**$299/month** (or $2,990/year - save 17%)
- 100,000 assessments/month
- 10,000 users tracked
- Everything in Pro, plus:
- Multi-model consensus
- Temporal analytics
- Unlimited webhooks
- Slack/Discord integration
- Video onboarding call
- 1-year data retention

**Target:** Established companies, enterprise teams
**Rationale:** Clear ROI at this scale

### Enterprise - "Custom Everything"
**Custom pricing** (starts at $999/month)
- Unlimited everything
- On-premise deployment option
- SSO / SAML
- SLA (99.9% uptime)
- Dedicated support
- Custom integrations
- Training & workshops
- Unlimited data retention

**Target:** Large companies, compliance-heavy industries

---

## Overage Pricing

**All paid tiers:**
- $0.01 per additional assessment
- Alerts at 80% and 100% of quota
- Automatic billing (can set hard caps)

**Example:**
Pro plan user processes 30,000 assessments:
- Base: $99
- Overage: 5,000 × $0.01 = $50
- Total: $149

---

## Add-ons

### Extra Data Retention
- +30 days: $19/month
- +90 days: $49/month
- +1 year: $99/month

### Priority Support Upgrade
- 4-hour SLA: +$49/month
- 1-hour SLA: +$149/month

### Custom Model Training
- Train on your data: $499 one-time + $99/month

### White Label
- Remove Aperture branding: +$199/month

---

## Special Programs

### Startup Program
**50% off for 1 year** if you:
- Raised <$2M
- Team <10 people
- Apply via YC, Techstars, or similar

### Open Source Discount
**Free Pro plan** if you:
- Have 1,000+ GitHub stars
- OSS project using Aperture
- Include "Powered by Aperture" badge

### Education Program
**Free Business plan** for:
- Accredited universities
- Research institutions
- Used for education/research only

---

## Pricing Philosophy

### 1. Value Metric: Assessments
**1 assessment = 1 extracted insight**

Examples:
- User message extracts 3 assessments → 3 counted
- Pattern discovery finds 10 patterns → 0 counted (bonus feature)
- User correction → 0 counted (encouraging improvement)

Clear, usage-based, fair.

### 2. Progressive Disclosure
- Start free, upgrade as you grow
- No credit card for free tier
- Easy self-serve upgrade
- Annual discount encourages commitment

### 3. Competitive Positioning

vs **Mixpanel/Amplitude** ($25-$200/month):
- Similar pricing but different value (conversations vs events)
- Our advantage: Richer context, explanatory

vs **ChatGPT Enterprise** ($25-60/user/month):
- Cheaper at scale (usage-based vs per-seat)
- Our advantage: Multi-provider, BYOK, transparency

vs **Customer.io** ($100-$1,000/month):
- Similar pricing structure
- Our advantage: Auto-discovery, AI-native

### 4. Why This Works

**Free → Starter ($29):**
- Low enough to impulse-buy
- 5x more assessments
- Removes data retention anxiety

**Starter → Pro ($99):**
- Clear inflection point (pattern discovery)
- 5x more assessments
- Unlimited constructs = serious use

**Pro → Business ($299):**
- Multi-model consensus (premium feature)
- 4x more assessments
- Integrations unlock team value

**Business → Enterprise (Custom):**
- Compliance/security features
- White glove service
- Clear enterprise needs

---

## Revenue Projections

### Conservative (Year 1)
- 1,000 free users
- 50 Starter ($29) = $1,450/mo
- 20 Pro ($99) = $1,980/mo
- 5 Business ($299) = $1,495/mo
- 2 Enterprise ($999) = $1,998/mo

**Total: $6,923/mo = $83k ARR**

### Moderate (Year 1)
- 2,000 free users
- 100 Starter = $2,900/mo
- 50 Pro = $4,950/mo
- 15 Business = $4,485/mo
- 5 Enterprise ($1,500 avg) = $7,500/mo

**Total: $19,835/mo = $238k ARR**

### Optimistic (Year 1)
- 5,000 free users
- 200 Starter = $5,800/mo
- 100 Pro = $9,900/mo
- 30 Business = $8,970/mo
- 10 Enterprise ($2,000 avg) = $20,000/mo

**Total: $44,670/mo = $536k ARR**

---

## Pricing Page Copy

### Above the Fold
**Headline:** "Pricing that grows with you"
**Subhead:** "Start free. Upgrade when you're ready. Cancel anytime."

### FAQ Section

**Q: What counts as an assessment?**
A: Each extracted insight from a conversation. If a user message results in detecting "technical_confidence: 0.7" and "emotional_state: curious", that's 2 assessments.

**Q: What happens if I exceed my limit?**
A: You'll get alerts at 80% and 100%. We'll automatically bill overages at $0.01/assessment, or you can set a hard cap.

**Q: Can I change plans anytime?**
A: Yes! Upgrade instantly. Downgrading takes effect next billing cycle. Prorated refunds available.

**Q: Do you offer refunds?**
A: 30-day money-back guarantee on annual plans. Monthly plans are billed in advance, no refunds, but you can cancel anytime.

**Q: Is there a discount for annual plans?**
A: Yes! Save 17% by paying annually.

**Q: Do you offer custom plans?**
A: Absolutely. Contact sales for custom assessment volumes, features, or deployment options.

**Q: What payment methods do you accept?**
A: Credit card (Visa, MC, Amex), ACH (for annual plans), or invoice (Enterprise only, $10k+ contracts).

---

## Pricing Calculator

Interactive tool on pricing page:

**Inputs:**
- Conversations per month: [slider 100-1,000,000]
- Average assessments per conversation: [3] (default)
- Estimated users tracked: [auto-calculated]

**Output:**
```
Estimated monthly assessments: 15,000
Recommended plan: Pro ($99/month)

With Pro you get:
✓ 25,000 assessments/month (10k headroom)
✓ Pattern discovery
✓ Unlimited custom constructs
✓ Priority support

Estimated annual cost: $1,188 ($990 if paid yearly - save $198)
```

**CTA:** "Start Free Trial" (14 days Pro, no credit card)

---

## Pricing Principles Summary

1. **Usage-based** - Fair, scales with value
2. **Transparent** - No hidden fees, clear limits
3. **Accessible** - Free tier + low $29 entry
4. **Predictable** - Monthly/annual options
5. **Flexible** - Easy upgrades, fair downgrades
6. **Competitive** - Priced vs Mixpanel, not vs ChatGPT API costs

**Positioning:** Premium but fair. "Mixpanel for AI" pricing, not "AWS" pricing.

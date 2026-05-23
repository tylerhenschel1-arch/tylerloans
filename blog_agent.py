import anthropic
import os
import json
import datetime
import re

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

TOPICS = [
    "How business owners in Katy TX can save thousands using the All-In-One mortgage",
    "VA loan benefits most Houston veterans don't know about",
    "FHA loans in Texas — complete guide for first time buyers in 2025",
    "Construction loans in Katy TX — what you need to know before you build",
    "How real estate investors use the AIO loan to preserve liquidity",
    "Conventional vs FHA loans in Houston — which is right for you",
    "How physicians and doctors can optimize their mortgage in Texas",
    "Self-employed mortgage guide for Houston business owners",
    "First time home buyer programs in Katy TX 2025",
    "How to use home equity as a business owner in Texas",
    "All-In-One mortgage vs HELOC — what is the difference",
    "Renovation loans in Houston — complete guide",
    "How to reduce mortgage interest without refinancing",
    "Builder spec financing in Katy TX — what developers need to know",
    "Jumbo loans in Houston — qualifying as a high income borrower",
    "How financial planners use the AIO loan for client wealth optimization",
    "Mortgage tips for real estate investors in the Houston market",
    "Custom home construction loans in Katy TX — step by step guide",
    "How to pay off your mortgage faster without extra payments",
    "Texas mortgage rates — what drives them and how to get the best rate",
]

day_of_year = datetime.datetime.now().timetuple().tm_yday
topic = TOPICS[day_of_year % len(TOPICS)]
date_str = datetime.datetime.now().strftime("%B %d, %Y")

slug = topic.lower()
slug = re.sub(r'[^a-z0-9\s]', '', slug)
slug = re.sub(r'\s+', '-', slug.strip())
slug = slug[:60].rstrip('-')

print(f"Writing: {topic}")

message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=2000,
    messages=[{
        "role": "user",
        "content": f"""Write an SEO-optimized blog post for tylerhloans.com about: {topic}

Tyler Henschel is a Senior Loan Officer at CMG Home Loans in Katy TX (NMLS 2034073).
Phone: (979) 255-6219
Email: thenschel@cmghomeloans.com
Calendly: https://calendly.com/thenschel-cmghomeloans/30min

Requirements:
- 800 to 1000 words
- Conversational but professional tone
- Target keywords naturally
- Focus on Katy TX and Houston TX market
- Strong CTA at the end to book a call with Tyler
- Format as clean HTML using h2, h3, p, ul, li tags only
- Start with a meta description comment like: <!-- META: description here -->
- Do NOT include DOCTYPE html head or body tags
- Mention Tyler naturally 2 to 3 times as the expert

COMPLIANCE RULES (CMG Financial Marketing Policy — strictly follow all of these):
- NEVER quote specific interest rates or APR figures. General language like "competitive rates" is fine.
- NEVER imply or state that any reader is pre-approved, guaranteed, or likely to qualify for any loan.
- NEVER use the word "fixed" in a way that could mislead readers about rate variability.
- NEVER make claims about eliminating, reducing, or restructuring debt.
- NEVER misrepresent any loan product as government-backed or government-affiliated unless it explicitly is (e.g., VA, FHA, USDA).
- NEVER state or imply that no fees or costs are associated with any loan product.
- NEVER make any claim about specific payment amounts without full context.
- Do NOT display or reference any specific current mortgage rates — rates change daily and must come from an approved source.
- All product descriptions must be accurate and not misleading. Do not overstate benefits.
- Use educational, informational language throughout. The post is informational, not a binding offer of credit."""
    }]
)

content = message.content[0].text

meta_match = re.search(r'<!-- META: (.*?) -->', content)
meta_desc = meta_match.group(1) if meta_match else f"Tyler Henschel, Senior Loan Officer in Katy TX, explains everything about {topic.lower()}."

full_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{topic} | Tyler Henschel CMG Home Loans Katy TX</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="https://tylerhloans.com/blog/{slug}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{{--navy:#0a1628;--gold:#c9a84c;--gold-light:#e8c97a;--cream:#f7f4ef;--text:#1a1a2e;--muted:#5a6070;--white:#ffffff}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'DM Sans',sans-serif;background:var(--cream);color:var(--text)}}
nav{{background:var(--navy);padding:1rem 2rem;display:flex;justify-content:space-between;align-items:center}}
.nav-name{{font-family:'Playfair Display',serif;color:var(--gold-light);font-size:1rem;text-decoration:none}}
.nav-cta{{background:var(--gold);color:var(--navy);padding:.5rem 1.2rem;border-radius:4px;text-decoration:none;font-size:.8rem;font-weight:500}}
.hero{{background:var(--navy);padding:4rem 2rem;text-align:center}}
.hero h1{{font-family:'Playfair Display',serif;color:var(--white);font-size:clamp(1.6rem,3vw,2.6rem);font-weight:400;max-width:800px;margin:0 auto 1rem;line-height:1.2}}
.hero-meta{{color:rgba(255,255,255,.45);font-size:.85rem}}
.article{{max-width:780px;margin:3rem auto;padding:0 2rem 4rem}}
.article h2{{font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:400;color:var(--navy);margin:2rem 0 .8rem}}
.article h3{{font-size:1.05rem;font-weight:500;color:var(--navy);margin:1.5rem 0 .5rem}}
.article p{{font-size:.97rem;font-weight:300;line-height:1.8;color:var(--muted);margin-bottom:1.1rem}}
.article ul,.article ol{{padding-left:1.5rem;margin-bottom:1.1rem}}
.article li{{font-size:.97rem;font-weight:300;line-height:1.8;color:var(--muted);margin-bottom:.3rem}}
.article strong{{font-weight:500;color:var(--text)}}
.cta-box{{background:var(--navy);border-radius:16px;padding:2.5rem;text-align:center;margin-top:3rem}}
.cta-box h3{{font-family:'Playfair Display',serif;color:var(--white);font-size:1.4rem;font-weight:400;margin-bottom:.8rem}}
.cta-box p{{color:rgba(255,255,255,.55);margin-bottom:1.5rem;font-weight:300}}
.cta-btn{{background:var(--gold);color:var(--navy);padding:.9rem 2rem;border-radius:4px;text-decoration:none;font-weight:500;display:inline-block}}
.back{{display:block;text-align:center;margin-top:2rem;color:var(--muted);text-decoration:none;font-size:.85rem}}
footer{{background:#060e1b;padding:2rem;text-align:center}}
footer p{{font-size:.7rem;color:rgba(255,255,255,.22);line-height:1.6;margin-bottom:.2rem}}
</style>
</head>
<body>
<nav>
<a class="nav-name" href="/">Tyler Henschel · CMG Home Loans</a>
<a class="nav-cta" href="https://calendly.com/thenschel-cmghomeloans/30min" target="_blank">Book a Call</a>
</nav>
<div class="hero">
<h1>{topic}</h1>
<p class="hero-meta">By Tyler Henschel &middot; {date_str} &middot; Katy, TX</p>
</div>
<article class="article">
{content}
<div class="cta-box">
<h3>Ready to explore your options?</h3>
<p>Tyler Henschel specializes in helping Houston-area borrowers find the right mortgage strategy. Book a free 20-minute call.</p>
<a class="cta-btn" href="https://calendly.com/thenschel-cmghomeloans/30min" target="_blank">Book a Free Strategy Call</a>
</div>
<a class="back" href="/blog">&larr; Back to all articles</a>
</article>
<footer>
<p>Tyler Henschel &middot; Senior Loan Officer &middot; CMG Home Loans &middot; NMLS #2034073</p>
<p>24285 Katy Freeway Suite 400-G, Katy, TX 77494 &middot; (979) 255-6219 &middot; thenschel@cmghomeloans.com</p>
<p>Offer of credit subject to credit approval. CMG Mortgage, Inc., dba CMG Financial NMLS #1820 is an equal opportunity lender.</p>
<p>&copy; 2025 CMG Home Loans. Not a commitment to lend. Equal Housing Lender.</p>
</footer>
</body>
</html>"""

os.makedirs(f"blog/{slug}", exist_ok=True)
with open(f"blog/{slug}/index.html", "w") as f:
    f.write(full_page)

print(f"Done: blog/{slug}/index.html")

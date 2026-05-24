import anthropic
import os
import json
import datetime
import re

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

TOPICS = [
    # First-time buyers — evergreen high volume
    "First time homebuyer mistakes to avoid in Houston TX in 2026",
    "How much house can you really afford in Katy TX",
    "FHA vs conventional loans in Houston — which is better for you",
    "VA loans explained for veterans and active duty buyers in Texas",
    "USDA loans in Texas — the hidden zero-down mortgage option",
    "What credit score do you need to buy a home in Texas",
    "How mortgage rates actually work — a Houston buyer's guide",
    "Why two buyers with the same credit score get different rates",
    "The complete mortgage pre-approval checklist for Houston homebuyers",
    "What underwriters really look for — Houston mortgage guide",
    "First time home buyer programs in Katy TX 2026",
    "Down payment assistance programs in Texas — complete guide",
    "TDHCA loan programs explained for Texas first time buyers",
    "Grants vs down payment assistance — what is the difference in Texas",
    "Can parents help with your down payment in Texas — gift fund rules explained",
    "How much money do you need to buy a house in Houston",
    "How to prepare financially one year before buying a home in Texas",
    "The real cost of waiting to buy a home in Houston",
    "Renting vs buying in Houston — the real numbers in 2026",
    "Why waiting for rates to drop might backfire for Houston buyers",
    "Is 2026 a good time to buy a home in the Houston area",
    "How to compete against cash buyers in Houston TX",
    "What closing costs should buyers expect in Texas",
    "Hidden costs of homeownership nobody talks about in Texas",
    "Can you buy a house with bad credit in Texas",
    "Can gig workers qualify for mortgages in Houston",
    "Self-employed mortgage guide for Houston business owners",
    "How bonuses commission and overtime income are calculated for mortgages",
    "Can you buy a home with student loans in Texas",
    "Co-signing a mortgage in Texas — risks and benefits explained",
    "Should you pay off debt before buying a home in Houston",
    "How to buy a home with low savings in Texas",
    "Buying a home after bankruptcy in Texas — what you need to know",
    "Buying a home after divorce in Texas — a complete guide",
    "Mortgage myths that cost Houston buyers money",
    "The psychology of buying your first house",
    "Top questions buyers should ask their mortgage lender in Houston",
    "What I wish every Houston homebuyer knew before starting the process",

    # Texas taxes and escrow — SEO goldmine
    "MUD taxes in the Houston area explained for homebuyers",
    "Why Texas property taxes shock first-time buyers",
    "What is a MUD district and why does it matter in Katy TX",
    "Houston area property taxes explained by county",
    "Montgomery County vs Harris County taxes — which is better",
    "Why new construction taxes are often estimated wrong in Texas",
    "How builders underestimate property taxes in the Houston area",
    "Why your mortgage payment can increase after closing in Texas",
    "Escrow shortages explained for Texas homeowners",
    "Why your escrow payment went up hundreds per month",
    "How mortgage escrow accounts actually work in Texas",
    "Can you waive escrow in Texas",
    "The difference between city taxes county taxes and MUD taxes in Texas",
    "What is a PID tax in Texas",
    "MUD vs PID vs HOA — what is the difference in Houston suburbs",
    "Why Texas has no state income tax but high property taxes",
    "How homestead exemptions save Texas homeowners money",
    "Over 65 property tax exemptions in Texas explained",
    "Disabled veteran property tax exemptions in Texas",
    "Why your first year tax bill on new construction is misleading in Texas",
    "How supplemental tax bills catch Texas buyers off guard",
    "Why Katy TX property taxes are higher than expected",
    "Cypress vs Tomball vs Magnolia property taxes compared",
    "Fort Bend County property tax breakdown for homebuyers",
    "The cheapest Houston suburbs for property taxes",
    "Why master-planned communities often have higher taxes in Texas",
    "What happens to MUD taxes over time in Houston suburbs",
    "Why some Texas neighborhoods have 3 percent or higher tax rates",
    "How to calculate your real mortgage payment in Texas including taxes",
    "Why Zillow mortgage payment estimates are often wrong in Texas",
    "Understanding principal interest taxes and insurance in a Texas mortgage",
    "Escrow refund checks explained for Texas homeowners",
    "What happens if your escrow account goes negative in Texas",
    "How lenders estimate taxes on new construction homes in Texas",
    "Why appraised value and purchase price can differ in Texas",
    "Texas appraisal districts explained for homeowners",
    "How to protest your property taxes in Texas",
    "Harris County property tax protest tips that actually work",
    "Montgomery County property tax protest guide",
    "How Texas property taxes affect debt-to-income ratios",
    "What is an escrow cushion and why does it matter",
    "How property tax payments work at closing in Texas",
    "Why Texas closing costs are different than other states",
    "Understanding daily interest charges at closing in Texas",
    "Why your cash to close changed before closing day",
    "Can MUD taxes ever go away in Texas",

    # Houston insurance — massive pain point
    "Why Texas insurance costs are rising in 2026",
    "Houston flood zones explained for homebuyers",
    "Do you need flood insurance in Houston TX",
    "Why Houston home insurance is so expensive",
    "How insurance premiums affect your buying power in Texas",
    "Why two homes with the same price have different payments in Houston",
    "Why insurance quotes should be done early in the loan process",
    "What happens if insurance comes in higher than expected at closing",
    "Why new roof discounts matter for homeowners insurance in Texas",
    "Does a pool increase your insurance costs in Texas",
    "How solar panels affect home insurance and appraisals in Texas",
    "Why Texas utility costs matter more than buyers think",
    "Why some Houston neighborhoods have lower insurance rates",
    "Understanding replacement cost vs market value insurance in Texas",
    "Homeowners insurance deductibles explained for Texans",
    "Why brick homes sometimes cost less to insure in Houston",
    "How hurricane risk affects Houston mortgage costs",
    "Why flood history matters more than flood zone maps in Houston",

    # New construction Houston — goldmine
    "New construction loans explained for Houston TX buyers",
    "Why builders offer mortgage incentives in Houston",
    "The pros and cons of buying new construction in the Houston area",
    "Spec home vs to-be-built — what is the difference in Katy TX",
    "MUD taxes on new construction homes in Houston explained",
    "Why new construction taxes are underestimated in Texas",
    "Builder lender incentives vs higher tax rates in Houston",
    "Why Texas new construction can still be a good deal in 2026",
    "What upgrades are worth it in a new build in Houston",
    "How long does it take to build a home in Texas",
    "Can builder lenders be trusted — a Houston buyer's honest guide",
    "New construction hidden costs Houston buyers need to know",
    "Best master-planned communities near Katy TX for new construction",
    "Custom home construction loans in Katy TX — step by step guide",
    "What buyers need to know about special assessment taxes on new builds",

    # Mortgage mechanics — education content
    "How mortgage rates actually work and what moves them daily",
    "Why mortgage rates change every day in Texas",
    "How inflation impacts mortgage rates in 2026",
    "What the Federal Reserve actually controls for mortgage rates",
    "Should you buy down your interest rate in Houston",
    "2-1 buydowns explained in simple terms for Texas buyers",
    "Temporary vs permanent rate buydowns — which is better",
    "How seller credits can save buyers thousands in Texas",
    "Understanding mortgage points — are they worth it in Houston",
    "Fixed rate vs adjustable rate mortgages in Texas",
    "What is an ARM and when does it make sense for Houston buyers",
    "What is debt-to-income ratio and how does it affect you in Texas",
    "How to lower your DTI before buying a home in Houston",
    "What happens after you go under contract in Texas",
    "The mortgage timeline from application to closing in Texas",
    "Why deals fall apart during escrow in Houston",
    "Common mortgage red flags that kill deals in Texas",
    "Why your online mortgage quote is not always real",
    "Mortgage shopping — how many lenders is too many in Texas",
    "Does getting pre-approved hurt your credit score",
    "How to read a loan estimate in Texas",
    "Loan estimate vs closing disclosure explained",
    "Why APR can be misleading for Texas homebuyers",
    "How fast can you close on a mortgage in Houston",
    "What delays mortgage closings in Texas",
    "Why some buyers qualify online but not with a real lender in Texas",
    "How HOA fees affect mortgage qualification in Texas",

    # Pain point searches — highest conversion
    "Why did my mortgage payment go up in Texas",
    "Why did my escrow go up — Texas homeowner explanation",
    "Why is homeowners insurance so expensive in Texas",
    "Why was my mortgage denied in Texas",
    "Why did underwriting ask for more documents",
    "Why did my appraisal come in low in Houston",
    "Why did my deal fall through at closing in Texas",
    "Why is my cash to close higher than expected",
    "Why is my debt-to-income ratio too high",
    "Why some buyers regret buying too much house in Texas",
    "What happens if property values decline in Texas",
    "What happens if mortgage rates fall after you buy in Houston",
    "Should you wait for a housing crash in Houston — honest answer",
    "The biggest financial surprises Houston homebuyers face",
    "Why Texans need larger emergency funds for homeownership",
    "What happens if home prices keep rising in Houston",

    # Investors and wealth
    "DSCR loans for real estate investors in Houston TX",
    "Bank statement loans explained for Texas business owners",
    "How real estate investors use the AIO loan to preserve liquidity",
    "How investors use leverage to scale real estate in Houston",
    "All-In-One mortgage vs HELOC — what is the difference",
    "Using home equity to build wealth in Texas",
    "Cash-out refinance vs HELOC in Texas — which is right for you",
    "How to use home equity as a business owner in Texas",
    "Turning your current home into a rental in Houston",
    "House hacking for beginners in the Houston area",
    "Duplexes triplexes and fourplexes explained for Houston investors",
    "FHA multi-unit loans for first-time investors in Texas",
    "Should you refinance in 2026 — Texas homeowner guide",
    "Can you buy a home before selling yours in Houston",
    "Bridge loans explained for Houston homebuyers",
    "Buying your second home while keeping your first in Texas",

    # AIO and specialty products
    "How business owners in Katy TX can save thousands using the All-In-One mortgage",
    "How the All-In-One loan works — daily interest explained",
    "All-In-One loan explained for Houston homeowners",
    "How physicians and doctors can optimize their mortgage in Texas",
    "How financial planners use the AIO loan for client wealth optimization",
    "The All-In-One loan for real estate investors in Texas",
    "How to reduce mortgage interest without refinancing in Texas",
    "How to pay off your mortgage faster without extra payments",
    "Jumbo loans in Houston — qualifying as a high income borrower",
    "How to buy a luxury home with financing in Houston TX",
    "Renovation loans in Houston — complete guide",
    "The best mortgage programs most Houston buyers never hear about",
    "VA loan benefits most Houston veterans do not know about",

    # Builder and spec construction
    "Spec construction financing for builders in the Houston area — how it works",
    "Bridge loans for builders in Katy TX — freeing up capital between projects",
    "CMG Build and Lock program — how Houston builders can lock rates before buyers are found",
    "What is BuilderFLEX — spec construction financing for production builders in Texas",
    "Spec vs custom construction loans in Katy TX — which is right for your project",
    "How Houston builders use spec financing to scale inventory",
    "What builders need to know about construction capital in the Houston market",
    "How to finance land development and vertical construction in Texas",

    # Realtor and referral SEO
    "How realtors and lenders work together in Houston TX",
    "What makes a great mortgage lender for Houston realtors",
    "How Houston realtors can build a stronger referral business",
    "Why buyers without realtors still need a great mortgage lender in Texas",
    "What every Houston realtor should know about mortgage pre-approval",
    "How a strong lender relationship helps Houston realtors close more deals",
    "Why having the right lender matters more than the interest rate in Texas",
    "What makes a great loan officer in Houston TX",
]

day_of_year = datetime.datetime.now().timetuple().tm_yday
topic = TOPICS[day_of_year % len(TOPICS)]
date_str = datetime.datetime.now().strftime("%B %d, %Y")

slug = topic.lower()
slug = re.sub(r'[^a-z0-9\s]', '', slug)
slug = re.sub(r'\s+', '-', slug.strip())
slug = slug[:60].rstrip('-')

print(f"Writing: {topic}")

faq_message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=600,
    messages=[{
        "role": "user",
        "content": f"""Generate 3 FAQ questions and answers about: {topic}

Format as JSON array only, no other text:
[
  {{"q": "Question one?", "a": "Answer one."}},
  {{"q": "Question two?", "a": "Answer two."}},
  {{"q": "Question three?", "a": "Answer three."}}
]

Keep answers 2-3 sentences. Focus on what Houston TX homebuyers actually search for."""
    }]
)

try:
    faq_data = json.loads(faq_message.content[0].text.strip())
except Exception:
    faq_data = []

faq_schema = ""
if faq_data:
    faq_items = ",\n".join([
        f'{{"@type":"Question","name":{json.dumps(f["q"])},"acceptedAnswer":{{"@type":"Answer","text":{json.dumps(f["a"])}}}}}'
        for f in faq_data
    ])
    faq_schema = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_items}]}}
</script>"""

faq_html = ""
if faq_data:
    faq_items_html = "\n".join([
        f'<div class="faq-item"><h3>{f["q"]}</h3><p>{f["a"]}</p></div>'
        for f in faq_data
    ])
    faq_html = f'<div class="faq-block"><h2>Frequently Asked Questions</h2>{faq_items_html}</div>'

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
- Use educational, informational language throughout. The post is informational, not a binding offer of credit.
- NEVER use unqualified superlatives or unprovable claims such as "best rates," "lowest costs," "cheapest," or "free" (unless a specific product genuinely has no fee and that is documented).
- Keep content general and educational in nature. Do not frame the post as a specific product advertisement with rate or payment terms.
- Use inclusive, welcoming language. Never use phrasing that could discourage any person from applying based on race, color, national origin, religion, sex, familial status, or disability (Fair Housing Act / ECOA compliance).
- Do not make any statement that is inaccurate, inconsistent, or could be considered deceptive or misleading under UDAAP standards.

PRODUCT ACCURACY — BUILDER AND SPEC FINANCING PROGRAMS:
- CMG offers spec construction financing for experienced builders across four main products: Spec (vertical/ground-up), Bridge (completed inventory), Horizontal (land development), and BuilderFLEX (one approval, multiple projects). Always describe these accurately.
- Spec construction financing targets experienced builders — typically 5 to 50 homes per year with a proven track record. Do not imply it is available to first-time or inexperienced builders.
- The Spec Lock (Build and Lock) program allows builders to reserve a rate for 60 or 90 days for Conventional, FHA, VA, and USDA loans only. It is NOT available for Non-Agency products. Do not imply otherwise.
- The List and Lock program is NOT available for AIO loans, HELOCs, construction loans, Non-QM, or bond/HFA loans. Do not describe it as available for those products.
- CRITICAL: The All-In-One (AIO) loan is NOT available for spec construction financing in Texas. Never suggest or imply that Texas builders can use the AIO loan for spec construction purposes."""
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
<meta property="og:title" content="{topic} | Tyler Henschel">
<meta property="og:description" content="{meta_desc}">
<meta property="og:url" content="https://tylerhloans.com/blog/{slug}">
<meta property="og:type" content="article">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":{json.dumps(topic)},"description":{json.dumps(meta_desc)},"datePublished":"{date_str}","author":{{"@type":"Person","name":"Tyler Henschel","url":"https://tylerhloans.com","jobTitle":"Senior Loan Officer","worksFor":{{"@type":"Organization","name":"CMG Home Loans"}}}},"publisher":{{"@type":"Organization","name":"CMG Home Loans","url":"https://tylerhloans.com"}}}}
</script>
{faq_schema}
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
<nav style="position:fixed;top:0;left:0;right:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:1rem 2.5rem;background:rgba(10,22,40,0.97);backdrop-filter:blur(12px);border-bottom:1px solid rgba(201,168,76,0.15)">
<a style="text-decoration:none" href="/"><div style="font-family:'Playfair Display',serif;font-size:1rem;color:#e8c97a">Tyler Henschel</div><div style="font-size:0.65rem;color:rgba(255,255,255,0.35);letter-spacing:0.08em">CMG Home Loans · Katy TX</div></a>
<div style="display:flex;gap:1.5rem;align-items:center">
<a style="color:rgba(255,255,255,0.65);text-decoration:none;font-size:0.85rem" href="/">Home</a>
<a style="color:rgba(255,255,255,0.65);text-decoration:none;font-size:0.85rem" href="/products/">Products</a>
<a style="color:rgba(255,255,255,0.65);text-decoration:none;font-size:0.85rem" href="/calculator/">Calculator</a>
<a style="color:#e8c97a;text-decoration:none;font-size:0.85rem" href="/blog/">Blog</a>
<a style="background:#c9a84c;color:#0a1628;font-size:0.78rem;font-weight:500;padding:0.5rem 1.2rem;border-radius:4px;text-decoration:none" href="https://calendly.com/thenschel-cmghomeloans/30min" target="_blank">Book a Call</a>
</div>
</nav>
<div class="hero">
<h1>{topic}</h1>
<p class="hero-meta">By Tyler Henschel &middot; {date_str} &middot; Katy, TX</p>
</div>
<article class="article">
{content}
{faq_html}
<style>.faq-block{{background:#f7f4ef;border-radius:12px;padding:2rem;margin:2rem 0}}.faq-block h2{{font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:400;color:#0a1628;margin-bottom:1.2rem}}.faq-item{{margin-bottom:1.2rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(10,22,40,0.08)}}.faq-item:last-child{{margin-bottom:0;padding-bottom:0;border-bottom:none}}.faq-item h3{{font-size:0.95rem;font-weight:500;color:#0a1628;margin-bottom:0.4rem}}.faq-item p{{font-size:0.88rem;font-weight:300;color:#5a6070;line-height:1.7}}</style>
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

# Update posts.json manifest (read existing, prepend new post, write back)
posts_file = "blog/posts.json"
posts = []
if os.path.exists(posts_file):
    with open(posts_file, "r") as f:
        try:
            posts = json.load(f)
        except Exception:
            posts = []

new_entry = {"title": topic, "slug": slug, "date": date_str, "meta": meta_desc}
posts = [p for p in posts if p.get("slug") != slug]  # remove duplicate if re-run
posts.insert(0, new_entry)

with open(posts_file, "w") as f:
    json.dump(posts, f, indent=2)

print(f"Updated posts.json ({len(posts)} posts)")

# Update sitemap.xml with all blog posts
blog_urls = "\n".join([
    f'  <url><loc>https://tylerhloans.com/blog/{p["slug"]}/</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>'
    for p in posts
])
sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://tylerhloans.com/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>
  <url><loc>https://tylerhloans.com/products/</loc><changefreq>monthly</changefreq><priority>0.9</priority></url>
  <url><loc>https://tylerhloans.com/calculator/</loc><changefreq>monthly</changefreq><priority>0.9</priority></url>
  <url><loc>https://tylerhloans.com/blog/</loc><changefreq>daily</changefreq><priority>0.8</priority></url>
  <url><loc>https://tylerhloans.com/all-in-one/</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
{blog_urls}
</urlset>"""

with open("sitemap.xml", "w") as f:
    f.write(sitemap)

print(f"Updated sitemap.xml")

# Auto-commit and push if running in CI
if os.environ.get("CI"):
    import subprocess
    subprocess.run(["git", "config", "user.email", "blog-agent@tylerhloans.com"], check=True)
    subprocess.run(["git", "config", "user.name", "Blog Agent"], check=True)
    subprocess.run(["git", "add", f"blog/{slug}/index.html"], check=True)
    subprocess.run(["git", "commit", "-m", f"blog: {topic[:72]}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("Pushed to GitHub.")

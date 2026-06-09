import requests, datetime, os, sys

METABASE_URL = "https://lecloset-metabase.lecloset.fr"
API_KEY = os.environ["METABASE_API_KEY"]

resp = requests.post(
    f"{METABASE_URL}/api/card/4019/query",
    headers={"Content-Type": "application/json", "x-api-key": API_KEY},
    json={}
)
if not resp.ok:
    print(f"Error {resp.status_code}: {resp.text[:300]}")
    sys.exit(1)

data = resp.json()["data"]
cols = [c["name"] for c in data["cols"]]
idx = {c: i for i, c in enumerate(cols)}
rows = data["rows"]

def urg(r):
    if r >= 60: return "#e74c3c", "red"
    if r >= 45: return "#e67e22", "orange"
    if r >= 35: return "#f39c12", "yellow"
    return "#27ae60", "green"

cards = ""
for row in rows:
    name  = str(row[idx["product_name"]]).replace('"', '&quot;').replace('<', '&lt;')
    brand = str(row[idx["brand_name"]]).replace('<', '&lt;')
    cat   = str(row[idx["category_name"]]).replace("_", " ").title()
    img   = str(row[idx["main_picture_url"]] or "")
    url   = str(row[idx["product_url"]])
    risk  = int(row[idx["at_risk_item_count"]])
    stock = int(row[idx["stock_utile_total"]])
    col, tier = urg(risk)
    pct = round(risk / stock * 100) if stock else 0
    cards += f"""
  <a class="card" href="{url}" target="_blank" data-tier="{tier}">
    <div class="photo"><img src="{img}" alt="" loading="lazy">
    <span class="dot" style="background:{col}"></span></div>
    <div class="info">
      <div class="name">{name}</div>
      <div class="sub">{brand} &middot; {cat}</div>
      <div class="pills">
        <span class="pill" style="background:{col}1a;color:{col};border:1px solid {col}44">{risk} \u00e0 risque</span>
        <span class="pill muted">{pct}% du stock</span>
      </div>
    </div>
  </a>"""

today = datetime.date.today().strftime("%d/%m/%Y")
template = open("template.html", encoding="utf-8").read()
html = template.replace("{{CARDS}}", cards).replace("{{DATE}}", today)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"Generated {len(rows)} products — {today}")

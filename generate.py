import requests, json, datetime, os

METABASE_URL = "https://lecloset-metabase.lecloset.fr"
SESSION = os.environ.get("METABASE_SESSION", "")

resp = requests.post(
    f"{METABASE_URL}/api/card/4019/query",
    headers={"Content-Type": "application/json", "X-Metabase-Session": SESSION},
    json={}
)
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
    name  = row[idx["product_name"]]
    brand = row[idx["brand_name"]]
    cat   = row[idx["category_name"]].replace("_", " ").title()
    img   = row[idx["main_picture_url"]]
    url   = row[idx["product_url"]]
    risk  = row[idx["at_risk_item_count"]]
    stock = row[idx["stock_utile_total"]]
    col, tier = urg(risk)
    pct = round(risk / stock * 100) if stock else 0
    cards += f"""
  <a class="card" href="{url}" target="_blank" data-tier="{tier}">
    <div class="img-wrap"><img src="{img}" alt="" loading="lazy">
    <span class="dot" style="background:{col}"></span></div>
    <div class="info">
      <div class="name">{name}</div>
      <div class="brand">{brand} · {cat}</div>
      <div class="stats">
        <span class="pill" style="background:{col}22;color:{col}">{risk} à risque</span>
        <span class="pill gray">{pct}% du stock</span>
      </div>
    </div>
  </a>"""

today = datetime.date.today().strftime("%d/%m/%Y")
template = open("template.html").read()
html = template.replace("{{CARDS}}", cards).replace("{{DATE}}", today)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"Generated {len(rows)} products")

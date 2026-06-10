import requests, datetime, os, sys

METABASE_URL = "https://lecloset-metabase.lecloset.fr"
API_KEY = os.environ["METABASE_API_KEY"]

resp = requests.post(
    METABASE_URL + "/api/card/4019/query",
    headers={"Content-Type": "application/json", "x-api-key": API_KEY},
    json={}
)
if not resp.ok:
    sys.exit("Error " + str(resp.status_code) + ": " + resp.text[:300])

data = resp.json()["data"]
cols = [c["name"] for c in data["cols"]]
idx = {c: i for i, c in enumerate(cols)}
rows = data["rows"]

CAT = {
    "jeans": "Jean", "dresses": "Robe", "pants": "Pantalon",
    "tee_shirt_and_tops": "Top", "shirts_and_blouses": "Chemise",
    "jackets_and_blazers": "Veste", "knits_and_sweaters": "Pull",
    "skirts_and_shorts": "Jupe", "jumpsuit_and_overalls": "Combi"
}
WF = {
    "tempere": "Tempéré", "tempere_ete": "Été",
    "tempere_hiver": "Hiver", "plein_ete": "Plein été", "plein_hiver": "Plein hiver"
}
WF_ICON = {
    "tempere": "🌤", "tempere_ete": "☀️",
    "tempere_hiver": "🍂", "plein_ete": "🌞", "plein_hiver": "❄️"
}

products = []
for row in rows:
    products.append({
        "name":    str(row[idx["product_name"]]),
        "brand":   str(row[idx["brand_name"]]),
        "cat":     str(row[idx["category_name"]]),
        "wf":      str(row[idx["weatherfit"]]),
        "img":     str(row[idx["main_picture_url"]] or ""),
        "url":     str(row[idx["product_url"]]),
        "risk":    int(row[idx["at_risk_item_count"]]),
        "stock":   int(row[idx["stock_utile_total"]]),
    })

all_cats = sorted(set(CAT.get(p["cat"], p["cat"]) for p in products))
total_risk = sum(p["risk"] for p in products)
today = datetime.date.today().strftime("%d/%m/%Y")

cards_html = ""
for p in products:
    cat   = CAT.get(p["cat"], p["cat"])
    wf    = WF.get(p["wf"], p["wf"])
    icon  = WF_ICON.get(p["wf"], "")
    risk  = p["risk"]
    stock = p["stock"]
    pct   = round(risk / stock * 100) if stock else 0
    name  = p["name"].replace("&", "&amp;")
    brand = p["brand"].replace("&", "&amp;")
    cards_html += (
        '<div class="card" data-cat="' + cat + '">'
        '<a href="' + p["url"] + '" target="_blank">'
        '<div class="photo"><img src="' + p["img"] + '" alt="" loading="lazy"></div>'
        '<div class="info">'
        '<div class="name">' + name + '</div>'
        '<div class="brand">' + brand + '</div>'
        '<div class="stats">'
        '<span class="stat-big">' + str(risk) + '</span><span class="stat-lbl"> \u00e0 risque</span>'
        '<span class="stat-sep">&nbsp;&middot;&nbsp;</span>'
        '<span class="stat-big">' + str(stock) + '</span><span class="stat-lbl"> stock total</span>'
        '<span class="stat-sep">&nbsp;&middot;&nbsp;</span>'
        '<span class="stat-big">' + str(pct) + '%</span><span class="stat-lbl"> taux</span>'
        '</div>'
        '<div class="tags">'
        '<span class="tag">' + cat + '</span>'
        '<span class="tag">' + icon + ' ' + wf + '</span>'
        '</div>'
        '<div class="factory-btn">Voir Factory &rarr;</div>'
        '</div>'
        '</a>'
        '</div>\n'
    )

filter_btns = '<button class="fbtn active" data-cat="all">Tout</button>\n'
for c in all_cats:
    filter_btns += '<button class="fbtn" data-cat="' + c + '">' + c + '</button>\n'

html = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reshoot stock \u00e0 risque</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0ede8;color:#111}
.header{background:#f0ede8;padding:20px 24px 0}
.kpis{display:flex;gap:24px;align-items:baseline;margin-bottom:16px}
.kpi-val{font-size:28px;font-weight:800;color:#111}
.kpi-lbl{font-size:12px;color:#888;margin-top:2px}
.filters{display:flex;gap:8px;flex-wrap:wrap;padding:0 24px 16px;background:#f0ede8}
.fbtn{padding:5px 14px;border-radius:20px;border:1.5px solid #ccc;background:#fff;font-size:12px;font-weight:600;cursor:pointer;color:#555;transition:all .12s}
.fbtn:hover{border-color:#999;color:#111}
.fbtn.active{background:#111;border-color:#111;color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:0;padding:0 16px 40px}
.card{background:#fff;border-radius:14px;overflow:hidden;margin:8px;display:flex;flex-direction:column;transition:transform .15s,box-shadow .15s}
.card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.12)}
.card[hidden]{display:none!important}
.card a{text-decoration:none;color:inherit;display:flex;flex-direction:column;height:100%}
.photo{aspect-ratio:3/4;overflow:hidden;background:#f5f3f0}
.photo img{width:100%;height:100%;object-fit:cover;display:block}
.info{padding:12px;flex:1;display:flex;flex-direction:column;gap:4px}
.name{font-size:13px;font-weight:700;color:#111;line-height:1.3}
.brand{font-size:11px;color:#999}
.stats{font-size:11px;color:#555;margin-top:2px}
.stat-big{font-weight:700;color:#111}
.stat-lbl{color:#999}
.stat-sep{color:#ccc}
.tags{display:flex;gap:5px;flex-wrap:wrap;margin-top:5px}
.tag{font-size:10px;background:#f0ede8;color:#666;padding:2px 8px;border-radius:10px;font-weight:500}
.factory-btn{margin-top:10px;background:#111;color:#fff;text-align:center;padding:8px;border-radius:8px;font-size:12px;font-weight:700;letter-spacing:.3px}
</style>
</head>
<body>
<div class="header">
  <div class="kpis">
    <div><div class="kpi-val">""" + str(len(products)) + """</div><div class="kpi-lbl">produits</div></div>
    <div><div class="kpi-val">""" + str(total_risk) + """</div><div class="kpi-lbl">pi\u00e8ces \u00e0 risque total</div></div>
    <div style="margin-left:auto"><div class="kpi-lbl" style="text-align:right">Mise \u00e0 jour """ + today + """</div></div>
  </div>
</div>
<div class="filters">
""" + filter_btns + """</div>
<div class="grid" id="grid">
""" + cards_html + """</div>
<script>
document.querySelectorAll('.fbtn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.fbtn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const cat = btn.dataset.cat;
    document.querySelectorAll('.card').forEach(c => {
      c.hidden = cat !== 'all' && c.dataset.cat !== cat;
    });
  });
});
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Generated " + str(len(rows)) + " products — " + today)

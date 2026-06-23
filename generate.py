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
idx  = {c: i for i, c in enumerate(cols)}
rows = data["rows"]

CAT = {"jeans":"Jean","dresses":"Robe","pants":"Pantalon","tee_shirt_and_tops":"Top",
       "shirts_and_blouses":"Chemise","jackets_and_blazers":"Veste","knits_and_sweaters":"Pull",
       "skirts_and_shorts":"Jupe","jumpsuit_and_overalls":"Combi"}
WF      = {"tempere":"Temper\u00e9","tempere_ete":"\u00c9t\u00e9","tempere_hiver":"Hiver",
           "plein_ete":"Plein \u00e9t\u00e9","plein_hiver":"Plein hiver"}
WF_ICON = {"tempere":"\U0001f324\ufe0f","tempere_ete":"\u2600\ufe0f","tempere_hiver":"\U0001f342",
           "plein_ete":"\U0001f31e","plein_hiver":"\u2744\ufe0f"}

products = [{
    "name":  str(r[idx["product_name"]]),
    "brand": str(r[idx["brand_name"]]),
    "cat":   str(r[idx["category_name"]]),
    "wf":    str(r[idx["weatherfit"]]),
    "img":   str(r[idx["main_picture_url"]] or ""),
    "url":   str(r[idx["product_url"]]),
    "risk":  int(r[idx["at_risk_item_count"]]),
    "stock": int(r[idx["stock_utile_total"]]),
    "dispo": int(r[idx["current_in_stock_item_count"]]),
} for r in rows]

all_cats = sorted(set(CAT.get(p["cat"], p["cat"]) for p in products))
all_wfs  = sorted(set(p["wf"] for p in products))
total_risk  = sum(p["risk"]  for p in products)
total_dispo = sum(p["dispo"] for p in products)
today = datetime.date.today().strftime("%d/%m/%Y")

def make_card(p):
    cat  = CAT.get(p["cat"], p["cat"])
    wf   = WF.get(p["wf"], p["wf"])
    icon = WF_ICON.get(p["wf"], "")
    name  = p["name"].replace("&","&amp;")
    brand = p["brand"].replace("&","&amp;")
    return (
        '<div class="card" data-cat="' + cat + '" data-wf="' + p["wf"] + '">'
        '<a href="' + p["url"] + '" target="_blank">'
        '<div class="photo"><img src="' + p["img"] + '" alt="" loading="lazy"></div>'
        '<div class="info">'
        '<div class="name">' + name + '</div>'
        '<div class="brand">' + brand + '</div>'
        '<div class="stats">'
        '<span class="stat-big">' + str(p["risk"]) + '</span><span class="stat-lbl"> \u00e0 risque</span>'
        ' <span class="stat-sep">&middot;</span> '
        '<span class="stat-big">' + str(p["dispo"]) + '</span><span class="stat-lbl"> dispo</span>'
        ' <span class="stat-sep">&middot;</span> '
        '<span class="stat-big">' + str(p["stock"]) + '</span><span class="stat-lbl"> stock utile</span>'
        '</div>'
        '<div class="tags"><span class="tag">' + cat + '</span>'
        '<span class="tag">' + icon + ' ' + wf + '</span></div>'
        '<div class="factory-btn">Voir Factory \u2192</div>'
        '</div></a></div>\n'
    )

cards_html = "".join(make_card(p) for p in products)

cat_btns = '<button class="fbtn active" data-cat="all">Tout</button>\n'
for c in all_cats:
    cat_btns += '<button class="fbtn" data-cat="' + c + '">' + c + '</button>\n'

wf_btns = '<button class="wbtn active" data-wf="all">Toutes saisons</button>\n'
for w in all_wfs:
    wf_btns += '<button class="wbtn" data-wf="' + w + '">' + WF_ICON.get(w,"") + " " + WF.get(w,w) + '</button>\n'

CSS = ("*{box-sizing:border-box;margin:0;padding:0}"
"body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0ede8;color:#111}"
".header{background:#f0ede8;padding:20px 24px 0}"
".kpis{display:flex;gap:24px;align-items:baseline;margin-bottom:16px;flex-wrap:wrap}"
".kpi-val{font-size:28px;font-weight:800;color:#111}"
".kpi-lbl{font-size:12px;color:#888;margin-top:2px}"
".toolbar{padding:0 24px 12px;background:#f0ede8;display:flex;flex-direction:column;gap:8px}"
".filter-row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}"
".filter-label{font-size:11px;color:#aaa;font-weight:600;min-width:80px}"
".fbtn,.wbtn{padding:5px 13px;border-radius:20px;border:1.5px solid #ccc;background:#fff;"
"font-size:12px;font-weight:600;cursor:pointer;color:#555;transition:all .12s}"
".fbtn:hover,.wbtn:hover{border-color:#999;color:#111}"
".fbtn.active,.wbtn.active{background:#111;border-color:#111;color:#fff}"
".count-bar{font-size:11px;color:#aaa;padding:0 24px 12px}"
".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:0;padding:0 16px 40px}"
".card{background:#fff;border-radius:14px;overflow:hidden;margin:8px;display:flex;"
"flex-direction:column;transition:transform .15s,box-shadow .15s}"
".card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.12)}"
".card[hidden]{display:none!important}"
".card a{text-decoration:none;color:inherit;display:flex;flex-direction:column;height:100%}"
".photo{aspect-ratio:3/4;overflow:hidden;background:#f5f3f0}"
".photo img{width:100%;height:100%;object-fit:cover;display:block}"
".info{padding:12px;flex:1;display:flex;flex-direction:column;gap:4px}"
".name{font-size:13px;font-weight:700;color:#111;line-height:1.3}"
".brand{font-size:11px;color:#999}"
".stats{font-size:11px;color:#555;margin-top:2px;line-height:1.8}"
".stat-big{font-weight:700;color:#111}.stat-lbl{color:#999}.stat-sep{color:#ddd}"
".tags{display:flex;gap:5px;flex-wrap:wrap;margin-top:5px}"
".tag{font-size:10px;background:#f0ede8;color:#666;padding:2px 8px;border-radius:10px;font-weight:500}"
".factory-btn{margin-top:10px;background:#111;color:#fff;text-align:center;"
"padding:8px;border-radius:8px;font-size:12px;font-weight:700;letter-spacing:.3px}")

JS = ("let activeCat=\"all\",activeWf=\"all\";\n"
"function applyFilters(){\n  let n=0;\n"
"  document.querySelectorAll(\".card\").forEach(c=>{\n"
"    const show=(activeCat===\"all\"||c.dataset.cat===activeCat)"
"&&(activeWf===\"all\"||c.dataset.wf===activeWf);\n"
"    c.hidden=!show; if(show)n++;\n  });\n"
"  document.getElementById(\"count-bar\").textContent="
"n+\" produit\"+(n>1?\"s\":\"\")+\" affich\u00e9\"+(n>1?\"s\":\"\");\n}\n"
"document.querySelectorAll(\".fbtn\").forEach(btn=>{\n"
"  btn.addEventListener(\"click\",()=>{\n"
"    document.querySelectorAll(\".fbtn\").forEach(b=>b.classList.remove(\"active\"));\n"
"    btn.classList.add(\"active\"); activeCat=btn.dataset.cat; applyFilters();\n  });\n});\n"
"document.querySelectorAll(\".wbtn\").forEach(btn=>{\n"
"  btn.addEventListener(\"click\",()=>{\n"
"    document.querySelectorAll(\".wbtn\").forEach(b=>b.classList.remove(\"active\"));\n"
"    btn.classList.add(\"active\"); activeWf=btn.dataset.wf; applyFilters();\n  });\n});")

html = (
    '<!DOCTYPE html>\n<html lang="fr">\n<head>\n'
    '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    '<title>Reshoot stock \u00e0 risque</title>\n<style>\n' + CSS + '\n</style>\n</head>\n<body>\n'
    '<div class="header"><div class="kpis">\n'
    '  <div><div class="kpi-val">' + str(len(products)) + '</div><div class="kpi-lbl">produits</div></div>\n'
    '  <div><div class="kpi-val">' + str(total_risk) + '</div><div class="kpi-lbl">pi\u00e8ces \u00e0 risque</div></div>\n'
    '  <div><div class="kpi-val">' + str(total_dispo) + '</div><div class="kpi-lbl">pi\u00e8ces dispo actuellement</div></div>\n'
    '  <div style="margin-left:auto"><div class="kpi-lbl" style="text-align:right">Mise \u00e0 jour ' + today + '</div></div>\n'
    '</div></div>\n'
    '<div class="toolbar">\n'
    '  <div class="filter-row"><span class="filter-label">Cat\u00e9gorie</span>\n' + cat_btns + '  </div>\n'
    '  <div class="filter-row"><span class="filter-label">Saison</span>\n' + wf_btns + '  </div>\n'
    '</div>\n'
    '<div class="count-bar" id="count-bar">' + str(len(products)) + ' produits affich\u00e9s</div>\n'
    '<div class="grid" id="grid">\n' + cards_html + '</div>\n'
    '<script>\n' + JS + '\n</script>\n</body>\n</html>'
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Generated " + str(len(rows)) + " products — " + today)

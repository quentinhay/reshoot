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
    "jeans": "Jeans", "dresses": "Robes", "pants": "Pantalons",
    "tee_shirt_and_tops": "Tops", "shirts_and_blouses": "Chemises",
    "jackets_and_blazers": "Vestes", "knits_and_sweaters": "Pulls",
    "skirts_and_shorts": "Jupes", "jumpsuit_and_overalls": "Combinaisons"
}
WF = {
    "tempere": "Toutes saisons",
    "tempere_ete": "Printemps / \u00c9t\u00e9",
    "tempere_hiver": "Automne / Hiver",
    "plein_ete": "Plein \u00e9t\u00e9",
    "plein_hiver": "Plein hiver",
}

cards = []
for row in rows:
    name  = str(row[idx["product_name"]])
    brand = str(row[idx["brand_name"]])
    cat   = CAT.get(str(row[idx["category_name"]]), str(row[idx["category_name"]]).replace("_"," ").title())
    wf    = WF.get(str(row[idx["weatherfit"]]), str(row[idx["weatherfit"]]))
    img   = str(row[idx["main_picture_url"]] or "")
    url   = str(row[idx["product_url"]])
    risk  = int(row[idx["at_risk_item_count"]])
    stock = int(row[idx["stock_utile_total"]])
    cards.append(
        '  <a class="card" href="' + url + '" target="_blank">\n'
        '    <div class="photo"><img src="' + img + '" alt="" loading="lazy"></div>\n'
        '    <div class="info">\n'
        '      <div class="name">' + name + '</div>\n'
        '      <div class="sub">' + brand + ' &middot; ' + cat + '</div>\n'
        '      <div class="season">' + wf + '</div>\n'
        '      <div class="meta">' + str(risk) + ' pcs \u00e0 risque &nbsp;&middot;&nbsp; ' + str(stock) + ' stock utile</div>\n'
        '      <div class="link">\u2192 Factory</div>\n'
        '    </div>\n'
        '  </a>'
    )

today = datetime.date.today().strftime("%d/%m/%Y")
template = open("template.html", encoding="utf-8").read()
html = template.replace("{{CARDS}}", "\n".join(cards)).replace("{{DATE}}", today)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Generated " + str(len(rows)) + " products — " + today)

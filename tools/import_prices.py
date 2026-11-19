"""
Import the Top Star Mobile price list (.xlsx) into products.js for the web app.

    pip install openpyxl
    python tools/import_prices.py "D:\\Downloads\\Top_Star_Mobile_Price_List_With_Search_Nov2026.xlsx"

Reads the "All Price List" sheet. Only the RETAIL price is exported —
wholesale prices and margins are never written to products.js (the site is public).
Rows with the same brand + model become one product with RAM/ROM options.
"""
import json
import re
import sys
import zlib
from pathlib import Path

import openpyxl

SHEET = "All Price List"
OUT = Path(__file__).resolve().parent.parent / "products.js"

COLOR_HEX = {
    "black": "#26282c", "white": "#eeeeec", "silver": "#c9ccd1", "gray": "#8a8d93",
    "green": "#6f9e84", "blue": "#4f74b8", "dark blue": "#22355e", "red": "#c0392b",
    "purple": "#9b7fc9", "violet": "#a08bd0", "pink": "#efb7c8", "gold": "#d8b46a",
    "orange": "#ef7d32", "coffee": "#6f4e37", "pale amber": "#e7c48f",
    "celadon cyan": "#9fd3c7", "ocean cyan": "#58b7c6",
}
COLOR_FIX = {"grey": "Gray", "silivery": "Silver"}

# brand group in sheet -> (brand label, camera style, warranty group)
def brand_info(group, wtype, model):
    g = group.lower()
    if g.startswith("xiaomi"):
        return "Xiaomi", "ring"
    if g.startswith("thai global"):
        return ("Xiaomi", "ring") if "redmi" in model.lower() else ("Global", "tri")
    if g.startswith("samsung"):
        return "Samsung", "vert"
    if g.startswith("honor"):
        return "Honor", "ring"
    if g.startswith("nubia"):
        return "Nubia", "duo"
    if g.startswith("m horse"):
        return "M Horse", "tri"
    return group.replace(" Official", "").strip(), "tri"


def display_name(brand, model):
    m = re.sub(r"\s+", " ", model).strip()
    if brand == "Xiaomi":
        if m.lower().startswith("xiao mi"):
            return "Xiaomi " + m[7:].strip()
        if m.lower().startswith("redmi"):
            return m
        return "Redmi " + m
    if brand == "Samsung":
        return "Galaxy " + m
    if brand == "Honor":
        return m if m.lower().startswith("honor") else "Honor " + m
    if brand in ("Nubia", "M Horse"):
        return f"{brand} {m}"
    return m


def warranty_group(wtype):
    w = wtype.lower()
    if "ceir" in w:
        return "ceir", "CEIR Paid"
    if "warranty" in w:
        return "official", "Official 1 Year Warranty"
    return "global", "Thai Global / Inter"


def clean_color(c):
    c = c.strip()
    c = COLOR_FIX.get(c.lower(), c)
    return c[:1].upper() + c[1:]


def ram_rom(s):
    s = str(s).strip()
    m = re.match(r"(\d+)\s*\+\s*(\d+)", s)
    if not m:
        return s, s
    ram, rom = m.groups()
    rom_label = f"{int(rom)//1024}TB" if int(rom) >= 1024 else f"{rom}GB"
    return f"{ram}GB + {rom_label}", f"{ram}+{rom}"


def stock_status(s):
    s = (s or "").lower()
    if "out" in s or "sold" in s:
        return "out"
    if "few" in s or "low" in s:
        return "few"
    return "in"


def main(path):
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb[SHEET]
    rows = list(ws.iter_rows(values_only=True))
    updated = next((str(r[0]) for r in rows[:3] if r and r[0] and "updated" in str(r[0]).lower()), "")
    updated = re.sub(r"(?i)^\s*updated\s*:\s*", "", updated.split("|")[0]).strip()
    header_i = next(i for i, r in enumerate(rows) if r and r[0] == "No.")
    head = [str(h or "").strip().lower() for h in rows[header_i]]
    col = lambda name: next(i for i, h in enumerate(head) if h.startswith(name))
    c_group, c_type, c_model, c_rr, c_col = col("category"), col("warranty"), col("model"), col("ram"), col("available colors")
    c_price, c_stock = col("retail"), col("stock")

    products, order = {}, []
    for r in rows[header_i + 1:]:
        if not r or not isinstance(r[0], (int, float)):
            continue  # skip blanks and TOTAL row
        group, wtype, model = str(r[c_group]).strip(), str(r[c_type]).strip(), str(r[c_model]).strip()
        price = r[c_price]
        if not isinstance(price, (int, float)):
            continue
        brand, cam = brand_info(group, wtype, model)
        name = display_name(brand, model)
        wid, wlabel = warranty_group(wtype)
        slug = re.sub(r"[^a-z0-9]+", "-", f"{brand}-{name}-{wid}".lower()).strip("-")
        if slug not in products:
            is_tab = model.lower().startswith("pad")
            products[slug] = {
                "id": zlib.crc32(slug.encode()) % 10**8,
                "slug": slug, "cat": "tablet" if is_tab else "phone",
                "brand": brand, "name": name, "model": model, "type": wid, "typeLabel": wlabel,
                "cam": cam, "colors": [], "storage": [],
                "note": "No adaptor included" if "no adaptor" in model.lower() else "",
            }
            if is_tab:
                products[slug].update(emoji="📲", bg=["#fde7d4", "#c2622d"])
            order.append(slug)
        p = products[slug]
        label, short = ram_rom(r[c_rr])
        idxs = []
        for cname in [clean_color(c) for c in str(r[c_col] or "").split(",") if c.strip()]:
            names = [c["n"] for c in p["colors"]]
            if cname not in names:
                p["colors"].append({"n": cname, "h": COLOR_HEX.get(cname.lower(), "#9aa3ad")})
                names.append(cname)
            idxs.append(names.index(cname))
        note = str(r[c_stock] or "")
        if any(v["k"] == short for v in p["storage"]):
            # same RAM/ROM listed twice with a different price (e.g. a special color) -> name the option by color
            label += " · " + ", ".join(p["colors"][i]["n"] for i in idxs)
        p["storage"].append({"s": label, "k": short, "price": int(price), "colors": idxs,
                             "stock": stock_status(note), **({"note": note} if "(" in note else {})})

    out = []
    for slug in order:
        p = products[slug]
        p["storage"].sort(key=lambda v: v["price"])
        p["price"] = p["storage"][0]["price"]
        st = [v["stock"] for v in p["storage"]]
        p["stock"] = "out" if all(s == "out" for s in st) else ("few" if all(s != "in" for s in st) else "in")
        out.append(p)

    js = ("/* AUTO-GENERATED by tools/import_prices.py — do not edit by hand. Retail prices only. */\n"
          f"window.SHOP_DATA = {json.dumps({'updated': updated, 'source': Path(path).name, 'products': out}, ensure_ascii=False, indent=1)};\n")
    OUT.write_text(js, encoding="utf-8")
    print(f"Wrote {len(out)} products ({sum(len(p['storage']) for p in out)} price rows) -> {OUT}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])

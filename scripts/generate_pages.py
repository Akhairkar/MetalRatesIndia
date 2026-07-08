#!/usr/bin/env python3
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE, "data", "metals.json"), encoding="utf-8") as f:
    metals = json.load(f)["metals"]
with open(os.path.join(BASE, "scripts", "metal_template.html"), encoding="utf-8") as f:
    template = f.read()

GRADES = {
    "copper": [
        ["Berry / Bright Copper Wire", "Clean, uncoated, no oxidation", "100% of base rate"],
        ["#1 Copper (Millberry)", "Bare bright wire, min. 16 gauge", "97–99% of base rate"],
        ["#2 Copper", "Copper with some oxidation/coating", "88–92% of base rate"],
        ["Copper Tubing / Pipe", "Clean, unpainted plumbing pipe", "90–94% of base rate"],
        ["Insulated Copper Wire", "Wire with plastic/rubber coating", "45–65% of base rate"],
    ],
    "brass": [
        ["Yellow Brass (Clean)", "Radiators, fittings, no iron/steel", "95–100% of base rate"],
        ["Red Brass", "Higher copper content, valves/fittings", "100–105% of base rate"],
        ["Brass Shells / Casings", "Ammunition brass, clean", "90–95% of base rate"],
        ["Brass Turnings", "Machine shop swarf, may have oil", "70–80% of base rate"],
    ],
    "aluminium": [
        ["Extrusion (6063, clean)", "Window frames, clean, no paint", "95–100% of base rate"],
        ["Aluminium Sheet/Cast", "Mixed cast + sheet scrap", "80–88% of base rate"],
        ["Aluminium Cans (UBC)", "Used beverage cans, baled", "70–78% of base rate"],
        ["Aluminium Radiators", "Mixed with some copper/plastic", "55–65% of base rate"],
    ],
    "iron": [
        ["Heavy Melting Scrap (HMS 1)", "Clean iron/steel, >6mm thick", "95–100% of base rate"],
        ["HMS 2", "Thinner gauge, some coating", "85–90% of base rate"],
        ["Cast Iron Scrap", "Engine blocks, pipes, machinery", "80–88% of base rate"],
        ["Iron Turnings/Borings", "Machine shop swarf", "55–65% of base rate"],
    ],
    "steel": [
        ["Prime Steel Scrap", "Clean, uncoated structural steel", "95–100% of base rate"],
        ["Mild Steel Sheet", "Sheet/plate offcuts", "88–94% of base rate"],
        ["Steel Rebar Scrap", "Construction rebar cut-offs", "85–90% of base rate"],
        ["Galvanized Steel", "Zinc-coated sheet", "75–82% of base rate"],
    ],
    "stainless-steel": [
        ["SS 304 Scrap", "Kitchen equipment, clean grade 304", "100% of base rate"],
        ["SS 316 Scrap", "Marine/medical grade, higher nickel", "108–115% of base rate"],
        ["SS 202 Scrap", "Lower nickel utility grade", "75–82% of base rate"],
        ["SS Turnings", "Machine shop swarf, mixed grade", "60–70% of base rate"],
    ],
    "zinc": [
        ["Zinc Die Cast (Clean)", "Clean die-cast alloy scrap", "90–96% of base rate"],
        ["Zinc Dross", "Skimmings from galvanizing", "60–70% of base rate"],
        ["Galvanizer's Slab Zinc", "New/unused slab zinc", "98–100% of base rate"],
        ["Old Zinc Sheet", "Roofing/gutter offcuts", "80–86% of base rate"],
    ],
    "lead": [
        ["Soft Lead Scrap", "Clean sheet lead, no battery acid", "95–100% of base rate"],
        ["Lead Battery Scrap", "Whole batteries, drained", "60–70% of base rate"],
        ["Lead Wheel Weights", "Mixed clip/stick-on weights", "80–86% of base rate"],
        ["Lead Pipe/Cable Sheathing", "Old plumbing/cable lead", "85–90% of base rate"],
    ],
    "nickel": [
        ["Nickel Plate/Sheet", "Clean pure nickel offcuts", "97–100% of base rate"],
        ["Nickel Alloy Scrap", "Inconel/Monel mixed alloys", "85–95% of base rate"],
        ["Nickel-Plated Steel", "Steel base with nickel plating", "40–55% of base rate"],
        ["Nickel Turnings", "Machine shop swarf", "70–78% of base rate"],
    ],
    "tin": [
        ["Pure Tin Ingot/Bar", "99.9% pure tin", "98–100% of base rate"],
        ["Tin Solder Scrap", "Electronics solder, mixed lead-tin", "70–85% of base rate"],
        ["Tin-Plated Steel (Tinplate)", "Food cans, mostly steel base", "20–30% of base rate"],
        ["Tin Alloy Scrap", "Bronze/pewter mixed alloys", "60–75% of base rate"],
    ],
}

os.makedirs(os.path.join(BASE, "pages"), exist_ok=True)

for mid, m in metals.items():
    html = template
    html = html.replace("{{NAME}}", m["name"])
    html = html.replace("{{NAME_LOWER}}", m["name"].lower())
    html = html.replace("{{NAME_HI}}", m["nameHi"])
    html = html.replace("{{ID}}", mid)
    html = html.replace("{{SYMBOL}}", m["symbol"])
    html = html.replace("{{COLOR}}", m["color"])
    html = html.replace("{{GRADE_ROWS_JSON}}", json.dumps(GRADES.get(mid, [])))
    out_path = os.path.join(BASE, "pages", f"{mid}-rate-today.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", out_path)

print(f"\nGenerated {len(metals)} metal pages.")

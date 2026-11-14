import ui
from content import get_faq

ui.page_head("Respect the Vest", ui.text("vest_intro"))
ui.split(ui.text("vest_photo"), ui.text("vest_photo_alt"), ui.paras(ui.text("vest_body")), reverse=True)

rules = get_faq()
rules = rules[rules["category"] == "etiquette"].to_dict("records") if not rules.empty else []
if rules:
    ui.section("Service dogs and the law")
    cards = [f'<article class="isd-card"><div class="isd-body"><h3>{ui.esc(r["question"])}</h3>{ui.paras(r["answer"])}</div></article>'
             for r in rules]
    ui.html_block(f'<div class="isd-grid isd-grid-wide">{"".join(cards)}</div>')
ui.html_block(ui.btn("More questions? Read the FAQ", "faq", kind="ghost") + ui.btn("Support our dogs", "sponsor"))

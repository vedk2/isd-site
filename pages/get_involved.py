import ui
from content import get_open_roles, get_site_text, safe_url

ui.page_head("Get Involved", "Foster a future service dog, join as a UIUC student, lend your expertise, or partner with us.")

ui.section("Become a puppy raiser")
docs = []
for key, label in (("puppy_doc_interim_url", "Interim Foster Expectations"),
                   ("puppy_doc_long_term_url", "Long-Term Puppy Raiser Expectations"),
                   ("puppy_doc_timeline_url", "Puppy Raiser Program Expected Timeline")):
    url = safe_url(get_site_text(key))
    if url:
        docs.append(f'<li><a href="{ui.esc(url)}" target="_blank" rel="noopener">{label} (PDF)'
                    f'<span class="isd-sr"> (opens in a new tab)</span></a></li>')
inner = (f'{ui.paras(ui.text("puppy_raiser_text"))}'
         f'{"<p><b>Read before you apply:</b></p><ul>" + "".join(docs) + "</ul>" if docs else ""}'
         f'{ui.btn("Apply to be a puppy raiser", get_site_text("puppy_raiser_form_url"), external=True)}')
ui.split(ui.text("puppy_photo"), ui.text("puppy_photo_alt"), inner, reverse=True)

ui.section("UIUC students")
ui.html_block(ui.paras(ui.text("student_membership_text")))

roles = get_open_roles().to_dict("records")
ui.section("Open volunteer roles", ui.text("volunteer_text"))
if roles:
    cards = []
    for r in roles:
        link = ui.btn("Full job description (PDF)", r["details_link"], kind="ghost", external=True)
        cards.append(f'<article class="isd-card"><div class="isd-body"><span class="isd-tag">Advisory Board</span>'
                     f'<h3>{ui.esc(r["title"])}</h3>{ui.paras(ui.show(r["description"]))}'
                     f'<div class="isd-actions">{link}</div></div></article>')
    ui.html_block(f'<div class="isd-grid isd-grid-wide">{"".join(cards)}</div>')
if ui.email_html("careers_email"):
    ui.html_block(f'<p>Send your resume and the position(s) you\'re interested in to {ui.email_html("careers_email")}.</p>')

ui.section("Partner with us")
partner = ui.text("partner_text")
if ui.email_html("contact_email"):
    ui.html_block(f'{ui.paras(partner)}<p>To plan something together, email {ui.email_html("contact_email")}.</p>')

if safe_url(get_site_text("newsletter_url")):
    ui.section("Stay in the loop")
    ui.html_block(ui.btn("Sign up for our newsletter", get_site_text("newsletter_url"), external=True))

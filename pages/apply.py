import ui
from content import get_site_text

ui.page_head("Apply for a Service Dog", ui.text("apply_who_we_serve"))

ui.section("How it works")
ui.steps([s for s in (ui.text(f"apply_step_{i}") for i in range(1, 6)) if s])

if ui.text("apply_timing_note"):
    ui.section("A note on timing")
    ui.html_block(ui.paras(ui.text("apply_timing_note")))

apply_btn = ui.btn("Open the service dog application", get_site_text("application_url"), external=True)
if apply_btn:
    ui.callout("Ready to apply?", "The application is a secure form hosted by ISD. This website doesn't collect or store any of your information.", apply_btn)
elif ui.email_html("applicants_email"):
    ui.html_block(f'<p>The online application link is being updated. Email {ui.email_html("applicants_email")}.</p>')

if ui.text("apply_eligibility"):
    ui.section("Our commitment to you")
    ui.html_block(ui.paras(ui.text("apply_eligibility")))

rows = []
if ui.email_html("applicants_email"):
    rows.append(f"<li>Questions about applying or your application's status: {ui.email_html('applicants_email')}</li>")
if ui.email_html("tech_email"):
    rows.append(f"<li>Trouble with the form itself: {ui.email_html('tech_email')}</li>")
if ui.email_html("contact_email"):
    rows.append(f"<li>Not sure we can help? Ask us at {ui.email_html('contact_email')}</li>")
if rows:
    ui.section("Questions")
    ui.html_block(f"<ul>{''.join(rows)}</ul>")
ui.html_block(ui.btn("Read the FAQ", "faq", kind="ghost"))

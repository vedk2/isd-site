import ui
from content import get_sponsors, get_team

ui.page_head("About Illini Service Dogs", ui.text("tagline"))

ui.section("Our mission")
ui.split(ui.text("mission_photo"), ui.text("mission_photo_alt"),
         ui.paras(ui.text("mission")) + ui.paras(ui.text("mission_how")), reverse=True)

ui.section("How it all started", "One girl. One dog. One dream.")
ui.split(ui.text("story_photo"), ui.text("story_photo_alt"), ui.paras(ui.text("founding_story")))

team = get_team().to_dict("records")
if team:
    ui.section("Our leadership")
    ui.html_block(ui.paras(ui.text("how_we_are_run")))
    ui.team_by_board(team)

sponsors = get_sponsors().to_dict("records")
if sponsors:
    ui.section("Our sponsors", ui.text("sponsors_intro"))
    ui.logos(sponsors)

ui.section("Contact us")
parts = [f"<p>Email {ui.email_html('contact_email')}. {ui.esc(ui.text('response_time'))}</p>"]
if ui.email_html("applicants_email"):
    parts.append(f"<p>Applying for a service dog or checking on an application? Email {ui.email_html('applicants_email')}.</p>")
parts.append(f"<p>{ui.esc(ui.text('address'))}</p>")
ui.html_block("".join(parts))

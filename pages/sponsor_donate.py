import ui
from content import get_site_text, get_sponsor_tiers

ui.page_head("Sponsor & Donate", ui.text("donation_use"))

give = (ui.btn("Donate with PayPal", get_site_text("paypal_url"), external=True)
        + ui.btn("Donate with Venmo", get_site_text("venmo_url"), external=True)
        + ui.btn("Shop our Amazon Wishlist", get_site_text("amazon_wishlist_url"), kind="ghost", external=True))
ui.section("Give in a minute")
ui.html_block(f"<div>{give}</div>")

tiers = [t for t in get_sponsor_tiers().to_dict("records") if ui.show(t["amount"])]
if tiers:
    ui.section("The impact of your gift", "No amount is too small. Here's what each gift pays for.")
    ui.levels(tiers)

if ui.text("sponsor_note"):
    email = ui.email_html("donate_email")
    ui.html_block(f'<section class="isd-callout"><h2>Sponsor a dog</h2><p>{ui.esc(ui.text("sponsor_note"))}</p>'
                  f'<p>Email {email}</p></section>')

ui.section("Mail a check")
ui.html_block(
    f'<div class="isd-card"><div class="isd-body"><p>Make checks payable to '
    f'<b>{ui.esc(ui.text("check_payable_to", "Illini Service Dogs"))}</b> and mail them to:</p>'
    f'<p>{ui.esc(ui.text("address"))}</p><p>{ui.esc(ui.text("tax_letter_note"))}</p></div></div>'
)

if ui.email_html("donate_email"):
    ui.section("Questions about giving?")
    ui.html_block(f'<p>Email {ui.email_html("donate_email")}.</p>')

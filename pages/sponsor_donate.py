import streamlit as st

import ui
from content import get_site_text, get_sponsor_tiers, safe_url

st.title("Sponsor & Donate")
if ui.text("donation_use"):
    ui.say(ui.text("donation_use"))
if ui.text("impact_line"):
    st.info(ui.md(ui.text("impact_line")), icon=":material/favorite:")

# ---- Sponsor tiers ---------------------------------------------------------
st.header("Sponsor a dog")
tiers = [t for t in get_sponsor_tiers().to_dict("records") if ui.show(t["amount"])]
if tiers:
    def tier_card(tier: dict) -> None:
        with st.container(border=True):
            st.subheader(ui.md(tier["tier_name"]))
            ui.say(f"**{tier['amount']}**")
            if ui.show(tier["covers"]):
                ui.say(tier["covers"])
            if not ui.link_button(f"Sponsor: {tier['tier_name']} ({tier['amount']})", tier["payment_link"],
                                  primary=True, key=f"tier-{tier['_pos']}"):
                # No dedicated link yet: fall back to PayPal, then to email.
                if not ui.link_button(f"Sponsor: {tier['tier_name']} with PayPal", get_site_text("paypal_url"),
                                      primary=True, key=f"tier-pp-{tier['_pos']}"):
                    if ui.email_link("donate_email"):
                        ui.say(f"Email {ui.email_link('donate_email')} to sponsor at this level.")

    ui.grid(tiers, tier_card)
else:
    msg = "Sponsorship levels are coming soon."
    if ui.email_link("donate_email"):
        msg += f" To sponsor a dog today, email {ui.email_link('donate_email')}."
    ui.say(msg)

# ---- Other ways to give ----------------------------------------------------
st.header("Other ways to give")
c1, c2, c3 = st.columns(3)
with c1:
    ui.link_button("Donate with PayPal", get_site_text("paypal_url"), primary=True, key="give-paypal")
with c2:
    ui.link_button("Donate with Venmo", get_site_text("venmo_url"), primary=True, key="give-venmo")
with c3:
    ui.link_button("Shop our Amazon Wishlist", get_site_text("amazon_wishlist_url"), key="give-amazon")

if ui.text("address"):
    st.subheader("Mail a check")
    payee = ui.text("check_payable_to", "Illini Service Dogs")
    ui.say(f"Make checks payable to **{payee}** and mail them to:")
    ui.say(ui.text("address"))

if ui.text("tax_letter_note"):
    ui.say(ui.text("tax_letter_note"))

if ui.email_link("donate_email"):
    st.subheader("Questions about giving?")
    ui.say(f"Email {ui.email_link('donate_email')}.")

if not (safe_url(get_site_text("paypal_url")) or safe_url(get_site_text("venmo_url"))):
    st.caption("Online giving links are being updated.")

import streamlit as st

import ui
from content import dogs_with_status

st.title("Meet the Dogs")
ui.say("These are the dogs in training right now.")

in_training = dogs_with_status("in_training").to_dict("records")
if in_training:
    st.header("In training")
    ui.grid(in_training, lambda d: ui.dog_card(d, key_prefix="training"))
else:
    st.info("Dog profiles are being updated. Check back soon, or follow us on Instagram.")

graduates = dogs_with_status("placed").to_dict("records")
if graduates:
    st.header("Graduates")
    ui.say("These dogs finished training and now work with their partners.")
    ui.grid(graduates, lambda d: ui.dog_card(d, with_sponsor=False, key_prefix="grad"))

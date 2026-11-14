import ui
from content import dogs_with_status, get_gallery

ui.page_head("Meet the Dogs", "Our service dogs in training spend about two years learning the skills their future partner will need. "
             "Follow their progress on Instagram, or sponsor one to help cover food, vet care and training.")

in_training = dogs_with_status("in_training").to_dict("records")
if in_training:
    ui.section("In training now")
    ui.dogs_grid(in_training)
else:
    ui.say("Dog profiles are being updated. Check back soon, or follow us on Instagram.")

graduates = dogs_with_status("placed").to_dict("records")
if graduates:
    ui.section("Graduates", "These dogs finished their training and now work full time with their partners.")
    ui.dogs_grid(graduates, sponsor=False)

photos = get_gallery().to_dict("records")
if photos:
    ui.section("Life at ISD", "Puppies, training days and the people who make it happen.")
    ui.gallery(photos)

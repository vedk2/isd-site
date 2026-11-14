import ui
from content import dogs_with_status, get_news, get_upcoming_events

ui.hero(
    ui.text("hero_eyebrow"),
    ui.text("hero_headline", "Illini Service Dogs"),
    ui.text("hero_subtext"),
    ui.text("hero_photo"),
    ui.text("hero_photo_alt"),
    ui.btn("Sponsor a Dog", "dogs") + ui.btn("Donate", "sponsor") + ui.btn("Apply for a Service Dog", "apply", kind="ghost"),
)
ui.stats()

if ui.text("home_intro"):
    ui.section("Who we are")
    ui.html_block(f'<div class="isd-lead">{ui.paras(ui.text("home_intro"))}</div>')

dogs = dogs_with_status("in_training").head(4).to_dict("records")
if dogs:
    ui.section("Meet the dogs in training", ui.text("home_dogs_lead", 'Every one of them will be placed free of charge with a partner who needs them.'))
    ui.dogs_grid(dogs)
    ui.html_block(ui.btn("Meet all the dogs", "dogs", kind="ghost"))

ui.callout(
    ui.text("home_callout_title", 'Every dog is a gift'),
    ui.text("impact_line", "Every service dog is placed free of charge, thanks to donors like you."),
    ui.btn("Give today", "sponsor", kind="light") + ui.btn("Ways to get involved", "involved", kind="light"),
)

events = get_upcoming_events().head(2).to_dict("records")
if events:
    ui.section("Upcoming events")
    ui.events_grid(events)

news = get_news().head(3).to_dict("records")
if news:
    ui.section("Program news")
    ui.news_cards(news, teaser_only=True)

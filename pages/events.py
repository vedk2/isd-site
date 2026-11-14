import ui
from content import get_site_text, get_upcoming_events

ui.page_head("Events", "Pet-A-Pups, fundraisers and campus events. Come meet the dogs!")

events = get_upcoming_events().to_dict("records")
if events:
    ui.events_grid(events)
else:
    ui.html_block(f'<p class="isd-lead">{ui.esc(ui.text("events_empty_text", "No upcoming events right now. Follow us on Instagram for updates."))}</p>'
                  f'{ui.btn("Illini Service Dogs on Instagram", get_site_text("instagram_url"), external=True)}')

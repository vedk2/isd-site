import ui
from content import get_news

ui.page_head("News", "Placements, new puppies and milestones from Illini Service Dogs.")
news = get_news().to_dict("records")
if news:
    ui.news_cards(news)
else:
    ui.say("No news yet. Check back soon!")

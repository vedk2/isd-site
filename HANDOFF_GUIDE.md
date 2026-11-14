# ISD Website: Guide for Board Members

This guide is for whoever keeps the Illini Service Dogs website up to date. You don't need to know how to code. **Almost everything on the site comes from one Google Sheet.** Edit the Sheet and the website updates itself.

---

## Where everything lives

Fill this table in at handoff and keep it current when board members change.

| What | Where | Who has access |
|---|---|---|
| The website | https://illini-service-dogs.streamlit.app | Anyone (it's public) |
| The Google Sheet (all the words, dogs, events) | [ISD Website Content](https://docs.google.com/spreadsheets/d/1z5ZwdqOOt_CUElizcebk31hHykSxfuWgVYExruFfpFA/edit) | Owner: ISD Google account (transfer at handoff). Editors: board members |
| Dog photos and the code (GitHub) | https://github.com/vedk2/isd-site (move to an ISD account at handoff) | ISD GitHub account + tech lead |
| Hosting (Streamlit Community Cloud) | https://share.streamlit.io (app name: illini-service-dogs) | Sign in with the GitHub account that owns the code |

**At least two board members should always have access to each account.** When someone graduates, add their replacement before removing them.

---

## The golden rules

1. **Don't rename the tabs** (`Dogs`, `FAQ`, `Events`, `SponsorTiers`, `SiteText`, `News`, `Team`, `Sponsors`, `Gallery`, `Roles`) and **don't change the top row** (the column names). The site finds information by those names.
2. **One row = one thing.** One dog, one question, one event.
3. **Not sure yet? Type `[ISD to confirm]`.** Anything that says that (or `$XX`) stays hidden from visitors until you replace it, and the Content Check page lists it so nothing gets forgotten.
4. **Give board members edit access by name** (Share → add their email → Editor). Don't change General access.
5. **Changes show up within 10 minutes.** You don't need to save anything or press a button. Google Sheets saves automatically.

---

## Add a new dog

**Step 1. Upload the photo (about 2 minutes)**

1. Name the photo with the dog's name in lowercase, with no spaces, for example `luna.jpg`.
2. Go to the GitHub link in the table above and sign in.
3. Click the **static** folder, then the **images** folder.
4. Click **Add file → Upload files** and drag in the photo.
5. Scroll down and click the green **Commit changes** button.

The photo is live in a minute or two.

**Step 2. Add a row in the Dogs tab**

| Column | What to type | Example |
|---|---|---|
| name | The dog's name | Luna |
| breed | Breed | Labrador Retriever |
| age | Age, in words | 1 year |
| bio | One or two friendly sentences | Luna loves tennis balls and is learning to open doors. |
| training_stage | A number from 1 to 4 (see below) | 1 |
| photo_file | The exact photo file name from Step 1 | luna.jpg |
| alt_text | A short description of **what's in the photo**, for visitors who are blind or use screen readers | Black Lab puppy in an orange ISD vest, sitting on grass |
| instagram_url | Link to her Instagram post or page (optional) | https://instagram.com/... |
| sponsor_link | A PayPal/Venmo link just for her (optional). Leave blank to send people to the Sponsor page | |
| status | `in_training` | in_training |

Training stages:

1. Puppy basics
2. Public access
3. Advanced mobility tasks
4. Ready for placement

**Writing good alt text:** describe the photo the way you would over the phone, in one sentence. Mention the dog, what they're doing, and anything notable. Skip "image of" or "photo of".

## When a dog is placed (or retires)

In the Dogs tab, change that dog's **status** to `placed`. The dog moves from "In training" to the "Graduates" section and the Sponsor button goes away. Use `retired` to hide the dog from the site completely. Don't delete the row, so you keep their history.

## Move a dog to the next training stage

Change the number in **training_stage**. The progress bar on their card updates.

---

## Edit or add an FAQ answer

These answers power both the FAQ and the **Ask ISD** chatbot.

- **To edit**, change the text in the **answer** column.
- **To add**, add a new row with a **question**, an **answer**, and a **category**: `applying`, `service_dogs`, `donating`, `sponsoring`, `puppy_raising`, `volunteering`, `about_isd` or `general`. The FAQ page groups questions by category.
- **The keywords column** is how you teach the chatbot. If people ask something in a way the bot doesn't recognize, add their words here, separated by commas. For example: `cost, price, fee, free, afford`.

If the chatbot isn't sure, it never guesses. It tells the visitor to email ContactUs@illiniservicedogs.com. So if the team keeps getting the same question by email, add it to the FAQ.

The starter FAQ was drafted by the student team from the old website. **Please read every answer once and correct anything that's out of date.**

---

## Post an event

Add a row in the **Events** tab:

| Column | Example |
|---|---|
| title | Pet-A-Pup on the Quad |
| date | 2027-04-18 (year-month-day works best) |
| start_time | 2:00 PM |
| location | Main Quad, near Foellinger |
| description | Meet our dogs in training! Donations welcome. |
| link | Optional: Facebook event, sign-up form, etc. |

Events show up in date order. **Once the date has passed, the event hides itself.** You can delete old rows whenever you want, or leave them.

---

## Change the giving levels

The **SponsorTiers** tab holds the "impact of your gift" levels on Sponsor & Donate (from $1 for a treat up to $10,000 to sponsor a dog). Each row is one level:

- **tier_name**: a short label, like `Food`.
- **amount**: the price, like `$30`. A level with `$XX` stays hidden.
- **covers**: what the money pays for.
- **payment_link**: optional. A PayPal or Venmo link just for that level adds a "Give" button to it.
- **sort_order**: 1 shows first, 2 second, and so on. The last level is highlighted.

## Post a news story

Add a row to the **News** tab: **title**, **date** (like `2027-04-18`), **body** (press Ctrl+Enter twice inside the cell to start a new paragraph), and optionally a **photo_file** and its **alt_text**. The newest stories show first, and the three newest also appear on the Home page.

## Update the leadership, sponsors, photos or open roles

- **Team** tab: one row per person. **board** is `administrative`, `executive` or `advisory`. Upload a headshot to static/images and put its file name in **photo_file**; without a photo, the site shows the person's initials. When someone leaves, delete their row.
- **Sponsors** tab: name, website link and (optionally) a logo file.
- **Gallery** tab: the photo grid on Meet the Dogs. Upload the photo, then add a row with its file name and a one-sentence **alt_text** describing it.
- **Roles** tab: open volunteer positions on Get Involved. Type `no` in **is_open** to hide a role without deleting it.

## Change any other words on the site

Every paragraph, email address and link is in the **SiteText** tab. Find the row (the **where_it_shows** column tells you which page it's on) and edit the **value** column. Don't change the **key** column.

---

## Something looks wrong? Check the Content Check page

Open the website and click **Content Check (board members)**, the last item in the menu. It tells you in plain English:

- whether the site is reading the Google Sheet or a backup copy
- rows it skipped and why (for example, an event date it couldn't read)
- dogs missing a photo or alt text
- anything still marked `[ISD to confirm]`

Fix the problem in the Sheet, then click **Check the Sheet again now** on that page.

**If a tab says "showing the backup copy":** the site couldn't read the Sheet, so it's showing the last saved version. Visitors still see a working site. The usual causes are that someone renamed a tab or a column, or the Sheet's sharing was changed. In the Sheet, **Share → General access** must stay **Anyone with the link → Viewer**. Viewer only: never give "Editor" to anyone with the link.

## The site is "asleep"

The free hosting puts the site to sleep when nobody has visited for a while. If you see a "This app has gone to sleep" message, click the button and wait about 30 seconds. Nothing is broken.

---

## Once a semester (5 minutes)

- [ ] Read the FAQ and fix anything outdated
- [ ] Update training stages and mark placed dogs
- [ ] Open Content Check and clear anything on it
- [ ] Make sure two current board members can sign in to the Google, GitHub and Streamlit accounts
- [ ] Ask your tech person to refresh the backup copy (README: "Refreshing the backup")

---

## Ideas for later

- **Newsletter:** set up a free Mailchimp or Google Form signup and put its link in SiteText → `newsletter_url`. A "Stay in the loop" button then appears on Get Involved.
- **More dog photos:** good photos are the biggest reason people sponsor. Aim for one clear, bright photo per dog.
- **Link from the main website:** add a big "Meet our dogs and sponsor one" button on illiniservicedogs.com that points here. It brings visitors and keeps the site from falling asleep.
- **Impact numbers:** fill in SiteText → `impact_line` (for example, how many dogs ISD has placed). Specific numbers help donations.
- **PayPal button:** paste ISD's PayPal donation link into SiteText → `paypal_url`. The old site's PayPal button was set up inside Wix, so we couldn't copy its link.
- **Fresh news:** the newest stories are from 2025. A short post each semester (new puppies, placements, events) keeps the site feeling alive.

Questions about the code go to whoever is listed as tech lead in the table at the top. Original builders: Ved Kulkarni and Nithin Raj (BUS 401, Fall 2026).

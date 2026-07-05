> *Retire gear before it retires you.*

You've got ropes that have seen better days, a helmet that might be older than your nephew, and a backpack stuffed with gear you can't quite account for. BasecampBuddy is the trusty logbook you always meant to keep — except it lives on your computer, doesn't get wet in the rain, and actually reminds you when something needs checking.

Born out of 10 years of iteration, false starts, and the occasional "why did I build it like *that*" moment, BasecampBuddy is a no-frills, terminal-based Python tool for climbers, campers, and outdoor enthusiasts who want to know exactly what's in their kit, how old it is, and whether it's ready for the next adventure — before they're halfway up a crag wondering.

---

- [Features](#features)
- [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
  * [Running the App](#running-the-app)
- [Project Structure](#project-structure)
- [Philosophy](#philosophy)
- [Thanks to:](#thanks-to-)

---

# Features
- **Gear inventory** — catalogue equipment by brand and category, with purchase dates and notes
- **Consumables tracking** — separate management for items that get used up (gas canisters, batteries, fuel) rather than just worn out
- **Age tracking** — know at a glance how long each piece of kit has been in service
- **Inspection logging** — record when you last checked each item and flag anything overdue
- **Trip & kit management** — organise gear into kits and trips so nothing gets left behind
- **Brand & category management** — keep your inventory structured your way
- **CLI menu interface** — clean, interactive terminal menus; no GUI required, no internet needed
- **SQLite storage** — lightweight local database; your data stays on your machine
- **Configurable setup** — sensible defaults out of the box, tweakable via 
``config/config.json``

- **Internationalisation** — built-in i18n support, English included and more languages ready to add

---

# Getting Started

## Prerequisites

- Python 3.8+
- No external services required — this runs fully offline

## Installation

```bash
git clone https://github.com/bashtux/BasecampBuddy.git
cd BasecampBuddy
pip install -r requirements.txt   # if a requirements file is present
```

## Running the App

```bash
python -m main
```

That's it. The app will initialise your data store on first run and drop you into the main menu.

---

# Project Structure

```
BasecampBuddy/
├── main.py                        # Entry point
└── app/
    ├── cli/                       # Interactive terminal menus & user-facing functions
    │   ├── menu.py                # Main menu navigation
    │   ├── gear_functions.py      # Gear CRUD operations
    │   ├── brand_functions.py     # Brand management
    │   ├── category_functions.py  # Category management
    │   └── consumable_functions.py# Consumables (e.g. gas, batteries)
    ├── core/                      # Domain models
    │   ├── gear_item.py           # Gear item model
    │   ├── kit_item.py            # Kit/bundle model
    │   ├── trip.py                # Trip model
    │   └── utils/
    │       ├── db_utils.py        # Database helpers
    │       └── validation.py      # Input validation
    ├── data/                      # Data layer
    │   ├── initializer.py         # DB bootstrap on first run
    │   ├── user_db.py             # User data access
    │   └── db/
    │       ├── base_db.py         # Base database class
    │       ├── gear_db.py         # Gear data access
    │       └── program_db.py      # App-level data access
    ├── config/
    │   ├── config.json            # User configuration
    │   └── defaults.json          # Default settings
    ├── i18n/en/                   # Localisation strings (English)
    ├── config_manager.py          # Configuration loading
    └── lang.py                    # Language/i18n loader
```

---

# Feature ideas

## General features
- [ ] implement sub categories for better sorting
- [ ] Data import
- [ ] before saving an editted item, show before and after and confirm
- [ ] Assign gear in trips to poeple of the crew
- [ ] Change from kg to lbs
- [ ] way to sort/search when selecting brand, consumables, gear (partially implemented)
- [ ] categories for consumables
- [ ] select localisation for date format
- [ ] set currency in configuration
- [ ] general install script
- [ ] Have sotrage place for gear

## Reports / Printing / Checking
- [ ] LaTex / LO calc / csv export of lists
- [ ] Check all Brand URL if they're (still) valid
- [ ] Print contents of strage places
- [ ] List by category
- [ ] check if gear / kit is deleted from kit / trip so there's no dangling kits or trips
- [ ] On startup check what gear has not been checked by now and inform user, possible to turn on/off in settings
- [ ] LaTex (pdf) export of trips and kits

## CLI
- [ ] Get Terminal widht and scale lists accordingly
- [ ]  nicer layout for lists and gear, kit, trips

## TUI
> not started at the moment, happy to take requests

## GUI 
> not started at the moment, happy to take requests

---

# Philosophy

BasecampBuddy is deliberately simple. It runs in your terminal, stores data locally, and does one thing well: helps you keep track of your outdoor gear so you can spend less time rummaging and more time out there.

No subscriptions. No cloud sync. No ads for carabiners. Just a solid piece of software for people who take their kit seriously.

---

# Thanks to:

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

*Happy trails. Check your gear. Come home safe.*

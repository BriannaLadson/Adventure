# Adventure v0.25.0

Adventure is an open-world sandbox RPG simulation built using Python and Tkinter.

Explore a procedurally generated fantasy world, earn a living through professions, trade with dynamic markets, discover new locations, and build your own story through interacting simulation systems rather than scripted quests.

For more information on game systems, modding, and development, see the project [Wiki](https://github.com/BriannaLadson/Adventure/wiki).

## Current Features

### World Generation & Exploration

- Procedurally generated worlds, civilizations, settlements, and local maps
- Persistent regions with biome-specific fauna, flora, minerals, trees, and water
- Human, Dwarf, Elf, and Goblin civilizations with distinct naming systems and profession distributions
- Location discovery and cartography
- Player-created maps with skill-based coordinate accuracy

### Characters & Progression

- Tabbed character creation with identity, ancestry, skill potential, starting items, and role selection
- Manual and procedural character naming, with Human, Dwarf, Elf, and Goblin naming systems
- Mixed ancestry with ancestry-based needs and dietary compatibility
- Skill XP, leveling, and configurable potential
- Strength and Speed progression through movement
- Strength-based carrying capacity and encumbrance-based movement penalties
- JSON-defined starting roles with related skills and equipment

### NPCs & AI

- Persistent town NPCs generated during world creation, with local positions assigned when the town map loads
- Settler, Wanderer, and Nomad migration traits with stay lengths based on the world calendar
- NPCs ready to migrate walk to the edge of the active town, then continue traveling across the overworld as time advances
- Traveling NPCs discover nearby settlements and can settle in a new town, where they begin a fresh stay
- JSON-defined NPC bitmap sprites and race-specific color palettes, with character symbols as a fallback
- Town and overworld debug logs for inspecting NPC actions and migration
- Profession-based work planning with queued actions
- First, second, and third work-shift traits
- Miners that collect ore and sell it at randomly selected shops
- Profession-defined starting equipment with randomized item variants
- Randomized profession skill levels and individual skill potentials
- Wandering and idling when no work is assigned
- Town pathfinding around buildings and occupied tiles
- Door-based building interactions, with NPCs hidden while inside
- NPC AI updates during player mining sessions
- Console debugging for following a selected NPC
- Hunters that catch biome-specific game and sell carcasses at local markets
- Butchers and tanners that buy materials, select matching recipes, and sell finished products
- Tree cutters that harvest wood using regional tree abundance and Wood Cutting skill, then sell it at local markets
- Local and offscreen work routines for all 15 NPC professions
- Migrants can work, buy necessities, and restock supplies in their destination towns
- Paper makers, wood burners, smelters, and blacksmiths that craft goods, sell them at local markets, and buy materials when supplies are available and affordable
- Coinsmiths that mint coins and keep the proceeds in their wallets
- Water collectors and foragers that gather local resources and sell them at market
- Cartographers that buy ink and available parchment variants, draw maps, and sell them at market
- Skill-based starting recipe selection and matching starter materials for professions such as smelters, coinsmiths, and blacksmiths

### Economy & Banking

- Dynamic pricing, supply and demand, production chains, and settlement inventories
- Markets and banks with unlimited transaction funding, independent of town treasuries
- Civilization-specific currencies and multi-currency wallets
- Player and NPC currency exchange with bank-specific fees, including offscreen NPC exchanges
- Checking accounts with minimum opening deposits, deposits, withdrawals, and account closure
- Market category filtering and scrollable Buy/Sell lists

### Items, Crafting & Gathering

- Inventory management, item transfers, dropping, and pickup
- Item weight and character encumbrance
- Data-driven item types and crafting reactions
- Skill-based crafting with ingredient consumption, crafting time, and recipe tooltips
- Biome-specific fruit foraging and multiple fruit and wine varieties
- Automatically generated wine types and brewing reactions
- JSON-defined metals with generated ores, bars, coins, and pickaxes
- Blacksmith production of metal pickaxes
- Pickaxe-required mining sessions lasting 1–24 hours
- Shared player and NPC mining results based on regional minerals and Mining skill
- JSON-defined animal species with biome habitats and configurable hide and meat yields
- Generated species-specific carcasses, hides, meat, leather, and crafting reactions
- Species-specific parchment made from matching animal hides
- Foraging success based on Foraging skill and local flora, with the biome determining which fruits can be found
- Water collection based on local water abundance

### Controls & Extensibility

- Wait command (`.`) to advance one turn without moving
- Data-driven systems designed for expansion and modding

## What's New in v0.25.0

- All 15 NPC professions now run in offscreen settlements. NPCs can gather resources, craft goods, sell products, and restock supplies according to their profession.
- Migrants can resume work and trade after settling in a new town.
- NPCs can exchange foreign coins for local currency at banks during their free time. In the active town, they walk to the bank. In offscreen towns, they can exchange coins during an offscreen update. Both use the local bank's exchange fee.
- Fixed duplicate town AI updates during player mining sessions.
- Migration now tracks an NPC's previous settlement by overworld coordinates, reducing the links between town objects in saved worlds.
- A temporarily unwritable debug log no longer interrupts the simulation.

### Save Compatibility

Start a new world for v0.25.0. Saves from earlier versions are unsupported.

## Screenshots

### World Generation

<img width="1366" height="768" alt="Screenshot (689)" src="https://github.com/user-attachments/assets/1169fd7e-50c6-424e-ae52-157c41584ab7" />

### NPC Migration
<img width="1366" height="768" alt="Adventure Migrant" src="https://github.com/user-attachments/assets/bcb62e97-b467-4afb-ab7b-c794db1acd68" />

## Installation

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually install dependencies:

```bash
pip install terraforge-core cqcalendar dyecon numpy pillow noise tkinter-tooltip bite-core
```

## Running the Project

```bash
python main.py
```

## Dependencies

Current dependencies include:

- terraforge-core
- cqcalendar
- dyecon
- numpy
- pillow
- noise
- tkinter-tooltip
- bite-core

## Libraries

- [CQCalendar](https://github.com/BriannaLadson/CQCalendar): A customizable, tick-based time and calendar system for Python games and simulations.
- [TerraForge](https://github.com/BriannaLadson/TerraForge): A versatile Python toolset for procedural map generation.
- [DyEcon](https://github.com/BriannaLadson/DyEcon): A lightweight dynamic economy simulation library for Python games and simulations.
- [Bite](https://github.com/BriannaLadson/Bite) — A Python library for defining, resizing, and recoloring 1-bit bitmap sprites.

## License

This project is licensed under the MIT License.

# Adventure v0.23.0

Adventure is an open-world sandbox RPG simulation built using Python and Tkinter.

Explore a procedurally generated fantasy world, earn a living through professions, trade with dynamic markets, discover new locations, and build your own story through interacting simulation systems rather than scripted quests.

For more information on game systems, modding, and development, see the project [Wiki](https://github.com/BriannaLadson/Adventure/wiki).

## Current Features

### World Generation & Exploration

- Procedurally generated worlds, civilizations, settlements, and local maps
- Persistent regions with biome-specific fauna, flora, minerals, trees, and water
- Human, Dwarf, and Elf civilizations with distinct profession distributions
- Location discovery and cartography
- Player-created maps with skill-based coordinate accuracy

### Characters & Progression

- Tabbed character creation with identity, ancestry, skill potential, starting items, and role selection
- Manual and procedural character naming, with Human, Dwarf, and Elf naming systems
- Mixed ancestry with ancestry-based needs and dietary compatibility
- Skill XP, leveling, and configurable potential
- Strength and Speed progression through movement
- Strength-based carrying capacity and encumbrance-based movement penalties
- JSON-defined starting roles with related skills and equipment

### NPCs & AI

- Persistent town NPCs generated from settlement demographics
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
- Work routines for all current NPC professions
- Paper makers, wood burners, smelters, and blacksmiths that craft goods, sell them at local markets, and buy materials when supplies are available and affordable
- Coinsmiths that mint coins and keep the proceeds in their wallets
- Water collectors and foragers that gather local resources and sell them at market
- Cartographers that buy ink and available parchment variants, draw maps, and sell them at market
- Skill-based starting recipe selection and matching starter materials for professions such as smelters, coinsmiths, and blacksmiths

### Economy & Banking

- Dynamic pricing, supply and demand, production chains, and settlement inventories
- Markets and banks with unlimited transaction funding, independent of town treasuries
- Civilization-specific currencies and multi-currency wallets
- Currency exchange with procedurally generated fees
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

## What's New in v0.23.0

- Completed work AI for the current NPC professions. NPCs can earn money through gathering, crafting, trade, and coin minting. Their earnings depend on skill, material availability, and local prices.
- Added paper maker work routines and species-specific parchment recipes. Cartographer NPCs can buy and use the new parchment variants to make maps.
- Added wood burner, smelter, and blacksmith work routines. Wood burners make coal, smelters turn ore into bars, and blacksmiths use bars, coal, and wood to forge pickaxes for sale.
- Added coinsmith work routines. Successfully minted coins go directly into the coinsmith's wallet.
- Added water collector and forager work routines. Water collectors supply local markets with water, and foragers gather biome-specific fruit using the Foraging skill.
- Removed water from background foraging, making water collectors the dedicated water-producing profession.

### Save Compatibility

Start a new save for v0.23.0.

## Screenshots

### Start Screen

<img width="1366" height="768" alt="Screenshot (711)" src="https://github.com/user-attachments/assets/40c47fa3-1d76-41cd-8c5c-3847fb5411c2" />

### Character Creation

<img width="1366" height="768" alt="Screenshot (713)" src="https://github.com/user-attachments/assets/e753174e-20fc-4849-933f-6156b434bed9" />

### World Generation

<img width="1366" height="768" alt="Screenshot (689)" src="https://github.com/user-attachments/assets/1169fd7e-50c6-424e-ae52-157c41584ab7" />

### Location Discovery

<img width="1366" height="768" alt="Screenshot (690)" src="https://github.com/user-attachments/assets/7e314f0c-3440-407d-8644-1ee6d94698ab" />

### Location Buildings

<img width="1366" height="768" alt="Screenshot (691)" src="https://github.com/user-attachments/assets/148166e2-c76e-4631-942d-9dada324dd4d" />

### Economy

<img width="1366" height="768" alt="Screenshot (714)" src="https://github.com/user-attachments/assets/4c972c49-b8ca-4b93-9816-05a27b68ebf6" />

### Character Sheet

<img width="1366" height="768" alt="Screenshot (715)" src="https://github.com/user-attachments/assets/03423746-b47a-4cc5-8893-513d8012aa05" />

<img width="1366" height="768" alt="Screenshot (716)" src="https://github.com/user-attachments/assets/3395247a-e779-4051-a745-dffce677f822" />

<img width="1366" height="768" alt="Screenshot (717)" src="https://github.com/user-attachments/assets/561f04c5-521d-4174-a6b0-4d680e0011b8" />

<img width="1366" height="768" alt="Screenshot (719)" src="https://github.com/user-attachments/assets/1b5e9ecb-90e7-4388-9a9c-bc42dd095e5b" />

<img width="1366" height="768" alt="Screenshot (720)" src="https://github.com/user-attachments/assets/23851090-11d5-4040-aef1-05a27b68ebf6" />

<img width="1366" height="768" alt="Screenshot (721)" src="https://github.com/user-attachments/assets/6507447d-b5b7-4b68-84e5-f2aeaf00fa9c" />

## Installation

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually install dependencies:

```bash
pip install terraforge-core cqcalendar dyecon numpy pillow noise tkinter-tooltip
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

## Libraries

- [CQCalendar](https://github.com/BriannaLadson/CQCalendar): A customizable, tick-based time and calendar system for Python games and simulations.
- [TerraForge](https://github.com/BriannaLadson/TerraForge): A versatile Python toolset for procedural map generation.
- [DyEcon](https://github.com/BriannaLadson/DyEcon): A lightweight dynamic economy simulation library for Python games and simulations.

## License

This project is licensed under the MIT License.
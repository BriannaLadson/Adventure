# Adventure v0.19.0

Adventure is an open-world sandbox RPG simulation built using Python and Tkinter.

Explore a procedurally generated fantasy world, earn a living through professions, trade with dynamic markets, discover new locations, and build your own story through interacting simulation systems rather than scripted quests.

For more information on game systems, modding, and development, see the project [Wiki](https://github.com/BriannaLadson/Adventure/wiki).

## Current Features

- Procedurally generated worlds, civilizations, settlements, and local maps
- Persistent overworld regions with biome-specific environmental resources
- Regional fauna, flora, minerals, trees, and water
- Biome-specific fruit foraging
- Multiple fruit and wine varieties
- Automatically generated wine types and crafting reactions
- Brewing and other resource-based professions
- Dynamic economy with production chains, supply and demand, and settlement inventories
- Data-driven crafting reactions and item types
- Exploration, cartography, and location discovery
- Character stats with skill XP, leveling, and progression
- Strength and Speed skills that improve through movement
- Strength-based maximum encumbrance
- Speed-based overworld travel time
- Over-encumbrance penalties that slow overworld movement
- Inventory management, item transfer, item dropping, and item pickup
- Item weight and character encumbrance system
- Multi-currency wallet system with civilization-specific currencies
- Trading with procedurally generated markets and dynamic pricing
- Banks with settlement-based currency reserves
- Currency exchange between civilization-specific currencies
- Procedurally generated currency exchange fees
- Checking accounts with procedurally generated minimum opening deposits
- Checking account deposits, withdrawals, balances, and account closure
- Data-driven architecture designed for expansion and modding
- Tabbed character creation with Identity, Items, and Start settings
- Ratio-based character ancestry with support for mixed ancestry
- Ancestry-based generation of need capacities, decay rates, and dietary compatibility
- Dietary compatibility checks to ensure generated characters can satisfy their needs
- Character sheet Identity tab displaying ancestry percentages
- Mine buildings with pickaxe-required mining sessions lasting 1–24 hours
- Mining success based on regional minerals and Mining skill
- JSON-defined metals with automatically generated ores, bars, coins, and pickaxes
- Blacksmith production of metal pickaxes
- Market category filtering and scrollable Buy/Sell lists
- Player crafting with skill filters and recipe tooltips
- Skill-based crafting success, ingredient consumption, and crafting time
- Player-created maps of discovered settlements with skill-based coordinate accuracy

## What's New in v0.19.0

- Added player crafting for brewing, smelting, coinsmithing, blacksmithing, butchering, tanning, wood burning, ink making, and parchment making.
- The Crafting tab lists reactions with a skill filter and hover tooltips showing ingredients, products, and time costs.
- Crafting success chance equals the relevant skill level as a percentage, capped at 100%.
- Failed crafting attempts consume ingredients and time but still grant skill XP.
- Added player cartography with a popup for selecting a discovered settlement.
- Drawing a map consumes Parchment and Ink, advances time, and grants Cartography XP. Cartography skill determines coordinate accuracy.
- Player and settlement maps now share a base-value formula: Parchment base value + Ink base value + Cartography level.
- Metal definitions now generate ores alongside bars, coins, and pickaxes, removing the need for separate ore JSON definitions.
- Coinsmiths can produce any loaded coin type and add it to the settlement's wallet.
- Parchment production now requires Animal Hide.
- Added `tkinter-tooltip` as a dependency.

### Save Compatibility

Start a new save for v0.19.0. Existing saves are not migrated to include the new crafting skills, reactions, and generated ore definitions.

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
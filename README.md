# Adventure v0.20.1

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
- Tabbed character creation with Identity, Skill Potential, Items, and Start settings
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
- JSON-defined starting roles with related skills and equipment
- Selectable starting skill experience for character roles
- Manual character naming and procedural name generation
- Human, Dwarf, and Elf civilizations with distinct profession distributions
- Persistent town NPCs generated from settlement demographics
- Goal-based NPC AI with action queues for wandering and idling
- Wait command (`.`) that advances one turn without moving
- Configurable potential for each skill, determining maximum XP gained per action

## What's New in v0.20.0

- Added starting roles defined through JSON, including Peasant and skill-based professions.
- Added starting experience options: Untrained, Beginner, Apprentice, Journeyman, and Master.
- Added first, middle, and last name entries with individual random name generation buttons and a naming system selector.
- Added Human, Dwarf, and Elf character naming systems.
- Added Elves with their own civilizations, settlements, dietary profile, currency, and nature-focused profession distribution.
- Added persistent NPCs to town maps, with generated names, ancestry, and professions.
- Generating an NPC removes one corresponding worker from the settlement's background demographics.
- Added an extensible NPC AI system with goals, queued actions, wandering, and idling.
- NPCs avoid buildings, occupied NPC tiles, and the player's tile when moving.
- Added the `.` key to wait one turn.
- Added a Skill Potential tab to character creation, with values from 1–100 and a default of 1.
- Added individual skill potential randomization buttons and presets for changing all potentials at once.
- Skill potential now determines the maximum XP gained per action.

### Save Compatibility

Start a new save for v0.20.0 to include roles, Elves, character naming systems, NPCs, and skill potential. Existing saves are not migrated to the new systems.

## Screenshots

### Start Screen

<img width="1366" height="768" alt="Screenshot (711)" src="https://github.com/user-attachments/assets/40c47fa3-1d76-41cd-8c5c-3847fb5411c2" />

### Character Creation

<img width="1366" height="768" alt="Screenshot (908)" src="https://github.com/user-attachments/assets/041eabe9-ec1d-474d-8a04-4d06b1d0bcb1" />

<img width="1366" height="768" alt="Screenshot (909)" src="https://github.com/user-attachments/assets/5666eb76-a3a2-49ae-8da1-741323332a96" />


### World Generation

<img width="1366" height="768" alt="Screenshot (689)" src="https://github.com/user-attachments/assets/1169fd7e-50c6-424e-ae52-157c41584ab7" />

### Location Discovery

<img width="1366" height="768" alt="Screenshot (690)" src="https://github.com/user-attachments/assets/7e314f0c-3440-407d-8644-1ee6d94698ab" />

### Towns

<img width="1366" height="768" alt="Screenshot (912)" src="https://github.com/user-attachments/assets/e4001999-03ee-4dda-813f-7f6e36a2be4e" />


### Economy

<img width="1366" height="768" alt="Screenshot (913)" src="https://github.com/user-attachments/assets/f7056559-6e0a-4eb3-937a-cbc1c99e00b1" />


### Character Sheet

<img width="1366" height="768" alt="Screenshot (910)" src="https://github.com/user-attachments/assets/ccb38f7d-39f1-4f78-8da8-e5937c3dbeda" />


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

# Adventure v0.10.0

Adventure is a sandbox RPG simulation built using Python and Tkinter.

The project focuses on procedural generation, exploration, simulation systems, and emergent gameplay.

Rather than following a predefined storyline, Adventure aims to create a world where stories emerge naturally through the interaction of game systems.

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
<img width="1366" height="768" alt="Screenshot (691)" src="https://github.com/user-attachments/assets/148166e2-c76e-4631-942c-9dada324dd4d" />

### Economy
<img width="1366" height="768" alt="Screenshot (714)" src="https://github.com/user-attachments/assets/4c972c49-b8ca-4b93-9816-2dd736781c6a" />

### Character Sheet
<img width="1366" height="768" alt="Screenshot (715)" src="https://github.com/user-attachments/assets/03423746-b47a-4cc5-8893-513d8012aa05" />

<img width="1366" height="768" alt="Screenshot (716)" src="https://github.com/user-attachments/assets/3395247a-e779-4051-a745-dffce677f822" />

<img width="1366" height="768" alt="Screenshot (717)" src="https://github.com/user-attachments/assets/561f04c5-521d-4174-a6b0-4d680e0011b8" />

<img width="1366" height="768" alt="Screenshot (719)" src="https://github.com/user-attachments/assets/1b5e9ecb-90e7-4388-9a9c-bc42dd095e5b" />

<img width="1366" height="768" alt="Screenshot (720)" src="https://github.com/user-attachments/assets/23851090-11d5-4040-aef1-05a27b68ebf6" />

<img width="1366" height="768" alt="Screenshot (721)" src="https://github.com/user-attachments/assets/6507447d-b5b7-4b68-84e5-f2aeaf00fa9c" />



## Current Features

### Procedural World Generation

* Procedurally generated overworld maps powered by TerraForge
* Multi-noise terrain generation using elevation, moisture, and temperature maps
* Rule-based biome generation system
* Configurable island generation settings
* Large configurable world sizes
* Configurable local map sizes
* Wraparound overworld generation and rendering
* Procedural biome map rendering
* Biome-colored local maps

### Civilization & Settlement Generation

* Procedurally generated civilizations
* Race-based civilization generation
* Procedurally generated capitals
* Procedurally generated settlements
* Biome-restricted settlement placement
* Civilization culture systems
* Procedural civilization naming
* Procedural settlement naming
* JSON-driven naming systems
* Custom settlement map icons and colors
* Procedurally generated settlement professions
* Procedurally generated settlement resources
* Procedurally generated settlement building layouts
* Enterable settlement maps powered by TownForge
* Market buildings

### Dynamic Economy

* DyEcon integration
* Global economy system
* Settlement-level sub economies
* Profession-based production
* Daily production cycles
* Dynamic item pricing
* Settlement inventories
* Settlement gold reserves
* Supply and demand simulation
* Production chain simulation
* Resource scarcity and surplus tracking
* Buy and sell item system
* Buy and sell map system
* Settlement consumption simulation

### Production Chains

Current production chains include:

* Animal Corpse → Animal Hide → Animal Leather → Parchment
* Wood → Coal → Ink
* Gold Ore → Gold Bar → Gold Coin

Current professions include:

* Hunter
* Butcher
* Tanner
* Paper Maker
* Tree Cutter
* Wood Burner
* Ink Maker
* Cartographer
* Miner
* Smelter
* Coinsmith
* Water Collector
* Forager

### Cartography

* Procedural location discovery
* Character location memory
* Known location tracking
* Settlement visibility based on player knowledge
* Cartographer profession
* Settlement-generated maps
* Unique map items
* Map buying and selling
* Cartography-based map accuracy
* Map production using parchment and ink
* Foundations for map-based exploration gameplay

### Exploration & Discovery

* Overworld exploration
* Local tile-based exploration
* Enterable locations
* Overworld-to-local map transitions
* 8-directional movement system
* Command-based input system
* Character memory system
* Location discovery system
* Discovery notifications
* Settlement visibility based on player knowledge
* Known location tracking
* Player location tracking across world and local maps

### Character & Inventory Systems

* Character Sheet
* Inventory system
* Item inspection interface
* Inventory tracking
* Player gold tracking
* Discovered location tracking
* Memory interface
* Map inventory items
* Character needs system
* Consumable food and drink items

### Survival
* Hunger system
* Thirst system
* Food consumption
* Drink consumption
* Need-based character death
* Settlement food production
* Settlement water production
* Settlement resource consumption

### Time & Simulation

* CQCalendar integration
* Persistent in-game calendar
* In-game clock
* Date tracking
* Variable time progression based on player actions
* Daily simulation updates
* Calendar-driven settlement production
* Hourley need decay
* Daily settlement consumption

### Rendering & UI

* Canvas-based tile map renderer
* Player-centered camera system
* Zoomable map display
* Dynamic tile resizing
* Settlement/location markers displayed on the overworld
* Settlement map rendering
* Building rendering
* Building interaction system
* Market interface
* Trade interface
* Character Sheet interface
* Dedicated world generation screen
* Interactive procedural generation settings UI
* Character creation flow
* Start screen with new game/load game options
* Multi-screen Tkinter UI architecture
* Fullscreen Tkinter application framework

### Procedural Generation Controls

* Editable procedural generation settings directly from the UI
* Configurable seeds
* Adjustable octaves
* Adjustable persistence
* Adjustable lacunarity
* Adjustable falloff settings
* Adjustable zoom values
* Adjustable redistribution values
* Randomize buttons for generation settings

### Architecture & Data Systems

* JSON-driven data architecture
* External world settings configuration
* External race configuration
* External biome configuration
* External naming system configuration
* Prefix-based modular data loader system
* Modular project structure
* Expandable procedural generation pipeline
* Expandable RPG framework
* Save system using shelve
* Utility systems for save management and procedural color handling

## Installation

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually install dependencies:

```bash
pip install terraforge-core cqcalendar dyecon numpy pillow noise
```

## Running the Project

```bash
python main.py
```

## Dependencies

Current dependencies include:

* terraforge-core
* cqcalendar
* dyecon
* numpy
* pillow
* noise

## Libraries

* [CQCalendar](https://github.com/BriannaLadson/CQCalendar): A customizable, tick-based time and calendar system for Python games and simulations.
* [TerraForge](https://github.com/BriannaLadson/TerraForge): TerraForge is a versatile Python toolset for procedural map generation.
* [DyEcon](https://github.com/BriannaLadson/DyEcon): A lightweight dynamic economy simulation library for Python games and simulations.

## License

This project is licensed under the MIT License.

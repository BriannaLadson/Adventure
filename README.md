# Adventure v0.3.0

Adventure is a sandbox RPG simulation built using Python, Tkinter, and TerraForge, a procedural generation library I created.

The project focuses on procedural generation, exploration, simulation systems, and emergent gameplay.

Rather than following a predefined storyline, Adventure aims to create a world where stories emerge naturally through the interaction of game systems.

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

### Gameplay Systems

* Overworld exploration
* Local tile-based exploration
* Enterable locations
* Overworld-to-local map transitions
* 8-directional movement system
* Command-based input system
* Player location tracking across world and local maps
* Save system with persistent world data
* Save slot creation and overwrite handling

### Rendering & UI

* Canvas-based tile map renderer
* Player-centered camera system
* Zoomable map display
* Dynamic tile resizing
* Settlement/location markers displayed on the overworld
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
* Utility systems for save management and procedural color handling

## Project Status

This repository contains the public release version of Adventure.

Development continues beyond the public release. New systems and features are developed and tested before eventually being merged into the public version.

## Planned Features

* Time and calendar systems
* Character memory
* Location discovery
* Cartography
* NPC simulation
* Conversations
* Professions
* Dynamic economy
* Information sharing
* Emergent storytelling

## Installation

### Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Adventure.git
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually install TerraForge:

```bash
pip install --upgrade terraforge-core
```

## Running the Project

```bash
python main.py
```

## Dependencies

Current dependencies include:

* terraforge-core
* numpy
* pillow
* noise

## About TerraForge

TerraForge is a procedural generation library I created for building overworld maps, biome systems, settlement generation tools, and other procedural game content.

## License

This project is licensed under the MIT License.

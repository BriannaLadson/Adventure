# Adventure v0.4.0

Adventure is a sandbox RPG simulation built using Python and Tkinter.

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
* Player location tracking across world and local maps

### Time & Simulation

* CQCalendar integration
* Persistent in-game calendar
* In-game clock
* Date tracking
* Variable time progression based on player actions

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

## Installation
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
* cqcalendar
* numpy
* pillow
* noise

## Libraries

* [CQCalendar](https://github.com/BriannaLadson/CQCalendar): A customizable, tick-based time and calendar system for Python games and simulations.
* [TerraForge](https://github.com/BriannaLadson/TerraForge): TerraForge is a versatile Python toolset for procedural map generation.

## Support Development

Adventure is actively developed, with new systems and features being added regularly.

The version available in this repository represents the current public release. New features are typically developed and tested in private builds before they are merged into the public version.

If you'd like to support the project and gain access to newer versions sooner, consider joining the Patreon.

[Patreon](patreon.com/BLCodes) supporters receive early access to development builds and source code updates, allowing them to explore new systems and features before they are released publicly.

## License

This project is licensed under the MIT License.

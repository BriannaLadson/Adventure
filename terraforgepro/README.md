# TerraForgePro 🗺️
**Advanced Procedural Island Map Generator using Simplex Noise**

**TerraForgePro** is a professional-grade Python tool for generating procedural island maps using noise-based algorithms. 
It provides fine-tuned control over terrain shaping, island clustering, and biome simulation via elevation, moisture, and temperature maps.

---

## 🚀 Features

- 🌍 Elevation, Moisture, and Temperature map generation
- 🏝️ Supports single and clustered multi-island generation
- 🌀 Falloff support: Radial, Edge, or None
- ⚙️ Parameters for island spread, spacing, scale, and strength
- 🌿 Basic biome color mapping based on environmental conditions
- 🖼️ Outputs high-resolution PNG images

---

## 🛠 Requirements

Install the required dependencies:

```bash
pip install numpy noise pillow
```

---

## 🧪 Demo

Run the included demo script:

```bash
python demo.py
```

The generated maps will be saved as biome_map, elevation_map, moisture_map, temperature_map, (noise_type)_map.

---

## ⚙️ Customization Options
Edit the values in terraforgepro.py or the demo to control:

- map_size and image_size

- falloff type: "radial", "edge", or None

- num_islands, island_spread, min_island_spacing

- noise types (elevation, moisture, temperature)

- biome_thresholds for  noise types (elevation, moisture, and temperature)

---

## 📁 Included Files
terraforgepro.py – Main terrain generation engine

demo.py – Sample usage script

licenses/ – Third-party license files
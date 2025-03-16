import json

def load_game_data(file_path):
    """Loads game data, including the summary and maps, from a single file."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        # Validate level count
        summary_levels = data.get("summary", {}).get("levels", {})
        actual_levels = data.get("levels", {})
        if len(summary_levels) != len(actual_levels):
            print("Warning: Mismatch in level count. Using actual levels in file.")
            data["summary"]["levels"] = {lvl: {} for lvl in actual_levels}

        return data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        raise ValueError("Invalid game data file format")


def load_map(game_data, level_name):
    """Retrieves a specific map and its description from the loaded game data."""
    if "levels" not in game_data or level_name not in game_data["levels"]:
        raise ValueError(f"Level '{level_name}' not found in game data")
    return game_data["levels"][level_name]


def map_decoder(game_map, map_description, width, height):
    units = []
    grid_width = width // len(game_map[0])
    grid_height = height // len(game_map)
    unit_counters = {key: 0 for key in map_description}  # Track usage of each unit type
    map_counts = {key: sum(row.count(key) for row in game_map) for key in map_description}  # Count occurrences in map
    desc_counts = {key: len(map_description[key]) for key in map_description}  # Count occurrences in description

    # Validate that the map and description match in unit counts
    for key in map_counts:
        if map_counts[key] != desc_counts.get(key, 0):
            raise ValueError(
                f"Mismatch for '{key}': Map has {map_counts[key]}, but description has {desc_counts.get(key, 0)}")

    for y, row in enumerate(game_map):
        for x, cell in enumerate(row):
            if cell in map_description and unit_counters[cell] < len(map_description[cell]):
                unit_info = map_description[cell][unit_counters[cell]]
                unit = {
                    "x": x * grid_width,
                    "y": y * grid_height,
                    "color": unit_info["color"],
                    "points": unit_info["points"],
                    "evolution": unit_info["evolution"],
                    "kind": unit_info["kind"]
                }
                units.append(unit)
                unit_counters[cell] += 1

    return units


game_data_file = "game_data.json"

game_data = load_game_data(game_data_file)
print("Game Summary:", game_data.get("summary", {}))

selected_level = "level1"
try:
    level_data = load_map(game_data, selected_level)
    game_map = level_data["map"]
    description = level_data["description"]
    decoded_units = map_decoder(game_map, description, 500, 500)
    print("Decoded Units:", decoded_units)
except (FileNotFoundError, ValueError) as e:
    print(f"Error: {e}")

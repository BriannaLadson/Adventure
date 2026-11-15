from pathlib import Path

DEBUG_PATHS = {
	"town_debug_log": Path("town_debug.txt"),
	"overworld_debug_log": Path("overworld_debug.txt"),
}


def write_log(game, buffer_name, message):
	path = DEBUG_PATHS[buffer_name]

	with path.open("a", encoding="utf-8") as log:
		log.write(message + "\n")

	getattr(game, buffer_name).append(message)


def clear_logs(game):
	game.town_debug_log.clear()
	game.overworld_debug_log.clear()
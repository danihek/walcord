import argparse
import pywal
import os
import sys
import re
import json

HOME_PATH = os.environ['HOME']
VESKTOP_THEME_PATH = os.path.join(HOME_PATH, ".config/vesktop/themes")
DEFAULT_THEME = """
/**
 * @name Walcord Default Theme
 * @description Hello source code reader! This is a default theme generated by Walcord.
 * @author Danrus110
 * @version 1.0.0
 * @website https://github.com/Danrus1100/walcord
**/

@import url(https://mwittrien.github.io/BetterDiscordAddons/Themes/DiscordRecolor/DiscordRecolor.css);


:root {
	--settingsicons:		0;
	--font:				"gg sans", "Noto Sans";												
	
	--accentcolor: 			KEY(a).rgb_values;
	--accentcolor2: 		KEY(a).rgb_values;
	--linkcolor: 			KEY(14).rgb_values;
	--mentioncolor: 		KEY(5).rgb_values;
	--successcolor: 		59,165,92;
	--warningcolor: 		250,166,26;
	--dangercolor:  		237,66,69;
	
	--textbrightest: 		KEY(t).rgb_values;
	--textbrighter: 		KEY(14).rgb_values;
	--textbright: 			KEY(t).rgb_values;
	--textdark: 			KEY(15).rgb_values;
	--textdarker: 			KEY(13).rgb_values;
	--textdarkest: 			KEY(13).rgb_values;
	
	--backgroundaccent: 		KEY(b).rgb_values;
	--backgroundprimary: 		KEY(b).rgb_values;
	--backgroundsecondary: 		KEY(b).rgb_values;
	--backgroundsecondaryalt: 	KEY(b).rgb_values;
	--backgroundtertiary: 		KEY(b).rgb_values;
	--backgroundfloating: 		KEY(b).rgb_values;
}
"""

def get_colors_pywal(image_path: str) -> dict:
    """
    Returns a dictionary of colors generated from the given image path.

    :param image_path: The path to the image to generate colors from.
    :type image_path: str
    :return: A dictionary of colors in the format of pywal.
    :rtype: dict
    """
    return pywal.colors.get(image_path)

def get_colors_json() -> dict:
    """
    Returns a dictionary of colors from the pywal json file.

    :return: A dictionary of colors in the format of pywal.
    :rtype: dict
    """
    cache_file = os.path.join(HOME_PATH, ".cache/wal/colors.json")
    if not os.path.exists(cache_file):
        print("Error: No cached colors found. Run pywal first or use --image <image_path>.")
        sys.exit(-1)

    with open(cache_file) as f:
        return json.load(f)

def map_colors(colors: dict) -> dict:
    """
    Maps the given colors to list.

    :param colors: The colors to map to the theme file.
    :type colors: dict
    """
    return {
        "background": colors["special"]["background"],
        "foreground": colors["special"]["foreground"],
        "0": colors["colors"]["color0"],
        "1": colors["colors"]["color1"],
        "2": colors["colors"]["color2"],
        "3": colors["colors"]["color3"],
        "4": colors["colors"]["color4"],
        "5": colors["colors"]["color5"],
        "6": colors["colors"]["color6"],
        "7": colors["colors"]["color7"],
        "8": colors["colors"]["color8"],
        "9": colors["colors"]["color9"],
        "10": colors["colors"]["color10"],
        "11": colors["colors"]["color11"],
        "12": colors["colors"]["color12"],
        "13": colors["colors"]["color13"],
        "14": colors["colors"]["color14"],
        "15": colors["colors"]["color15"],

        # special colors
        "border": colors["colors"]["color2"],
        "text": colors["colors"]["color15"],
        "accent": colors["colors"]["color13"],

        # short names
        "b": colors["special"]["background"], 
        "f": colors["special"]["foreground"],
        "br": colors["colors"]["color2"],
        "t": colors["colors"]["color15"],
        "a": colors["colors"]["color13"],

    }

def hex_to_rgb_map(colors: dict) -> dict:
    """
    Maps the hex colors to rgb colors.

    :param color: The colors to map to rgb.
    :type color: dict
    :return: A list of colors mapped to rgb.
    :rtype: dict
    """
    returned = {}
    for color in colors:
        returned[color] = tuple(int(colors[color].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    return returned

def return_rgba(color_tuple, opacity):
    return f"rgba({color_tuple[0]},{color_tuple[1]},{color_tuple[2]},{opacity})"

def return_rgb(color_tuple, opacity):
    return f"rgb({color_tuple[0]},{color_tuple[1]},{color_tuple[2]})"

def return_values(color_tuple, opacity):
    return f"{color_tuple[0]},{color_tuple[1]},{color_tuple[2]},{opacity}"

def return_values_without_opacity(color_tuple, opacity):
    return f"{color_tuple[0]},{color_tuple[1]},{color_tuple[2]}"

def return_red(color_tuple, opacity):
    return f"{color_tuple[0]}"

def return_green(color_tuple, opacity):
    return f"{color_tuple[1]}"

def return_blue(color_tuple, opacity):
    return f"{color_tuple[2]}"

def return_opacity(color_tuple, opacity):
    return f"{opacity}"

def return_hex(color_tuple, opacity):
    return f"#{color_tuple[0]:02x}{color_tuple[1]:02x}{color_tuple[2]:02x}"

def return_hex_values(color_tuple, opacity):
    return f"{color_tuple[0]:02x}{color_tuple[1]:02x}{color_tuple[2]:02x}"

MODIFIER_HANDLERS = {
    'DEFAULT': return_rgba,
    '.rgba': return_rgba,
    '.rgb': return_rgb,
    '.hex': return_hex,

    '.rgba_values': return_values,
    '.rgb_values': return_values_without_opacity,
    '.hex_values': return_hex_values,

    '.r': return_red,
    '.red': return_red,

    '.g': return_green,
    '.green': return_green,

    '.b': return_blue,
    '.blue': return_blue,

    '.o': return_opacity,
    '.opacity': return_opacity,
}

def remap_key(match) -> str:
    """
    Remaps the key to the css rgba format.

    :param match: The match object to remap.
    :type match: re.Match
    """
    global colors

    first_arg = match.group(1).lower()
    first_arg_values = colors.get(first_arg)
    if not first_arg_values:
        raise ValueError(f"Цвет '{first_arg}' не найден в словаре colors.")

    second_arg = match.group(2)
    opacity = float(second_arg) if second_arg else 1.0

    modifier = match.group(3).lower() if match.group(3) else None

    if modifier and modifier in MODIFIER_HANDLERS:
        return MODIFIER_HANDLERS[modifier](first_arg_values, opacity)
    return MODIFIER_HANDLERS['DEFAULT'](first_arg_values, opacity)

def replace_key(text: str) -> str:
    """
    Replaces the key with the rgba format.

    :param text: The text to replace the key in.
    :type text: str
    :return: The text with the key replaced.
    :rtype: str
    """
    return re.sub(r'KEY\((\w+)(?:,\s*(0\.\d+))?\)(\.\w+)?', remap_key, text)

def check_path(path: str, file_name: str = "") -> None:
    """
    Checks if the path exists and if not creates it.

    :param path: The path to check.
    :param file_name: The name of the file to create if name dosent given.
    :type path: str
    """
    if not os.path.exists(path):
        if "." in path:
            with open(path, "w+") as f:
                pass
        else:
            os.makedirs(path)
            if file_name != "":
                with open(os.path.join(path, file_name), "w+") as f:
                    pass

colors = {}

def main():
    global colors
    global VESKTOP_THEME_PATH

    parser = argparse.ArgumentParser(description="Create a theme file from pywal colors.")
    parser.add_argument("--image", "-i", type=str, help="The path to the image to generate colors from.", required=False)
    parser.add_argument("--theme", "-t", type=str, help="The path to the theme file to replace colors in.", required=False)
    parser.add_argument("--output", "-o", type=str, help="The path to the output file. default: ~/.config/vesktop/themes/", required=False)
    args = parser.parse_args()
    
    if args.theme:
        theme_path = args.theme
        theme_file_name = os.path.basename(theme_path)
        with open(theme_path, "r") as theme_file:
            theme_lines = theme_file.readlines()
    else:
        theme_lines = DEFAULT_THEME.split("\n")
        theme_file_name = "walcord.theme.css"

    if args.output:
        VESKTOP_THEME_PATH = args.output
        if "." in VESKTOP_THEME_PATH:
            check_path(VESKTOP_THEME_PATH)
        else:
            check_path(VESKTOP_THEME_PATH, theme_file_name)
            VESKTOP_THEME_PATH = os.path.join(VESKTOP_THEME_PATH, theme_file_name)
    else:
        check_path(VESKTOP_THEME_PATH)
        VESKTOP_THEME_PATH = os.path.join(VESKTOP_THEME_PATH, theme_file_name)

    if args.image:
        colors = hex_to_rgb_map(map_colors(get_colors_pywal(args.image)))
    else:
        colors = hex_to_rgb_map(map_colors(get_colors_json()))
    theme_text = ""
    
    for i in theme_lines:
        if "@description" in i:
            i = re.sub(r'@description.*', f"@description Generated by Walcord", i)
        i = replace_key(i)
        i += "\n" if not args.theme else ""
        theme_text += i

    with open(VESKTOP_THEME_PATH, "w+") as file:
        file.write(theme_text)

if __name__ == "__main__":
    main()

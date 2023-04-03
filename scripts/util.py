import collections, sys, os, random, time, json
from datetime import datetime
try:
    from pytesseract import pytesseract
    import pyautogui as p
    import numpy as np
except ImportError:
    import subprocess
    subprocess.run(["python", "-m", "pip", "install", "-r", "../requirements.txt"])
    import pyautogui as p
    import numpy as np
    from pytesseract import pytesseract

Box = collections.namedtuple('Box', 'left top width height')

DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
RESOURCES_DIR = os.path.join(DIR, "resources")
TEMP_DIR = os.path.join(DIR, "temp_im")

STANDBY = 's'           # not in fishing state
WAITING = 'w'           # fishing pre-stage 1, waiting for bonus rate hit yellow and fish bite
READY = 'r'             # fishing pre-stage 3, ready to fish
PULLING = 'p'           # fishing main stage, pulling fish up
INTERRUPTED_LAIR = 'l'  # interrupted by lair auto navigation
INTERRUPTED_PARTY = 'i' # interrupted by party invite
INTERRUPTED_RAID = 'd'  # interrupted by raid invite
TALK = 't'              # when npc talking is available
PICK = 'k'              # when picking items is available

im_data = {
    STANDBY:            os.path.join(RESOURCES_DIR, "standby.png"),
    WAITING:            os.path.join(RESOURCES_DIR, "not_ready.png"),
    READY:              os.path.join(RESOURCES_DIR, "pull.png"),
    PULLING:            os.path.join(RESOURCES_DIR, "pulling.png"),
    INTERRUPTED_LAIR:   os.path.join(RESOURCES_DIR, "cancel_lair.png"),
    INTERRUPTED_PARTY:  os.path.join(RESOURCES_DIR, "cancel.png"),
    INTERRUPTED_RAID:   os.path.join(RESOURCES_DIR, "cancel.png"),
    TALK:               os.path.join(RESOURCES_DIR, "talk.png"),
    PICK:               os.path.join(RESOURCES_DIR, "pick.png"),
    "npc":              os.path.join(RESOURCES_DIR, "npc.png"),
    "trade":            os.path.join(RESOURCES_DIR, "trade.png"),
    "select":           os.path.join(RESOURCES_DIR, "select_all.png"),
    "exchange":         os.path.join(RESOURCES_DIR, "exchange.png"),
    "x":                os.path.join(RESOURCES_DIR, "x.png"),
    "shop":             os.path.join(RESOURCES_DIR, "shop.png"),
    "amount":           os.path.join(RESOURCES_DIR, "amount.png"),
    "9":                os.path.join(RESOURCES_DIR, "number9.png"),
    "buy":              os.path.join(RESOURCES_DIR, "buy.png"),
    "find_npc":         os.path.join(RESOURCES_DIR, "find_npc.png"),
    "navigate":         os.path.join(RESOURCES_DIR, "navigate.png"),
    "icon_fish":        os.path.join(RESOURCES_DIR, "icon_fish.png"),
    "icon_bs":          os.path.join(RESOURCES_DIR, "icon_bs.png"),
    "npc_fish":         os.path.join(RESOURCES_DIR, "npc_fish.png"),
    "npc_bs":           os.path.join(RESOURCES_DIR, "npc_bs.png"),
    "services":         os.path.join(RESOURCES_DIR, "services.png"),
    "white_unticked":   os.path.join(RESOURCES_DIR, "white_unticked.png"),
    "blue_unticked":    os.path.join(RESOURCES_DIR, "blue_unticked.png"),
    "yellow_unticked":  os.path.join(RESOURCES_DIR, "yellow_unticked.png"),
    "no_white":         os.path.join(RESOURCES_DIR, "no_white.png"),
    "no_blue":          os.path.join(RESOURCES_DIR, "no_blue.png"),
    "no_yellow":        os.path.join(RESOURCES_DIR, "no_yellow.png"),
    "salvage":          os.path.join(RESOURCES_DIR, "salvage.png"),
    "icon_bag":         os.path.join(RESOURCES_DIR, "icon_bag.png")
}

FISH_TYPE_COLOR = (125, 125, 120)
FISH_TYPE_X_COORD_TOLERANCE = 100

if sys.platform == 'darwin':
    from locate_im import locate_on_screen, pixel_match_color, screenshot, locate
    import subprocess
    FISH_TYPE_X_COORD = {"white": 0, "blue": 910, "yellow": 1050}
    FISH_TYPE_Y_COORD = 137
    MAX_FISHING_TIME = 20
    MAX_TIMEOUT = 2
    KEY_MOVE = {'bilefen': ('w', 's'), 'tundra': ('w', 's'), 'ashwold': ('a', 'w')}
    NPC_NAME_COLOR = (230, 190, 135)

    pos = subprocess.run(["osascript", "-e",
                          'tell application "System Events" to tell process "Diablo Immortal" to get position of window 1'],
                         stdout=subprocess.PIPE)
    x0, y0 = [int(n) for n in pos.stdout.decode("utf-8").strip().split(", ")]
    x0, y0 = x0 * 2, y0 * 2

    regions = {
        INTERRUPTED_LAIR: (x0 + 735, y0 + 945, 180, 40),
        INTERRUPTED_PARTY: (x0 + 760, y0 + 1255, 225, 45),
        INTERRUPTED_RAID: (x0 + 760, y0 + 1255, 225, 45),
        PULLING: (x0 + 528, y0 + 200, 83, 31),
        READY: (x0 + 1800, y0 + 1100, 230, 230),
        WAITING: (x0 + 1800, y0 + 1100, 230, 230),
        STANDBY: (x0 + 1540, y0 + 860, 100, 100),
        TALK: (x0 + 1540, y0 + 860, 100, 100),
        PICK: (x0 + 1540, y0 + 860, 100, 100)
    }

    window = None

else:
    # assume windows
    import DIKeys, hexKeyMap
    locate_on_screen, pixel_match_color, screenshot, locate = p.locateOnScreen, p.pixelMatchesColor, p.screenshot, p.locate

    FISH_TYPE_X_COORD = {"white": 0, "blue": 826, "yellow": 955}
    FISH_TYPE_Y_COORD = 75
    MAX_FISHING_TIME = 40
    MAX_TIMEOUT = 5
    PICKUP_LIMIT = 10
    NPC_NAME_COLOR = (248, 198, 134)
    KEY_MOVE = {'bilefen': hexKeyMap.DIK_S, 'tundra': hexKeyMap.DIK_S, 'ashwold': hexKeyMap.DIK_D}
    BACK_TO_FISHING_COORD = {'bilefen': (970, 670), 'tundra': (1100, 670), 'ashwold': (1400, 385)}

    window = p.getWindowsWithTitle("Diablo Immortal")[0]
    x0, y0 = window.left, window.top
    boxes = {}

    if os.path.exists(os.path.join(RESOURCES_DIR, "regions.json")):
        try:
            with open(os.path.join(RESOURCES_DIR, "regions.json"), 'r') as f:
                regions = json.load(f)
        except:
            regions = {}
    else:
        regions = {}


def clear_temp_screenshots():
    for filename in os.listdir(os.getcwd()):
        if "screenshot" in filename:
            os.unlink(os.path.join(os.getcwd(), filename))
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)


def activate_diablo():
    if sys.platform == "darwin":
        subprocess.run(["osascript", "-e", 'tell application "Diablo Immortal" to activate'])
    else:
        window.activate()


def click_box(box: Box, clicks=1, interval=0.01, button=p.PRIMARY,
              offset_left=0.2, offset_top=0.2, offset_right=-0.2, offset_bottom=-0.2):
    left = box.left + offset_left * box.width
    width = box.width * (1 - offset_left + offset_right)
    top = box.top + offset_top * box.height
    height = box.height * (1 - offset_top + offset_bottom)
    x = left + random.random() * width
    y = top + random.random() * height
    if sys.platform == "darwin":
        x, y = x // 2, y // 2
    else:
        x, y = int(x), int(y)
    p.click(x, y, clicks=clicks, interval=interval, button=button)


def cast_fishing_rod(key, box):
    if key == "mouseRight":
        click_box(box, button=p.SECONDARY)
    else:
        if key not in hexKeyMap.DI_KEYS:
            raise KeyError(f"The key {key} is not an accepted keyboard key.")
        DIKeys.press(hexKeyMap.DI_KEYS[key])


def check(status, confidence=0.85, region_boarder_x=20, region_boarder_y=20):
    if sys.platform == "win32" and status in [TALK, PICK]:
        return None
    global boxes
    global regions
    im_name = im_data[status]
    region = regions.get(status)
    box = locate_on_screen(im_name, region=region, confidence=confidence)
    if sys.platform == "win32" and box:
        if status not in boxes:
            boxes.update({status: box})
        if status not in regions:
            regions.update({status: [int(n) for n in [box.left - region_boarder_x,
                                                      box.top - region_boarder_y,
                                                      box.width + 2 * region_boarder_x,
                                                      box.height + 2 * region_boarder_y]]})
            with open(os.path.join(RESOURCES_DIR, "regions.json"), 'w') as f:
                json.dump(regions, f)
    return box


def match_box(box1: Box, box2: Box, max_diff=5):
    return (np.abs(np.array([[1, 0, 0, 0],
                             [0, 1, 0, 0],
                             [1, 0, 1, 0],
                             [0, 1, 0, 1]]).dot(np.array(box1) - np.array(box2))) <= max_diff).all()


def scroll_down(x, y, amount=200):
    if sys.platform == "darwin":
        p.moveTo(x // 2, y // 2 + 200)
        p.sleep(0.1)
        p.drag(yOffset=-amount, duration=0.3 + 0.2 * random.random(), button='left')
    else:
        p.scroll(-1, x=x, y=y)


def click_image(im_state, start_time, max_time, clicks=1, interval=0.01, confidence=0.9, region_boarder_x=10,
                region_boarder_y=10, offset=(0.2, 0.2, -0.2, -0.2)):
    while True:
        box = check(im_state, confidence=confidence,
                    region_boarder_x=region_boarder_x, region_boarder_y=region_boarder_y)
        if not box:
            box = check(im_state, confidence=confidence - 0.02,
                        region_boarder_x=region_boarder_x, region_boarder_y=region_boarder_y)
        if box:
            p.sleep(1)
            click_box(box, clicks, interval, offset_left=offset[0], offset_top=offset[1],
                      offset_right=offset[2], offset_bottom=offset[3])
            return 0  # success
        if time.time() - start_time > max_time:
            return 1  # fail


def click_center(box):
    x = box.left + box.width // 2
    y = box.top + box.height // 2
    p.click(x, y)


def find_npc(npc_color_rgb=np.array(NPC_NAME_COLOR)):
    im = p.screenshot()
    matches = np.argwhere((np.abs(np.array(im)[:, :, :3] - npc_color_rgb) <= 5).all(axis=2))
    if matches.shape[0] > 50:
        position = np.median(matches, axis=0)[::-1]
        return int(position[0]), int(position[1])


def find_npc_2(npc_name_im, npc_color_rgb=np.array(NPC_NAME_COLOR)):
    # if sys.platform == "darwin":
    #     find_region = (x0, y0, 2100, 1630)
    #     color_threshold = 40  # could tune higher or lower depending on brightness.
    #     rgb_image = False  # screenshot uses opencv for macos, image in BGR mode.
    # else:
    #     find_region = None
    #     color_threshold = 30  # could tune higher or lower depending on brightness.
    #     rgb_image = True
    # im_array = np.array(screenshot(region=find_region))  # uses Pillow for windows, so image in RGB mode
    # if rgb_image:
    #     im_array = im_array[:, :, ::-1]  # convert RGB to BGR
    # im_array[np.where((np.abs(im_array - npc_color_rgb[::-1]) >= color_threshold).any(axis=2))] = np.array([0, 0, 0])
    im_array = extract_color_from_screen(npc_color_rgb)
    # from PIL import Image
    # Image.fromarray(im_array[:,:,::-1]).save("npc_im_black.png")
    return locate(npc_name_im, im_array, confidence=0.6)


def find_npc_3(npc_name, npc_color_rgb=np.array(NPC_NAME_COLOR)):
    full_name = {"fish": "Fisher", "bs": "Blacksmith"}[npc_name]
    im_array = extract_color_from_screen(npc_color_rgb)
    config = "-c tessedit_char_whitelist=aBceFhlkimrst"
    if sys.platform == "win32":
        pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
    try:
        outputs = pytesseract.image_to_data(im_array, config=config, output_type=pytesseract.Output.DICT)
        print(outputs)
        if full_name in outputs["text"]:
            i_row = outputs["text"].index(full_name)
            return Box(outputs["left"][i_row], outputs["top"][i_row], outputs["width"][i_row], outputs["height"][i_row])
    except pytesseract.TesseractNotFoundError:
        log("Tesseract not installed. Follow the instruction on the project homepage.")
        return locate(im_data[f"npc_{npc_name}"], im_array, confidence=0.5)


def extract_color_from_screen(color_rgb: np.ndarray):
    if sys.platform == "darwin":
        find_region = (x0, y0, 2100, 1630)
        color_threshold = 40  # could tune higher or lower depending on brightness.
        rgb_image = False  # screenshot uses opencv for macos, image in BGR mode.
    else:
        find_region = None
        color_threshold = 30  # could tune higher or lower depending on brightness.
        rgb_image = True
    im_array = np.array(screenshot(region=find_region))  # uses Pillow for windows, so image in RGB mode
    if rgb_image:
        im_array = im_array[:, :, ::-1]  # convert RGB to BGR
    im_array[np.where((np.abs(im_array - color_rgb[::-1]) >= color_threshold).any(axis=2))] = np.array([0, 0, 0])
    return im_array


def log(contents):
    print(f"[{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')}] {contents}")

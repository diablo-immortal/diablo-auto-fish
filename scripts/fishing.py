import pyautogui as p
import numpy as np
import subprocess, random, time, os, sys, collections, json, threading
from PIL import Image
from gui import GUI

if sys.platform == "darwin":
    from locate_im import locate_on_screen, pixel_match_color

Box = collections.namedtuple('Box', 'left top width height')

for filename in os.listdir(os.getcwd()):
    if "screenshot" in filename:
        os.unlink(os.path.join(os.getcwd(), filename))

RESOURCES_DIR = os.path.join(os.path.dirname(os.getcwd()), "resources")
TEMP_DIR = os.path.join(os.path.dirname(os.getcwd()), "temp_im")

if not os.path.exists(TEMP_DIR):
    os.mkdir(TEMP_DIR)

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
    "buy":              os.path.join(RESOURCES_DIR, "buy.png")
}

FISH_TYPE_COLOR = (125, 125, 120)
FISH_TYPE_X_COORD_TOLERANCE = 100

if sys.platform == 'darwin':
    FISH_TYPE_X_COORD = {"white": 0, "blue": 910, "yellow": 1050}
    FISH_TYPE_Y_COORD = 137
    MAX_FISHING_TIME = 20
    MAX_TIMEOUT = 2
    KEY_MOVE = {'bilefen': ('w', 's'), 'tundra': ('w', 's'), 'ashwold': ('a', 'w')}

    # subprocess.run(["osascript", "-e", 'tell application "Diablo Immortal" to activate'])
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
    locate_on_screen, pixel_match_color = p.locateOnScreen, p.pixelMatchesColor

    FISH_TYPE_X_COORD = {"white": 0, "blue": 826, "yellow": 955}
    FISH_TYPE_Y_COORD = 75
    MAX_FISHING_TIME = 40
    MAX_TIMEOUT = 5
    PICKUP_LIMIT = 10
    KEY_MOVE = {'bilefen': ('w', 's'), 'tundra': ('w', 's'), 'ashwold': ('a', 'w')}

    window = p.getWindowsWithTitle("Diablo Immortal")[0]
    # window.activate()
    x0, y0 = window.left, window.top

    if os.path.exists(os.path.join(RESOURCES_DIR, "regions.json")):
        try:
            with open(os.path.join(RESOURCES_DIR, "regions.json"), 'r') as f:
                regions = json.load(f)
        except:
            regions = {}
    else:
        regions = {}

boxes = {}
# boxes = {k: Box(*v) for k, v in regions.items()}

# log(x0, y0)

# region_pull = (x0/2 + 930, y0/2 + 590, 50, 50)

# width = subprocess.run(["osascript", "-e",
#                         'tell application "System Events" to tell process "Diablo Immortal" to get size of window 1'],
#                        stdout=subprocess.PIPE)
# dx, dy = [int(n) for n in width.stdout.decode("utf-8").strip().split(", ")]
#
# whole_region = [n * 2 for n in [x0, y0, dx, dy]]
# log(whole_region)

# x0, y0 = 718, 256

# if __name__ == '__main__':
#     log = print
# else:
#     from gui import log


def activate_diablo():
    if sys.platform == "darwin":
        subprocess.run(["osascript", "-e", 'tell application "Diablo Immortal" to activate'])
    else:
        window.activate()


def click_box(box, clicks=1, interval=0.01, button=p.PRIMARY, offset_left=0.2, offset_top=0.2, offset_right=-0.2, offset_bottom=-0.2):
    left = box.left + offset_left * box.width
    width = box.width * (1 - offset_left + offset_right)
    top = box.top + offset_top * box.height
    height = box.height * (1 - offset_top + offset_bottom)
    x = left + random.random() * width
    y = top + random.random() * height
    # x = box.left + (0.2 + 0.6 * random.random()) * box.width
    # y = box.top + (0.2 + 0.6 * random.random()) * box.height
    if sys.platform == "darwin":
        x, y = x // 2, y // 2
    else:
        x, y = int(x), int(y)
    p.click(x, y, clicks=clicks, interval=interval, button=button)


def pull(brightness=50):
    # t0 = time.time()
    # im_bar = p.screenshot("temp.png", region=[x0+610, y0+214, 885, 1])
    # im_bar = ImageGrab.grab(bbox=(x0//2+305, y0//2+107, x0//2+305+442, y0//2+107+1))
    if sys.platform == "darwin":
        subprocess.run(["screencapture", "-x", "-R" f"{x0//2+306},{y0//2+107},441,1", os.path.join(TEMP_DIR, "temp.png")])
        im_bar = Image.open(os.path.join(TEMP_DIR, "temp.png"))
        dark_color_gray = 70
        bright_color_gray = 165
        n_dark = 10  # number of consecutive dark pixels to determine current position
        n_offset = 8  # backward offset after finding n_dark consecutive dark pixels
        lb_range = 150
        ub_range = 350
        lb_right_end = 650
        amount_pull = 80  # amount of position change for each pull

    else:
        im_bar = p.screenshot(os.path.join(TEMP_DIR, "temp.png"), region=(x0+560, y0+145, 806, 1))
        dark_color_gray = 70
        bright_color_gray = int(brightness / 10) + 150
        n_dark = 9  # number of consecutive dark pixels to determine current position
        n_offset = 7  # backward offset after finding n_dark consecutive dark pixels
        lb_range = 130
        ub_range = 300
        lb_right_end = 600
        amount_pull = 65  # amount of position change for each pull

    # t1 = time.time()
    # bar = np.array(im_bar)[0, :, :3]
    # current = np.where((bar < 50).all(axis=1))[0][0]
    # bounds = np.where((bar > np.array([180, 150, 100])).all(axis=1))[0]
    bar_g = np.dot(np.array(im_bar)[0, :, :3], [0.2989, 0.5870, 0.1140])
    dark = np.where(bar_g < dark_color_gray)[0]
    diff_dark = np.diff(dark)
    # t2 = time.time()

    bounds = np.where(bar_g > bright_color_gray)[0]
    bound_range = bounds.ptp() if bounds.shape[0] > 1 else 0
    current = None
    j = 0
    while j < len(diff_dark) - n_dark:
        next_dark = np.where(diff_dark[j:j+n_dark] != 1)[0]
        if next_dark.shape[0] == 0:
            current = dark[j] - n_offset
            break
        j += next_dark[-1] + 1
    if current is None or current < 0 or bounds.shape[0] == 0:
        return None
    # t3 = time.time()
    # log(t1-t0, t2-t1, t3-t2)

    # log(current)
    # log(bounds, bounds.shape, bounds.shape[0])
    if (2 <= bounds.shape[0] <= 10 and lb_range < bound_range < ub_range) or (bounds[0] > lb_right_end and bound_range < 10):
        if bounds[0] < current < bounds[-1] - amount_pull:
            if sys.platform == "darwin":
                p.press('n')
            else:
                click_box(boxes[READY])
            # p.sleep(random.random()*0.03)
        elif bound_range < 10:
            pull_count = (bar_g.shape[0] - current) // amount_pull
            if sys.platform == "darwin":
                p.write('n' * pull_count)
            else:
                click_box(boxes[READY], pull_count)
        elif current < bounds[0]:
            pull_count = (bounds[-1] - current) // amount_pull
            if sys.platform == "darwin":
                p.write('n' * pull_count)
            else:
                click_box(boxes[READY], pull_count)
            # for _ in range((bounds[-1] - current) // 100 + 1):
            #     p.press('n')
            #     p.sleep(random.random()*0.03)
        else:
            p.sleep(random.random()*0.03)
        return bound_range
    return None


def check_status(prev_status, fish_type="yellow"):
    t0 = time.time()
    box = check(INTERRUPTED_LAIR)
    if box:
        if prev_status != INTERRUPTED_LAIR:
            log(f"interrupted by lair, check took {time.time() - t0:.2f} seconds.")
        return INTERRUPTED_LAIR, box
    box = check(INTERRUPTED_PARTY)
    if box:
        if prev_status != INTERRUPTED_PARTY:
            log(f"interrupted by party, check took {time.time() - t0:.2f} seconds.")
        return INTERRUPTED_PARTY, box
    if sys.platform == "win32":
        box = check(INTERRUPTED_RAID)
        if box:
            if prev_status != INTERRUPTED_RAID:
                log(f"interrupted by raid, check took {time.time() - t0:.2f} seconds.")
            return INTERRUPTED_RAID, box
    box = check(PULLING)
    if box:
        if prev_status != PULLING:
            log(f"pulling fish, check took {time.time() - t0:.2f} seconds.")
        return PULLING, box
    box = check(READY, confidence=0.99)
    if box:
        if prev_status != WAITING:
            log(f"fish up, check took {time.time() - t0:.2f} seconds.")
        fish_type_coords = (x0 + FISH_TYPE_X_COORD[fish_type], y0 + FISH_TYPE_Y_COORD)
        if pixel_match_color(*fish_type_coords, FISH_TYPE_COLOR, FISH_TYPE_X_COORD_TOLERANCE) or fish_type == "white":
            if prev_status != READY:
                log(f"ready to fish, check took {time.time() - t0:.2f} seconds.")
            return READY, box
        if prev_status != WAITING:
            log(f"bonus did not reach yellow, check took {time.time() - t0:.2f} seconds.")
        return WAITING, box
    box = check(WAITING, confidence=0.99)
    if box:
        if prev_status != WAITING:
            log(f"waiting for fish, check took {time.time() - t0:.2f} seconds.")
        return WAITING, box
    box = check(STANDBY, confidence=0.8)
    if box:
        if prev_status != STANDBY:
            log(f"standby, check took {time.time() - t0:.2f} seconds.")
        return STANDBY, box
    box = check(PICK)
    if box:
        if prev_status != PICK:
            log(f"pick an item, check took {time.time() - t0:.2f} seconds.")
        return PICK, box
    return None, None


def check(status, confidence=0.9, region_boarder=10):
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
            regions.update({status: [int(n) for n in [box.left - region_boarder,
                                                      box.top - region_boarder,
                                                      box.width + 2 * region_boarder,
                                                      box.height + 2 * region_boarder]]})
            with open(os.path.join(RESOURCES_DIR, "regions.json"), 'w') as f:
                json.dump(regions, f)
    return box


def fish(fish_type="yellow", brightness=50, stop=None):
    if stop is None:
        def stop():
            return False
    prev_status = ''
    pickup_attempted = 0
    fishing_attempted = 0
    n_standby_cont = 0
    activate_diablo()
    while fishing_attempted < 30 and n_standby_cont < 3:
        if stop():
            return False
        status, box = check_status(prev_status, fish_type)
        if not status:
            continue
        if status == PULLING:
            t = time.time()
            bar_or_bounds_not_found_time = time.time()
            while time.time() - t < MAX_FISHING_TIME and bar_or_bounds_not_found_time < MAX_TIMEOUT:
                if pull(brightness):  # successful pull
                    bar_or_bounds_not_found_time = time.time()
            continue

        if status == INTERRUPTED_PARTY or status == INTERRUPTED_LAIR or status == INTERRUPTED_RAID:
            activate_diablo()
            # subprocess.run(["osascript", "-e", 'tell application "Diablo Immortal" to activate'])
            click_box(box)
            # p.click(x, y)
        elif status == PICK:
            activate_diablo()
            # subprocess.run(["osascript", "-e", 'tell application "Diablo Immortal" to activate'])
            click_box(box)
            # p.click(x, y)
        elif status == STANDBY:
            activate_diablo()
            # subprocess.run(["osascript", "-e", 'tell application "Diablo Immortal" to activate'])
            if sys.platform == "darwin":
                click_box(box)
            else:
                click_box(box, button=p.SECONDARY)
            # p.click(x, y)
            fishing_attempted += 1
            if prev_status == STANDBY:
                n_standby_cont += 1
            else:
                n_standby_cont = 1
            p.sleep(1)
            log(f"number of fishing attempts: {fishing_attempted}")
        elif status == READY:
            activate_diablo()
            # subprocess.run(["osascript", "-e", 'tell application "Diablo Immortal" to activate'])
            p.sleep(0.1)
            click_box(box)
            # p.click(x, y)
            # p.click(region_pull[0] + random.random() * region_pull[2],
            #         region_pull[1] + random.random() * region_pull[3])
            p.sleep(0.1)
            status = PULLING
            t = time.time()
            bar_or_bounds_not_found_time = time.time()
            while time.time() - t < MAX_FISHING_TIME and time.time() - bar_or_bounds_not_found_time < MAX_TIMEOUT:
                if pull(brightness):  # successful pull
                    bar_or_bounds_not_found_time = time.time()
        elif status == WAITING and sys.platform == "win32" and pickup_attempted < PICKUP_LIMIT:
            if pickup_win32(pickup_attempted):
                pickup_attempted += 1
            else:
                pickup_attempted = 10
        prev_status = status
    return True


def check_npc_or_fish():
    box = check(INTERRUPTED_PARTY)
    if box:
        return INTERRUPTED_PARTY, box

    box = check(TALK)
    if box:
        return TALK, box

    box = check(STANDBY)
    if box:
        return STANDBY, box

    box = check(PICK)
    if box:
        log("picking up items")
        return PICK, box

    return None, None


def walk(key, duration=0.1):
    activate_diablo()
    # subprocess.run(["osascript", "-e", 'tell application "Diablo Immortal" to activate'])
    p.sleep(0.3)
    p.keyDown(key)
    p.sleep(duration)
    p.keyUp(key)


def trade_fish_buy_bait_go_back(key_to_npc, key_to_fish):
    stage = "trade"
    while True:
        log(stage)  # TODO
        status, box = check_npc_or_fish()

        if status == INTERRUPTED_PARTY:
            x = box.left / 2 + random.random() * box.width / 2
            y = box.top / 2 + random.random() * box.height / 2
            activate_diablo()
            # subprocess.run(["osascript", "-e", 'tell application "Diablo Immortal" to activate'])
            p.sleep(0.1)
            p.click(x, y)
        elif status == TALK and stage == "trade":
            trade_fish()
            stage = "buy"
            p.sleep(1)
        elif status == TALK and stage == "buy":
            buy_bait()
            stage = "back"
        elif status == STANDBY and stage == "back":
            return 0
        elif status == PICK:
            activate_diablo()
            # subprocess.run(["osascript", "-e", 'tell application "Diablo Immortal" to activate'])
            p.sleep(0.1)
            p.press('space')
        elif stage == "trade":
            walk(key_to_npc)
            p.sleep(0.1)
        elif stage == "buy":
            walk(key_to_npc, 0.05)
            p.sleep(0.1)
        elif stage == "back":
            walk(key_to_fish)
            p.sleep(0.1)


def trade_fish():
    log("selling fish to npc...")
    p.press('space')
    p.sleep(1)
    p.click(x0//2 + 850, y0//2 + 540)
    p.sleep(0.5)
    p.click(x0//2 + 530, y0//2 + 660)
    p.sleep(0.2)
    p.click(x0//2 + 880, y0//2 + 650)
    p.sleep(0.2)
    p.click(x0//2 + 1010, y0//2 + 170)
    p.sleep(15)
    walk('w', 0.2)


def buy_bait():
    log("buying baits...")
    p.press('space')
    p.sleep(1)
    p.click(x0//2 + 840, y0//2 + 600)
    p.sleep(1)
    p.click(x0//2 + 890, y0//2 + 600)
    p.sleep(0.2)
    p.click(x0//2 + 960, y0//2 + 470)
    p.sleep(0.2)
    p.click(x0//2 + 960, y0//2 + 470)
    p.sleep(0.2)
    p.click(x0//2 + 960, y0//2 + 470)
    p.sleep(0.2)
    p.click(x0//2 + 900, y0//2 + 655)
    p.sleep(0.2)
    p.click(x0//2 + 1010, y0//2 + 170)
    p.sleep(0.2)
    p.click(x0//2 + 1010, y0//2 + 170)


def click_image(im_state, start_time, max_time, clicks=1, interval=0.01, confidence=0.9, region_boarder=10,
                offset=(0.2, 0.2, -0.2, -0.2)):
    while True:
        box = check(im_state, confidence=confidence, region_boarder=region_boarder)
        if box:
            p.sleep(1)
            click_box(box, clicks, interval, offset_left=offset[0], offset_top=offset[1], offset_right=offset[2], offset_bottom=offset[3])
            return 0  # success
        if time.time() - start_time > max_time:
            return 1  # fail


def find_npc(npc_color_rgb=np.array([248, 198, 134])):
    im = p.screenshot()
    matches = np.argwhere((np.abs(np.array(im)[:, :, :3] - npc_color_rgb) <= 5).all(axis=2))
    if matches.shape[0] > 50:
        position = np.median(matches, axis=0)[::-1]
        return int(position[0]), int(position[1])


def trade_with_gui(attempts_trade=3, attempts_sell=3):
    if attempts_trade > 0:
        p.sleep(1)
        log("selling based on gui")
        # position = p.locateCenterOnScreen("resources/npc.png", confidence=0.8)
        position = find_npc()
        if not position:
            return trade_with_gui(attempts_trade - 1)
        p.click(position)
        error = 0
        error += click_image("trade", time.time(), 3)
        error += click_image("select", time.time(), 3)
        error += click_image("exchange", time.time(), 3, confidence=0.95)
        p.sleep(1)
        if error > 0:
            p.click(window.center)
            p.sleep(0.3)
            p.click(window.center)
            p.sleep(0.3)
            click_image("x", time.time(), 1)
            p.sleep(0.5)
            p.click(window.center)
            p.sleep(1)
            return trade_with_gui(attempts_trade - 1)
        else:
            return trade_with_gui(0)
    elif attempts_sell > 0:
        p.sleep(3)
        log("buying baits...")
        while True:
            for status in [INTERRUPTED_LAIR, INTERRUPTED_PARTY, INTERRUPTED_RAID]:
                box = check(status)
                if box:
                    click_box(box)
            if not box:
                break
        # position = p.locateCenterOnScreen("resources/npc.png", confidence=0.8)
        position = find_npc()
        if not position:
            return trade_with_gui(0, attempts_sell - 1)
        p.click(position)
        error = 0
        error += click_image("shop", time.time(), 3)
        error += click_image("amount", time.time(), 3, offset=(0.2, 0.7, -0.2, -0.1))
        error += click_image("9", time.time(), 3, clicks=3, interval=0.5)
        error += click_image("buy", time.time(), 3, confidence=0.95, region_boarder=15)
        error += click_image("x", time.time(), 3)
        if error > 0:
            return trade_with_gui(0, attempts_sell - 1)
    return 0


def pickup_win32(attempted=0, pickup_blue=True, legendary_alarm=False):
    # log(f"start picking items, attempt #{attempted + 1}")

    blue_rgb = np.array([89, 96, 241])
    yellow_rgb = np.array([233, 231, 77])
    orange_rgb = np.array([243, 143, 36])
    color_threshold = 5
    min_y_offset = 30
    max_y_offset = 150
    click_span = 120
    click_flex = 30
    region = (470, 240, 980, 600)
    im = p.screenshot(os.path.join(TEMP_DIR, "items_check.png"), region=region)
    if pickup_blue:
        pts = np.argwhere((np.abs(np.array(im)[:, :, :3] - blue_rgb) <= color_threshold).all(axis=2) |
                          (np.abs(np.array(im)[:, :, :3] - yellow_rgb) <= color_threshold).all(axis=2) |
                          (np.abs(np.array(im)[:, :, :3] - orange_rgb) <= color_threshold).all(axis=2))
    else:
        pts = np.argwhere((np.abs(np.array(im)[:, :, :3] - yellow_rgb) <= color_threshold).all(axis=2) |
                          (np.abs(np.array(im)[:, :, :3] - blue_rgb) <= color_threshold).all(axis=2))
    if pts.shape[0] == 0:
        return False
    top_left = pts.min(axis=0)
    height_width = pts.max(axis=0) - top_left
    click_region = (region[0] + top_left[1],            region[1] + top_left[0] + min_y_offset,
                    height_width[1],                    height_width[0] + max_y_offset - min_y_offset)
    for j in range(1, click_region[3] // click_span + 1):
        y = int(click_region[1] + click_span * j + (random.random() - 0.5) * click_flex)
        for i in range(1, click_region[2] // click_span + 1):
            x = int(click_region[0] + click_span * i + (random.random() - 0.5) * click_flex)
            p.click(x, y)
            p.sleep(0.1)
    if legendary_alarm and attempted >= PICKUP_LIMIT - 1:
        if np.where((np.abs(np.array(im)[:, :, :3] - orange_rgb) <= color_threshold).all(axis=2))[0].shape[0] > 10:
            alarm_legendary()
    log(f"finished picking attempt #{attempted + 1}")
    return True


def alarm_legendary():
    log("there are legendary items you can't pick up")


def trade(location):
    activate_diablo()
    if sys.platform == "darwin":
        key_to_npc, key_to_fish = KEY_MOVE[location]
        trade_fish_buy_bait_go_back(key_to_npc, key_to_fish)
    else:
        trade_with_gui()


def fish_and_trade(location, fish_type, brightness=50, stop=None):
    if stop is None:
        def stop():
            return False
    if fish(fish_type, brightness, stop):
        p.sleep(1)
        trade(location)
        p.sleep(1)


def auto_fishing(location, fish_type, brightness=50, stop=None):
    if stop is None:
        def stop():
            return None
    while True:
        fish_and_trade(location, fish_type, brightness, stop)
        if stop():
            break


def log(contents):
    print(contents)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ["bilifen", "ashwold", "tundra"]:
            location = sys.argv[1]
        else:
            # location = "bilefen"
            # location = "ashwold"
            location = "tundra"
        if len(sys.argv) > 2 and sys.argv[2] in ["white", "blue", "yellow"]:
            fish_type = sys.argv[2]
        else:
            # fish_type = "white"
            # fish_type = "blue"
            fish_type = "yellow"

        auto_fishing(location, fish_type)
    else:
        root = GUI()

        def start_auto_fishing(button):
            root.not_fishing = False
            args = (root.loc_var.get(), root.type_var.get(), root.bright_var.get(), lambda: root.not_fishing)
            root.thread = threading.Thread(target=auto_fishing, args=args, daemon=True)
            root.thread.start()
            button.config(text="Stop fishing", command=lambda: stop_auto_fishing(button))

        def stop_auto_fishing(button):
            root.not_fishing = True
            button.config(text="Auto Fishing", command=lambda: start_auto_fishing(button))

        def log(contents):
            root.log_text.insert('end', f"{contents}\n")

        root.fish_button.config(command=lambda: fish(root.type_var.get(), root.bright_var.get()))
        root.trade_button.config(command=lambda: trade(root.loc_var.get()))
        root.auto_fish_button.config(command=lambda: start_auto_fishing(root.auto_fish_button))

        root.mainloop()



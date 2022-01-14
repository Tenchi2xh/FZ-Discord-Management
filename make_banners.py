#!/usr/bin/env python3
import io
import os
import json
import yaml
import time
import re

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from yaml import Loader


with open("template.html", "r") as f:
    template = f.read()


def send(cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({"cmd": cmd, "params": params})
    driver.command_executor._request("POST", url, body)


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--force-device-scale-factor=2");
chrome_options.add_argument("--high-dpi-support=2");
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(3000, 800)
send("Emulation.setDefaultBackgroundColorOverride", {"color": {"r": 0, "g": 0, "b": 0, "a": 0}})


def body(banner):
    r = '<div class="FZ"><div class="main" id="banner">'

    if any(l in banner for l in ["cn", "jp", "kr"]):
        r += '<div class="CJK"><ruby>'
        langs = []
        if "jp" in banner: langs.append(banner["jp"])
        if "kr" in banner: langs.append(banner["kr"])
        if "cn" in banner: langs.append(banner["cn"])
        for i in range(len(langs)):
            pairs = langs[i]
            for pair in pairs:
                r += f'{pair[0]}<rt>{pair[1]}</rt>'
            if i < len(langs) - 1:
                r += '<div class="sep"></div><rt></rt>'
        r += '</ruby></div>'

    if banner.get("kaji", False):
        r += '<img class="kaji" src="kaji.png" />'

    r += re.sub(r"([A-Z])", r'<span class="cap">\1</span>', banner["title"])
    r += '<div class="dot"></div><div class="stick"></div>'

    if "subtitle" in banner:
        r += f'<div class="subtitle">{banner["subtitle"]}</div>'

    r += '</div></div>'

    return r


def screenshot(banner):
    filename = banner["title"].lower().replace(" ", "_") + ".png"

    with open("banner.html", "w") as f:
        f.write(template.format(body=body(banner)))

    driver.get(f"file://{os.path.join(os.getcwd(), 'banner.html')}")

    element = driver.find_element(By.ID, "banner")
    time.sleep(0.5)
    image = element.screenshot_as_png
    img = Image.open(io.BytesIO(image))
    img.save("banners/" + filename)


if __name__ == "__main__":
    with open("banners.yaml", "r") as f:
        banners = yaml.load(f, Loader=Loader)["banners"]

    if not os.path.isdir("banners"):
        os.makedirs("banners")

    for banner in banners:
        screenshot(banner)

    driver.quit()

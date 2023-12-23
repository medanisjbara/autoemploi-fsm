import base64
import io
import os
import re

import numpy as np
import pytesseract
import requests
from pdf2image import convert_from_bytes
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By


url_pattern = r'/useruploads/files/[^"]+\.pdf'


def browser_init(headless=True):
    """
    Initialises the browser
    """
    opts = webdriver.FirefoxOptions()
    opts.headless = headless
    driver = webdriver.Firefox(options=opts)
    return driver


def extranet_login(username, password, driver):
    """
    Automates the login process to https://fsm.rnu.tn/extranet
    Works by using pytesseract on the captcha.

    Note that this function does this in a while loop. Make sure to provide
    the correct credentials
    """
    driver.get("https://fsm.rnu.tn//extranet")
    while True:
        ## Fields to fill
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.ID, "password")
        captcha_field = driver.find_element(By.NAME, "anti_bots_text")

        ## Get captcha
        try:
            captcha_base64 = (
                driver.find_element(By.CLASS_NAME, "captcha_glinse")
                .get_attribute("src")
                .split(",")[1]
            )
        except Exception as e:
            print(f"Couldn't get captcha image: {e}")

        captcha_pic = Image.open(io.BytesIO(base64.b64decode(captcha_base64)))
        captcha_text = pytesseract.image_to_string(captcha_pic)[:-1]

        ## Fill the fields
        username_field.send_keys(username)
        password_field.send_keys(password)
        captcha_field.send_keys(captcha_text)

        ## Actual login
        driver.find_element(By.CLASS_NAME, "button").click()

        if driver.current_url != "https://fsm.rnu.tn/fra/intranet/auth/wrong-auth":
            break


def process_pdf(pdf_link):
    """
    Takes a URL to a pdf file as an argument and loops through every page
    applying OCR and cropping using prepare_image() as needed
    """
    image_bytes = requests.get(pdf_link).content
    # TODO: Save file for future use.
    for i, page in enumerate(convert_from_bytes(image_bytes)):
        print(f"Processing page number {i} in document {pdf_link}")
        # TODO: Use appropriate naming
        name = pdf_link.split("/")[-1] + str(i)
        open("text_pages/" + name + ".txt", "w").write(
            pytesseract.image_to_string(page)
        )
        prepare_image(page, name + ".png")


def prepare_image(image, name, darkmode=False):
    """
    Crops images as needed and saves them with the appropriate name
    """
    print(f"Cropping {name}...", end="")
    if "l" in name.lower():
        img_arr = np.array(image)[20:400, 1000:1700]
    elif "m" in name.lower():
        img_arr = np.array(image)[100:420, :]
    else:
        img_arr = np.array(image)[20:420, :]
    if darkmode:
        img_arr = 255 - img_arr
    print("Done!")
    print("Saving...", end="")
    Image.fromarray(img_arr).save("images/" + name)
    print("Done!\n")


def scrape_source(source, last=False):
    """
    Takes html suorce and scrapes it for PDF links that match the needed specifications
    `last` indicates whether the result should only consist of the last day.
    """
    # First PDF in the page is to be ignored
    # (Not an exam related pdf)
    matches = re.findall(url_pattern, source)[1:]

    for match in matches:
        process_pdf("https://fsm.rnu.tn/" + match)
        if last:
            break


def fetch_update(username="", password="", target="", local=False):
    driver = browser_init()
    if not os.path.exists("local-source.html"):
        open("local-source.html", "w")
    if not local:
        assert username and password and target
        # TODO 1: Use same session when possible
        # TODO 2: Make optional (in case files are accessible from extranet)
        extranet_login(username, password, driver)
        driver.get(target)
        source = "\n".join(
            driver.page_source.splitlines()[:-1]
        )  # Last line always changes
        if source == open("local-source.html").read():
            return
        open("local-source.html", "w").write(source)
    else:
        source = open("local-source.html").read()

    # init directories
    # TODO: Replace deletion with checks later on
    for folder in ["images", "text_pages"]:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                os.remove(folder + "/" + file)
            os.rmdir(folder)
        os.mkdir(folder)

    scrape_source(source)

from PIL import Image
from pdf2image import convert_from_bytes
import json, os, requests, io
import pytesseract, base64
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.by import By



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
        captcha_base64 = driver.find_element(By.CLASS_NAME, "captcha_glinse").get_attribute('src').split(',')[1]
      except:
        continue

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

def process_pdf(pdf):
    """
    Takes a URL to a pdf file as an argument and loops through every page
    applying OCR and cropping using prepare_image() as needed
    """
    image_bytes = requests.get('https://fsm.rnu.tn'+pdf).content
    # TODO: Save file for future use.
    for i,page in enumerate(convert_from_bytes(image_bytes)):
        print(f'Processing page number {i} in document {pdf}')
        # TODO: Use appropriate naming
        name = pdf.split('/')[-1]+str(i)
        open('text_pages/'+name+'.txt', 'w').write(pytesseract.image_to_string(page))
        prepare_image(page, name+'.png')


def prepare_image(image,name, darkmode=True):
    """
    Crops images as needed and saves them with the appropriate name
    """
    print(f'Cropping {name}...', end='')
    if 'l' in name.lower():
        img_arr =  np.array(image)[20:400 , 1000:1700]
    elif 'm' in name.lower():
        img_arr =  np.array(image)[100:420 , :]
    else:
        img_arr =  np.array(image)[20:420 , :]
    if darkmode:
        img_arr = 255 - img_arr
    print('Done!')
    print('Saving...', end='')
    Image.fromarray(img_arr).save('images/'+name)
    print('Done!\n')

def scrape_source(source, driver, last=True):
    """
    Takes html suorce and scrapes it for PDF links that match the needed specifications
    It uses the selenium driver instead of parsing.
    `last` indicates whether the result should only consist of the last day.
    """
    def parse_ul(e):
        for li in e.find_elements(By.XPATH, './*'):
            if li.tag_name != 'li':
                print(li.tag_name, "found where it shouldn't be")
                print("Manual intervention is needed")
                continue
            for a in li.find_elements(By.XPATH, './*'):
                process_pdf(driver.execute_script('return arguments[0].getAttribute("href")', a))
    html_bs64 = base64.b64encode(source.encode('utf-8')).decode()
    driver.get("data:text/html;base64," + html_bs64)

    for e in driver.find_elements(By.XPATH, '/html/body/div/div/div/div/span/*'):
        if e.tag_name not in ['ul', 'div']:
            continue
        if e.tag_name == 'ul':
            parse_ul(e)
            if last:
                break
            continue
        for tag in e.find_elements(By.XPATH, './*'):
            if tag.tag_name == 'ul':
                print("Found nested tags")
                parse_ul(e)
                if last:
                    break

def fetch_update(username, password, target):
    driver = browser_init()
    extranet_login(username, password, driver)
    driver.get(target)
    source = driver.page_source
    if not os.path.exists('local-source.html'):
        open('local-source.html','w')
    elif source == open('local-source.html').read():
        return
    open('local-source.html', 'w').write(source)

    # init directories
    for folder in ['images', 'text_pages']:
      if os.path.exists(folder):
        for file in os.listdir(folder):
          os.remove(folder+'/'+file)
        os.rmdir(folder)
      os.mkdir(folder)

    scrape_source(source, driver)

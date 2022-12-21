# Imports
from PIL import Image
from pdf2image import convert_from_bytes
import json, os, requests, io
import pytesseract, base64
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.by import By


text_pages = os.listdir('text_pages') if os.path.exists('text_pages') else []

# User data
username = ''
password = ''
# Link to the link that will be scraped after login
# Example: "https://fsm.rnu.tn/fra/intranet/news/etu.view/358"
devoir_url = ""
if os.path.exists('credentials.json'):
    creds = json.load(open('credentials.json'))
    username = creds['username']
    password = creds['password']
    devoir_url = creds['url']


def fetch_update():
    # init selenium browser
    opts = webdriver.FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)
    driver.get("https://fsm.rnu.tn//extranet")
    
    # init directories
    for folder in ['images', 'text_pages']:
      if os.path.exists(folder):
        for file in os.listdir(folder):
          os.remove(file)
        os.rmdir(folder)
      os.mkdir(folder)

    # Ask for username and password
    global username, password
    if not username:
      username = input('Enter extranet\'s username: ')
    if not password:
      password = input('Enter extranet\'s password: ')
    if not devoir_url:
      print('Enter the link of the page containing the files')
      print('Example: https://fsm.rnu.tn/fra/intranet/news/etu.view/358')
      devoir_url = input('URL: ')
    json.dump({'username':username, 'password': password, 'url':devoir_url}, open('credentials.json','w'))
    
    # Login
    while True:
      ## Fields to fill
      username_field = driver.find_element(By.NAME, "username")
      password_field = driver.find_element(By.ID, "password")
      captcha_field = driver.find_element(By.NAME, "anti_bots_text")
    
      ## Get captcha
      captcha_base64 = driver.find_element(By.CLASS_NAME, "captcha_glinse").get_attribute('src').split(',')[1]
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
    
    driver.get(devoir_url)
    
    for e in driver.find_elements(By.XPATH, '/html/body/div/div/div/div/span/*'):
        if e.tag_name == 'ul':
            for li in e.find_elements(By.XPATH, './*'):
                if li.tag_name != 'li':
                    print(li.tag_name, "found where it shouldn't be")
                    print("Manual intervention is needed")
                else:
                    seance = driver.execute_script('return arguments[0].outerHTML', li)
                    for devoir in seance[seance.find('(') +1 : seance.find(')')].split(', '):
                        pdf = devoir[devoir.find('"')+1:]
                        pdf = pdf[:pdf.find('"')]
                        process_pdf(pdf)
            break
        elif e.tag_name == 'div':
            for tag in e.find_elements(By.XPATH, './*'):
                if tag.tag_name == 'ul':
                    print("Found nested tags")
                    for li in tag.find_elements(By.XPATH, './*'):
                        if li.tag_name == 'li':

                            seance = driver.execute_script('return arguments[0].outerHTML', li)
                            for devoir in seance[seance.find('(') +1 : seance.find(')')].split(', '):
                                pdf = devoir[devoir.find('"')+1:]
                                pdf = pdf[:pdf.find('"')]
                                process_pdf(pdf)
                        else:
                            print('(nested)',li.tag_name, "found where it shouldn't be")
                            print("Manual intervention is needed")

def process_pdf(pdf):
    image_bytes = requests.get('https://fsm.rnu.tn'+pdf).content
    for i,page in enumerate(convert_from_bytes(image_bytes)):
        print(f'Processing page number {i} in document {pdf}')
        name = pdf.split('/')[-1]+str(i)
        open('text_pages/'+name+'.txt', 'w').write(pytesseract.image_to_string(page))
        prepare_image(page, name+'.png')


def prepare_image(image,name, darkmode=True):
    print(f'Cropping {name}...', end='')
    img_arr =  np.array(image)[50:310 , 1200:1600]
    if darkmode:
        img_arr = 255 - img_arr
    print('Done!')
    print('Saving...', end='')
    Image.fromarray(img_arr).save('images/'+name)
    print('Done!\n')


if __name__=='__main__':
    if len(argv) != 2:
        print('Usage: '+argv[0]+' [fetch|find]')
        print('\tfetch:\tgrabs pdf files from FSM website')
        print('\tfind:\tfinds your class based on your CIN')
    else:
        if argv[1] == 'fetch':
            fetch_update()
        elif argv[1] == 'find':
            x = get_user_output(input('CIN: '))
            print(x)
        else:
            print('Usage: '+argv[0]+' [fetch|find]')
            print('\tfetch:\tgrabs pdf files from FSM website')
            print('\tfind:\tfinds your class based on your CIN')

from random import randint
from time import sleep

from goto import with_goto
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

import requests, os
from beauty_predict import scores
from secrets import firebase_pass, firebase_user, firebase_url, firebase_service_account_path
from firebase import firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import hashlib

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def download_image(source, destination):
    img_data = requests.get(source).content
    with open(destination, 'wb') as out:
        out.write(img_data)

class TinderAutoSwipeBot():
    def __init__(self, threshold = 6.2):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.threshold = threshold
        self.begining = True
        self.current_image = None
        self.likes_num = 0
        self.dislikes_num = 0
        self.swipes_thresold = 100
        self.firebase = None

    # Open New Browser window with Tinder Web
    def login(self):
        self.driver.get('https://tinder.com')

    # Stop the Bot
    def stop(self):
        print('Stopping Bot')
        self.driver.close()

    # Like Profile
    def like(self):
        self.driver.find_element_by_tag_name('body').send_keys(Keys.ARROW_RIGHT)
        print('Liking....')
        self.likes_num += 1

    # Dislike Profile
    def dislike(self):
        self.driver.find_element_by_tag_name('body').send_keys(Keys.ARROW_LEFT)
        print('Disliking....')
        self.dislikes_num += 1

    # Auto Swiping Functionality
    def ai_swipe(self):
        while True:
            if self.likes_num + self.dislikes_num >= self.swipes_thresold:
                self.stop()
                break
            sleep(randint(1,4))
            try:
                self.choose()
            except Exception as err:
                try:
                    self.close_popup()
                except Exception:
                    try:
                        self.close_match()
                    except Exception:
                         print("Error: {0}".format(err))

    def choose(self):
        scrs = self.current_scores()
        choice = "DISLIKE"
        if len(scrs) == 0:
            self.dislike()
        elif [scr > self.threshold for scr in scrs] == len(scrs) * [True]:
            self.like() # if there are several faces, they must all have
            choice = "LIKE" # better score than threshold to be liked
        else:
            self.dislike()

        print("Scores : ",
              scrs,
              " | Choice : ",
              choice,
              " | Threshold : ",
              self.threshold)
        self.move_image(choice)

    def move_image(self, choice="DISLIKE"):
        if self.current_image is None:
            try:                
                filename = os.path.basename(self.current_image)
                dir      = os.path.dirname(self.current_image)
                os.replace(self.current_image, dir + os.path.pathsep + choice.lower() + filename)
            except Exception as err:
                print("Error moving the filename: {0}".format(err))
        self.current_image = None

    def current_scores(self):
        url = self.get_image_path()
        outPath = os.path.join(APP_ROOT, 'images', os.path.basename(url))
        download_image(url, outPath)
        return scores(outPath)

    def close_popup(self):
        popup_3 = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div[2]/button[2]')
        popup_3.click()

    def close_match(self):
        match_popup = self.driver.find_element_by_xpath('//*[@id="modal-manager-canvas"]/div/div/div[1]/div/div[3]/a')
        match_popup.click()

    def get_image_path(self):
        
        name_node = self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[1]/div[3]/div[6]/div/div[1]/div/div/span')
        name = name_node.get_attribute('innerText')
        div_image = self.driver.find_element_by_css_selector('[aria-label="'+name+'"]')
        bodyHTML = div_image.get_attribute('style')        
        return self.parse_url(bodyHTML)

    def get_matches(self):
        sleep(3)
        matches = []
        image_elements = self.driver.find_elements_by_css_selector('#matchListNoMessages div.recCard__img')
        for image_element in image_elements:
            image_url = image_element.get_attribute('style')        
            name = image_element.get_attribute('aria-label')
            if name and image_url:
                result = self.parse_url(image_url)
                match = {
                    'username': name,
                    'image': result,
                    'hash': hashlib.sha256(result.encode('utf-8')).hexdigest()
                }
                if self.post_firebase(match):
                    matches.append(match)
        return matches
        
    def parse_url(self, bodyHTML):
        startMarker = 'background-image: url(&quot;'
        endMarker = '");'

        if not self.begining:
            urlStart = bodyHTML.rfind(startMarker)
            urlStart = bodyHTML[:urlStart].rfind(startMarker)+len(startMarker)
        else:
            urlStart = bodyHTML.rfind(startMarker)+len(startMarker)

        self.begining = False
        urlEnd = bodyHTML.find(endMarker, urlStart)        
        return "http"+bodyHTML[urlStart:urlEnd]
    def init_firebase(self):
        if self.firebase is not None:
            return self.firebase
        cred = credentials.Certificate(firebase_service_account_path)
        app = firebase_admin.initialize_app(cred, {
            'databaseUrl': firebase_url
        }, 'tinder-bot')
        self.firebase = db.reference('/matches', app, firebase_url)
        return self.firebase
    def post_firebase(self, match={}):
        if 'username' not in match: 
            return False

        ref = self.init_firebase()

        all_matches = ref.get()
        if all_matches:
            for i in all_matches:
                if 'hash' in all_matches[i] and all_matches[i]['hash'] == hashlib.sha256(match['image'].encode('utf-8')).hexdigest():
                    return False
            
        ref.push({
            'username': match['username'],
            'image': match['image'],
            'hash': match['hash']
        })
        return True

@with_goto
def main():
    # Call the Bot
    bot = TinderAutoSwipeBot()
    # Start Login Process
    bot.login()

    print('---------------------------------------------------------------------------------------')
    print('STEP 1: Kindly login to your Tinder account manually in newly open browser screen. '
          'Allow all required permission location, notification etc')
    print('STEP 2: One You done with login. Input Yes or 1 and Hit Enter Key')
    print('STEP 3: Enjoy! Auto Swiping :)')
    print('---------------------------------------------------------------------------------------')

    # Start the Auto Liking / Disliking
    label.begin
    answer = input("Have you logged in? (Yes | 1): ")
    if answer.lower() == '1' or answer.lower() == 'yes':
        bot.ai_swipe()
    else:
        print("Enter Correct Value: Yes or 1")
        goto.begin


if __name__ == '__main__':
    main()

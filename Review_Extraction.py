from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from amazoncaptcha import AmazonCaptcha
from googletrans import Translator,LANGUAGES
import re
import pandas as pd
import csv
from time import sleep

class Amazon_Review_Extract:
    def __init__(self):
        chrome_options = Options()
#         Uncommenting below 2 lines can disable the browser pop up
#         chrome_options.add_argument('--headless')
#         chrome_options.add_argument('--disable-gpu')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.trans = Translator()
        
    def bypass(self):
        try:
            self.link = self.driver.find_element(By.XPATH,"//div[@class = 'a-row a-text-center']//img").get_attribute('src')
            captcha = AmazonCaptcha.fromlink(self.link)
            captcha_v = AmazonCaptcha.solve(captcha)
            ip = self.driver.find_element(By.ID,'captchacharacters').send_keys(captcha_v)
            butt = self.driver.find_element(By.CLASS_NAME,"a-button-text")
            butt.click()
        except :
            return 
        
    def extract(self):
        reviews = self.driver.find_elements(By.XPATH,"//span[@data-hook='review-body']")
        revs = []
        for i in reviews:
            rev = i.text
            lan = self.trans.detect(rev[:5]).lang
            if lan != 'en':
                rev = self.trans.translate(rev,src=lan,dest='en').text
            revs.append(rev.replace('\n',''))
        return revs
    
    def price_cal(self,url):
        try:
            self.driver.get("https://pricehistoryapp.com/")
            element = self.driver.find_element(By.CSS_SELECTOR, "input.w-full")
            element.send_keys(url)
            element.send_keys(Keys.ENTER)
            sleep(10)
            html = BeautifulSoup(self.driver.page_source,'lxml')
            text = html.find('div',class_="content-width mx-auto px-3").text
            for i in range(len(text)):
                if text[i:i+5] == '. Thi':
                    text = text[i+1:]
                    break
            
            price_pattern = re.compile(r'(\d+(\.\d+)?)')
            prices = [match[0] for match in price_pattern.findall(text)]
            self.prices = {'Current':float(prices[0]),'Lowest':float(prices[1]),'Average':float(prices[2]),'Highest':float(prices[3])}
            self.fairness = self.fairness_score(self.prices['Lowest'],self.prices['Highest'],self.prices['Average'],self.prices['Current'])
            return True
        except:
            return False
    
    def fairness_score(self,Pmin, Pmax, Pavg, Pcur):
        if Pmax == Pmin:
            return 50 if Pcur == Pavg else (100 if Pcur == Pmin else 0)
        else:
            return (abs(Pcur-Pavg)/(Pmax - Pmin))*100

    def start(self,p_url):
        reviews = []
        self.driver.get(p_url)
        self.bypass()
        self.driver.find_element(By.XPATH,"//a[@data-hook='see-all-reviews-link-foot']").click()
        sleep(2)
        self.product_name = self.driver.find_element(By.XPATH,"//a[@class='a-link-normal']")
        c = 0
        while True:
            review = self.extract()
            reviews.extend(review)
            
            try:
                self.driver.find_element(By.CLASS_NAME,"a-last").click()
                sleep(3)
                self.driver.find_element(By.XPATH,"//li[@class='a-disabled a-last']")
                break
            except :
                pass
        
        return pd.DataFrame(reviews)
#         df_reviews.to_csv('scrapedReviews.csv', index=False)
    def finish(self):
        self.driver.quit()        
        

class Flipkart_Review_Extract:
    def __init__(self):
        chrome_options = Options()
#         Uncommenting below 2 lines can disable the browser pop up
#         chrome_options.add_argument('--headless')
#         chrome_options.add_argument('--disable-gpu')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.data = []
        self.trans = Translator()
        
    def review_link_extract(self,link):
        self.driver.get(link)
        try:
            a = self.driver.find_element(By.XPATH,"//div[@class='col JOpGWq']//a")
            self.driver.get(a.get_attribute('href'))
        except :
            print('MEE')
        sleep(1)
        try:
            a = self.driver.find_element(By.XPATH,"//div[@class='col-9-12']//a")
            self.driver.get(a.get_attribute('href'))
        except :
            print('YOUUU')
        sleep(1)
        a = self.driver.find_element(By.XPATH,"//nav[@class='yFHi8N']//a")
        page_count = self.driver.find_element(By.XPATH,"//div[@class='_2MImiq _1Qnn1K']//span").text
        return a.get_attribute('href')[:-1],int(page_count.split()[-1])
    
    def extract(self,link):
        self.driver.get(link)
        reviews = self.driver.find_elements(By.XPATH,"//div[@class='_1YokD2 _3Mn1Gg col-9-12']//div[@class='_1AtVbE col-12-12']")
        review_list = []
        reviews.pop()
        reviews.pop(0)
        for i in reviews:

            try:
                rm_btn = i.find_element(By.XPATH,"//span[@class='_1BWGvX']//span")
                while True :
                    try:
                        rm_btn.click()
                    except :
                        break
            except:
                pass
            try:
                rev = i.find_element(By.CLASS_NAME,"t-ZTKy").text
                lan = self.trans.detect(rev[:5]).lang
                if lan != 'en':
                    rev = self.trans.translate(rev,src=lan,dest='en').text
                review_list.append(rev)
            except :
                review_list.append('')
        return review_list
        
    def start(self,link):
        link,page_count = self.review_link_extract(link)
        l = []
        for i in range(1,page_count+1):
            l.extend(self.extract(link+str(i)))
        return pd.DataFrame(l)
    
    def price_cal(self,url):
        try:
            self.driver.get("https://pricehistoryapp.com/")
            element = self.driver.find_element(By.CSS_SELECTOR, "input.w-full")
            element.send_keys(url)
            element.send_keys(Keys.ENTER)
            sleep(10)
            html = BeautifulSoup(self.driver.page_source,'lxml')
            text = html.find('div',class_="content-width mx-auto px-3").text
            for i in range(len(text)):
                if text[i:i+5] == '. Thi':
                    text = text[i+1:]
                    break
            
            price_pattern = re.compile(r'(\d+(\.\d+)?)')
            prices = [match[0] for match in price_pattern.findall(text)]
            self.prices = {'Current':float(prices[0]),'Lowest':float(prices[1]),'Average':float(prices[2]),'Highest':float(prices[3])}
            self.fairness = self.fairness_score(self.prices['Lowest'],self.prices['Highest'],self.prices['Average'],self.prices['Current'])
            return True
        except:
            return False
    
    def fairness_score(self,Pmin, Pmax, Pavg, Pcur):
        if Pmax == Pmin:
            return 50 if Pcur == Pavg else (100 if Pcur == Pmin else 0)
        else:
            return (abs(Pcur-Pavg)/(Pmax - Pmin))*100
        
    def finish(self):
        self.driver.quit()

# 
#
# obj = Amazon_Review_Extract()
# obj.bypass()
# print(obj.start("https://www.amazon.in/Apple-iPhone-Pro-Max-256/dp/B0CHX1K2ZC/ref=cm_cr_arp_d_pdt_img_top?ie=UTF8&tag=coa_in_g-21"))

# obj = Flipkart_Review_Extract()
# obj.start("https://www.flipkart.com/sony-alpha-full-frame-ilce-7m2k-bq-in5-mirrorless-camera-body-28-70-mm-lens/p/itm92df94dc68fff?pid=DLLF6QZPNKTQMS8J&fm=organic&ppt=dynamic&ppn=dynamic&ssid=fnewy5pmbk0000001706938474552")
# 
# 
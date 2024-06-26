from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from amazoncaptcha import AmazonCaptcha

import re
import pandas as pd
from time import sleep

class Review_Extract:
    def launch(self):
        chrome_options = Options()
    #         Uncommenting below 2 lines can disable the browser pop up
#         chrome_options.add_argument('--headless')
#         chrome_options.add_argument('--disable-gpu')
#         chrome_options.add_argument('--no-sandbox')
        
        self.driver = webdriver.Chrome(options=chrome_options)

    def price_cal(self,url,bulk=False):
        try:
            self.driver.get("https://pricehistoryapp.com/")
            element = self.driver.find_element(By.CSS_SELECTOR, "input.w-full")
            element.send_keys(url)
            element.send_keys(Keys.ENTER)
            sleep(10)
            text = self.driver.find_element(By.XPATH,"//div[@class='content-width mx-auto px-3']").text
            for i in range(len(text)):
                if text[i:i+5] == '. Thi':
                    text = text[i+1:]
                    break
            
            price_pattern = re.compile(r'(\d+(\.\d+)?)')
            prices = [match[0] for match in price_pattern.findall(text)]
            self.prices = {'Current':float(prices[0]),'Lowest':float(prices[1]),'Average':float(prices[2]),'Highest':float(prices[3])}
            self.fairness = self.fairness_score(self.prices['Lowest'],self.prices['Highest'],self.prices['Average'],self.prices['Current'])
            con = self.driver.find_element(By.XPATH,"//p[@class='text-gray-500 dark:text-gray-400 text-sm']").text
            if not bulk:
                self.driver.find_element(By.XPATH,"//button[@class='px-4 py-2 bg-gray-400 text-white font-medium rounded hidden md:block']").click()
                sleep(4)
                i = self.driver.find_element(By.XPATH,"//code[@class='language-html']").text
            else:
                return self.fairness
            return [True,i,con]
        except :
            if bulk:
                return -1
            self.fairness = 0
            return [False,'','']

    def fairness_score(self,Pmin, Pmax, Pavg, Pcur):
        if Pavg > Pcur:
            return 50+(Pavg-Pcur)*50/(Pavg-Pmin)
        elif Pavg < Pcur:
            return 50-(Pcur-Pavg)*50/(Pmax-Pavg)
        
        return 50

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

    def amazon_extract(self):
        reviews = self.driver.find_elements(By.XPATH,"//span[@data-hook='review-body']")
        revs = []
        for i in reviews:
            rev = i.text
            revs.append(rev.replace('\n',''))
        return revs

    def amazon_start(self,p_url):
        reviews = []
        self.driver.get(p_url)
        self.bypass()
        self.driver.find_element(By.XPATH,"//a[@data-hook='see-all-reviews-link-foot']").click()
        sleep(2)
        self.product_name = self.driver.find_element(By.XPATH,"//a[@class='a-link-normal']")
        c = 0
        while True:
            review = self.amazon_extract()
            reviews.extend(review)
            
            try:
                self.driver.find_element(By.CLASS_NAME,"a-last").click()
                sleep(3)
                self.driver.find_element(By.XPATH,"//li[@class='a-disabled a-last']")
                break
            except :
                pass
            
        df = pd.DataFrame(reviews)
        df.to_csv('scrapedReviews.csv',encoding='utf-8', index=False)
        return pd.DataFrame(reviews,columns=['Review'])
     

    def review_link_extract(self,link):
        self.driver.get(link)
        try:
            a = self.driver.find_element(By.XPATH,"//div[@class='col JOpGWq']//a")
            self.driver.get(a.get_attribute('href'))
        except :
            pass
        sleep(1)
        try:
            a = self.driver.find_element(By.XPATH,"//div[@class='col-9-12']//a")
            self.driver.get(a.get_attribute('href'))
        except :
            pass
        sleep(1)
        try:
            a = self.driver.find_element(By.XPATH,"//nav[@class='yFHi8N']//a")
        except:
            pass
        try:
            page_count = self.driver.find_element(By.XPATH,"//div[@class='_2MImiq _1Qnn1K']//span").text
        except:
            page_count = 1
        return a.get_attribute('href')[:-1],int(page_count.split()[-1])

    def flipkart_extract(self,link):
        try:
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
        except:
            pass
        return review_list
        
    def flipkart_start(self,link):
        link,page_count = self.review_link_extract(link)
        l = []
        for i in range(1,page_count+1):
            try:
                l.extend(self.flipkart_extract(link+str(i)))
            except:
                break
        return pd.DataFrame(l,columns=['Review'])
    
    def is_scrollbar_at_end(self):
        initial_scroll_position = self.driver.execute_script("return window.scrollY;")
        
        self.driver.find_element(By.TAG_NAME,'body').send_keys(Keys.PAGE_DOWN)
        sleep(2)    
        
        updated_scroll_position = self.driver.execute_script("return window.scrollY;")
        
        return initial_scroll_position == updated_scroll_position
    
    def myntra_extract(self,link):
        self.driver.get(link)

        pid = self.driver.find_element(By.CLASS_NAME,'supplier-styleId').text
        self.driver.get('https://www.myntra.com/reviews/'+pid)

        while not self.is_scrollbar_at_end():
            pass
            
        self.driver.find_element(By.TAG_NAME,'body').send_keys(Keys.HOME)
        reviews = self.driver.find_elements(By.CLASS_NAME,'user-review-reviewTextWrapper')
        return pd.DataFrame({'Reviews':list(map(lambda i:i.text,reviews))})



    def start(self,link):
        if 'flipkart' in link:
            return self.flipkart_start(link)
        elif 'myntra' in link:
            return self.myntra_extract(link)
        return self.amazon_start(link)
        

    def finish(self):
        self.driver.quit()

if __name__ == '__main__':
    obj = Review_Extract()
    obj.launch()
#     print(obj.start("https://www.flipkart.com/sony-alpha-full-frame-ilce-7m2k-bq-in5-mirrorless-camera-body-28-70-mm-lens/p/itm92df94dc68fff?pid=DLLF6QZPNKTQMS8J&fm=organic&ppt=dynamic&ppn=dynamic&ssid=fnewy5pmbk0000001706938474552"))
#     obj.price_cal("https://www.flipkart.com/sony-alpha-full-frame-ilce-7m2k-bq-in5-mirrorless-camera-body-28-70-mm-lens/p/itm92df94dc68fff?pid=DLLF6QZPNKTQMS8J&fm=organic&ppt=dynamic&ppn=dynamic&ssid=fnewy5pmbk0000001706938474552")
    print(obj.start('https://www.amazon.in/Apple-iPhone-Pro-Max-256/dp/B0CHWV2WYK/ref=sr_1_3?sr=8-3'))
    obj.finish()

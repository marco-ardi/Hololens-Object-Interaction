from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time
import threading
#settings
options = Options()
options.headless = True
#driver = webdriver.Chrome(options=options)
#driver.set_window_size(1024, 600)
#driver.maximize_window()
#driver.get("http://localhost:5601/app/dashboards#/view/4453cab0-324f-11ec-a193-15f18747c5bf?_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!t%2Cvalue%3A0)%2Ctime%3A(from%3A'2021-10-18T14%3A07%3A48.777Z'%2Cto%3A'2021-10-18T14%3A09%3A42.437Z'))")


#function to loop
def scrape():
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 600)
    driver.maximize_window()
    driver.get("http://localhost:5601/app/dashboards#/view/e6d05390-3cc1-11ec-ad71-ad824bcd705f?_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!f%2Cvalue%3A5000)%2Ctime%3A(from%3A'2021-11-02T15%3A59%3A55.196Z'%2Cto%3Anow))")
    time.sleep(10)
    print("im scraping")
    try:
        dismiss1 = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//*[@id="0"]/div[2]/div/div/div[5]/div[2]/button')))
        dismiss1.click()
        images = WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located((By.XPATH,'//*[@id="kibana-body"]/div/div/div/div[2]/div/div/div/div/div/div/div')))
        print(len(images))
        for i in range(0, len(images)-1):
            images[i].screenshot("/home/marco/Desktop/FlaskWebServer/static/image"+str(i)+".png") 
    except:
        print("error")
    driver.close()
    
    


    #dismiss1 = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="0"]/div[2]/div/div/div[5]/div[2]/button')))
    #dismiss1.click()
while True:
    scrape()

    

#dismiss1 = driver.find_element_by_xpath('//*[@id="0"]/div[2]/div/div/div[5]/div[2]/button')
#dismiss1.click()
#dismiss2 = driver.find_element_by_xpath('//*[@id="globalHeaderBars"]/div[2]/div[3]/div/div/span/nav/div/button[1]')
#dismiss2.click()
#driver.save_screenshot("/home/marco/Desktop/selenium/mydash.png")
#driver.execute_script("document.body.style.zoom='90%'")
#image = driver.find_element_by_xpath('//*[@id="kibana-body"]/div/div[2]/div/div[2]/div/div/div/div/div/div[2]/div')#change last index for a different panel
#dash = driver.find_element_by_xpath('//*[@id="kibana-body"]/div/div/div/div[2]/div/div/div/div/div/div')#class=react-griditem
#print(image)                        //*[@id="kibana-body"]/div/div/div/div[2]/div/div/div/div/div/div
#images = driver.find_elements_by_xpath('//*[@id="kibana-body"]/div/div/div/div[2]/div/div/div/div/div/div/div')#need to go 1 div deeper and select div with no index
#image.
#print(len(images))
#for i in range(0, len(images)-1):
#    images[i].screenshot("/home/marco/Desktop/FlaskWebServer/static/image"+str(i)+".png")    
#images[1].screenshot("/home/marco/Desktop/FlaskWebServer/static/mynewdash.png")
#imageStream = io.BytesIO(image)
#im = Image.open(imageStream)
#im.save("/home/marco/Desktop/selenium/mydash.png")

#driver.save_screenshot("mydash.png")
#driver.quit()
from amazoncaptcha import AmazonCaptcha
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

CAPTCHA_OK_MSG = "已解决验证码"
CAPTCHA_ERROR_MSG = "验证码出现问题"
        
def handleCaptcha(driver):
    try:
        soup = BeautifulSoup(driver.page_source, features="lxml")
        # 找到验证码图片并解析
        src = soup.find(class_="a-row a-text-center").findChild(name="img").attrs["src"]
        captcha = AmazonCaptcha.fromlink(src)
        solution = captcha.solve(keep_logs=True)
        # print(solution)
        # 输入验证码解决方案
        input_element = driver.find_element(By.ID, "captchacharacters")
        input_element.send_keys(solution)
        button = driver.find_element(By.XPATH, "//button")
        button.click()
        print(CAPTCHA_OK_MSG)
    except:
        print(CAPTCHA_ERROR_MSG)
    
    return 
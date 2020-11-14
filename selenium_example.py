from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
driverPath = ChromeDriverManager().install()
driver = webdriver.Chrome(driverPath, desired_capabilities=caps)
driver.get("https://cn.ad101.org/watch?v=dbgBV7pm82G")
# assert "EF" in driver.title
time.sleep(20)
# elem = driver.find_element_by_name("username")
# elem.clear()
# elem.send_keys("abc")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in driver.page_source

for entry in driver.get_log('performance'):
    print(entry)
# driver.close()
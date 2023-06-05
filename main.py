from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller 
import re
import os 

#variables =============================================================

CANVASLINK = "https://katyisd.instructure.com/"
MODULESLINK = "https://katyisd.instructure.com/courses/537853/modules"

USERNAME = ""
PASSWORD = ""

MAX_WAITING_TIME = 5

#variables =============================================================

regex = r'[^\w_. -]' #for filenames
download_dir = os.path.join(os.getcwd(), "canvas")

#options =============================================================
options = webdriver.ChromeOptions()
options.add_argument('disable-blink-features=AutomationControlled')
options.add_argument('user-agent=Type user agent here')
options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
})
options.add_argument("--headless")
#options =============================================================

#install chromedriver if not installed
chromedriver_autoinstaller.install() 

def apply_regex_substitution(regex, input_list):
    result_list = []

    for item in input_list:
        substituted_item = re.sub(regex, '_', item)
        result_list.append(substituted_item)

    return result_list

def apply_regex_substitution_2d(regex, input_array):
    result_array = []

    for row in input_array:
        result_row = []
        for item in row:
            substituted_item = re.sub(regex, '_', item)
            result_row.append(substituted_item)
        result_array.append(result_row)

    return result_array

def save_page(title, moduleTitle):
    driver.switch_to.window(driver.window_handles[1])
    WebDriverWait(driver, MAX_WAITING_TIME).until(
        EC.presence_of_element_located((By.ID, "content")) #This is a dummy element
    )
    new_path = os.path.join(download_dir, moduleTitle, title + ".html")
    with open(new_path,
                "w",
                encoding='utf-8'
            ) as f:
        f.write(driver.page_source)


driver = webdriver.Chrome(options=options) 

driver.get(CANVASLINK)




print(driver.find_element(By.ID, "userNameInput"))
driver.find_element(By.ID, "userNameInput").send_keys(USERNAME)
driver.find_element(By.ID, "passwordInput").send_keys(PASSWORD)
driver.find_element(By.ID, "submitButton").click()

WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.ID, "content"))
)

driver.get(MODULESLINK)

WebDriverWait(driver, MAX_WAITING_TIME).until(
    EC.presence_of_element_located((By.ID, "context_modules")) 
)


getmoduletitlescript = """
var final = []

const modulesHolder = document.getElementById("context_modules")
    const modulesList = modulesHolder.children

for(const child of modulesList){
    final.push(child.children[1].children[1].innerHTML)
}
return final;
"""

moduleTitleParseResult = driver.execute_script(getmoduletitlescript) 

getmodulescript = """
function parseModules(){
    const modulesHolder = document.getElementById("context_modules")
    const modulesList = modulesHolder.children
    var finalList = []

    for(const child of modulesList){
        tmpList = []
        for (const a of child.getElementsByClassName("ig-list items context_module_items")[0].children){
            if(a.getElementsByTagName("a")[0] == undefined){
                tmpList.push(a.getElementsByClassName("title locked_title")[0].innerText)
            }
            else{
                tmpList.push(a.getElementsByTagName("a")[0].href)
            }  
        }
        finalList.push(tmpList)
    }
    return finalList;
}
return parseModules();
"""

moduleParseResult = driver.execute_script(getmodulescript) 

getpagetitlescript = """
const modulesHolder = document.getElementById("context_modules")
    const modulesList = modulesHolder.children
    var finalList = []
    for(const child of modulesList){
        tmpList = []
        for (const a of child.getElementsByClassName("ig-list items context_module_items")[0].children){
            if(a.getElementsByTagName("a")[0] == undefined){
                tmpList.push(a.getElementsByClassName("title locked_title")[0].innerText)
            }
            else{
                tmpList.push(a.getElementsByTagName("a")[0].innerHTML)
            }  
        }
        finalList.push(tmpList)
    }
    return finalList;
"""

courseTitles = driver.execute_script(getpagetitlescript) 


for q in courseTitles:
    q[:] = [info.strip() for info in q] #stripping titles
moduleTitleParseResult = apply_regex_substitution(regex, moduleTitleParseResult)
courseTitles = apply_regex_substitution_2d(regex, courseTitles)




#creating module directories
for i in moduleTitleParseResult:
    try:

        os.makedirs(download_dir + f"\\{i}")

    except FileExistsError:
        print("Directory already exists")


for i in range(len(moduleTitleParseResult)):
    try:
        module = moduleTitleParseResult[i]
        print("MODULE : "  + module)
        for j in range(len(moduleParseResult[i])):
            courseTitle = courseTitles[i][j]
            link = moduleParseResult[i][j]
            print("COURSE : " + courseTitle)
            print("LINK : " + link)
            print(f"{i} {j}")
            driver.execute_script(f'''window.open("{link}","_blank");''')
            save_page(f"{j} - " + courseTitle, module)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        break


driver.quit()



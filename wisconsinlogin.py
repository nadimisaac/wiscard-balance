import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, NoSuchFrameException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import PySimpleGUI as gui

# NEED TO IMPROVE PAGE WAIT CODE AND EXCEPTION HANDLING
# FIND A BETTER LIBRARY FOR GUI, OR LOOK INTO REACT DASHBOARD POSSIBILITY

init_layout = [[gui.Text('Please Enter Your UW NetID', size=(50, 3), key='message')],
               [gui.Text("Username:", size=(10, 1)), gui.Input(key='user')],
               [gui.Text("Password:", size=(10, 1)), gui.Input(key='pass')],
               [gui.Submit()]
               ]

window = gui.Window('Wiscard Balance', init_layout, size=(500, 300))


options = webdriver.ChromeOptions()
options.headless = True

path = '/Users/nadimisaac/Downloads/chromedriver'
driver = webdriver.Chrome(executable_path=path, options=options)

def login_Attempt(username, password):

    driver.get('https://my.wisc.edu/portal/Login')

    username_field = driver.find_element_by_id('j_username')
    password_field = driver.find_element_by_id('j_password')
    login_button = driver.find_element_by_name('_eventId_proceed')

    username_field.send_keys(username)
    password_field.send_keys(password)

    login_button.click()

    time.sleep(5)

    if(len(driver.find_elements_by_id("loginForm")) != 0):
        raise LookupError("Invalid Credentials")


def duoAuth():
    while True:
        try:
            driver.switch_to.frame('duo_iframe')
            time.sleep(1)
            break
        except (NoSuchElementException, NoSuchFrameException) as error:
            pass

    send_push_button = driver.find_element_by_tag_name('button')
    send_push_button.click()

    try:
        while send_push_button.is_displayed():
            pass
    # will flow to this error handling when duo button no longer exists, hence it has been authenticated
    except Exception as e:
        time.sleep(1)


def html_balance():
    while True:
        try:
            wiscard_balance_button = driver.find_element_by_css_selector(
                '#widget-id-wiscard-balance > md-card-content > widget-content > div > div > content-item > a')
            wiscard_balance_button.click()
            break
        except Exception as e:
            pass

    while True:
        try:
            if(driver.current_window_handle != driver.window_handles[1]):
                driver.switch_to.window(driver.window_handles[1])

            view_more_list = driver.find_elements_by_link_text('View More')
            wiscard_acc_more = view_more_list[0]
            resident_acc_more = view_more_list[1]

            resident_acc_more.click()
            break
        # come back here and play around with Exception (sometimes throws weird exception)
        except (IndexError, NoSuchElementException, Exception) as ie:
            pass

    while True:
        try:
            view_statement_button = driver.find_element_by_id(
                'view-statement-button')
            view_statement_button.click()
            break
        except NoSuchElementException as e:
            pass


while True:                             # The Event Loop
    event, values = window.read()
    if event == "Submit":
        try:
            # this block of code is best case
            # code it as if user inputs everything right
            window['message'].update(
                "Attempting to Login...")
            window.refresh()
            time.sleep(1)
            login_Attempt(values['user'], values['pass'])
            window['message'].update(
                "Login Successful...Please Authenticate DUO 2FA")
            window.refresh()
            time.sleep(1)
            duoAuth()
            window['message'].update(
                "DUO 2FA Authenticated... Attempting to Retrieve Balance")
            window.refresh()
            html_balance()
            window.close()
        except LookupError as le:
            window['message'].update(
                "Invalid Login Credentials... Please Try Again")
            pass

    elif event == gui.WIN_CLOSED:
        window.close()
        break

statement_html = driver.page_source
soup = BeautifulSoup(statement_html, 'lxml')
transactions_table = soup.find("table", attrs={"class": "jsa_transactions"})
table_data = transactions_table.tbody.find_all("tr")[1:10]

balance = ""

for tr in table_data:
    balance += "\n"
    for html in tr.find_all(["td", "th"]):
        balance += "\n" + html.text


balance_layout = [[gui.Text(balance)]]

window2 = gui.Window('Wiscard Balance', balance_layout).Finalize()
window2.Maximize()


window2.read()


driver.quit()

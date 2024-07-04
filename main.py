import logging
import email
import imaplib
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# IMAP server credentials
sender_email = 'info@account.netflix.com'
username = ''
password = ''

# IMAP server details
imap_server = 'outlook.office365.com'

def get_html_from_msg(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "attachment" not in content_disposition:
                if content_type == "text/html":
                    html = part.get_payload(decode=True).decode()
                    return html
    else:
        content_type = msg.get_content_type()
        if content_type == "text/html":
            html = msg.get_payload(decode=True).decode()
            return html
    return None


def extract_link_from_html(html_content, link_text):
    soup = BeautifulSoup(html_content, 'lxml')
    link = soup.find('a', string=link_text)
    if link:
        return link['href']
    return None

def open_link(link):
    if link:
        try:
            logger.info("Abrindo o link...")
            driver.get(link)
            wait = WebDriverWait(driver, 10)
            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Confirmar atualização']")))
            button.click()
            time.sleep(10)
        except Exception as e:
            logger.info(f"Não foi possível clicar no botão: {e}")
        finally:
            driver.get('about:blank')


def get_firefox_driver():
    options = FirefoxOptions()
    options.add_argument("--headless")
    geckodriver_path = '/usr/local/bin/geckodriver'
    service = FirefoxService(executable_path=geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)
    return driver


def search_emails_by_sender(email_address):
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        while True:
            logger.info("Buscando novas mensagens...")
            mail.noop()
            mail.select('inbox')
            status, response = mail.search(None, f'(UNSEEN FROM "{email_address}")')

            if status == 'OK':
                for num in response[0].split():
                    status, data = mail.fetch(num, '(RFC822)')
                    if status == 'OK':
                        # Parse the email message
                        msg = email.message_from_bytes(data[0][1])
                        html_content = get_html_from_msg(msg)
                        if html_content:
                            # Extract and print the specific link
                            link_text = "Sim, fui eu"
                            link = extract_link_from_html(html_content, link_text)
                            open_link(link)
                        mail.store(num, '+FLAGS', '\\Seen')

            time.sleep(20)

    except Exception as e:
        logger.info(f"An error occurred: {e}")
    finally:
        mail.logout()


driver = get_firefox_driver()

if __name__ == "__main__":
    logger.info('Start searching emails...')
    try:
        search_emails_by_sender(sender_email)
    except Exception as e:
        logger.info(f"An error occurred: {e}")

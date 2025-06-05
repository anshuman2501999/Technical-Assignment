import requests
from bs4 import BeautifulSoup
import pdb
import re

session = requests.Session()
# Step 1: Start a session
def get_hidden_value(soup,name):
    element = soup.find("input", {"name": name})
    return element["value"] if element else ""




def get_data(district, tehsil, sro,doc_type):


# Step 2: Load the page to get hidden fields
    url = "https://epanjiyan.rajasthan.gov.in/e-search-page.aspx"


    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = session.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    viewstate = get_hidden_value(soup,"__VIEWSTATE")
    eventvalidation = get_hidden_value(soup,"__EVENTVALIDATION")
    viewstategenerator = get_hidden_value(soup,"__VIEWSTATEGENERATOR")
    districts = get_districts(soup)
    document_types = get_documents_type(soup)
    district_id = districts[district]
    document_type_id = document_types[doc_type]
    
    payload_type="district"
    district_payload = get_payload(payload_type,viewstate,viewstategenerator,eventvalidation,district_id,tehsil_id=None)
    district_response = session.post(url, headers=headers, data=district_payload)
    district_soup = BeautifulSoup(district_response.text, "html.parser")

    match = re.search(r'hiddenField\|__VIEWSTATE\|([^|]+)',district_response.text )
    viewstate_tehsil = match.group(1)

    match_event = re.search(r'\|hiddenField\|__EVENTVALIDATION\|(.+?)(?:\||$)',district_response.text )
    eventvalidation_tehsil = match_event.group(1)

    match_generator = re.search(r'\|__VIEWSTATEGENERATOR\|([^|]+)', district_response.text)
    viewstategenerator_tehsil =  match_generator.group(1)


    tehsils = get_tehsils(district_soup)
    tehsil_id = tehsils[tehsil]

    payload_type = "tehsil"
    tehsil_payload = get_payload(payload_type,viewstate_tehsil,viewstategenerator_tehsil,eventvalidation_tehsil,district_id,tehsil_id)
    sro_post_response = session.post(url, headers=headers, data=tehsil_payload)
    sro_soup = BeautifulSoup(sro_post_response.text, "html.parser")
    sros = get_sro(sro_soup)





    def get_sro(soup):

        sro_select = soup.find("select", {"name": "ctl00$ContentPlaceHolder1$ddlSRO"})

        # Build the dictionary from option tags
        sro = {}
        for option in sro_select.find_all("option"):
            value = option.get("value")
            label = option.text.strip()
            if value and value.isdigit():
                sro[label] = int(value)
        return sro



def get_tehsils(district_soup):
    tehsil_select = district_soup.find("select", {"name": "ctl00$ContentPlaceHolder1$ddlTehsil"})

# Build the dictionary from option tags
    tehsil = {}
    for option in tehsil_select.find_all("option"):
        value = option.get("value")
        label = option.text.strip()
        if value and value.isdigit():
            tehsil[label] = int(value)

    return tehsil



# Build the dictionary from option tags
def get_districts(soup):
    select = soup.find("select", {"name": "ctl00$ContentPlaceHolder1$ddlDistrict"})
    districts = {}
    for option in select.find_all("option"):
        value = option.get("value")
        label = option.text.strip()
        if value and value.isdigit():
            districts[label] = int(value)
    return districts

def get_documents_type(soup):

    document_select = soup.find("select", {"name": "ctl00$ContentPlaceHolder1$ddldocument"})
    doc_types = {}
    for option in document_select.find_all("option"):
        value = option.get("value")
        label = option.text.strip()
        # Skip the default option and invalid values
        if value and value.strip().isdigit():
            doc_types[label] = int(value)
    return doc_types


# Step 3: Prepare your payload
def get_payload(payload_type,viewstate,viewstategenerator,eventvalidation,district_id, tehsil_id=None):
    if payload_type == "district":
        payload = {
            "ctl00$ScriptManager1": "ctl00$upContent|ctl00$ContentPlaceHolder1$ddlDistrict",
            "ctl00$ContentPlaceHolder1$a": "",
            "ctl00$ContentPlaceHolder1$rbtrural": "rbtrural",
            "ctl00$ContentPlaceHolder1$ddlDistrict": district_id,
            "ctl00$ContentPlaceHolder1$ddldocument": " -- Select -- ",
            "ctl00$ContentPlaceHolder1$txtexcutent": "",
            "ctl00$ContentPlaceHolder1$txtclaiment": "",
            "ctl00$ContentPlaceHolder1$txtexecutentadd": "",
            "ctl00$ContentPlaceHolder1$txtprprtyadd": "",
            "ctl00$ContentPlaceHolder1$txtimgcode": "",  # You may need to scrape this from the CAPTCHA or image
            "ctl00$hdnCSRF": "",
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$ddlDistrict",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__SCROLLPOSITIONX":"0",
            "__SCROLLPOSITIONY":"0",
            "__VIEWSTATEENCRYPTED":"",
            "__EVENTVALIDATION": eventvalidation,
            "__ASYNCPOST":"true"
        }
    elif payload_type == "tehsil":
        payload = {
            "ctl00$ScriptManager1": "ctl00$upContent|ctl00$ContentPlaceHolder1$ddlTehsil",
            "ScriptManager1_HiddenField":"",
            "ctl00$ContentPlaceHolder1$a": "rbtrural",
            "ctl00$ContentPlaceHolder1$ddlDistrict": district_id,
            "ctl00$ContentPlaceHolder1$ddlTehsil":tehsil_id,
            "ctl00$ContentPlaceHolder1$ddldocument": " -- Select -- ",
            "ctl00$ContentPlaceHolder1$txtexcutent": "",
            "ctl00$ContentPlaceHolder1$txtclaiment": "",
            "ctl00$ContentPlaceHolder1$txtexecutentadd": "",
            "ctl00$ContentPlaceHolder1$txtprprtyadd": "",
            "ctl00$ContentPlaceHolder1$txtimgcode": "",  # You may need to scrape this from the CAPTCHA or image
            "ctl00$hdnCSRF": "",
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$ddlTehsil",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__SCROLLPOSITIONX":"0",
            "__SCROLLPOSITIONY":"0",
            "__EVENTVALIDATION": eventvalidation,
            "__VIEWSTATEENCRYPTED":"",
            "__ASYNCPOST":"true"
        }
    return payload







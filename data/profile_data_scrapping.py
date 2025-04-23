import agentql
from playwright.sync_api import sync_playwright, Geolocation
import asyncio
import time
import csv
import json
import random

'''
Preqrequisites
Run:
    1) pip install agentql
    2) agentql init - provide your API key
'''

BROWSER_IGNORED_ARGS = [
    "--enable-automation",
    "--disable-extensions",
]
BROWSER_ARGS = [
    "--disable-xss-auditor",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-blink-features=AutomationControlled",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-infobars",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0",
]


LOCATIONS = [
    ("America/New_York", Geolocation(longitude=-74.006, latitude=40.7128)),  # New York, NY
    ("America/Chicago", Geolocation(longitude=-87.6298, latitude=41.8781)),  # Chicago, IL
    ("America/Los_Angeles", Geolocation(longitude=-118.2437, latitude=34.0522)),  # Los Angeles, CA
    ("America/Denver", Geolocation(longitude=-104.9903, latitude=39.7392)),  # Denver, CO
    ("America/Phoenix", Geolocation(longitude=-112.0740, latitude=33.4484)),  # Phoenix, AZ
    ("America/Anchorage", Geolocation(longitude=-149.9003, latitude=61.2181)),  # Anchorage, AK
    ("America/Detroit", Geolocation(longitude=-83.0458, latitude=42.3314)),  # Detroit, MI
    ("America/Indianapolis", Geolocation(longitude=-86.1581, latitude=39.7684)),  # Indianapolis, IN
    ("America/Boise", Geolocation(longitude=-116.2023, latitude=43.6150)),  # Boise, ID
]

REFERERS = ["https://www.google.com", "https://www.bing.com", "https://www.yahoo.com/"]

ACCEPT_LANGUAGES = ["en-US,en;q=0.9", "en-GB,en;q=0.9", "fr-FR,fr;q=0.9"]

PROXIES = [
    {
        "server": "brd.superproxy.io:33335",
        "username": "brd-customer-hl_8ce11ce5-zone-residential_proxy1",
        "password": "1xjzwjp4xy8s",
    }
]

BASIC_QUERY = """
    name
    profile_pic (This is located in a <img> tag with width 200 and height 200)
    headline
    location
    about
"""
EXP_QUERY = """
    experiences[] {
        title
        company
        work_type
        start_date
        end_date
        location
        description
    }
"""

EDU_QUERY = """
    educations[] {
        school
        degree
        major
        start_date
        end_date
        description
    }
"""

PROJ_QUERY = """
    projects[] {
        project_name
        start_date
        end_date
        description
    }
"""

CERT_QUERY = """
    certifications[] {
        certificate_name
        issued_by
        issue_date
        exp_date
    }
"""

URL_CSV_PATH = "merged_urls.csv"
OUTPUT_JSON_PATH = "profile_data_6.json"

urls = []
with open(URL_CSV_PATH, newline='') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        urls.append(row[0])

testing_urls = urls[111: 154]

def create_context(browser):
    user_agent = random.choice(USER_AGENTS)
    header_dnt = random.choice(["0", "1"])
    location = random.choice(LOCATIONS)
    referer = random.choice(REFERERS)
    accept_language = random.choice(ACCEPT_LANGUAGES)
    proxy = random.choice(PROXIES) if PROXIES else None
    context = browser.new_context(
        locale="en-US, en, ru",
        timezone_id=location[0],
        extra_http_headers={
        "Accept-Language": accept_language,
        "Referer": referer,
        "DNT": header_dnt,
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
    },
    geolocation=location[1],
    user_agent=user_agent,
    permissions=["notifications"],
    viewport={
        "width": 1920 + random.randint(-50, 50),
        "height": 1080 + random.randint(-50, 50),
    }
    )
    return context

def random_mouse_movement(page):
    for _ in range(10):
        page.mouse.move(random.randint(0, 1000), random.randint(0, 1000))
        time.sleep(random.uniform(0.1, 0.5))
        
def random_scroll(page):
    page.mouse.wheel(0, 1000)
    time.sleep(random.uniform(0.1, 0.5))

def query_show_all_data(page, show_all_button, query, profile_data_dict, url):
    show_all_button.click()
    random_scroll(page)
    random_mouse_movement(page)
    random_mouse_movement(page)
    random_scroll(page)
    page.wait_for_page_ready_state()
    query = f"""{{
        {query}
    }}"""
    data = page.query_data(query)
    profile_data_dict.update(data)
    
    page.goto(url)
    page.wait_for_timeout(3000)

    return True

# def load_login_state(username, password):
#     with sync_playwright() as playwright, playwright.chromium.launch(headless=False, args=BROWSER_ARGS,
#     ignore_default_args=BROWSER_IGNORED_ARGS,) as browser:
        
#         page = agentql.wrap(browser.new_page())
        
#         # Login first
#         page.goto("https://www.linkedin.com/login")
#         username_input = page.get_by_prompt("Email or Phone Input")
#         username_input.type(username)
#         password_input = page.get_by_prompt("Password Input")
#         password_input.type(password)
#         page.get_by_prompt("Sign In Button").click()
#         page.wait_for_page_ready_state()
#         page.wait_for_timeout(5000)
#         browser.contexts[0].storage_state(path="login.json")
#         browser.close()

# load_login_state(username, password)

def login (browser, username, password):
    context = create_context(browser)
    page = agentql.wrap(context.new_page())
    # page.enable_stealth_mode()
    page.goto("https://www.linkedin.com/login")
    username_input = page.get_by_prompt("Email or Phone Input")
    username_input.type(username)
    password_input = page.get_by_prompt("Password Input")
    password_input.type(password)
    page.get_by_prompt("Sign In Button").click()
    page.wait_for_timeout(10000)
    return page

try: 
    all_profile_data = []
    
    with sync_playwright() as playwright, playwright.chromium.launch(headless=False, args=BROWSER_ARGS,
    ignore_default_args=BROWSER_IGNORED_ARGS,) as browser, open("accounts.json", "r") as f:
        accounts = json.load(f)
        total = 0
        for account in accounts:
            page = login(browser, account["username"], account["password"])
            print(f"Logged in as {account['username']}")
            for i in range(10):
                url = testing_urls[i + total]
                # context = create_context(browser)
                # page = agentql.wrap(context.new_page())
                # page.enable_stealth_mode()
            
                page.goto(url, timeout=60000)
                page.wait_for_timeout(5000)
                random_mouse_movement(page)
                random_scroll(page)
                show_more_exp, show_more_edu, show_more_proj, show_more_cert = False, False, False, False
                profile_data = {}
                
                # parse work history info
                show_all_exp_button = page.locator(f"//a[starts-with(@href, '{url}/details/experience')]")
                if show_all_exp_button.count() == 1:
                    show_more_exp = query_show_all_data(page, show_all_exp_button, EXP_QUERY, profile_data, url)
                    
                # parse education info
                show_all_edu_button = page.locator(f"//a[starts-with(@href, '{url}/details/education')]")
                if show_all_edu_button.count() == 1:
                    show_more_edu = query_show_all_data(page, show_all_edu_button, EDU_QUERY, profile_data, url)

                # parse project info
                show_all_proj_button = page.locator(f"//a[starts-with(@href, '{url}/details/projects')]")
                if show_all_proj_button.count() == 1:
                    show_more_proj = query_show_all_data(page, show_all_proj_button, PROJ_QUERY, profile_data, url)

                # parse certification info
                show_all_cert_button = page.locator(f"//a[starts-with(@href, '{url}/details/certifications')]")
                if show_all_cert_button.count() == 1:
                    show_more_cert = query_show_all_data(page, show_all_cert_button, CERT_QUERY, profile_data, url)
        
                final_query = f"""{BASIC_QUERY}"""
                if not show_more_exp: final_query += EXP_QUERY
                if not show_more_edu: final_query += EDU_QUERY
                if not show_more_proj: final_query += PROJ_QUERY
                if not show_more_cert: final_query += CERT_QUERY
                final_query = f"""{{
                    {final_query}
                }}"""
                final_data = page.query_data(final_query)
                profile_data.update(final_data)
                profile_data['id'] = url
        
                all_profile_data.append(profile_data)
                
                print(f"Processed {url}")
            page.close()
            total += 10
            # Take a break after each batch
            time.sleep(5)
        browser.close()
    with open(OUTPUT_JSON_PATH, 'w') as f:
        json.dump(all_profile_data, f, indent=4)
    print(f"Finished. Processed {len(all_profile_data)} profiles")
except Exception as e:
    print(e)
    with open(OUTPUT_JSON_PATH, 'w') as f:
        json.dump(all_profile_data, f, indent=4)



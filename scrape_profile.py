import agentql
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import asyncio
import time



with sync_playwright() as playwright, playwright.chromium.launch(headless=False) as browser:
    page = agentql.wrap(browser.new_page())
    page.goto("https://www.linkedin.com/login")
    
    username = page.get_by_prompt("Email or Phone Input")
    username.type("ym931511210@gmail.com")
    password = page.get_by_prompt("Password Input")
    password.type("Myh1101.")
    page.get_by_prompt("Sign In Button").click()
    page.wait_for_timeout(5000)
    page.goto("https://www.linkedin.com/in/yihaomai/")
    page.wait_for_timeout(3000)

    basic, work, edu, proj = {}, {}, {}, {}

    # parse basic info

    # parse work history info

    # parse education info
    show_all_edu_button = page.locator("//a[starts-with(@href, 'https://www.linkedin.com/in/yihaomai/details/education')]")
    print(show_all_edu_button)
    if show_all_edu_button.is_visible():
        show_all_edu_button.click()
        page.wait_for_timeout(3000)
        # parse education info        
        page.goto("https://www.linkedin.com/in/yihaomai/")

    # parse project info


    input("Press Enter to close the browser...")
    browser.close()

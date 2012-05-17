# Set up Offices
__all__ = ["org010"]
# Selenium WebDriver
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
#from selenium.webdriver.common.keys import Keys
from gluon import current
from s3 import s3_debug
from tests import *

def org010():
    """
    1. Log in as admin
    2. Give test user org admin rights over default domain (Timor-Leste)
    3. Give user margarida.martins@redcross.tl some access on Timor-Leste
    4. Log in as test user
    5. Revoke all access for margarida.martins@redcross.tl on Timor-Leste
    """
    config = current.test_config
    browser = config.browser
    driver = browser

    #homepage()
    login(account='admin')

    # Manage the system roles for Test User
    driver.find_element_by_link_text("Administration").click()
    driver.find_element_by_link_text("Manage Users & Roles").click()

    # Go to the next page of the list
    driver.find_element_by_xpath("//a[@id='list_next']").click()
    driver.find_element_by_xpath("//a[@href='/eden/admin/user/25/roles']").click()

    # Give org admin rights to Test User on Timor-Leste Red Cross Society
    driver.find_element_by_xpath("//select[@name='group_id']/option[@value='6']").click()
    driver.find_element_by_xpath("//select[@name='pe_id']/optgroup[2]/option[@value='77']").click()
    driver.find_element_by_xpath("//select[@name='pe_id']/optgroup[2]/option[@value='77']").submit()
    
    # Go to the organisation list
    driver.find_element_by_link_text("Organizations").click()
    driver.find_element_by_link_text("List Organizations").click()

    # Go to the next page of the list
    driver.find_element_by_xpath("//a[@id='list_next']").click()

    # Select Timor-Leste from the list
    driver.find_element_by_xpath("//a[@href='/eden/org/organisation/35/update']").click()

    # Go to the organisations' User Roles tab
    driver.find_element_by_link_text("User Roles").click()

    # Select a user from the drop-down list
    driver.find_element_by_xpath("//select[@name='user']/option[@value='4']").click()
    driver.find_element_by_xpath("//select[@name='user']/option[@value='4']").submit()
    
    # Set some new access levels
    driver.find_element_by_id('role_volvol_read').click()
    driver.find_element_by_id('role_projectproject_data_entry').click()
    driver.find_element_by_id('role_projectproject_data_entry').submit()

    # Log out the admin user
    logout()

    # Log in as test user
    login()

    # Go to the organisation list
    driver.find_element_by_link_text("Organizations").click()
    driver.find_element_by_link_text("List Organizations").click()

    # Go to the next page of the list
    driver.find_element_by_xpath("//a[@id='list_next']").click()

    # Select Timor-Leste from the list
    driver.find_element_by_xpath("//a[@href='/eden/org/organisation/35']").click()

    # Go to the organisations' User Roles tab
    driver.find_element_by_link_text("User Roles").click()

    # Select a user from the drop-down list
    driver.find_element_by_xpath("//select[@name='user']/option[@value='4']").click()
    driver.find_element_by_xpath("//select[@name='user']/option[@value='4']").submit()

    # Reset those access levels back to None
    driver.find_element_by_id('role_volNone').click()
    driver.find_element_by_id('role_projectNone').click()
    driver.find_element_by_id('role_projectNone').submit()

    # Logout
    logout()
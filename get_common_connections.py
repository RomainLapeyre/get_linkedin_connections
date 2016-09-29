from selenium import webdriver
import time
import pandas as pd
from collections import OrderedDict
from selenium.common.exceptions import NoSuchElementException
import csv
from collections import defaultdict


d = webdriver.Chrome()
employees = []
connections = []

email = "youremail@company.com"
password = "your linkedin password"


def linkedin_login(email, password):
    d.get('https://www.linkedin.com/nhome')
    d.find_elements_by_xpath("//input[@name='session_key']")[0].send_keys(email)
    d.find_elements_by_xpath("//input[@name='session_password']")[0].send_keys(password)
    d.find_element_by_id("login-submit").click()
    time.sleep(4)
    print("We're connected")


def company_connections_url(company):
    # Make sure the company name doesn't break the query
    company = company.replace(" ", "%20")

    # 2nd degree connections currently at this company
    url = "https://www.linkedin.com/vsearch/p?company=" + company + \
          "&openAdvancedForm=true&companyScope=C&locationType=Y&f_N=S&rsid=2290651101464384368834&orig=MDYS"
    return url


def get_shared_connection(current_html, person, company):
    # Note: an optimization could be to get more than 3 common connections

    current_html.find_element_by_class_name("shared-conn-expando").click()
    time.sleep(4)
    shared_connections = current_html.find_elements_by_class_name("small-result")

    for sc in shared_connections:
        connection = OrderedDict()
        bd = sc.find_element_by_class_name("bd")
        connection['connection.name'] = bd.find_element_by_tag_name("a").text
        connection['connection.degree'] = sc.find_element_by_class_name("degree-icon").text
        connection['connection.title'] = sc.find_element_by_class_name("headline").text
        connection['connection.linkedin_url'] = sc.find_element_by_tag_name("a").get_attribute('href').split("&", 1)[0]
        connection['employee.name'] = person['name']
        connection['employee.company'] = company
        connection['employee.title'] = person['title']
        connection['employee.linkedin_url'] = person['linkedin_url']
        connections.append(connection)


def profile_list_details(url, company):
    d.get(url)
    time.sleep(4)
    try:
        d.find_element_by_class_name("search-results")
    except NoSuchElementException:
        print("There's no common connection for this company:", company)
        print("Error message is:", NoSuchElementException)
        return
    list = d.find_element_by_class_name("search-results")
    people = list.find_elements_by_class_name("people")
    for p in people:
        person = OrderedDict()
        person['company'] = company
        person['name'] = p.find_element_by_class_name("main-headline").text
        person['degree'] = p.find_element_by_class_name("degree-icon").text
        person['title'] = p.find_element_by_class_name("description").text
        person['linkedin_url'] = p.find_element_by_class_name("main-headline").get_attribute('href').split("&", 1)[0]
        employees.append(person)

        get_shared_connection(p, person, company)



def scrape(companies):
    linkedin_login(email, password)

    for company in companies:
        company_url = company_connections_url(company)
        profile_list_details(company_url, company)
        print("—————")
        print ("done with:", company)
        time.sleep(3)
    pd.DataFrame(employees).to_csv('employees.csv')
    pd.DataFrame(connections).to_csv('connections.csv')


# Import company list from a csv with a header row "Company Name"
companies = defaultdict(list) # each value in each column is appended to a list
with open('companies.csv') as f:
    reader = csv.DictReader(f) # read rows into a dictionary format
    for row in reader: # read a row as {column1: value1, column2: value2,...}
        for (k,v) in row.items(): # go over each column name and value
            companies[k].append(v) # append the value into the appropriate list
                                 # based on column name k
    companies = companies['Company Name'] # remove the head row

scrape(companies)

# Work to do
# - Orderdict is ordering by alphabetical order. We want our own order
# - Get 1st name & last name from names
# - Get sex of names to adapt wording


# Close the browser once it's done
time.sleep(10)
d.close()


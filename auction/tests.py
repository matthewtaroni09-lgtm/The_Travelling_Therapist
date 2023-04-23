from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Create your tests here.
class PlayerFormTest(LiveServerTestCase):

  def testform(self):
    selenium = webdriver.Chrome()
    #Choose your url to visit
    selenium.get('http://127.0.0.1:8000/login')
    #find the elements you need to submit form
    username = selenium.find_element("id", 'username')
    password = selenium.find_element("id", 'password')

    submit = selenium.find_element("id", 'submitButton')

    #populate the form with data
    username.send_keys('jim@jim.com')
    password.send_keys('Ontario2')

    #submit form
    submit.send_keys(Keys.RETURN)

    #check result; page source looks at entire html document
    # assert 'Jim' in selenium.page_source
    heading = selenium.find_element("id", 'welcomeClinicHeading').text
    print(heading)
    self.assertEqual(heading, "Welcoime, Jim's Clinic")
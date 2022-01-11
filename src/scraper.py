from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class Ticket:
    SINGLE = 1
    RETURN = 2
    ARRIVE_BEFORE = 1
    DEPART_AFTER = 2


class TheTrainLine:

    # provide apis to TheTrainLine website
    def __init__(self):
        service = Service('../resources/chromedriver')
        self.driver = webdriver.Chrome(service=service)
        self.driver.get("https://www.thetrainline.com")

        # wait for accept cookies popup and click on accept
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
        # accept cookies on the page
        self.driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()

    def __del__(self):
        self.driver.quit()
        sleep(1)

    @staticmethod
    def round_to_15(tempus):
        mins = ((tempus.minute + 7) // 15) * 15
        return datetime(tempus.year, tempus.month, tempus.day, tempus.hour, 0) + timedelta(minutes=mins)

    def get_ticket(self, from_station, to_station, outward_time, adults=1, children=0,
                   inbound_time=None, outward_time_type=Ticket.ARRIVE_BEFORE,
                   inbound_time_type=Ticket.ARRIVE_BEFORE, ticket_type=Ticket.SINGLE):

        self.driver.get("https://www.thetrainline.com")

        outward_time = TheTrainLine.round_to_15(outward_time)  # only accepts 15-minute intervals
        if inbound_time:
            inbound_time = TheTrainLine.round_to_15(inbound_time)  # only accepts 15-minute intervals

        # what is the starting station

        from_box = self.driver.find_element(By.ID, 'from.search')
        from_box.send_keys(Keys.SHIFT, Keys.ARROW_UP)
        from_box.send_keys(Keys.DELETE)
        from_box.send_keys(from_station)

        # what is the destination
        to_box = self.driver.find_element(By.ID, 'to.search')
        to_box.send_keys(Keys.SHIFT, Keys.ARROW_UP)
        to_box.send_keys(Keys.DELETE)
        to_box.send_keys(to_station)

        if ticket_type == Ticket.SINGLE:
            button = self.driver.find_element(By.ID, 'single')
        else:
            button = self.driver.find_element(By.ID, 'return')
        button.click()

        outbound_element = self.driver.find_element(By.ID, 'page.journeySearchForm.outbound.title')
        outbound_element.send_keys(Keys.SHIFT, Keys.ARROW_UP)
        outbound_element.send_keys(Keys.DELETE)
        outbound_element.send_keys(outward_time.strftime('%d-%m-%y'))  # needs to be correct format
        outbound_element.send_keys(Keys.RETURN)

        # choosing leave by or arrive by time
        out_leave_or_arrive = Select(self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/main/div[2]/div["
                                                                        "4]/div/div/div[1]/section/form/div["
                                                                        "3]/fieldset[1]/div[3]/div/select"))

        if outward_time_type == Ticket.DEPART_AFTER:
            out_leave_or_arrive.select_by_value('departAfter')
        else:
            out_leave_or_arrive.select_by_value('arriveBefore')

        # select the hour of time
        out_hour = Select(
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/main/div[2]/div[4]/div/div/div['
                                               '1]/section/form/div[3]/fieldset[1]/div[4]/div[1]/select'))
        out_hour.select_by_value(outward_time.strftime('%H'))

        # select minutes of time
        out_min = Select(
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/main/div[2]/div[4]/div/div/div['
                                               '1]/section/form/div[3]/fieldset[1]/div[4]/div[2]/select'))
        out_min.select_by_value(outward_time.strftime('%M'))

        if inbound_time:
            # inbound date
            inbound_element = self.driver.find_element(By.ID, 'page.journeySearchForm.inbound.title')
            inbound_element.send_keys(Keys.SHIFT, Keys.ARROW_UP)
            inbound_element.send_keys(Keys.DELETE)
            inbound_element.send_keys(inbound_time.strftime('%d-%m-%y'))  # need date format for this field
            inbound_element.send_keys(Keys.RETURN)

            # choosing leave by or arrive by time
            in_leave_or_arrive = Select(
                self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/main/div[2]/div['
                                                   '4]/div/div/div[1]/section/form/div[3]/fieldset[2]/div['
                                                   '3]/div/select'))

            if inbound_time_type == Ticket.DEPART_AFTER:
                in_leave_or_arrive.select_by_value('departAfter')
            else:
                in_leave_or_arrive.select_by_value('arriveBefore')

            # select the hour of time
            in_hour = Select(
                self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/main/div[2]/div[4]/div/div/div['
                                                   '1]/section/form/div[3]/fieldset[2]/div[4]/div[1]/select'))
            in_hour.select_by_value(inbound_time.strftime('%H'))

            # select minutes of time
            in_min = Select(
                self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/main/div[2]/div[4]/div/div/div['
                                                   '1]/section/form/div[3]/fieldset[2]/div[4]/div[2]/select'))
            in_min.select_by_value(inbound_time.strftime('%M'))

        # enter number of adults and children in journey
        self.driver.find_element(By.ID, 'passenger-summary-btn').click()
        adults_element = Select(
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/main/div[2]/div[4]/div/div/div['
                                               '1]/section/form/div[4]/div/div/div/div[1]/div/div/select'))
        adults_element.select_by_value(str(adults))

        children_element = Select(
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/main/div[2]/div[4]/div/div/div['
                                               '1]/section/form/div[4]/div/div/div/div[2]/div[1]/div/select'))
        children_element.select_by_value(str(children))

        self.driver.find_element(By.XPATH,
                                 '/html/body/div[2]/div/div[2]/main/div[2]/div[4]/div/div/div[1]/section/form/div['
                                 '4]/div/div/button').click()

        sleep(0.5)  # sleep to make sure all data has been entered
        self.driver.find_element(By.XPATH,
                                 '/html/body/div[2]/div/div[2]/main/div[2]/div[4]/div/div/div[1]/section/form/div['
                                 '5]/button').click()  # submit travel details to find cheapest price

        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='the cheapest fare']")))
        # driver.find_element(By.CLASS_NAME, '_hsf37jx').click()  # if popup

        # find cheapest ticket label to print cheapest ticket and page url
        cheapest_ticket = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='the cheapest fare']").text

        return float(cheapest_ticket[1:]), self.driver.current_url


if __name__ == '__main__':
    trainline = TheTrainLine()

    #   trainline.getTicket('milton keynes central', 'norwich', datetime.now())
    cost, url = trainline.get_ticket('milton keynes central', 'norwich', datetime.now(),
                                     inbound_time=datetime.now() + timedelta(days=2),
                                     ticket_type=Ticket.RETURN)
    trainline = TheTrainLine()
    print(f"Cheapest ticket: £{cost}")
    print(f"Buy ticket: {url}")

    cost, url = trainline.get_ticket('milton keynes central', 'london euston', datetime.now(),
                                     inbound_time=datetime.now() + timedelta(days=2),
                                     ticket_type=Ticket.RETURN)

    trainline = TheTrainLine()
    print(f"Cheapest ticket: £{cost}")
    print(f"Buy ticket: {url}")

    cost, url = trainline.get_ticket("Norwich", "Southampton", adults=2, children=0, outward_time_type=Ticket.DEPART_AFTER,
                                     outward_time=datetime.now() + timedelta(days=4), ticket_type=Ticket.SINGLE)
    print(f"Cheapest ticket: £{cost}")
    print(f"Buy ticket: {url}")

    del trainline

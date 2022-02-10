from experta import *

from NLP.nlpu import *
from scraper import *
from partTwoHighLevel import *
import Chat.Helper as h

# Knowledge Engine
class KEngine(KnowledgeEngine):

    # Initialiser method for the engine, which also takes in the UI so that the PyQT GUI can be run from here
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.input_data = ""

    # Write method to publish a message to the PYQT UI
    def write(self, message):
        self.ui.send_message("Bot", message)

    # Prompt method to write a message to PYQT
    # It'll write, then wait and check every second to see if the input has been updated
    def prompt(self, message):
        self.write(message)
        while True:
            if self.input_data == "":
                sleep(1)
            else:
                response = self.input_data
                self.input_data = ""
                return response

    # Helper method to set the input data string
    def set_input(self, i):
        self.input_data = i

    # Function to define the inital facts, which is only the greeting state, but can be used for other things if restarting from a partial state
    @DefFacts()
    def _initial_action(self):
        yield Fact(state="greeting")

        # Debug stuff
        # yield Fact(origin_station="Norwich")
        # yield Fact(destination_station="London")
        # yield Fact(leave_time="Monday")
        #
        # yield Fact(ticket_type="return")
        # yield Fact(return_time="Friday")  # N/A
        #
        # yield Fact(adult_count="1")
        # yield Fact(children_count="1")

    # Initial method asking how can the bot help, will always run first
    @Rule(Fact(state='greeting'))
    def ask_how_can_help(self):
        # Now timestamp to record when the questions started, used for time comparisons
        self.declare(Fact(now=pd.Timestamp(datetime.now()).ceil("1min").to_pydatetime()))

        q = h.helper_input(self,"How can I help you? ")
        data = parse_query(q)

        # Loop while we don't understand what the user is asking (booking/delay)
        while data["query type"] == "unknown":
            data = parse_query(h.helper_input(self,"I didn't understand, if you want to book a ticket, use words like \"book\" or \"ticket\". If you'd like to predict a delay, use words like \"delay\" or \"predict\". "))

        # Cheapest ticket booking query
        if data["query type"] == "cheapest":

            # If the data exists, set
            if data["from"] is not None:
                self.declare(Fact(origin_station=data["from"]))

            if data["to"] is not None:
                self.declare(Fact(destination_station=data["to"]))

            if data["time"] is not None:
                self.declare(Fact(leave_time=data["time"]))
            self.declare(Fact(ticket_type=data["type"]))
            self.declare(Fact(adult_count=str(data["adult"])))
            self.declare(Fact(children_count=str(data["child"])))

            # Depending on the boolean value, we associate the correct Ticket value
            self.declare(Fact(leave_time_type=Ticket.DEPART_AFTER if data['arrive'] == False else Ticket.ARRIVE_BEFORE))
            self.declare(Fact(return_time_type=Ticket.DEPART_AFTER if data['arrive'] == False else Ticket.ARRIVE_BEFORE))

            if data["return_time"] is not None:
                self.declare(Fact(return_time=data["return_time"]))

            # Set the state to queue the booking questions
            self.modify(self.facts[self.__find_fact("state")], state="booking")

        # Prediction query
        elif data["query type"] == "prediction":

            # Set the state to delay, for the prediction questions
            self.modify(self.facts[self.__find_fact("state")], state="delay")

            # If the data exists, set
            if data["from"] is not None:
                self.declare(Fact(current_station=data["from"]))
            if data["to"] is not None:
                self.declare(Fact(target_station=data["to"]))
            if data["delay"] is not None:
                self.declare(Fact(current_delay=data["delay"]))

    # Question to ask the origin station, if it hasn't been asked already
    @Rule(Fact(state="booking"), NOT(Fact(origin_station=W())))
    def ask_origin_station(self):
        self.declare(Fact(origin_station=h.helper_input(self,"Where are you travelling from? ")))

    # Validate and check the origin station, calls another function. Will run if the origin station has been set, and isn't a perfect match for  a known station
    @Rule(Fact(state="booking"), Fact(origin_station=MATCH.origin_station), TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] != 100))
    def check_origin_station(self, origin_station):
        self.__validate_station(origin_station, True)

    # Asks the destination station if it hasn't been asked
    @Rule(Fact(state="booking"), NOT(Fact(destination_station=W())))
    def ask_destination_station(self):
        self.declare(Fact(destination_station=h.helper_input(self,"Where would you like to go? ")))

    # Check the destination station if it has been set and fails validation
    @Rule(Fact(state="booking"), Fact(destination_station=MATCH.destination_station), TEST(lambda destination_station: get_matching_stations(destination_station)[0][-1] != 100))
    def check_destination_station(self, destination_station):
        self.__validate_station(destination_station, False)


    '''
    Validate station function, this will check for the matching stations.
    
    If there is a single matching stations it'll ask "Did you mean X?"
    
    if there are more matching stations, it'll present a list from which the user can choose from.
    
    Will call itself until the requirements have been met
    '''
    def __validate_station(self, station, leaving):
        message = "Which of these did you mean for where you are leaving from? " if leaving else "Which of these did you mean for where you want to go? "

        found = 0
        stations = get_matching_stations(station)

        for s in stations:
            if s[-1] >= 85:
                message += "\n " + str(found + 1) + ") " + s[0] + " (" + str(s[-1]) + "% match)"
                found += 1

        # Ask single did you mean?
        if found == 1:
            confirmation = h.helper_input(self,"Did you mean " + str(stations[0][0]) + "? ")

            if confirmation.lower() == "yes":  # TODO Add support for more answers
                if leaving:
                    self.modify(self.facts[self.__find_fact("origin_station")], origin_station=stations[0][0])
                else:
                    self.modify(self.facts[self.__find_fact("destination_station")], destination_station=stations[0][0])
            elif confirmation.lower() == "no":  # TODO Add support for more variations of no
                self.__validate_station(h.helper_input(self,"Can you double check the name of the station and tell me again? "), leaving)
            else:
                self.__validate_station(h.helper_input(self,"I didn't understand what you said, please could you double check the name of the station and tell me again? "), leaving)

            return
        # No matches found, so ask again
        elif found == 0:
            self.__validate_station(h.helper_input(self,"I'm not sure what station you meant. Can you double check the name of the station you are " + ("travelling from" if leaving else "going to") + " and tell me again? "), leaving)

            return

        # Display list response
        else:
            list_response = h.helper_input(self,message + "\n")

            if list_response.isnumeric() and int(list_response) <= found and stations[int(list_response) - 1][0] is not None:
                if leaving:
                    self.modify(self.facts[self.__find_fact("origin_station")], origin_station=stations[int(list_response) - 1][0])
                else:
                    self.modify(self.facts[self.__find_fact("destination_station")], destination_station=stations[int(list_response) - 1][0])
            else:
                local_stations = get_matching_stations(list_response)

                if local_stations[0][-1] == 100:
                    if leaving:
                        self.modify(self.facts[self.__find_fact("origin_station")], origin_station=local_stations[0][0])
                    else:
                        self.modify(self.facts[self.__find_fact("destination_station")], destination_station=local_stations[0][0])

                else:
                    self.__validate_station(list_response, leaving)

            return

    # Function to find the index of a fact by a given key. Will return -1 if not found
    def __find_fact(self, key):
        for f in self.facts:
            if key in self.facts[f].as_dict().keys():
                return f

        return -1

    # Ask if the user wants a single or return ticket. Will only run if it hasn't been asked, the origin station is set, and the origin station passes validation
    @Rule(Fact(state="booking"), NOT(Fact(ticket_type=W())), Fact(origin_station=MATCH.origin_station), TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100))
    def ask_ticket_type(self):
        self.declare(Fact(ticket_type=h.helper_input(self,"Would you like a single, or a return ticket? ")))

    # Confirm the ticket type, will only run if the ticket type has been set, but it isn't "return" or "single"
    @Rule(Fact(state="booking"), Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type != "return" and ticket_type != "single"))
    def check_ticket_type(self):
        self.__validate_ticket_type(h.helper_input(self,"I didn't understand, did you want a single, or a return ticket? "))

    # Function to check the ticket type. Will call itself again if it fails.
    def __validate_ticket_type(self, ticket_type):
        response = nlp(ticket_type)

        for token in response:
            if token.lemma_.lower() == "return":
                self.modify(self.facts[self.__find_fact("ticket_type")], ticket_type="return")
                return
            elif token.lemma_.lower() == "single":
                self.modify(self.facts[self.__find_fact("ticket_type")], ticket_type="single")
                return

        self.__validate_ticket_type(h.helper_input(self,"I didn't understand, did you want a single, or a return ticket? "))

    # Function to ask when the user wants to leave, will only run if it hasn't been asked, and the origin station is valid
    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          NOT(Fact(leave_time=W())),
          )
    def ask_leave_time(self, origin_station):
        self.declare(Fact(leave_time=extract_journey_time(nlp("leaving at " + h.helper_input(self,"When would you like to travel? "))[0])))

    # Function to check if the leave time is correct, will only run if it has been set, but fails validation. The origin station is also required to be validated.
    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(leave_time=MATCH.leave_time),
          TEST(lambda leave_time: validate_ticket_time(leave_time) == False)
          )
    def check_leave_time(self):
        self.__validate_ticket_time(h.helper_input(self,"I couldn't understand the time you wanted to leave. I'm looking for something like 18:00 21/01/2021, please tell me again? "), True)

    # Ask the leave time type, aka if the user wants to arrive by the specified time, or depart at the specified time.
    # Will only run if the origin station is valid, the destination station is valid, the two stations are different, the leave time is validated and in the future, and the question hasn't already been asked,
    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(destination_station=MATCH.destination_station),
          TEST(lambda destination_station: get_matching_stations(destination_station)[0][-1] == 100),
          TEST(lambda origin_station, destination_station: origin_station.lower() != destination_station.lower()),
          Fact(leave_time=MATCH.leave_time),
          TEST(lambda leave_time: validate_ticket_time(leave_time) == True),
          Fact(now=MATCH.now),
          TEST(lambda leave_time, now: leave_time > now),
          NOT(Fact(leave_time_type=W()))
          )
    def ask_leave_time_type(self, origin_station, destination_station, leave_time):
        leave_time_type = h.helper_input(self,"For your outbound journey from " + origin_station + " to " + destination_station + ", would you like to arrive by, or depart at " + format_tempus(leave_time) + "? ")

        failures = 0

        while leave_time_type != "arrive by" and leave_time_type != "depart at":
            failures = failures + 1

            if failures > 3:
                leave_time_type = h.helper_input(self,
                    "I didn't understand. For your outbound journey from " + origin_station + " to " + destination_station + ", would you like to arrive by, or depart at " + format_tempus(
                        leave_time) + "? (I'm looking for \"arrive by\" or \"depart at\") ")
            else:
                leave_time_type = h.helper_input(self,"I didn't understand. For your outbound journey from " + origin_station + " to " + destination_station + ", would you like to arrive by, or depart at " + format_tempus(leave_time) + "? ")

        if leave_time_type.lower() == "arrive by":
            self.declare(Fact(leave_time_type=Ticket.ARRIVE_BEFORE))
        elif leave_time_type.lower() == "depart at":
            self.declare(Fact(leave_time_type=Ticket.DEPART_AFTER))

    # Function to ask the return time type. Aka, if the user wanrs to arrive by, or depart at a time.
    # Will only run if the origin station is valid, the destination is valid, they aren't the same stations, the ticket time is a return, the return and leave times are valid and in the future, as well as  the return is after the leave, and hasn't already been asked.
    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(destination_station=MATCH.destination_station),
          TEST(lambda destination_station: get_matching_stations(destination_station)[0][-1] == 100),
          TEST(lambda origin_station, destination_station: origin_station.lower() != destination_station.lower()),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "return"),
          Fact(leave_time=MATCH.leave_time),
          Fact(return_time=MATCH.return_time),
          TEST(lambda return_time: validate_ticket_time(return_time) == True),
          TEST(lambda leave_time: validate_ticket_time(leave_time) == True),
          TEST(lambda leave_time, return_time: return_time > leave_time),
          Fact(now=MATCH.now),
          TEST(lambda return_time, now: return_time > now),
          TEST(lambda leave_time, now: leave_time > now),
          NOT(Fact(return_time_type=W()))
          )
    def ask_return_time_type(self, origin_station, destination_station, return_time):
        return_time_type = h.helper_input(self,
            "For your return journey from " + destination_station + " to " + origin_station + ", would you like to arrive by, or depart at " + format_tempus(
                return_time) + "? ")

        failures = 0

        while return_time_type != "arrive by" and return_time_type != "depart at":
            failures = failures + 1

            if failures > 3:
                return_time_type = h.helper_input(self,
                    "I didn't understand. For your return journey from " + destination_station + " to " + origin_station + ", would you like to arrive by, or depart at " + format_tempus(
                return_time) + "? (I'm looking for \"arrive by\" or \"depart at\") ")
            else:
                return_time_type = h.helper_input(self,
                    "I didn't understand. For your return journey from " + destination_station + " to " + origin_station + ", would you like to arrive by, or depart at " + format_tempus(
                        return_time) + "? ")

        if return_time_type.lower() == "arrive by":
            self.declare(Fact(return_time_type=Ticket.ARRIVE_BEFORE))
        elif return_time_type.lower() == "depart at":
            self.declare(Fact(return_time_type=Ticket.DEPART_AFTER))

    # Ask the return time, the origin must be valid, it must be a return journey, and not already been asked.
    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "return"),
          NOT(Fact(return_time=W()))
          )
    def ask_return_time(self, origin_station):
        self.declare(Fact(return_time=extract_journey_time(nlp("leaving at " + h.helper_input(self,"When would you like return to {0}? ".format(origin_station)))[0])))

    # Check the return time. Will only run if the origin is valid, the ticket is a return, and the return time is invalid.
    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "return"),
          Fact(return_time=MATCH.return_time),
          TEST(lambda return_time: validate_ticket_time(return_time) == False)
          )
    def check_return_time(self):
        self.__validate_ticket_time(h.helper_input(self,"I couldn't understand the time you wanted to return. I'm looking for something like 18:00 21/01/2021, please tell me again? "), False)

    # Validate a ticket time. Will keep asking until the time is valid
    def __validate_ticket_time(self, time, leaving):
        extracted_time = extract_journey_time(nlp("leaving at " + time)[0])

        if extracted_time is not None:
            if leaving:
                self.modify(self.facts[self.__find_fact("leave_time")], leave_time=extracted_time)
            else:
                self.modify(self.facts[self.__find_fact("return_time")], return_time=extracted_time)
        else:
            self.__validate_ticket_time(h.helper_input(self,"I couldn't understand when you wanted to " + ("leave" if leaving else "return") + ". I'm looking for something like 18:00 21/01/2021, please tell me again? "), leaving)

    # Ask how many adults are travelling. It won't stop running until the answer is valid.
    @Rule(Fact(state="booking"), NOT(Fact(adult_count=W())))
    def ask_adults_count(self):
        response = h.helper_input(self,"How many adults are traveling? ")

        while not response.isnumeric():
            response = h.helper_input(self,"I didn't understand, please give me a number, such as: 2, or 3")

        self.declare(Fact(adult_count=response))

    # Ask how many children are travelling. Will not end until the input is valid.
    @Rule(Fact(state="booking"), NOT(Fact(children_count=W())))
    def ask_children_count(self):
        response = h.helper_input(self,"How many children are traveling? ")

        while not response.isnumeric():
            response = h.helper_input(self,"I didn't understand, please give me a number, such as: 2, or 3")

        self.declare(Fact(children_count=response))

    # Verify tht the return is after the leave time. It must be a return, the two times must be valid, and the return must be before the leave, so the user can be prompted to re input the data
    @Rule(Fact(state="booking"),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "return"),
          Fact(leave_time=MATCH.leave_time),
          Fact(return_time=MATCH.return_time),
          TEST(lambda return_time: validate_ticket_time(return_time) == True),
          TEST(lambda leave_time: validate_ticket_time(leave_time) == True),
          TEST(lambda leave_time, return_time: return_time <= leave_time)
          )
    def check_return_after_leave(self):
        h.helper_print(self, "Your inbound trip should be after your outbound trip")

        self.retract(self.facts[self.__find_fact("leave_time")])
        self.retract(self.facts[self.__find_fact("return_time")])

    # Verify the return time is in the future, the return needs to be set, valid and in the past before being re-prompted for an answer.
    @Rule(Fact(state="booking"),
          Fact(return_time=MATCH.return_time),
          Fact(now=MATCH.now),
          TEST(lambda return_time: validate_ticket_time(return_time) == True),
          TEST(lambda return_time, now: return_time < now)
          )
    def check_return_in_future(self):
        h.helper_print(self, "Your inbound trip should be in the future")

        self.retract(self.facts[self.__find_fact("return_time")])

    # Verify the leave time is in the future, it must be set, valid but in the past before being prompted again for an answer
    @Rule(Fact(state="booking"),
          Fact(leave_time=MATCH.leave_time),
          Fact(now=MATCH.now),
          TEST(lambda leave_time: validate_ticket_time(leave_time) == True),
          TEST(lambda leave_time, now: leave_time < now)
          )
    def check_leave_in_future(self):
        h.helper_print(self, "Your outbound trip should be in the future")

        self.retract(self.facts[self.__find_fact("leave_time")])

    # Function to ask for the stations again. Will run if they are both valid, but are equal to each other
    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(destination_station=MATCH.destination_station),
          TEST(lambda destination_station: get_matching_stations(destination_station)[0][-1] == 100),
          TEST(lambda origin_station, destination_station: origin_station.lower() == destination_station.lower())
          )
    def check_origin_equals_destination(self):
        h.helper_print(self, "You can't go to the same station you left from")

        self.retract(self.facts[self.__find_fact("origin_station")])
        self.retract(self.facts[self.__find_fact("destination_station")])

    # Function to check the total tickets are at least 1, if they are not it will ask the user to input the numbers again.
    @Rule(Fact(state="booking"),
          Fact(adult_count=MATCH.adult_count),
          Fact(children_count=MATCH.children_count),
          TEST(lambda adult_count, children_count: (int(adult_count) + int(children_count)) < 1)
          )
    def check_total_tickets_above_one(self):
        h.helper_print(self, "The sum of adult and children tickets must be at least 1")

        self.retract(self.facts[self.__find_fact("children_count")])
        self.retract(self.facts[self.__find_fact("adult_count")])

    '''
    Asks the user for confirmation of a single ticket.
    Must be:
        Origin valid
        Destination valid
        Origin different to return
        Ticket type is a single
        Have a valid leave time
        The leave time is in the future
        There is at least one ticket between the adults and children
        The ticket time type is valid.
    '''
    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(destination_station=MATCH.destination_station),
          TEST(lambda destination_station: get_matching_stations(destination_station)[0][-1] == 100),
          TEST(lambda origin_station, destination_station: origin_station.lower() != destination_station.lower()),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "single"),
          Fact(leave_time=MATCH.leave_time),
          TEST(lambda leave_time: validate_ticket_time(leave_time) == True),
          Fact(now=MATCH.now),
          TEST(lambda leave_time, now: leave_time > now),
          Fact(adult_count=MATCH.adult_count),
          Fact(children_count=MATCH.children_count),
          TEST(lambda adult_count, children_count: (int(adult_count) + int(children_count)) > 0),
          Fact(leave_time_type=MATCH.leave_time_type),
          TEST(lambda leave_time_type: leave_time_type==Ticket.ARRIVE_BEFORE or leave_time_type==Ticket.DEPART_AFTER)
          )
    def ask_confirmation(self, origin_station, destination_station, ticket_type, leave_time, adult_count, children_count, leave_time_type):
        self.run_confirmation(origin_station, destination_station, ticket_type, leave_time, "N/A", adult_count, children_count, leave_time_type, "N/A")

    '''
        Asks the user for confirmation of a return ticket.
        Will verify:
            Origin must be valid
            Destination must be valid
            The origin must be different to the desination
            The ticket must be a return
            The leave and return times must be valid
            The return must be after the leave time
            The return and leave must be in the future
            There must be at least one ticket between the adults and children
            The leave and return time types must be valid
    '''
    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(destination_station=MATCH.destination_station),
          TEST(lambda destination_station: get_matching_stations(destination_station)[0][-1] == 100),
          TEST(lambda origin_station, destination_station: origin_station.lower() != destination_station.lower()),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "return"),
          Fact(leave_time=MATCH.leave_time),
          Fact(return_time=MATCH.return_time),
          TEST(lambda return_time: validate_ticket_time(return_time) == True),
          TEST(lambda leave_time: validate_ticket_time(leave_time) == True),
          TEST(lambda leave_time, return_time: return_time > leave_time),
          Fact(now=MATCH.now),
          TEST(lambda return_time, now: return_time > now),
          TEST(lambda leave_time, now: leave_time > now),
          Fact(adult_count=MATCH.adult_count),
          Fact(children_count=MATCH.children_count),
          TEST(lambda adult_count, children_count: (int(adult_count) + int(children_count)) > 0),
          Fact(leave_time_type=MATCH.leave_time_type),
          TEST(lambda leave_time_type: leave_time_type == Ticket.ARRIVE_BEFORE or leave_time_type == Ticket.DEPART_AFTER),
          Fact(return_time_type=MATCH.return_time_type),
          TEST(lambda return_time_type: return_time_type == Ticket.ARRIVE_BEFORE or return_time_type == Ticket.DEPART_AFTER)
          )
    def ask_confirmation_with_return(self, origin_station, destination_station, ticket_type, leave_time, return_time, adult_count, children_count, leave_time_type, return_time_type):
        self.run_confirmation(origin_station, destination_station, ticket_type, leave_time, return_time, adult_count, children_count, leave_time_type, return_time_type)

    # Asks how long is the train currently delayed by. Will keep asking until the response is valid
    @Rule(Fact(state="delay"), NOT(Fact(current_delay=W())))
    def delay_ask_delay(self):
        read_delay = input("How much is your train delayed so far by? ")
        while len(read_delay.split()) == 0:
            read_delay = input("How much is your train delayed so far by (I'm looking for something like \"6 minutes\")? ")

            if len(read_delay.split()) == 1:
                read_delay = read_delay + " minutes"

        self.declare(Fact(current_delay=extract_NUM(nlp(read_delay)[1])))

    # Asks where the person is currently at
    @Rule(Fact(state="delay"), NOT(Fact(current_station=W())))
    def delay_ask_current_station(self):
        self.declare(Fact(current_station=h.helper_input(self,"What station are you currently at? ")))

    # Validates the current station, if invalid.
    @Rule(Fact(state="delay"), Fact(current_station=MATCH.current_station),
          TEST(lambda current_station: get_matching_stations(current_station)[0][-1] != 100))
    def delay_check_current_station(self, current_station):
        self.__delay_validate_station(current_station, True)

    # Asks the user where they want the delay to be predicted at.
    @Rule(Fact(state="delay"), NOT(Fact(target_station=W())))
    def delay_ask_target_station(self):
        self.declare(Fact(target_station=h.helper_input(self,"What station would you like the delay to be predicted at? ")))

    # Runs the station validation if the target station is invalid.
    @Rule(Fact(state="delay"), Fact(target_station=MATCH.target_station),
          TEST(lambda target_station: get_matching_stations(target_station)[0][-1] != 100))
    def delay_check_target_station(self, target_station):
        self.__delay_validate_station(target_station, False)

    '''
        Validate station function, this will check for the matching stations.

        If there is a single matching stations it'll ask "Did you mean X?"

        if there are more matching stations, it'll present a list from which the user can choose from.

        Will call itself until the requirements have been met
        '''
    def __delay_validate_station(self, station, current):
        message = "Which of these did you mean for where you are currently? " if current else "Which of these did you mean for where you want the delay to be predicted at? "

        found = 0
        stations = get_matching_stations(station)

        for s in stations:
            if s[-1] >= 85:
                message += "\n " + str(found + 1) + ") " + s[0] + " (" + str(s[-1]) + "% match)"
                found += 1

        if found == 1:
            confirmation = h.helper_input(self,"Did you mean " + str(stations[0][0]) + "? ")

            if confirmation.lower() == "yes":  # TODO Add support for more answers
                if current:
                    self.modify(self.facts[self.__find_fact("current_station")], current_station=stations[0][0])
                else:
                    self.modify(self.facts[self.__find_fact("target_station")], target_station=stations[0][0])
            elif confirmation.lower() == "no":  # TODO Add support for more variations of no
                self.__delay_validate_station(h.helper_input(self,"Can you double check the name of the station and tell me again? "), current)
            else:
                self.__delay_validate_station(h.helper_input(self,"I didn't understand what you said, please could you double check the name of the station and tell me again? "), current)

            return

        elif found == 0:
            self.__delay_validate_station(h.helper_input(self,"I'm not sure what station you meant. Can you double check the name of the station you " + ("are currently at" if current else "want the delay to be predicted at") + " and tell me again? "), current)

            return
        else:
            list_response = h.helper_input(self,message + "\n")

            if list_response.isnumeric() and int(list_response) <= found and stations[int(list_response) - 1][0] is not None:
                if current:
                    self.modify(self.facts[self.__find_fact("current_station")], current_station=stations[int(list_response) - 1][0])
                else:
                    self.modify(self.facts[self.__find_fact("target_station")], target_station=stations[int(list_response) - 1][0])
            else:
                local_stations = get_matching_stations(list_response)

                if local_stations[0][-1] == 100:
                    if current:
                        self.modify(self.facts[self.__find_fact("current_station")], current_station=local_stations[0][0])
                    else:
                        self.modify(self.facts[self.__find_fact("target_station")], target_station=local_stations[0][0])

                else:
                    self.__delay_validate_station(list_response, current)

            return

    # Function to verify the origin isn't the same as the destination, will prompt them again if they are.
    @Rule(Fact(state="delay"),
          Fact(current_station=MATCH.current_station),
          TEST(lambda current_station: get_matching_stations(current_station)[0][-1] == 100),
          Fact(target_station=MATCH.target_station),
          TEST(lambda target_station: get_matching_stations(target_station)[0][-1] == 100),
          TEST(lambda current_station, target_station: current_station.lower() == target_station.lower())
          )
    def delay_check_origin_equals_destination(self):
        h.helper_print(self, "You can't predict the delay to and from the same station")

        self.retract(self.facts[self.__find_fact("current_station")])
        self.retract(self.facts[self.__find_fact("target_station")])

    # Verifies the station order. If they aren't correct, it will ask for them again.
    @Rule(Fact(state="delay"),
          Fact(current_station=MATCH.current_station),
          TEST(lambda current_station: get_matching_stations(current_station)[0][-1] == 100),
          Fact(target_station=MATCH.target_station),
          TEST(lambda target_station: get_matching_stations(target_station)[0][-1] == 100),
          TEST(lambda current_station, target_station: current_station.lower() != target_station.lower()),
          TEST(lambda current_station, target_station: verify_station_order(station_map[current_station.lower()], station_map[target_station.lower()]) == False)
          )
    def delay_check_station_order(self):
        h.helper_print(self, "The stations you have chosen are either not on the same line, or are in the wrong order")

        self.retract(self.facts[self.__find_fact("current_station")])
        self.retract(self.facts[self.__find_fact("target_station")])

    def ask_if_user_is_finished(self):
        """
        Ask if the user wants to continue and ask another query
        """
        more = h.helper_input(self, "Can I help you with anything else? ")
        if more.lower() == "yes":  # if yes, reset
            self.reset()
            self.run()
        else:
            if more.lower() == "no":  # if no, end
                h.helper_print("Thanks! Have a great day!")
            else:  # else, unsure so end
                h.helper_print(
                    "I'm not sure what you meant. But if you need anything else just launch the window again!")

    @Rule(Fact(state="delay"),
          Fact(current_delay=MATCH.current_delay),
          Fact(current_station=MATCH.current_station),
          Fact(target_station=MATCH.target_station),
          TEST(lambda current_station: get_matching_stations(current_station)[0][-1] == 100),
          TEST(lambda target_station: get_matching_stations(target_station)[0][-1] == 100),
          TEST(lambda current_station, target_station: current_station.lower() != target_station.lower()),
          TEST(lambda current_station, target_station: verify_station_order(station_map[current_station.lower()],
                                                                            station_map[
                                                                                target_station.lower()]) == True)
          )
    def delay_send_delay_prediction(self, current_delay, current_station, target_station):
        """
        Print the prediction output

        Ask if the user want to do anything else with the chatbot
        """
        predicted_delay = predict(station_map[current_station.lower()], station_map[target_station.lower()],
                                  current_delay)

        h.helper_print(
            "Predicted delay at {0} from {1} when you are currently delayed by {2} will be {3}".format(target_station,
                                                                                                       current_station,
                                                                                                       str(current_delay) + " minutes",
                                                                                                       str(math.ceil(
                                                                                                           predicted_delay)) + " minutes"))

        self.ask_if_user_is_finished()

    def run_confirmation(self, origin_station, destination_station, ticket_type, leave_time, return_time, adult_count,
                         children_count, leave_time_type, return_time_type):
        """
        Print the output from the data into a more readable format
        Confirm that the facts gathered are correct
        If they are go and scrape
        Otherwise delete all the facts and start again asking specific questions
        """
        adult_num = int(adult_count)
        children_num = int(children_count)
        total_count = adult_num + children_num

        # Some complex conditional response building
        adult_string = adult_count + " adult" + ("s" if adult_num > 1 else "") if adult_num > 0 else ""
        children_string = children_count + " child" + ("ren" if children_num > 1 else "") if children_num > 0 else ""
        and_string = " and " if adult_num > 0 and children_num > 0 else ""
        ticket_string = ("a " if total_count == 1 else str(total_count) + " ") + (
            "return " if ticket_type == "return" else "") + "ticket" + (
                            "s for " + adult_string + and_string + children_string if total_count > 1 else "")

        return_string = "and returning " + (
            "by " if return_time_type == Ticket.ARRIVE_BEFORE else "at ") + format_tempus(
            return_time) if ticket_type == "return" else ""

        bot_message = "Awesome! I'm going to look for {0} from {1} to {2} {3} {4} {5}".format(
            ticket_string,
            origin_station,
            destination_station,
            "arriving by" if leave_time_type == Ticket.ARRIVE_BEFORE else "leaving at",
            format_tempus(leave_time),
            return_string)
        # print(bot_message)
        h.helper_print(bot_message)

        correct = h.helper_input(self, "Is that all correct? ")

        if correct.lower() == "no":  # TODO Add support for more variations of no
            h.helper_print(
                "Sorry about that! I'm going to ask you the questions again to make sure I get it right this time!")
            # this section deletes all of the found facts to start again asking specific questions
            try:
                self.retract(self.facts[self.__find_fact("origin_station")])
            except KeyError:
                pass

            try:
                self.retract(self.facts[self.__find_fact("destination_station")])
            except KeyError:
                pass

            try:
                self.retract(self.facts[self.__find_fact("ticket_type")])
            except KeyError:
                pass

            try:
                self.retract(self.facts[self.__find_fact("leave_time")])
            except KeyError:
                pass

            try:
                self.retract(self.facts[self.__find_fact("return_time")])
            except KeyError:
                pass

            try:
                self.retract(self.facts[self.__find_fact("adult_count")])
            except KeyError:
                pass

            try:
                self.retract(self.facts[self.__find_fact("children_count")])
            except KeyError:
                pass

            try:
                self.retract(self.facts[self.__find_fact("leave_time_type")])
            except KeyError:
                pass

            try:
                self.retract(self.facts[self.__find_fact("return_time_type")])
            except KeyError:
                pass
        else:
            if correct.lower() != "yes":  # input wasnt "yes" or "no" so the bot assumes that everything was correct and goes and scrapes. We assumed this because it isnt the end of the world if the user gets a ticket that isnt relivent
                h.helper_print("I'm not sure what you meant. So I'm going to assume everything is alright!")

            if correct.lower() == "yes":  # TODO Add support for more answers
                h.helper_print("Just finding your ticket. This may take a few moments...")
                trainline = TheTrainLine()  # init the scraper
                cost, url = trainline.get_ticket(origin_station,
                                                 destination_station,
                                                 leave_time,
                                                 adults=adult_num,
                                                 children=children_num,
                                                 inbound_time=return_time,
                                                 outward_time_type=leave_time_type,
                                                 inbound_time_type=return_time_type,
                                                 ticket_type=Ticket.RETURN) \
                    if ticket_type == "return" \
                    else trainline.get_ticket(origin_station,
                                              destination_station,
                                              leave_time,
                                              adults=adult_num,
                                              children=children_num,
                                              outward_time_type=leave_time_type,
                                              ticket_type=Ticket.SINGLE)
                h.helper_print(f"The cheapest ticket will cost £{cost} and can be purchased here: {url}")

                self.ask_if_user_is_finished()


def validate_ticket_time(time):  # validates the ticket time
    extracted_time = extract_journey_time(nlp("leaving at " + time)[0])  # extracts the time from the nlpu
    return extracted_time is not None


def format_tempus(tempus):
    return tempus.strftime("%H:%M %d/%m/%Y")


if __name__ == '__main__':
    engine = KEngine()

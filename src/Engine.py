from experta import *

from NLP.nlpu import *
from scraper import *
from partTwoHighLevel import *

# Knowledge Engine
class KEngine(KnowledgeEngine):

    def __init__(self):
        super().__init__()
        self.reset()
        self.run()

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

    @Rule(Fact(state='greeting'))
    def ask_how_can_help(self):
        self.declare(Fact(now=pd.Timestamp(datetime.now()).ceil("1min").to_pydatetime()))

        q = input("How can I help you? ")
        data = parse_query(q)

        while data["query type"] == "unknown":
            data = parse_query(input("I didn't understand, if you want to book a ticket, use words like \"book\" or \"ticket\". If you'd like to predict a delay, use words like \"delay\" or \"predict\". "))

        if data["query type"] == "cheapest":
            if data["from"] is not None:
                self.declare(Fact(origin_station=data["from"]))

            if data["to"] is not None:
                self.declare(Fact(destination_station=data["to"]))

            if data["time"] is not None:
                self.declare(Fact(leave_time=data["time"]))
            self.declare(Fact(ticket_type=data["type"]))
            self.declare(Fact(adult_count=str(data["adult"])))
            self.declare(Fact(children_count=str(data["child"])))
            self.declare(Fact(leave_time_type=Ticket.DEPART_AFTER if data['arrive'] == False else Ticket.ARRIVE_BEFORE))
            self.declare(Fact(return_time_type=Ticket.DEPART_AFTER if data['arrive'] == False else Ticket.ARRIVE_BEFORE))

            if data["return_time"] is not None:
                self.declare(Fact(return_time=data["return_time"]))

            self.modify(self.facts[self.__find_fact("state")], state="booking")
        elif data["query type"] == "prediction":
            self.modify(self.facts[self.__find_fact("state")], state="delay")

            if data["from"] is not None:
                self.declare(Fact(current_station=data["from"]))
            if data["to"] is not None:
                self.declare(Fact(target_station=data["to"]))
            if data["delay"] is not None:
                self.declare(Fact(current_delay=data["delay"]))

    @Rule(Fact(state="booking"), NOT(Fact(origin_station=W())))
    def ask_origin_station(self):
        self.declare(Fact(origin_station=input("Where are you travelling from? ")))

    @Rule(Fact(state="booking"), Fact(origin_station=MATCH.origin_station), TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] != 100))
    def check_origin_station(self, origin_station):
        self.__validate_station(origin_station, True)

    @Rule(Fact(state="booking"), NOT(Fact(destination_station=W())))
    def ask_destination_station(self):
        self.declare(Fact(destination_station=input("Where would you like to go? ")))

    @Rule(Fact(state="booking"), Fact(destination_station=MATCH.destination_station), TEST(lambda destination_station: get_matching_stations(destination_station)[0][-1] != 100))
    def check_destination_station(self, destination_station):
        self.__validate_station(destination_station, False)

    def __validate_station(self, station, leaving):
        message = "Which of these did you mean for where you are leaving from? " if leaving else "Which of these did you mean for where you want to go? "

        found = 0
        stations = get_matching_stations(station)

        for s in stations:
            if s[-1] >= 85:
                message += "\n " + str(found + 1) + ") " + s[0] + " (" + str(s[-1]) + "% match)"
                found += 1

        if found == 1:
            confirmation = input("Did you mean " + str(stations[0][0]) + "? ")

            if confirmation.lower() == "yes":  # TODO Add support for more answers
                if leaving:
                    self.modify(self.facts[self.__find_fact("origin_station")], origin_station=stations[0][0])
                else:
                    self.modify(self.facts[self.__find_fact("destination_station")], destination_station=stations[0][0])
            elif confirmation.lower() == "no":  # TODO Add support for more variations of no
                self.__validate_station(input("Can you double check the name of the station and tell me again? "), leaving)
            else:
                self.__validate_station(input("I didn't understand what you said, please could you double check the name of the station and tell me again? "), leaving)

            return

        elif found == 0:
            self.__validate_station(input("I'm not sure what station you meant. Can you double check the name of the station you are " + ("travelling from" if leaving else "going to") + " and tell me again? "), leaving)

            return
        else:
            list_response = input(message + "\n")

            if list_response.isnumeric() and stations[int(list_response) - 1][0] is not None:
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

    def __find_fact(self, key):
        for f in self.facts:
            if key in self.facts[f].as_dict().keys():
                return f

        return -1

    @Rule(Fact(state="booking"), NOT(Fact(ticket_type=W())), Fact(origin_station=MATCH.origin_station), TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100))
    def ask_ticket_type(self):
        self.declare(Fact(ticket_type=input("Would you like a single, or a return ticket? ")))

    @Rule(Fact(state="booking"), Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type != "return" and ticket_type != "single"))
    def check_ticket_type(self):
        self.__validate_ticket_type(input("I didn't understand, did you want a single, or a return ticket? "))

    def __validate_ticket_type(self, ticket_type):
        response = nlp(ticket_type)

        for token in response:
            if token.lemma_.lower() == "return":
                self.modify(self.facts[self.__find_fact("ticket_type")], ticket_type="return")
                return
            elif token.lemma_.lower() == "single":
                self.modify(self.facts[self.__find_fact("ticket_type")], ticket_type="single")
                return

        self.__validate_ticket_type(input("I didn't understand, did you want a single, or a return ticket? "))

    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          NOT(Fact(leave_time=W())),
          )
    def ask_leave_time(self, origin_station):
        self.declare(Fact(leave_time=extract_journey_time(nlp("leaving at " + input("Can you give me a time for the outbound journey? (I will clarify arrive by or depart at in a later question)"))[0])))

    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(leave_time=MATCH.leave_time),
          TEST(lambda leave_time: validate_ticket_time(format_tempus(leave_time)) == False)
          )
    def check_leave_time(self):
        self.__validate_ticket_time(input("I couldn't understand the time you wanted to leave. I'm looking for something like 18:00 21/01/2021, please tell me again? "), True)

    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(destination_station=MATCH.destination_station),
          TEST(lambda destination_station: get_matching_stations(destination_station)[0][-1] == 100),
          TEST(lambda origin_station, destination_station: origin_station.lower() != destination_station.lower()),
          Fact(leave_time=MATCH.leave_time),
          TEST(lambda leave_time: validate_ticket_time(format_tempus(leave_time)) == True),
          Fact(now=MATCH.now),
          TEST(lambda leave_time, now: leave_time > now),
          NOT(Fact(leave_time_type=W()))
          )
    def ask_leave_time_type(self, origin_station, destination_station, leave_time):
        leave_time_type = input("For your outbound journey from " + origin_station + " to " + destination_station + ", would you like to arrive by, or depart at " + format_tempus(leave_time) + "? ")

        failures = 0

        while leave_time_type != "arrive by" and leave_time_type != "depart at":
            failures = failures + 1

            if failures > 3:
                leave_time_type = input(
                    "I didn't understand. For your outbound journey from " + origin_station + " to " + destination_station + ", would you like to arrive by, or depart at " + format_tempus(
                        leave_time) + "? (I'm looking for \"arrive by\" or \"depart at\") ")
            else:
                leave_time_type = input("I didn't understand. For your outbound journey from " + origin_station + " to " + destination_station + ", would you like to arrive by, or depart at " + format_tempus(leave_time) + "? ")

        if leave_time_type.lower() == "arrive by":
            self.declare(Fact(leave_time_type=Ticket.ARRIVE_BEFORE))
        elif leave_time_type.lower() == "depart at":
            self.declare(Fact(leave_time_type=Ticket.DEPART_AFTER))

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
          TEST(lambda return_time: validate_ticket_time(format_tempus(return_time)) == True),
          TEST(lambda leave_time: validate_ticket_time(format_tempus(leave_time)) == True),
          TEST(lambda leave_time, return_time: return_time > leave_time),
          Fact(now=MATCH.now),
          TEST(lambda return_time, now: return_time > now),
          TEST(lambda leave_time, now: leave_time > now),
          NOT(Fact(return_time_type=W()))
          )
    def ask_return_time_type(self, origin_station, destination_station, return_time):
        return_time_type = input(
            "For your return journey from " + destination_station + " to " + origin_station + ", would you like to arrive by, or depart at " + format_tempus(
                return_time) + "? ")

        failures = 0

        while return_time_type != "arrive by" and return_time_type != "depart at":
            failures = failures + 1

            if failures > 3:
                return_time_type = input(
                    "I didn't understand. For your return journey from " + destination_station + " to " + origin_station + ", would you like to arrive by, or depart at " + format_tempus(
                return_time) + "? (I'm looking for \"arrive by\" or \"depart at\") ")
            else:
                return_time_type = input(
                    "I didn't understand. For your return journey from " + destination_station + " to " + origin_station + ", would you like to arrive by, or depart at " + format_tempus(
                        return_time) + "? ")

        if return_time_type.lower() == "arrive by":
            self.declare(Fact(return_time_type=Ticket.ARRIVE_BEFORE))
        elif return_time_type.lower() == "depart at":
            self.declare(Fact(return_time_type=Ticket.DEPART_AFTER))

    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "return"),
          NOT(Fact(return_time=W()))
          )
    def ask_return_time(self, origin_station):
        self.declare(Fact(return_time=extract_journey_time(nlp("leaving at " + input("When would you like return to %s? " % (origin_station)))[0])))

    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "return"),
          Fact(return_time=MATCH.return_time),
          TEST(lambda return_time: validate_ticket_time(format_tempus(return_time)) == False)
          )
    def check_return_time(self):
        self.__validate_ticket_time(input("I couldn't understand the time you wanted to return. I'm looking for something like 18:00 21/01/2021, please tell me again? "), False)

    def __validate_ticket_time(self, time, leaving):
        extracted_time = extract_journey_time(nlp("leaving at " + time)[0])

        if extracted_time is not None:
            if leaving:
                self.modify(self.facts[self.__find_fact("leave_time")], leave_time=extracted_time)
            else:
                self.modify(self.facts[self.__find_fact("return_time")], return_time=extracted_time)
        else:
            self.__validate_ticket_time(input("I couldn't understand when you wanted to " + ("leave" if leaving else "return") + ". I'm looking for something like 18:00 21/01/2021, please tell me again? "), leaving)

    @Rule(Fact(state="booking"), NOT(Fact(adult_count=W())))
    def ask_adults_count(self):
        response = input("How many adults are traveling? ")

        while not response.isnumeric():
            response = input("I didn't understand, please give me a number, such as: 2, or 3")

        self.declare(Fact(adult_count=response))

    @Rule(Fact(state="booking"), NOT(Fact(children_count=W())))
    def ask_children_count(self):
        response = input("How many children are traveling? ")

        while not response.isnumeric():
            response = input("I didn't understand, please give me a number, such as: 2, or 3")

        self.declare(Fact(children_count=response))

    @Rule(Fact(state="booking"),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "return"),
          Fact(leave_time=MATCH.leave_time),
          Fact(return_time=MATCH.return_time),
          TEST(lambda return_time: validate_ticket_time(format_tempus(return_time)) == True),
          TEST(lambda leave_time: validate_ticket_time(format_tempus(leave_time)) == True),
          TEST(lambda leave_time, return_time: return_time <= leave_time)
          )
    def check_return_after_leave(self):
        print("Your inbound trip should be after your outbound trip")

        self.retract(self.facts[self.__find_fact("leave_time")])
        self.retract(self.facts[self.__find_fact("return_time")])

    @Rule(Fact(state="booking"),
          Fact(return_time=MATCH.return_time),
          Fact(now=MATCH.now),
          TEST(lambda return_time: validate_ticket_time(format_tempus(return_time)) == True),
          TEST(lambda return_time, now: return_time < now)
          )
    def check_return_in_future(self):
        print("Your inbound trip should be in the future")

        self.retract(self.facts[self.__find_fact("return_time")])

    @Rule(Fact(state="booking"),
          Fact(leave_time=MATCH.leave_time),
          Fact(now=MATCH.now),
          TEST(lambda leave_time: validate_ticket_time(format_tempus(leave_time)) == True),
          TEST(lambda leave_time, now: leave_time < now)
          )
    def check_leave_in_future(self):
        print("Your outbound trip should be in the future")

        self.retract(self.facts[self.__find_fact("leave_time")])

    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(destination_station=MATCH.destination_station),
          TEST(lambda destination_station: get_matching_stations(destination_station)[0][-1] == 100),
          TEST(lambda origin_station, destination_station: origin_station.lower() == destination_station.lower())
          )
    def check_origin_equals_destination(self):
        print("You can't go to the same station you left from")

        self.retract(self.facts[self.__find_fact("origin_station")])
        self.retract(self.facts[self.__find_fact("destination_station")])

    @Rule(Fact(state="booking"),
          Fact(adult_count=MATCH.adult_count),
          Fact(children_count=MATCH.children_count),
          TEST(lambda adult_count, children_count: (int(adult_count) + int(children_count)) < 1)
          )
    def check_total_tickets_above_one(self):
        print("The sum of adult and children tickets must be at least 1")

        self.retract(self.facts[self.__find_fact("children_count")])
        self.retract(self.facts[self.__find_fact("adult_count")])

    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(destination_station=MATCH.destination_station),
          TEST(lambda destination_station: get_matching_stations(destination_station)[0][-1] == 100),
          TEST(lambda origin_station, destination_station: origin_station.lower() != destination_station.lower()),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "single"),
          Fact(leave_time=MATCH.leave_time),
          TEST(lambda leave_time: validate_ticket_time(format_tempus(leave_time)) == True),
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
          TEST(lambda return_time: validate_ticket_time(format_tempus(return_time)) == True),
          TEST(lambda leave_time: validate_ticket_time(format_tempus(leave_time)) == True),
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

    @Rule(Fact(state="delay"), NOT(Fact(current_delay=W())))
    def delay_ask_delay(self):
        self.declare(Fact(current_delay=extract_NUM(nlp(input("How much is your train delayed so far by? "))[1])))

    @Rule(Fact(state="delay"), NOT(Fact(current_station=W())))
    def delay_ask_current_station(self):
        self.declare(Fact(current_station=input("What station are you currently at? ")))

    @Rule(Fact(state="delay"), Fact(current_station=MATCH.current_station),
          TEST(lambda current_station: get_matching_stations(current_station)[0][-1] != 100))
    def delay_check_current_station(self, current_station):
        self.__delay_validate_station(current_station, True)

    @Rule(Fact(state="delay"), NOT(Fact(target_station=W())))
    def delay_ask_target_station(self):
        self.declare(Fact(target_station=input("What station would you like the delay to be predicted at? ")))

    @Rule(Fact(state="delay"), Fact(target_station=MATCH.target_station),
          TEST(lambda target_station: get_matching_stations(target_station)[0][-1] != 100))
    def delay_check_target_station(self, target_station):
        self.__delay_validate_station(target_station, False)

    def __delay_validate_station(self, station, current):
        message = "Which of these did you mean for where you are currently? " if current else "Which of these did you mean for where you want the delay to be predicted at? "

        found = 0
        stations = get_matching_stations(station)

        for s in stations:
            if s[-1] >= 85:
                message += "\n " + str(found + 1) + ") " + s[0] + " (" + str(s[-1]) + "% match)"
                found += 1

        if found == 1:
            confirmation = input("Did you mean " + str(stations[0][0]) + "? ")

            if confirmation.lower() == "yes":  # TODO Add support for more answers
                if current:
                    self.modify(self.facts[self.__find_fact("current_station")], current_station=stations[0][0])
                else:
                    self.modify(self.facts[self.__find_fact("target_station")], target_station=stations[0][0])
            elif confirmation.lower() == "no":  # TODO Add support for more variations of no
                self.__delay_validate_station(input("Can you double check the name of the station and tell me again? "), current)
            else:
                self.__delay_validate_station(input("I didn't understand what you said, please could you double check the name of the station and tell me again? "), current)

            return

        elif found == 0:
            self.__delay_validate_station(input("I'm not sure what station you meant. Can you double check the name of the station you " + ("are currently at" if current else "want the delay to be predicted at") + " and tell me again? "), current)

            return
        else:
            list_response = input(message + "\n")

            if list_response.isnumeric() and stations[int(list_response) - 1][0] is not None:
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

    @Rule(Fact(state="delay"),
          Fact(current_station=MATCH.current_station),
          TEST(lambda current_station: get_matching_stations(current_station)[0][-1] == 100),
          Fact(target_station=MATCH.target_station),
          TEST(lambda target_station: get_matching_stations(target_station)[0][-1] == 100),
          TEST(lambda current_station, target_station: current_station.lower() == target_station.lower())
          )
    def delay_check_origin_equals_destination(self):
        print("You can't predict the delay to and from the same station")

        self.retract(self.facts[self.__find_fact("current_station")])
        self.retract(self.facts[self.__find_fact("target_station")])

    @Rule(Fact(state="delay"),
          Fact(current_station=MATCH.current_station),
          TEST(lambda current_station: get_matching_stations(current_station)[0][-1] == 100),
          Fact(target_station=MATCH.target_station),
          TEST(lambda target_station: get_matching_stations(target_station)[0][-1] == 100),
          TEST(lambda current_station, target_station: current_station.lower() != target_station.lower()),
          TEST(lambda current_station, target_station: verify_station_order(station_map[current_station.lower()], station_map[target_station.lower()]) == False)
          )
    def delay_check_station_order(self):
        print("The stations you have chosen are either not on the same line, or are in the wrong order")

        self.retract(self.facts[self.__find_fact("current_station")])
        self.retract(self.facts[self.__find_fact("target_station")])

    @Rule(Fact(state="delay"),
          Fact(current_delay=MATCH.current_delay),
          Fact(current_station=MATCH.current_station),
          Fact(target_station=MATCH.target_station),
          TEST(lambda current_station: get_matching_stations(current_station)[0][-1] == 100),
          TEST(lambda target_station: get_matching_stations(target_station)[0][-1] == 100),
          TEST(lambda current_station, target_station: current_station.lower() != target_station.lower()),
          TEST(lambda current_station, target_station: verify_station_order(station_map[current_station.lower()], station_map[target_station.lower()]) == True)
          )
    def delay_send_delay_prediction(self, current_delay, current_station, target_station):
        predicted_delay = predict(station_map[current_station.lower()], station_map[target_station.lower()], current_delay)

        print("Predicted delay at %s from %s when you are currently delayed by %s will be %s" % (target_station, current_station, str(current_delay) + " minutes", str(predicted_delay) + " minutes"))

    def run_confirmation(self, origin_station, destination_station, ticket_type, leave_time, return_time, adult_count,
                         children_count, leave_time_type, return_time_type):
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

        print("Awesome! I'm going to look for %s from %s to %s %s %s %s" % (
            ticket_string, origin_station, destination_station,
            "arriving by" if leave_time_type == Ticket.ARRIVE_BEFORE else "leaving at", format_tempus(leave_time),
            return_string))

        correct = input("Is that all correct? ")

        if correct.lower() == "no":  # TODO Add support for more variations of no
            print("Sorry about that! I'm going to ask you the questions again to make sure I get it right this time!")

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
            if correct.lower() != "yes":
                print("I'm not sure what you meant. So I'm going to assume everything is alright!")

            if correct.lower() == "yes":  # TODO Add support for more answers
                trainline = TheTrainLine()
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
                print(f"The cheapest ticket will cost £{cost} and can be purchased here: {url}")


def validate_ticket_time(time):
    extracted_time = extract_journey_time(nlp("leaving at " + time)[0])

    return extracted_time is not None


def format_tempus(tempus):
    return tempus.strftime("%H:%M %d/%m/%Y")

if __name__ == '__main__':
    engine = KEngine()
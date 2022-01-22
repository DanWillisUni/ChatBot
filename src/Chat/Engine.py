from experta import *
from src.NLP.nlpu import *


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
        q = input("How can I help you? ")
        data = cheapest_ticket_query(q)

        if data["from"] is not None:
            self.declare(Fact(origin_station=data["from"]))

        if data["to"] is not None:
            self.declare(Fact(destination_station=data["to"]))

        self.declare(Fact(leave_time=data["time"]))
        self.declare(Fact(ticket_type=data["type"]))
        self.declare(Fact(adult_count=str(data["adult"])))
        self.declare(Fact(children_count=str(data["child"])))

        if data["return_time"] is not None:
            self.declare(Fact(return_time=data["return_time"]))

        self.modify(self.facts[1], state="booking")

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
        message = "Which of these did you mean for where you are leaving from?" if leaving else "Which of these did you mean for where you want to go?"

        found = 0
        stations = get_matching_stations(station)

        for s in stations:
            if s[-1] >= 85:
                message += "\n " + str(found + 1) + ") " + s[0] + " (" + str(s[-1]) + "%)"
                found += 1

        if found == 1:
            confirmation = input("Did you mean " + str(stations[0][0]) + "?")

            if confirmation.lower() == "yes":  # TODO Add support for more answers
                if leaving:
                    self.modify(self.facts[self.__find_fact("origin_station")], origin_station=stations[0][0])
                else:
                    self.modify(self.facts[self.__find_fact("destination_station")], destination_station=stations[0][0])
            elif confirmation.lower() == "no":  # TODO Add support for more variations of no
                self.__validate_station(input("Can you double check the name of the station and tell me again?"), leaving)
            else:
                self.__validate_station(input("I didn't understand what you said, please could you double check the name of the station and tell me again?"), leaving)

            return

        elif found == 0:
            self.__validate_station(input("I'm not sure what station you meant. Can you double check the name of the station you are " + ("travelling from" if leaving else "going to") + " and tell me again?"), leaving)

            return
        else:
            list_response = input(message)

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
        self.declare(Fact(leave_time=input("When would you like to leave %s? " % (origin_station))))

    # TODO Uncomment once date validation is done
    # @Rule(Fact(state="booking"),
    #       Fact(origin_station=MATCH.origin_station),
    #       TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
    #       Fact(leave_time=MATCH.leave_time),
    #       TEST(lambda leave_time: extract_journey_time(leave_time) is None)
    #       )
    # def check_leave_time(self):
    #     self.__validate_ticket_time("I couldn't understand the time you wanted to leave. Please tell me again?", True)

    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "return"),
          NOT(Fact(return_time=W()))
          )
    def ask_return_time(self, origin_station):
        self.declare(Fact(return_time=input("When would you like return to %s? " % (origin_station))))

    # @Rule(Fact(state="booking"),
    #       Fact(origin_station=MATCH.origin_station),
    #       TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
    #       Fact(ticket_type=MATCH.ticket_type),
    #       TEST(lambda ticket_type: ticket_type == "return"),
    #       Fact(return_time=MATCH.return_time),
    #       TEST(lambda return_time: extract_journey_time(return_time) is None)
    #       )
    # def check_return_time(self):
    #     self.__validate_ticket_time("I couldn't understand the time you wanted to return. Please tell me again?", False)

    def __validate_ticket_time(self, time, leaving):
        extracted_time = extract_journey_time(nlp(time))

        if extracted_time is not None:
            if leaving:
                self.modify(self.facts[self.__find_fact("leave_time")], leave_time=extracted_time)
            else:
                self.modify(self.facts[self.__find_fact("return_time")], return_time=extracted_time)
        else:
            self.__validate_ticket_time("I couldn't understand when you wanted to " + ("leave" if leaving else "return") + ". Please tell me again?")

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

    # TODO Ensure that the number of adults + children > 0
    # TODO Ensure that the leave time is before the return time
    # TODO Ensure that the destination and origin aren't the same place

    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(destination_station=MATCH.destination_station),
          TEST(lambda destination_station: get_matching_stations(destination_station)[0][-1] == 100),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "single"),
          Fact(leave_time=MATCH.leave_time),
          Fact(adult_count=MATCH.adult_count),
          Fact(children_count=MATCH.children_count)
          )
    def ask_confirmation(self, origin_station, destination_station, ticket_type, leave_time, adult_count, children_count):
        self.__run_confirmation(origin_station, destination_station, ticket_type, leave_time, "N/A", adult_count, children_count)

    # TODO Add some caching to the get matching stations function, it's called way to much to not cache results
    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          TEST(lambda origin_station: get_matching_stations(origin_station)[0][-1] == 100),
          Fact(destination_station=MATCH.destination_station),
          TEST(lambda destination_station: get_matching_stations(destination_station)[0][-1] == 100),
          Fact(ticket_type=MATCH.ticket_type),
          TEST(lambda ticket_type: ticket_type == "return"),
          Fact(leave_time=MATCH.leave_time),
          Fact(return_time=MATCH.return_time),
          Fact(adult_count=MATCH.adult_count),
          Fact(children_count=MATCH.children_count)
          )
    def ask_confirmation_with_return(self, origin_station, destination_station, ticket_type, leave_time, return_time, adult_count, children_count):
        self.__run_confirmation(origin_station, destination_station, ticket_type, leave_time, return_time, adult_count, children_count)

    def __run_confirmation(self, origin_station, destination_station, ticket_type, leave_time, return_time, adult_count, children_count):
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

        return_string = "and returning by " + return_time if ticket_type == "return" else ""

        print("Awesome! I'm going to look for %s from %s to %s leaving by %s %s" % (
            ticket_string, origin_station, destination_station, leave_time, return_string))

    # @Rule(Fact(state="delay"), NOT(Fact(current_delay=W())))
    # def delay_ask_delay(self):
    #     self.declare(Fact(current_delay=input("How much is your train delayed so far by? ")))
    #
    # @Rule(Fact(state="delay"), NOT(Fact(current_station=W())))
    # def delay_ask_current_station(self):
    #     self.declare(Fact(current_station=input("What station are you currently at? ")))
    #
    # @Rule(Fact(state="delay"), NOT(Fact(target_station=W())))
    # def delay_ask_target_station(self):
    #     self.declare(Fact(target_station=input("What station would you like the delay to be predicted at? ")))
    #
    # @Rule(Fact(state="delay"),
    #       Fact(current_delay=MATCH.current_delay),
    #       Fact(current_station=MATCH.current_station),
    #       Fact(target_station=MATCH.target_station))
    # def delay_send_delay_prediction(self, current_delay, current_station, target_station):
    #     on_time = True
    #
    #     if on_time:
    #         print("The train is predicted to arrive at %s on time." % target_station)
    #     else:
    #         print("The predicted delay at %s is %s." % (target_station, "DELAY GOES HERE"))


if __name__ == '__main__':
    engine = KEngine()
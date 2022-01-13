from experta import *


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
        input("How can I help you? ")
        self.modify(self.facts[1], state="booking")  # TODO Modify this to booking/delays respectively

    @Rule(Fact(state="booking"), NOT(Fact(origin_station=W())))
    def ask_origin_station(self):
        self.declare(Fact(origin_station=input("Where are you travelling from? ")))

    @Rule(Fact(state="booking"), NOT(Fact(destination_station=W())))
    def ask_destination_station(self):
        self.declare(Fact(destination_station=input("Where would you like to go? ")))

    @Rule(Fact(state="booking"), NOT(Fact(ticket_type=W())))
    def ask_ticket_type(self):
        self.declare(Fact(ticket_type=input("Would you like a single, or a return ticket? ")))

    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          NOT(Fact(leave_time=W())),
          )
    def ask_leave_time(self, origin_station):
        self.declare(Fact(leave_time=input("When would you like to leave %s? " % (origin_station))))

    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          NOT(Fact(return_time=W()))
          )
    def ask_return_time(self, origin_station):
        self.declare(Fact(return_time=input("When would you like return to %s? " % (origin_station))))

    @Rule(Fact(state="booking"), NOT(Fact(adult_count=W())))
    def ask_adults_count(self):
        self.declare(Fact(adult_count=input("How many adults are traveling? ")))

    @Rule(Fact(state="booking"), NOT(Fact(children_count=W())))
    def ask_children_count(self):
        self.declare(Fact(children_count=input("How many children are traveling? ")))

    @Rule(Fact(state="booking"),
          Fact(origin_station=MATCH.origin_station),
          Fact(destination_station=MATCH.destination_station),
          Fact(ticket_type=MATCH.ticket_type),
          Fact(leave_time=MATCH.leave_time),
          Fact(return_time=MATCH.return_time),
          Fact(adult_count=MATCH.adult_count),
          Fact(children_count=MATCH.children_count)
          )
    def ask_confirmation(self, origin_station, destination_station, ticket_type, leave_time, return_time, adult_count,
                         children_count):

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
        print(self.facts)

    @Rule(Fact(state="delay"), NOT(Fact(current_delay=W())))
    def delay_ask_delay(self):
        self.declare(Fact(current_delay=input("How much is your train delayed so far by? ")))

    @Rule(Fact(state="delay"), NOT(Fact(current_station=W())))
    def delay_ask_current_station(self):
        self.declare(Fact(current_station=input("What station are you currently at? ")))

    @Rule(Fact(state="delay"), NOT(Fact(target_station=W())))
    def delay_ask_target_station(self):
        self.declare(Fact(target_station=input("What station would you like the delay to be predicted at? ")))

    @Rule(Fact(state="delay"),
          Fact(current_delay=MATCH.current_delay),
          Fact(current_station=MATCH.current_station),
          Fact(target_station=MATCH.target_station))
    def delay_send_delay_prediction(self, current_delay, current_station, target_station):
        on_time = True

        if on_time:
            print("The train is predicted to arrive at %s on time." % target_station)
        else:
            print("The predicted delay at %s is %s." % (target_station, "DELAY GOES HERE"))


if __name__ == '__main__':
    engine = KEngine()
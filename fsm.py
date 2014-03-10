
""" Generic finite state machine class
    Initialise the class with a list of tuples - or by adding transitions
    Tony Flury - November 2012
    Released under an MIT License - free to use so long as the author and other contributers are credited.
"""


class fsm(object):
    """ A simple to use finite state machine class.
        Allows definition of multiple states, condition functions from state to state and optional callbacks
    """
    def __init__(self, states=[]):
        self._states=states
        self.currentState = None

    def start(self,startState=None):
        """ Start the finite state machine
        """
        if not startState or not (startState in [x[0] for x in self._states]):
            raise ValueError("Not a valid start state")
        self.currentState = startState

    def stop(self):
        """ Stop the finite state machine
        """
        # Bug fix 15 Dec 2012 - self.currentState should be reset, not startState - Identified by Holger Waldmann
        self.currentState = None

    def addTransition(self,fromState, toState, condition, callback=None):
        """ Add a state transition to the list, order is irellevant, loops are undetected
            Can only add a transition if the state machine isn't started.
        """
        if not self.currentState:
            raise ValueError("StateMachine already Started - cannot add new transitions")

        # add a transition to the state table
        self._states.append( (fromState, toState,condition, callback))

    def event(self, value):
        """ Trigger a transition - return a tuple (<new_state>, <changed>)
            Raise an exception if no valid transition exists.
            Callee needs to determine if the value will be consumed or re-used
        """

        if not self.currentState:
            raise ValueError("StateMachine not Started - cannot process event")

        # get a list of transitions which are valid
        self.nextStates = [ x for x in self._states\
                            if x[0] == self.currentState\
        and (x[2]==True or (callable(x[2]) and x[2](value))) ]

        if not self.nextStates:
            raise ValueError("No Transition defined from state {0} with value '{1}'".format(self.currentState, value))
        elif len(self.nextStates) > 1:
            raise ValueError("Ambiguous transitions from state {0} with value '{1}' ->  New states defined {2}".format(self.currentState, value, [x[0] for x in self.nextStates]))
        else:
            if len(self.nextStates[0]) == 4:
                current, next, condition, callback = self.nextStates[0]
            else:
                current, next, condition = self.nextStates[0]
                callback = None

            print("transitioning from state {0} to state {1} given input {2}".format( self.currentState, next, value ) )

            self.currentState, changed = (next,True)\
            if self.currentState != next else (next, False)

            # Execute the callback if defined
            if callable(callback):
                callback(self, value)

            return self.currentState, changed

    def CurrentState(self):
        """ Return the current State of the finite State machine
        """
        return self.currentState



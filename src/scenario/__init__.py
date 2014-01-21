"""Scenario - a tool for automating various scenarios
Copyleft 2014 Antoine d'Otreppe <a.dotreppe@aspyct.org>

Available in the public domain. Feel free to do anything.
"""

class ScenarioStepDelegate:
    def stepSucceeded(self, step): pass
    def stepFailed(self, step, reason): pass

class ScenarioStep:
    def __init__(self):
        self.delegate = None

    def run(self):
        self.delegate.stepSucceeded(self)

class ScenarioNode(ScenarioStepDelegate):
    def __init__(self, step):
        self.step = step
        self.successNode = None
        self.failureNode = None

    def run(self):
        self.step.delegate = self
        self.step.run()

    def stepSucceeded(self, step):
        if self.successNode is not None:
            self.successNode.run()

    def stepFailed(self, step, reason):
        if self.failureNode is not None:
            self.failureNode.run()

Scenario = ScenarioNode


# Test code
class NetworkTestStep(ScenarioStep):
    def __init__(self, address):
        ScenarioStep.__init__(self)
        self.address = address

    def run(self):
        # Test if www.aspyct.org is reachable
        if self.isReachable(self.address):
            self.delegate.stepSucceeded(self)
        else:
            print("{} is not reachable".format(self.address))
            self.delegate.stepFailed(self, "Could not reach {}".format(self.address))

    def isReachable(self, address):
        return True

class QuestionStep(ScenarioStep):
    def __init__(self, question):
        ScenarioStep.__init__(self)
        self.question = question

    def run(self):
        response = input(self.question + " (y/n) ")
        if response.lower().startswith("y"):
            self.delegate.stepSucceeded(self)
        else:
            self.delegate.stepFailed(self, "User answered no")


class EchoStep(ScenarioStep):
    def __init__(self, message):
        ScenarioStep.__init__(self)
        self.message = message

    def run(self):
        print(self.message)
        self.delegate.stepSucceeded(self)

testAspyctStep = NetworkTestStep("www.aspyct.org")
bootOfflineStep = QuestionStep("Boot in offline mode ?")
bootingOnlineStep = EchoStep("Booting online")
bootingOfflineStep = EchoStep("Booting offline")

testAspyctNode = ScenarioNode(testAspyctStep)
bootOfflineNode = ScenarioNode(bootOfflineStep)
bootingOnlineNode = ScenarioNode(bootingOnlineStep)
bootingOfflineNode = ScenarioNode(bootingOfflineStep)

testAspyctNode.successNode = bootingOnlineNode
testAspyctNode.failureNode = bootOfflineNode

bootOfflineNode.successNode = bootingOfflineNode
bootOfflineNode.failureNode = testAspyctNode

bootScenario = testAspyctNode


bootScenario.run()

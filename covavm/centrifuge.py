import json
import hashlib
import types

# Policy Builtins

class PolicyViolationError(Exception):
    "for dealing with general policy violations"
    pass

class PolicyRuntimeError(Exception):
    "for dealing with runtime errors such as unregistered policies"
    pass

class PolicySyntaxError(Exception):
    "for dealing with malformed policy text"
    pass

class PolicyManager(object):

    """PolicyManagers are objects that live within the CovaVM instance that propagate
    bytecode dispatch events to loaded Smart Policies, using a publish and subscribe
    model."""
    def __init__(self, vm, policy_text):
        self.vm = vm

        try:
            policy = json.loads(policy_text)
            self.policy = policy

            self.preconditions = []
            for key in policy.get("pre", {}):
                options = policy["pre"][key]
                self.preconditions.append(PRECONDITIONS[key](options))
            
            self.monitors = []
            for key in policy.get("runtime", {}):
                options = policy["runtime"][key]
                self.monitors.append(RUNTIME_MONITORS[key](options))
            
            self.postconditions = []
            for key in policy.get("post", {}):
                options = policy["post"][key]
                self.postconditions.append(POSTCONDITIONS[key](options))
        except ValueError as e:
            raise PolicySyntaxError(e.message)
        except KeyError as e:
            raise PolicyRuntimeError("Unregistered Validator '%s'" % e.message)
    
    def run_preconditions(self):
        context = {
            "program": self.vm.code
        }

        for v in self.preconditions:
            v.run(context)
    
    def run_postconditions(self):
        for v in self.postconditions:
            v.run(self.vm.result)
    
    def broadcast_bytecode(self, bytecode, args):
        for monitor in self.monitors:
            monitor.receive_bytecode(bytecode, args)
    # TODO: Figure out more efficient way to broadcast events

class PolicyValidator(object):
    
    name = "PolicyValidator"
    default_opts = dict()
    required_opts = dict()

    def __init__(self, options = dict()):
        self.options = dict()
        self.options.update(self.default_opts)
        self.options.update(options)
        for key in self.required_opts:
            t = self.required_opts[key]
            try:
                if type(t) == list or type(t) == tuple:
                    # check if each type might be acceptable
                    if not any(map(lambda _t: type(self.options[key]) == _t, t)):
                        raise PolicySyntaxError("Validator %s requires option '%s' to be of %s, not %s" % (self.name, key, str(t), type(self.options[key])))
                elif type(self.options[key]) != t:
                    raise PolicySyntaxError("Validator %s requires option '%s' to be of %s, not %s" % (self.name, key, str(t), type(self.options[key])))
            except KeyError:
                raise PolicySyntaxError("Validator %s expects option '%s' of %s, not found." % (self.name, key, str(t)))


    def violation(self, message):
        raise PolicyViolationError(message)

class Precondition(PolicyValidator):
    def run(self, context):
        pass

"""
Runtime Monitors can be simple to write and express complex behavior by using the policy
pattern of using a finite state automaton. Keep a policy state and create transition
functions that change the state upon bytecode dispatch events from receive_bytecode().
"""
class RuntimeMonitor(PolicyValidator):
    def receive_bytecode(self, bytecode, args):
        pass

class Postcondition(PolicyValidator):
    def run(self, data):
        pass

class FileHashValidator(Precondition):
    name = "fileHash"
    required_opts = {
        "equalTo": list(types.StringTypes) + [types.ListType]
    }
    def run(self, context):
        text = context["program"]
        hashed = hashlib.md5(text.encode()).hexdigest()
        if type(self.options["equalTo"]) == list:
            if not any(map(lambda x: x == hashed, self.options["equalTo"])):
               self.violation('Program hash "%s" does not match any in "%s"' % (hashed, self.options["equalTo"]))
        elif (hashed != self.options["equalTo"]):
            self.violation('Program hash "%s" does not match "%s"' % (hashed, self.options["equalTo"]))

class PrintBytecodeValidator(RuntimeMonitor):
    name = "_printBytecode"
    def receive_bytecode(self, bytecode, args):
        print(bytecode, args)


PRECONDITIONS = {
    "fileHash": FileHashValidator
}

RUNTIME_MONITORS = {
    "_printBytecode": PrintBytecodeValidator
}

POSTCONDITIONS = {
}
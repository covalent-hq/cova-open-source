import imp
import os
import sys
import vm
import json

try:
    # In Py 2.x, the builtins were in __builtin__
    BUILTINS = sys.modules['__builtin__']
except KeyError:
    # In Py 3.x, they're in builtins
    BUILTINS = sys.modules['builtins']

def run_with_covavm(code_src, data, policy_text, args, package=None):
    # code_src = data user source code in Python
    # data = data owner's data object
    # policy_text = data owner's policy in JSON
    # args = list of arguments

    # parse the policy
    # TODO: Replace with Centrifuge parser
    policy = json.loads(policy_text)

    # Create a module to serve as __main__
    old_main_mod = sys.modules['__main__']
    main_mod = imp.new_module('__main__')
    sys.modules['__main__'] = main_mod
    main_mod.__file__ = '__covaprogram__'
    if package:
        main_mod.__package__ = package
    main_mod.__builtins__ = BUILTINS

    # Set sys.argv and the first path element properly.
    old_argv = sys.argv
    old_path0 = sys.path[0]
    sys.argv = args
    if package:
        sys.path[0] = ''

    # Instantiate a fresh CovaVM
    vm_instance = vm.CovaVM(code=code_src, data=data, policy=policy, env=main_mod.__dict__)
    vm_instance.run_program() # gitrun program with policies
    sys.modules['__main__'] = old_main_mod

    # Restore the old argv and path
    sys.argv = old_argv
    sys.path[0] = old_path0
    return vm_instance.result
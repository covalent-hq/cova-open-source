----------------------------
Purpose of SealedData
----------------------------
The project demonstrates:
- How an application enclave can encrypt and integrity-protect enclave secrets
to store them outside the enclave
- How an application enclave can use Monotonic Counter to implement
replay-protected policy, and Trusted Time to enforce time based policy
- Covalent is using this intel provided source code to build a local storage that persist credentials while CovaClave is offline
------------------------------------
How to Build/Execute the Sample Code
------------------------------------
1. Install Intel(R) Software Guard Extensions (Intel(R) SGX) SDK for Linux* OS
2. Make sure your environment is set:
```bash
    $ source ${sgx-sdk-install-path}/environment
 ```
3. Build the project with the prepared Makefile:
```bash
    a. Hardware Mode, Debug build:
        $ make
    b. Hardware Mode, Pre-release build:
        $ make SGX_PRERELEASE=1 SGX_DEBUG=0
    c. Hardware Mode, Release build:
        $ make SGX_DEBUG=0
    d. Simulation Mode, Debug build:
        $ make SGX_MODE=SIM
    e. Simulation Mode, Pre-release build:
        $ make SGX_MODE=SIM SGX_PRERELEASE=1 SGX_DEBUG=0
    f. Simulation Mode, Release build:
        $ make SGX_MODE=SIM SGX_DEBUG=0
4. Execute the binary directly:
    $ ./app
5. Remember to "make clean" before switching build mode
```

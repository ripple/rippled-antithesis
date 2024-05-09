<h1 align="center">rippled test framework</h1>

The rippled test framework enables users to run end to end test case scenarios against a local rippled instance or against a rippled network

<h3>Setup</h3>
The rippled testing framework is built using python3. This document lists the instructions to setup on linux.

1. Python and virtual env setup
    - Setup python3 on Mac: https://gist.github.com/pandafulmanda/730a9355e088a9970b18275cb9eadef3
    - Setup python3 on Linux:	https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-ubuntu-16-04

1. Clone rippled test repository https://gitlab.ops.ripple.com/xrpledger/automation to the desired location

    ```
    git clone git@gitlab.ops.ripple.com:xrpledger/automation.git
   ```

1. Install required python packages 
   ```
   cd automation 
   pip install -r rippled_automation/requirement.txt
   ```

1. Install/build rippled

   To install rippled on linux, 

   ```
   sh install_rippled.sh
   ```

   To build rippled on linux, 
   ```
   sh install_rippled.sh --mode build
   ```
   
   For more options,
   ```
   sh install_rippled.sh --help
   ```

<h3>Run tests</h3>

The tests will run against a locally running rippled instance 

<b>Using CI wrapper (run_test.sh)</b>

To run smoke tests,
```
sh run_test.sh
```

To run all tests (nightly),
```
$ sh run_test.sh --runType nightly
```

For more options,
```
sh run_test.sh --help
```


<b>More options to run tests</b>

Run all tests for a feature (example: `payment`)
   ```
   pytest --hostname <optional validator_ip to run the test against (default: localhost)>
          --port <optional port validator is listening on (default: 51234)>
          <feature_name>.py

   Example: pytest --hostname "10.31.97.171" --port 5005 rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/payment_test.py
   ```
Run a specific test (example: `escrow_test.py::test_escrow_create_cancel`)
   ```
   pytest --hostname <optional validator_ip to run the test against (default: localhost)>
          --port <optional port validator is listening on (default: 51234)>
          <feature_name>.py -k <test_name>

   Example: pytest --hostname "10.31.97.171" --port 5005 rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/escrow_test.py -k test_escrow_create_cancel
   ```


<h3>Join QE network with local instance of rippled and running the tests</h3>

1. Keep the rippled.cfg file to its default configuration 

2. Change the validator.txt file to the following
```
    [validator_list_sites]
    https://gist.githubusercontent.com/manojsdoshi/9b154da59b85fc4de73178e5923ba4e8/raw/6dd96ddabc3f0b6cf6dcda71b061c10a44de0ec4/index.json

    [validator_list_keys]
    ED4C955BA5D4BFFEABFA33017C60916C0552F49A24C83EE15C4AF7BE806396405C
``` 
3. Now restart rippled and confirm it is connected to the QE network


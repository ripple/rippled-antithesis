Rippled test framework: The rippled testing framework enables users to run end to end test case scenarios againsts a local rippled instance or against a rippled network

1.Setup: The rippled testing framework is built using python3
   
	1. Python and virtual env setup: 
				Instruction on setting up python3 on Mac: https://gist.github.com/pandafulmanda/730a9355e088a9970b18275cb9eadef3
				Instruction on setting up python3 on Linux:	
		https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-ubuntu-16-04
	2. Clone the repository (https://github.com/ripple/automation) to the desired location 

	3. pip install -r rippled-automation/requirement.txt

	4. The tests will run against a locally running rippled instance
	    1. cd automation
        2. pytest rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/payment_test.py::test_xrp_payment_flow
	
    
2.Running tests 
	
	1. pytest running all tests suite: pytest -q --hostname="<validator_ip to run the test against or if tunned is setup from the above step use localhost>" 
		Example: pytest payment_test.py -q --hostname="10.31.97.171" --html=report.html

	2. pytets running running tests for a feature: pytest <feature_name>.py -q --hostname="<validator_ip to run the test against or if tunned is setup from the above step use localhost>" 
		Example: pytest payment_test.py -q --hostname="10.31.97.171" --html=report.html

	3. pytest running a test: pytest <test_file_name>.py -k <test_name> -q --hostname="<validator_ip to run the test against or if tunned is setup from the above step use localhost>" --html=report.html
		Example: pytest escrow_test.py -k test_escrow_create_cancel -q --hostname="10.31.97.171" --html=report.html

3.Join the QE network with your local instance of rippled and running the tests 
	
	1. Keep the rippled.cfg file to its default configuration 
	
	2. Change the validator.txt file to the following 
	    [validator_list_sites]
        https://gist.githubusercontent.com/manojsdoshi/9b154da59b85fc4de73178e5923ba4e8/raw/6dd96ddabc3f0b6cf6dcda71b061c10a44de0ec4/index.json

        [validator_list_keys]
        ED4C955BA5D4BFFEABFA33017C60916C0552F49A24C83EE15C4AF7BE806396405C
        
    3. Now restart rippled and confirm its connected to the QE network
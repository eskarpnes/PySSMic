# PySSMic

Project in TDT4290 Customer driven project. This is a python implementation of the CoSSMic project. The CoSSMic (Collaborating Smart Solar-powered Microgrid) is a proposed peer-to-peer microgrid system where neighbourhoods can buy and sell local green power.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

- [Python 3.x](https://www.python.org/downloads/) Follow the instructions

### Installing

A step by step series of examples that tell you how to get a development env running

1. Open your terminal and clone the github repo to the folder you want

```
git clone https://github.com/eskarpnes/PySSMic.git
```

2. Change directory to PySSMic and create a virtual environment called venv

```
cd pyssmic && python3 -m venv venv
```

3. Go activate the virtual environment and install requirements from requirements.txt

```
source venv/bin/activate
pip install -r requirements.txt
```

You should now have a working project locally

## Running the simulator

You can run the simulator from the rootfolder with

```
python index.py
```

Open your preferred browser and go to http://127.0.0.1:8050/

### Create a simulation

To create a new simulation, go to http://127.0.0.1:8050/apps/create_sim.
From the select ESN dropdown list, you can choose the ESN you want to use for the simulation. To add ESN to the list, click on 'Create ESN' or add files to your input folder, where the name of the folder equals the name of the ESN.

The days to simulate field is to tell the simulation to quit after the given time, so that it doesn't run forever because of a typo in one of the input files, e.g. a timestamp in a job that doesn't corespond with the rest of the inputfiles.

Choose your preferred optimization algorithm and how many times you want to run the simulation with the given inputs and press 'Start Simulation'.

When the simulation is done, you can go to http://127.0.0.1:8050/apps/simulate_esn to see your results.

### Create an ESN

You can create a new neighbourhood from scratch or from a XML file. Example of how to structure a neighbourhood XML file is [Here](input/example).

When you have a neighbourhood, you can add and remove houses directly by pressing the buttons. For each house you can add, remove and configure the devices by pressing 'Add or Config Device'. Every consumer can have a loadprofile and every producer can have up to four PV prediction files.
For every device you can add one or more jobs. From the 'Add jobs' button you can fill in the time to run the job. You must be sure that the timeinput you give corespond to the other timestamps you have in your configuration.
A second way to add jobs is by a XML file. Example of how to structure a job XML file is [Here](input/example).

When your configuration is done, type in the name of the neighbourhood and press 'Save Neighbourhood'.

### See the results

To review the simualtion results, go to http://127.0.0.1:8050/apps/simulate_esn. You can see the total results for the whole neighbourhood in the "All households" tab. Here you can specify which run to review by the 'Choose run' dropdown menu. To get specific results for one household go to 'One houshold' tab and choose your house from the dropdown list. To see total results for all runs, go to the 'All runs' tab.
You can send results to your colleagues by sending the pkl file in the resultfolder. In the same way you can see results other have created by adding result files to the result folder.

## Testing with pytest

In order to test our system, we have used pytest - An alternative to Pythons standard unit test module. More documentation about pytest can be found [here](https://docs.pytest.org/en/latest/).

### Install pytest

```
pip install pytest==version (TODO)
```

### Run all tests

```
python -m pytest
```


## Built With

- [Python 3.x](https://www.python.org/downloads/) - Programming language
- [SciPy](https://www.scipy.org/) -
- [pytest](https://docs.pytest.org/en/latest/) - Testing framework
- [Dash](https://dash.plot.ly/) - The web framework used
- [PyCharm](https://www.jetbrains.com/pycharm/) - Python IDE

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

See [Contributers](https://github.com/eskarpnes/PySSMic/graphs/contributors)

## Versioning

We use [GIT](https://git-scm.com/) for versioning.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

- SINTEF Digital for the project
- CoSSMiC
- Supervisor

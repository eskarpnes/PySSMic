# PySSMic

Project in TDT4290 Customer driven project. This is a python implementation of the CoSSMic project. The CoSSMic (Collaborating Smart Solar-powered Microgrid) is a proposed peer-to-peer microgrid system where neighbourhoods can buy and sell local green power.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

- [Python 3.6](https://www.python.org/downloads/) or higher. Follow the instructions in the link.

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
# Mac/Linux
source venv/bin/activate

# Windows
/venv/Scripts/activate.bat

# All
pip install -r requirements.txt
```

You should now have a working project locally

## Running the simulator

You can run the simulator from the rootfolder with

```
python start.py
```

### Create a simulation

To create a new simulation, go to http://127.0.0.1:8050/apps/create_sim.
From the select ESN dropdown list, you can choose the ESN you want to use for the simulation. To add ESN to the list, click on 'Create ESN' or add files to your input folder, where the name of the folder equals the name of the ESN.

#### Configuration

##### Days to simulate

The days to simulate field is to tell the simulation to quit after the given time, so that it doesn't run forever because of a typo in one of the input files, e.g. a timestamp in a job that doesn't corespond with the rest of the inputfiles.

##### Select Optimization Algorithm(s)

Choose your preferred optimization algorithm. The algorithms `L-BFGS-B`, `SLSQP` and `TNC` are all part of `scipy.optimize.minimize`-package, and are used with the Basin-hopping algorithm for finding global minimums. Read more about them [here](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html)

When choosing either of the scipy-algorithms, "Step size" and "Tolerance" can be set. These are the parameters in `scipy.optimize.minimize()` called `eps` and `tol`. "Step size" is the step size used for numerical approximation of the jacobian. "Tolerance" sets the tolerance for termination. 

##### Number of runs

Sets how many times you will run the simulator with the configuration specified.

##### Start simulation

Press Start simulation to start the simulation. The simulation will now finish before you can do anything more. The result file will be saved in the format: date_time_esnName_algorithm_numOfRuns.pkl in the [result folder](/results).

When the simulation is done, you can go to http://127.0.0.1:8050/apps/results to see your results.

#### Producer scores

As a part of the algorithm for choosing producers among consumers, the manager keeps a scoreboard of scores for every producer in the neighbourhood.
The consumers use these scores in a priority queue when choosing producers, so the producer with the lowest score is chosen first.
As it is implemented right now, the producers gets -1 to the score when accepting a job, and +1 when declining. This means that a lower score is better.

The simulator saves the producer ranking scores after each simulation. These are saved under input/neighbourhood_name/producer_scores.pkl.
If you want to reset the producer ranking for any reason, you can simply delete this file. The simulator will then create a new one in the next run with starting values. 

### Create an ESN

You can import an ESN in three ways: from XML, create one from scratch or from .pkl files.

#### Configuration

You can create a new neighbourhood from scratch or from a XML file. Example of how to structure a neighbourhood XML file is [here](input). (TODO: create an example folder)

##### Add house to neighbourhood

When you press the 'add house' a new house will be added to the neighbourhood. It will automatically get an ID and one user who will have all the devices.

##### Remove house from neighbourhood

To remove a house, press the tab for the house you want to delete and press delete house.

##### Add device

Press the "Add or config device" button. You can add consumer from the "Add new consumer" tab or a producer for the "Add new producer" tab.

- All fields need to be filled to configure the house correctly.
- The ID for every device need to be unique within the neighbourhood.
- The templatenumber refers to which loadprofile or PV Prediction files you want to connect the device to. If you add a loadprofile or predictionfiles for this device, you should set the template number to the same as the ID.

##### Delete device

Press the "Add or config device" button and press the "Configure a device" tab and select the device you want to delete from the dropdownlist. When you have selected the device, you can press the delete device button.

##### Configure a device

You can change ID, Name, Template, Type and loadprofiles/Pv prediction files for every device.
Press the "Add or config device" button and press the "Configure a device" tab. Do your changes and press save.

##### Add jobs

You can add jobs for every consumer in the neighbourhood. You can specify it by pressing "Add Job" button. From here you can specify your device, and specify the earliest- and latest start time. Press save to add the job and you should now see it in the jobslist.

You can also add multiple jobs for the neighbourhood by pressing "Add jobs from XML". Example of how to structure the XML file is [here](/input/example/jobs.xml).

#### Save

When your configuration is done, type in the name of the neighbourhood and press 'Save Neighbourhood'. The neighbourhood will be a folder in the input folder and as a pickle object in the neighbourhood folder.

### See the results

To review the simualtion results, go to http://127.0.0.1:8050/apps/results. You can see the total results for the whole neighbourhood in the "All households" tab. Here you can specify which run to review by the 'Choose run' dropdown menu. To get specific results for one household go to 'One houshold' tab and choose your house from the dropdown list. To see total results for all runs, go to the 'All runs' tab.
You can send results to your colleagues by sending the pkl file in the resultfolder. In the same way you can see results other have created by adding result files to the result folder. 

In addition, a log file, `log.txt`, is created when a run is executed. Here, details about what has happened during the run can be seen. Each class can write to the log by calling the logging functions on `self.logger`.

## Testing with pytest

In order to test our system, we have used pytest - An alternative to Pythons standard unit test module. More documentation about pytest can be found [here](https://docs.pytest.org/en/latest/).

### Install pytest

pytest are installed through the installation from the requirement file. Make sure to be in the virtual environment to run the test.

_Version 3.8.2 is used in PySSMic_

### Run all tests

```
python -m pytest
```

## Built With

- [Python 3.x](https://www.python.org/downloads/) - Programming language
- [SciPy](https://www.scipy.org/) - Optimization algorithms
- [pytest](https://docs.pytest.org/en/latest/) - Testing framework
- [Dash](https://dash.plot.ly/) - The web framework used
- [SimPy](https://simpy.readthedocs.io/en/latest/) - Discrete simulation framework
- [PyCharm](https://www.jetbrains.com/pycharm/) - Python IDE
- [pandas](https://pandas.pydata.org/) - Framework for handling data series
- [pykka](https://www.pykka.org/en/latest/api/) - Actor framework used in communication between producers and consumers

## Contributers

See [Contributers](https://github.com/eskarpnes/PySSMic/graphs/contributors)

## Versioning

We use [GIT](https://git-scm.com/) for versioning.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

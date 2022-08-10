# python-gui-real-time-plotting

## About
A python GUI for plotting real time data over a serial connection


## Configure

Absolute path to sphere object needs to be changed in realtimeplotter.plotter class.
COM port connects must be configured in realtimeplott.real_time_plotter class.


## Commands

isntall dependencies using poetry.

```
poetry install
```

```
poetry run py setup.py
```

alternatively, using a shell

```
poetry shell
py setup.py
```

launch application

```
py setup.py
```



## Simulating

use com0com to create virtual com ports (only tested on windows)

connect real_time_sender to one of the newly created virtual ports
connect real_time_plotter to one of the newly created virtual ports

run setup.py
run real_time_plotter.py

press connect on real_time_sender
press connect on real_time_plotter



## Todo
add a counter label for both the simulation and the plotte so we know howmany 
data points were sent and how many were received! checking to see if anything was lost
also a counter for how many pints were plotted 
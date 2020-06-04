# EcoDyco

A macroeconomic software for a ﬁnite world: a short presentation 


**EcoDyco** is an overlay for macro-economic models that aim to take into account the constraints related to resources, particularly in terms of their quantity and quality. The *EcoDyco Manual V1.pdf* explains the different parameters and a paper (in preparation) explains how to build the model.


### Licence

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


### Requirements
Proposed version of EcoDyco works with Python 3. Required libraries:
- numpy
- matplotlib
- pandas
- xlsxwriter
- tkinter
- math

### World settings
The general parameters are in the header of *main.py*. To create new airframes and economical engines see the *EcoDyco Manual V1.pdf*.


### Run the world
A minimum configuration includes the files *main.py*, *PhysicalWorld.py*, at least one economic engine (e.g. *Goodwin.py*, *ZeroGrowth.py*, *Solow.py*) and the corresponding parameter files in *preproc/*

Then, from a terminal, execute :
```
python3 main.py
```
or in an ipython console (via spyder or other)
```
run main.py
```

<!-- ### New economical engine -->
<!-- See the manual *Manual EcoDyco V1.pdf* -->


<!-- ### New resource sheet -->
<!-- See the manual *Manual EcoDyco V1.pdf* -->




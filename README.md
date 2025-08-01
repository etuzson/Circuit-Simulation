# Circuit-Simulation
Start with the building blocks of logic gates and build any circuit imaginable. An improvement over the first attempt I made at writing a circuit simulator at https://github.com/etuzson/circuit. Using basic logic gates, I implemented up to an 8-bit full adder supporting subtraction and negative numbers represented as the 2s complement.

Each component of the circuit is an instance of the Component class. Each Component has a list of inner Components, a list of input indexes, a list of output indexes, and a dictionary defining how the inner components are connected to each other and to the inputs/outputs of the encompassing Component.

Component.evaluate() recursively evaluates each inner Component. The base case is a Component object with no further inner Components (the basic logic gates).

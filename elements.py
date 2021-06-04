"""
elements.py
A module containing implementaions of logic elements.
You can use the following classes from this module:
- Connnection
- Constant
- Variable
- AndGate
- OrGate
- NotGate
- XorGate
- NandGate
- NorGate
- Multiplexer
- Encoder
- Decoder
- FullAdder
- AdderSubtractor
- RightShifter
- SRFlipFlop
"""

import functools
import random


class Connection:
    """Represents the connection between the output of some element and the input of
    another element.
    Attributes
    ----------
    source: BasicElement
        the logic element from which binary output is taken
    output_label: str
        the name of the output of the source element (it can have several outputs)
    destination: BasicElement
        the logic element, to which the signal is passed
    input_label: str
        the name of the input of the destination element (it can have several inputs)
    """

    def __init__(self, source, output_label, destination, input_label):
        self.source = source
        self.output_label = output_label
        self.destination = destination
        self.input_label = input_label


class BasicElement:
    """An abstract class for defining the interface of logic elements.
    Logic element:
    - has inputs with associated labels
    - each input is associated with zero or one connections (see class Connection)
    - has outputs with associated labels
    - each output can be associated with any number of connections (see class Connection).
    Attributes
    ----------
    value: dict
        a dictionary (each key is a name of the output of the logic element, each value is a
        boolean) that represents the output of the logic element.
    position: tuple
        Cell that element posses on separated square.
        First cell has position (1, 1)
    outs: dict
        outputs of the element
    ins: dict
        inputs of the element
    Methods
    -------
    set_input_connection(connection)
        Associate the passed in connection with the specified input
    delete_input_connection(input_label)
        Delete the connection associated with the specified input
    set_output_connection(connection)
        Add passed in connection to the connections associated with the specified output
    delete_output_connection(output_label)
        Clear all the output connections
    reset_value()
        Forgets the previously calculated value
    """

    def __init__(self, id_, position):
        self._ins = {}
        self._outs = {}
        self._value = None
        self._id = id_
        self._element_type = None
        self.position = position

    def set_input_connection(self, connection: Connection):
        if connection.input_label not in self._ins:
            raise KeyError("No such label in the labels of inputs.")
        self._ins[connection.input_label] = connection

    def delete_input_connection(self, input_label: str):
        self._ins[input_label] = None

    def set_output_connection(self, connection: Connection):
        if connection.output_label not in self._outs:
            raise KeyError("No such label in the labels of outputs.")
        self._outs[connection.output_label].append(connection)

    def delete_output_connection(self, output_label: str):
        self._outs[output_label] = []

    def check_added_connection(self, compare_id: str, first_call: bool = False):
        """Return True if connection doesn't create a cycle.
        Otherwise, return False

        Attributes
        --------------
            first_call: if element from the connection call this method
        """
        if not first_call and self._id == compare_id:
            return False
        for in_label, connection in self._ins.items():
            if not connection:
                continue
            source = connection.source
            if not source.check_added_connection(compare_id):
                return False
        return True

    @property
    def value(self) -> dict:
        raise NotImplementedError

    @property
    def id(self):
        return self._id

    def reset_value(self):
        self._value = None

    @property
    def element_type(self):
        return self._element_type

    def _read_input_value(self, input_label: str):
        connection = self._ins[input_label]
        if connection is None:
            return False
        return connection.source.value[connection.output_label]

    @property
    def outs(self):
        return self._outs

    @property
    def ins(self):
        return self._ins


class BasicLogicGate(BasicElement):
    """An abstract class for basic logic gates (such as AND, OR, XOR, NAND, NOR).
    AndGate, OrGate, XorGate, NandGate and NorGate classes inherit from this class.
    This class provides multi-input variants of the elements mentioned above.
    The interface of every gate mentioned above is the following:
    - input:
        in1
        in2
        ...
        in{num_inputs}
    - output:
        out
    """

    def __init__(self, id_, position, num_inputs: int):
        """Initialize an instance with num_inputs.
        :id_: name or id of the element
        :num_inputs: the number of inputs of an element
        """
        if num_inputs < 2:
            raise ValueError("Number of inputs should be >= 2")
        super().__init__(id_, position)
        self._num_inputs = num_inputs
        for i in range(1, num_inputs + 1):
            self._ins['in' + str(i)] = None
        self._outs['out'] = []

    def _logic_of_element(self, *inputs) -> bool:
        raise NotImplementedError

    def _iterate_over_input_values(self):
        for input_label in self._ins:
            yield self._read_input_value(input_label)

    @property
    def value(self):
        if self._value is None:
            self._value = self._logic_of_element(*self._iterate_over_input_values())
        return {'out': self._value}


class AndGate(BasicLogicGate):
    def __init__(self, id_, position=None, num_inputs=2):
        super().__init__(id_, position, num_inputs)
        self._element_type = "AND"

    def _logic_of_element(self, *inputs):
        return functools.reduce(lambda a, b: a and b, inputs)


class OrGate(BasicLogicGate):
    def __init__(self, id_, position=None, num_inputs=2):
        super().__init__(id_, position, num_inputs)
        self._element_type = "OR"

    def _logic_of_element(self, *inputs):
        return functools.reduce(lambda a, b: a or b, inputs)


class XorGate(BasicLogicGate):
    def __init__(self, id_, position=None, num_inputs=2):
        super().__init__(id_, position, num_inputs)
        self._element_type = "XOR"

    def _logic_of_element(self, *inputs):
        return functools.reduce(lambda a, b: a != b, inputs)


class NandGate(BasicLogicGate):
    def __init__(self, id_, position=None, num_inputs=2):
        super().__init__(id_, position, num_inputs)
        self._element_type = "NAND"

    def _logic_of_element(self, *inputs):
        return not functools.reduce(lambda a, b: a and b, inputs)


class NorGate(BasicLogicGate):
    def __init__(self, id_, position=None, num_inputs=2):
        super().__init__(id_, position, num_inputs)
        self._element_type = "NOR"

    def _logic_of_element(self, *inputs):
        return not functools.reduce(lambda a, b: a or b, inputs)


class NotGate(BasicElement):
    """A class for NOT gate.
    The interface of the not gate is the following:
    - input:
        in
    - output:
        out
    """

    def __init__(self, id_, position=None):
        super().__init__(id_, position)
        self._ins['in'] = None
        self._outs['out'] = []
        self._element_type = "NOT"

    @property
    def value(self):
        if self._value is None:
            self._value = not self._read_input_value('in')
        return {'out': self._value}


class Constant(BasicElement):
    """A class for constant source of signal.
    The interface of the element is the following:
    - input:
    - output:
        out
    """

    def __init__(self, id_, position=None, constant_value: bool = True):
        """Initialize a constant with its value and id and position.
        """
        super().__init__(id_, position)
        self._constant_value = constant_value
        self._outs['out'] = []
        self._element_type = "CONSTANT"

    @property
    def value(self):
        return {'out': self._constant_value}


class Variable(BasicElement):
    """A class for variable source of signal.
    The interface of the element is the following:
    - input:
    - output:
        out
    """

    def __init__(self, id_, position=None, init_value: bool = True):
        """Initialize a variable source of signal with its initial value, id and position.
        """
        super().__init__(id_, position)
        self._variable_value = init_value
        self._outs['out'] = []
        self._element_type = "VARIABLE"

    def switch(self):
        self._variable_value = not self._variable_value

    @property
    def value(self):
        return {'out': self._variable_value}


class Multiplexer(BasicElement):
    """A class for multiplexor element.
    A multiplexer has n select lines and 2**n input lines. The select lines decide signal from
    which input line to send to the output.
    The interface of the multiplexer element is the following:
    - input:
        sel1
        sel2
        ...
        sel{num_select_lines}
        in1
        in2
        ...
        in{num_select_lines**2}
    - output:
        out
    """

    def __init__(self, id_, position=None, num_select_lines: int = 2):
        """Initialize a multiplexer with teh number of select lines.
        """
        if num_select_lines < 1:
            raise ValueError("Number of select lines must be >= 1")
        super().__init__(id_, position)
        self._num_select_lines = num_select_lines
        for i in range(1, num_select_lines + 1):
            self._ins[f'sel{i}'] = None
        for i in range(1, 2 ** num_select_lines + 1):
            self._ins[f'in{i}'] = None
        self._outs['out'] = []
        self._element_type = "MULTIPLEXER"

    def _get_number_of_selected_line(self):
        base = "sel"
        selected_line = 0
        for i in range(self._num_select_lines):
            if self._read_input_value(base + str(i + 1)):
                selected_line += 2 ** i
        return selected_line + 1

    @property
    def number_select_lines(self):
        return self._num_select_lines

    @property
    def value(self):
        if self._value is None:
            needed_input = 'in' + str(self._get_number_of_selected_line())
            self._value = self._read_input_value(needed_input)
        return {'out': self._value}


class Encoder(BasicElement):
    """A class for encoder element.
    A decoder knows the number of the high input line, and outputs this number represented by n output lines.
    If several input lines are high, this implementation of encoder takes into account the first one that is high.
    If none of input lines are high, then the all the output lines are low.
    The interface of the encoder element is the following:
    - input:
        input line 1
        input line 2
        ...
        input line {num_output_lines**2}
    - output:
        output line 1
        output line 2
        ...
        output line {num_output_lines}
    """

    def __init__(self, id_, position=None, num_output_lines: int = 2):
        """Initialize an encoder with the number of output lines and id.
        """
        if num_output_lines < 1:
            raise ValueError("Number of output lines must be >= 1")
        super().__init__(id_, position)
        self._num_output_lines = num_output_lines
        for i in range(1, 2 ** num_output_lines + 1):
            self._ins[f'input line {i}'] = None
        for i in range(1, num_output_lines + 1):
            self._outs[f'output line {i}'] = []
        self._element_type = "ENCODER"

    def _input_lines_to_number(self):
        base = "input line "
        for i in range(2 ** self._num_output_lines):
            if self._read_input_value(base + str(i + 1)):
                return i
        return -1

    @property
    def number_output_lines(self):
        return self._num_output_lines

    @property
    def value(self):
        if self._value is None:
            self._value = {key: False for key in self._outs}
            number = self._input_lines_to_number()
            idx = 1
            while number > 0:
                number, remainder = divmod(number, 2)
                self._value["output line " + str(idx)] = bool(remainder)
                idx += 1

        return self._value


class Decoder(BasicElement):
    """A class for decoder element.
    A decoder reads a number represented by n input lines and based on that turns on
    one of 2**n output lines.
    The interface of the encoder element is the following:
    - input:
        input line 1
        input line 2
        ...
        input line {num_input_lines}
    - output:
        output line 1
        output line 2
        ...
        output line {num_input_lines**2}
    """

    def __init__(self, id_, position=None, num_input_lines: int = 2):
        """Initialize a decoder with number of input lines and id.
        """
        if num_input_lines < 1:
            raise ValueError("Number of input lines must be >= 1")
        super().__init__(id_, position)
        self._num_input_lines = num_input_lines
        for i in range(1, num_input_lines + 1):
            self._ins[f'input line {i}'] = None
        for i in range(1, 2 ** num_input_lines + 1):
            self._outs[f'output line {i}'] = []
        self._element_type = "DECODER"

    def _input_lines_to_number(self):
        base = "input line "
        number = 0
        for i in range(self._num_input_lines):
            if self._read_input_value(base + str(i + 1)):
                number += 2 ** i
        return number + 1

    @property
    def number_input_lines(self):
        return self._num_input_lines

    @property
    def value(self):
        if self._value is None:
            self._value = {key: False for key in self._outs}
            self._value[f"output line {self._input_lines_to_number()}"] = True

        return self._value


class FullAdder(BasicElement):
    """A class for full adder element.
    A full adder element calculates the sum of three bits (2 summands and 1 carry) and outputs the
    sum and the resulting carry.
    The interface of the full adder element is the following:
    - input:
        A
        B
        Cin
    - output:
        S
        Cout
    """

    def __init__(self, id_, position=None):
        """Initialize a full adder element with id.
        """
        super().__init__(id_, position=position)
        self._ins['A'] = None
        self._ins['B'] = None
        self._ins['Cin'] = None
        self._outs['S'] = []
        self._outs['Cout'] = []
        self._element_type = "FULLADDER"

    @property
    def value(self):
        if self._value is None:
            bitA = self._read_input_value("A")
            bitB = self._read_input_value("B")
            carry_in = self._read_input_value('Cin')

            self._value = {'S': (bitA != bitB) != carry_in,
                           'Cout': (bitA and bitB) or (bitA and carry_in) or (bitB and carry_in)}

        return self._value


class AdderSubtractor(BasicElement):
    """A class for adder-subtractor element.
    An adder-subtractor element calculates the sum or the difference (based on the state of 'sub')
    of two n-digit numbers.
    The interface of an adder-subtractor element is the following:
    - input:
        A0
        A1
        ...
        A{num_bits-1}
        B0
        B1
        ...
        B{num_bits-1}
        sub
    - output:
        S0
        S1
        ...
        S{num_bits-1}
        Cout
    """

    def __init__(self, id_, position=None, num_bits: int = 4):
        """Initialize an adder/subtractor element with number of bits and id.
        """
        if num_bits < 1:
            raise ValueError("Number of bits must be >= 1")
        super().__init__(id_, position)
        self._num_bits = num_bits
        for i in range(num_bits):
            self._ins[f'A{i}'] = None
            self._ins[f'B{i}'] = None
        self._ins['sub'] = None
        for i in range(num_bits):
            self._outs[f'S{i}'] = []
        self._outs['Cout'] = []
        self._element_type = "ADDERSUBTRACTOR"

    def _get_number(self, base, invert=False):
        number = []
        for i in range(self._num_bits):
            val = self._read_input_value(base + str(i))
            number.append(val != invert)
        return number

    @property
    def number_bits(self):
        return self._num_bits

    @property
    def value(self):
        if self._value is None:
            sub = self._read_input_value('sub')
            number_A = self._get_number("A")
            number_B = self._get_number("B", sub)

            self._value = {}
            carry = sub
            for i in range(self._num_bits):
                self._value["S" + str(i)] = (number_A[i] != number_B[i]) != carry
                carry = (number_A[i] and number_B[i]) or (number_A[i] and carry) or (number_B[i] and carry)
            self._value['Cout'] = carry

        return self._value


class RightShifter(BasicElement):
    """A class for right shifter element.
    A right shifter element shifts bits by some number of bits that depends on which shift line is high.
    In cases when several or zero shift lines are high, the element behaves according to the scheme it implements.
    The following scheme is implemented in this class: images/schemes/right_shifter.png
    Note that it is reasonable to use this element with a decoder.
    The interface of a right shifter element is the following:
    - input:
        in0
        in1
        ...
        in{num_bits-1}
        shift_line0
        shift_line1
        ...
        shift_line{num_bits-1}
    - output:
        out0
        out1
        ...
        out{num_bits-1}
    """

    def __init__(self, id_, position=None, num_bits: int = 4):
        """Initialize a right shifter element with the number of bits and id.
        """
        if num_bits < 2:
            raise ValueError("Number of bits must be >= 2")
        super().__init__(id_, position=position)
        self._num_bits = num_bits
        for i in range(num_bits):
            self._ins[f'in{i}'] = None
            self._ins[f'shift_line{i}'] = None
            self._outs[f'out{i}'] = []
        self._element_type = "SHIFTER"

    def _read_input(self, base: str):
        number = []
        for i in range(self._num_bits):
            number.append(self._read_input_value(base + str(i)))
        return number

    @property
    def number_bits(self):
        return self._num_bits

    @property
    def value(self):
        if self._value is None:
            self._value = {}
            shift_by = self._read_input('shift_line')
            to_shift = self._read_input('in')
            for i in range(self._num_bits):
                self._value[f"out{i}"] = False
                for j in range(i + 1):
                    self._value[f"out{i}"] = self._value[f"out{i}"] or (to_shift[i - j] and shift_by[j])
        return self._value


class ForbiddenSrLatchStateError(Exception):
    """
    The exception is raised when both inputs S and R of SR latch equal to 1
    In such a case the output is determined randomly which is unacceptable in real electric circuits
    """
    def __init__(self):
        self.message = "The forbidden state of SR latch has been reached!"
        super().__init__(self.message)


class GatedSRFlipFlop(BasicElement):
    """A class for Gated SR (set - reset) flip-flop element.
    A Gated SR flip-flop can store a single bit.
    It can be either turned on or turned off.
    If it's turned on then it acts like regular SR latch
    It it's turned off then is doesn't react to any change of R and S and return saved output state
    The truth table of this element is the following:
    E = 1
        S = 0, R = 0 -> Q (initial or previous state)
        S = 1, R = 0 -> 1
        S = 0, R = 1 -> 0
        S = 1, R = 1 -> Forbidden SR latch state
    E = 0
        Return Q regardless of S and R states
    - input:
        S
        R
        E
    - output:
        Q
    """

    def __init__(self, id_, position=None, enable_state: bool = 1):
        """Initialize a gated SR flipflop element with id and, optionally,
        its position and initial enable state"""
        super().__init__(id_, position)
        self._ins[f'S'] = None
        self._ins[f'R'] = None
        self._outs[f'Q'] = []
        self._element_type = "SR_FLIPFLOP"
        self._q = 1
        self.enable_state = enable_state

    def _logic(self, s, r):
        if self.enable_state:
            if not s and not r:
                return self._q
            if not s and r:
                self._q = False
                return False
            if s and not r:
                self._q = True
                return True
            if s and r:
                raise ForbiddenSrLatchStateError()
        return self._q

    def switch_enable_state(self):
        self.enable_state = not self.enable_state

    @property
    def value(self):
        if self._value is None:
            output = self._logic(self._read_input_value('S'), self._read_input_value('R'))
            self._value = {'Q': output}
        return self._value


class GatedDFlipFlop(BasicElement):
    """A class for gated D (data) flip-flop element.
    A gated D flip-flop can store a single bit.
    It behaves exactly as gated SR flip flop but has 2 inputs instead of 3 and it always behaves predictably
    The truth table of this element is the following:
    E = 1
        D = Q -> Q
    E = 0
        Return Q regardless of D state
    - input:
        D
        E
    - output:
        Q
    """

    def __init__(self, id_, position=None, enable_state: bool = 1):
        """Initialize a gated D flipflop element with id and, optionally,
        its position and initial enable state"""
        super().__init__(id_, position)
        self._ins[f'D'] = None
        self._outs[f'Q'] = []
        self._element_type = "D_FLIPFLOP"
        self._q = False
        self.enable_state = enable_state

    def _logic(self, d):
        if self.enable_state:
            self._q = d
            return self._q
        return self._q

    def switch_enable_state(self):
        self.enable_state = not self.enable_state

    @property
    def value(self):
        if self._value is None:
            output = self._logic(self._read_input_value('D'))
            self._value = {'Q': output}
        return self._value


if __name__ == "__main__":
    constant = Constant("1", constant_value=False)
    or_gate = OrGate("2", num_inputs=2)

    connection = Connection(constant, 'out', or_gate, 'in1')
    or_gate.set_input_connection(connection)
    constant.set_output_connection(connection)

    print(or_gate.value)
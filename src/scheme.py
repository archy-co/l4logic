'''
scheme.py

Implements Scheme class and related exceptions
'''

from typing import Tuple
import copy
import src.elements as elements


class IdIsAlreadyTakenError(Exception):
    '''
    This exception is raised in Scheme add_element method if the id argument
    for this method is already taken by another element in the scheme
    '''
    def __init__(self, id_):
        self.message = f'ID <{id_}> is already taken'
        super().__init__(self.message)

class NoSuchIdError(Exception):
    '''
    This exception is raised when scheme element is being accessed with non-existent id
    '''
    def __init__(self, id_):
        self.message = f'There\'s no element with ID <{id_}>'
        super().__init__(self.message)

class NoSuchOutputLabelError(Exception):
    def __init__(self, output_label):
        self.message = f'There\'s no <{output_label}> output label'
        super().__init__(self.message)

class NoSuchInputLabelError(Exception):
    def __init__(self, input_label):
        self.message = f'There\'s no <{input_label}> input label'
        super().__init__(self.message)

class InputIsTakenError(Exception):
    '''
    This exception is raised in Scheme _validate_connection method when user tries
    to connect new element to already taken input of the existing element.

    This is not fatal Error, but user may have option to be informed about this
    occasion and may have an opporunity to tackle it.

    Also this exception can be handled without user interference, ignoring this
    exception it in main module
    '''
    def __init__(self, input_label):
        self.message = f'Input <{input_label}> is already taken'
        super().__init__(self.message)

class WrongElementTypeError(Exception):
    '''
    This exception is raised when specified element type represented by str does not
    match any class, so it can not be created
    '''
    def __init__(self, element_type):
        self.message = f'Element type <{element_type}> is does not exist or is not supported'
        super().__init__(self.message)


class Scheme:
    '''
    ADT Scheme that contains elements
    '''
    def __init__(self):
        self._elements = {}

    def add_element(self, element_type: str, element_id: str, position: Tuple[int, int], **kwargs):
        '''
        Validates element_id and element_type, then if they are valid,
        adds new element to the scheme at specified position
        '''
        elem_type_to_class_dct = {
            'multiplexer': elements.Multiplexer,
            'and': elements.AndGate,
            'or': elements.OrGate,
            'not': elements.NotGate,
            'nor': elements.NorGate,
            'xor': elements.XorGate,
            'nand': elements.NandGate,
            'constant': elements.Constant,
            'variable': elements.Variable,
            'decoder': elements.Decoder,
            'encoder': elements.Encoder,
            'fulladder': elements.FullAdder,
            'addersubtractor': elements.AdderSubtractor,
            'shifter': elements.RightShifter,
            'srflipflop': elements.GatedSRFlipFlop,
            'dflipflop': elements.GatedDFlipFlop
        }
        if not self._validate_id(element_id):
            raise IdIsAlreadyTakenError(element_id)

        try:
            new_element = elem_type_to_class_dct[element_type.lower()](element_id, position, **kwargs)
        except KeyError as keyerror:
            raise WrongElementTypeError(element_type) from keyerror

        self._elements[element_id] = new_element

    def _validate_id(self, id_: str) -> bool:
        '''
        Checks if the <id> is already assigned to an element in <self._elements> (there is
        an element with such id as key in the self._elements dictionary)
        Return:  True if id is available
                 False if id is already taken
        '''
        return not id_ in self._elements.keys()

    def add_connection(self, source_id, output_label, destination_id, input_label):
        '''
        Add connection from *output_label* output of element with id *source_id*
        to *input_label* input of element with id *destination_id* if validation
        is successful

        If there is no such output label / input label, corresponding Exception
        will be raised
        '''
        source = self._elements[source_id]
        destination = self._elements[destination_id]

        connection = elements.Connection(source, output_label, destination, input_label)
        self._validate_connection(connection)

        try:
            source.set_output_connection(connection)
        except KeyError as keyerror:
            raise NoSuchOutputLabelError(output_label) from keyerror

        destination.set_input_connection(connection)


    def _validate_connection(self, connection: elements.Connection):
        try:
            if connection.destination.ins[connection.input_label]:
                raise InputIsTakenError(connection.input_label)
        except KeyError as keyerror:
            raise NoSuchInputLabelError(connection.input_label) from keyerror

    def __getitem__(self, key):
        try:
            return self._elements[key]
        except KeyError as keyerror:
            raise NoSuchIdError(key) from keyerror

    def delete_element(self, element_id: str):
        '''
        Deletes element from scheme with all conections. Corresponding connections
        of connected elements are set to None
        '''
        if element_id not in self._elements.keys():
            raise NoSuchIdError(element_id)

        element = self._elements[element_id]

        for _out in element.outs:
            for out_connection in element.outs[_out]:
                out_connection.source.delete_output_connection(out_connection.output_label)
                out_connection.destination.delete_input_connection(out_connection.input_label)

        for _in in element.ins:
            in_connection = element.ins[_in]
            if in_connection is None:
                continue
            in_connection.source.delete_output_connection(in_connection.output_label)
            in_connection.destination.delete_input_connection(in_connection.input_label)

        self._elements.pop(element_id)

    def delete_connection(self, source_id: str, output_label: str,
                            destination_id: str, input_label: str):
        '''
        Deletes connection between elements by deliting source output and destination input
        '''
        source = self._elements[source_id]
        destination = self._elements[destination_id]

        source.delete_output_connection(output_label)
        destination.delete_input_connection(input_label)

    def _update_values(self, new_values):
        for id_ in new_values:
            self._elements[id_].value = new_values[id_]

    def run(self):
        values_to_update = {}
        for _ in range(len(self._elements)):
            for id_ in self._elements:
                values_to_update[id_] = self._elements[id_].calc_value(update=False)
            self._update_values(values_to_update)

        records_of_out_values = []
        final_out_values = copy.deepcopy(values_to_update)

        while True:
            cur_out_values = {}
            for element_id in self._elements:
                cur_out_values[element_id] = self._elements[element_id].calc_value()
                for out_name in cur_out_values[element_id]:
                    if cur_out_values[element_id][out_name] != final_out_values[element_id][out_name]:
                        final_out_values[element_id][out_name] = None
            if cur_out_values in records_of_out_values:
                # current values was previously encountered, so we went through the whole period
                break
            records_of_out_values.append(cur_out_values)

        return final_out_values

    def __iter__(self):
        return iter(self._elements.values())

    def _reset(self):
        for element in self._elements.values():
            element.reset_value()

    def move(self, element_id, new_position):
        '''
        Moves element with element_id to new_position
        '''
        self._elements[element_id].position = new_position

    def __str__(self):
        return str(list(self._elements.items()))

    def clear(self):
        '''
        Deletes all elements from scheme and their connections
        '''
        iter_elements = self._elements.copy()
        for elem_id in iter_elements.keys():
            self.delete_element(elem_id)


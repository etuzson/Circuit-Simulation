class Component:

    def __init__(self):
        # [value, [[inner_component1_index, inner_component1_input_index], [], ... ]]
        self.inputs = []
        # [index: [value, inner_component_index, inner_component_output_index]]
        self.outputs = []
        # {inner_component_index: [[inner_component_output_index, inner_component_index, inner_component_input_index]]]}
        self.inner_links = {}
        self.inner_components = []

    def set_input(self, index, value):
        self.inputs[index][0] = value

    def set_inputs_from_array(self, input_array):
        for i, value in enumerate(input_array):
            self.inputs[i][0] = value

    def get_input(self, index):
        return self.inputs[index][0]

    def get_output(self, index):
        return self.outputs[index][0]

    def get_all_outputs(self):
        outputs = []
        for out in self.outputs:
            value = out[0]
            outputs.append(value)
        return outputs

    def connect_input(self, index, inner_component_index, inner_component_input_index, default_value=0):
        if index > len(self.inputs):
            raise ValueError(f"Next index has to be {len(self.inputs)}")
        if index < len(self.inputs):
            inp = self.inputs[index]
            connections = inp[1]
            connections.append([inner_component_index, inner_component_input_index])
        else:
            self.inputs.insert(index, [default_value, [[inner_component_index, inner_component_input_index]]])

    def disconnect_input(self, index, inner_component_index, inner_component_input_index):
        if index > len(self.inputs):
            raise ValueError(f"Index out of range of array of inputs")
        inp = self.inputs[index]
        connections = inp[1]
        connections.remove([inner_component_index, inner_component_input_index])

    def connect_output(self, index, inner_component_index, inner_component_output_index):
        self.outputs.append([index, inner_component_index, inner_component_output_index])

    def connect_inner_components(self, out_component_index, out_component_output_index, in_component_index, in_component_input_index):
        link = self.inner_links.get(out_component_index)
        if link is None:
            self.inner_links[out_component_index] = [[out_component_output_index, in_component_index, in_component_input_index]]
        else:
            link.append([out_component_output_index, in_component_index, in_component_input_index])

    def evaluate(self):
        for inp in self.inputs:
            value = inp[0]
            inner_components = inp[1]
            for inner_component in inner_components:
                inner_component_index = inner_component[0]
                inner_component_input_index = inner_component[1]
                self.inner_components[inner_component_index].set_input(inner_component_input_index, value)
        for index, inner_component in enumerate(self.inner_components):
            inner_component.evaluate()
            links = self.inner_links.get(index)
            if links is not None:
                for out in links:
                    out_index = out[0]
                    inner_component_index = out[1]
                    inner_component_input_index = out[2]
                    self.inner_components[inner_component_index].set_input(inner_component_input_index, inner_component.get_output(out_index))
        for out in self.outputs:
            inner_component_index = out[1]
            inner_component_output_index = out[2]
            out[0] = self.inner_components[inner_component_index].get_output(inner_component_output_index)


class AndGate(Component):

    def __init__(self):
        super().__init__()
        self.inputs = [[0, None, None], [0, None, None]]
        self.outputs = [[0, None, None]]

    def evaluate(self):
        if self.get_input(0) and self.get_input(1):
            self.outputs[0] = [1, None, None]
        else:
            self.outputs[0] = [0, None, None]


class OrGate(Component):

    def __init__(self):
        super().__init__()
        self.inputs = [[0, None, None], [0, None, None]]
        self.outputs = [[0, None, None]]

    def evaluate(self):
        if self.get_input(0) or self.get_input(1):
            self.outputs[0] = [1, None, None]
        else:
            self.outputs[0] = [0, None, None]


class NandGate(Component):

    def __init__(self):
        super().__init__()
        self.inputs = [[0, None, None], [0, None, None]]
        self.outputs = [[1, None, None]]

    def evaluate(self):
        if self.get_input(0) and self.get_input(1):
            self.outputs[0] = [0, None, None]
        else:
            self.outputs[0] = [1, None, None]


class NorGate(Component):

    def __init__(self):
        super().__init__()
        self.inputs = [[0, None, None], [0, None, None]]
        self.outputs = [[1, None, None]]

    def evaluate(self):
        if not self.get_input(0) and not self.get_input(1):
            self.outputs[0] = [1, None, None]
        else:
            self.outputs[0] = [0, None, None]


class NotGate(Component):

    def __init__(self):
        super().__init__()
        self.inputs = [[0, None, None]]
        self.outputs = [[1, None, None]]

    def evaluate(self):
        if self.get_input(0):
            self.outputs[0] = [0, None, None]
        else:
            self.outputs[0] = [1, None, None]


class XorGate(Component):

    def __init__(self):
        super().__init__()
        self.connect_input(0, 0, 0)  # Inp 0 to Inp 0 of OrGate
        self.connect_input(1, 0, 1)  # Inp 1 to Inp 1 of OrGate
        self.connect_input(0, 1, 0)  # Inp 0 to Inp 0 of NandGate
        self.connect_input(1, 1, 1)  # Inp 1 to Inp 1 of NandGate
        self.connect_output(0, 2, 0)  # Out 0 of AndGate to Out 0 of Component
        self.connect_inner_components(0, 0, 2, 0)  # Out 0 of OrGate to Inp 0 of AndGate
        self.connect_inner_components(1, 0, 2, 1)  # Out 0 of NandGate to Inp 1 of AndGate
        self.inner_components = [OrGate(), NandGate(), AndGate()]


class HalfAdder(Component):

    def __init__(self):
        super().__init__()
        self.connect_input(0, 0, 0)
        self.connect_input(1, 0, 1)
        self.connect_input(0, 1, 0)
        self.connect_input(1, 1, 1)
        # 0: result, 1: carry
        self.connect_output(0, 0, 0)
        self.connect_output(0, 1, 0)
        self.inner_components = [XorGate(), AndGate()]


class TwoBitAddressDecoder(Component):

    def __init__(self):
        super().__init__()
        # A and B
        self.connect_input(0, 0, 0)
        self.connect_input(1, 0, 1)
        # A and not B
        self.connect_input(0, 1, 0)
        self.connect_input(1, 2, 0)
        # not A and B
        self.connect_input(0, 3, 0)
        self.connect_input(1, 4, 1)
        # A nor B
        self.connect_input(0, 5, 0)
        self.connect_input(1, 5, 1)
        self.connect_output(0, 0, 0)
        self.connect_output(1, 1, 0)
        self.connect_output(2, 4, 0)
        self.connect_output(3, 5, 0)
        self.connect_inner_components(2, 0, 1, 1)
        self.connect_inner_components(3, 0, 4, 0)
        self.inner_components = [AndGate(), AndGate(), NotGate(), NotGate(), AndGate(), NorGate()]


class TwoToOneMultiplexer(Component):

    def __init__(self):
        super().__init__()
        self.connect_input(0, 0, 0)  # Inp 0 to AndGate 0 Inp 0
        self.connect_input(1, 2, 0)  # Inp 1 to AndGate 1 Inp 0
        self.connect_input(2, 0, 1)  # Inp S to AndGate 0 Inp 1
        self.connect_input(2, 1, 0)  # Inp S to NotGate Inp 0
        self.connect_inner_components(1, 0, 2, 1)  # NotGate Out 0 to AndGate 1 Inp 1
        self.connect_inner_components(0, 0, 3, 0)  # AndGate 0 Out 0 to OrGate Inp 0
        self.connect_inner_components(2, 0, 3, 1)  # AndGate 1 Out 0 to OrGate Inp 1
        self.connect_output(0, 3, 0)
        self.inner_components = [AndGate(), NotGate(), AndGate(), OrGate()]


class FullAdder(Component):

    def __init__(self):
        super().__init__()
        self.connect_input(0, 0, 0)  # Inp 0 to XorGate 0 Inp 0
        self.connect_input(1, 0, 1)  # Inp 1 to XorGate 0 Inp 1
        self.connect_input(2, 1, 0)  # Inp 2 to XorGate 1 Inp 0
        self.connect_input(0, 2, 0)  # Inp 0 to AndGate 0 Inp 0
        self.connect_input(1, 2, 1)  # Inp 1 to AndGate 0 Inp 1
        self.connect_input(0, 3, 0)  # Inp 0 to AndGate 1 Inp 0
        self.connect_input(2, 3, 1)  # Inp 2 to AndGate 1 Inp 1
        self.connect_input(1, 4, 0)  # Inp 1 to AndGate 2 Inp 0
        self.connect_input(2, 4, 1)  # Inp 2 to AndGate 2 Inp 1
        self.connect_inner_components(0, 0, 1, 1)  # XorGate 0 output to XorGate 1 Inp 1
        self.connect_inner_components(2, 0, 5, 0)  # AndGate 0 output to OrGate 0 Inp 0
        self.connect_inner_components(3, 0, 5, 1)  # AndGate 1 output to OrGate 0 Inp 1
        self.connect_inner_components(4, 0, 6, 0)  # AndGate 2 output to OrGate 1 Inp 0
        self.connect_inner_components(5, 0, 6, 1)  # OrGate 0 output to OrGate 1 Inp 1
        self.connect_output(0, 1, 0)  # XorGate 1 output sum
        self.connect_output(1, 6, 0)  # OrGate 1 output carry
        self.inner_components = [XorGate(), XorGate(), AndGate(), AndGate(), AndGate(), OrGate(), OrGate()]


class EightBitBinaryAdder(Component):

    def __init__(self):
        super().__init__()
        self.connect_input(0, 7, 1)  # Inp 0 to FullAdder 6 Inp 1
        self.connect_input(1, 6, 1)  # Inp 1 to FullAdder 5 Inp 1
        self.connect_input(2, 5, 1)  # Inp 2 to FullAdder 4 Inp 1
        self.connect_input(3, 4, 1)  # Inp 3 to FullAdder 3 Inp 1
        self.connect_input(4, 3, 1)  # Inp 4 to FullAdder 2 Inp 1
        self.connect_input(5, 2, 1)  # Inp 5 to FullAdder 1 Inp 1
        self.connect_input(6, 1, 1)  # Inp 6 to FullAdder 0 Inp 1
        self.connect_input(7, 0, 1)  # Inp 7 to HalfAdder Inp 1
        self.connect_input(8, 7, 0)  # Inp 8 to FullAdder 6 Inp 0
        self.connect_input(9, 6, 0)  # Inp 9 to FullAdder 5 Inp 0
        self.connect_input(10, 5, 0)  # Inp 10 to FullAdder 4 Inp 0
        self.connect_input(11, 4, 0)  # Inp 11 to FullAdder 3 Inp 0
        self.connect_input(12, 3, 0)  # Inp 12 to FullAdder 2 Inp 0
        self.connect_input(13, 2, 0)  # Inp 13 to FullAdder 1 Inp 0
        self.connect_input(14, 1, 0)  # Inp 14 to FullAdder 0 Inp 0
        self.connect_input(15, 0, 0)  # Inp 15 to HalfAdder Inp 0
        self.connect_inner_components(0, 1, 1, 2)  # HalfAdder carry to FullAdder 0 Inp 2
        self.connect_inner_components(1, 1, 2, 2)  # FullAdder 0 carry to FullAdder 1 Inp 2
        self.connect_inner_components(2, 1, 3, 2)  # FullAdder 1 carry to FullAdder 1 Inp 2
        self.connect_inner_components(3, 1, 4, 2)  # FullAdder 2 carry to FullAdder 1 Inp 2
        self.connect_inner_components(4, 1, 5, 2)  # FullAdder 3 carry to FullAdder 1 Inp 2
        self.connect_inner_components(5, 1, 6, 2)  # FullAdder 4 carry to FullAdder 1 Inp 2
        self.connect_inner_components(6, 1, 7, 2)  # FullAdder 5 carry to FullAdder 1 Inp 2
        self.connect_output(0, 7, 1)  # FullAdder 6 carry to Out 0
        self.connect_output(1, 7, 0)  # FullAdder 6 sum to Out 1
        self.connect_output(2, 6, 0)  # FullAdder 5 sum to Out 2
        self.connect_output(3, 5, 0)  # FullAdder 4 sum to Out 3
        self.connect_output(4, 4, 0)  # FullAdder 3 sum to Out 4
        self.connect_output(5, 3, 0)  # FullAdder 2 sum to Out 5
        self.connect_output(6, 2, 0)  # FullAdder 1 sum to Out 6
        self.connect_output(7, 1, 0)  # FullAdder 0 sum to Out 7
        self.connect_output(8, 0, 0)  # HalfAdder sum to Out 8
        self.inner_components = [HalfAdder(), FullAdder(), FullAdder(), FullAdder(), FullAdder(), FullAdder(), FullAdder(), FullAdder()]


class TwoBit2sComplementAdderSubtractor(Component):

    def __init__(self):
        super().__init__()
        self.connect_input(0, 1, 0)  # Inp 0 to FullAdder Inp 0
        self.connect_input(1, 0, 0)  # Inp 1 to XorGate Inp 0
        self.connect_input(2, 0, 1)  # Inp 2 to XorGate Inp 1
        self.connect_input(3, 1, 2)  # Inp 3 to FullAdder Inp 2 carry
        self.connect_inner_components(0, 0, 1, 1)  # XorGate to FullAdder Inp 1
        self.connect_output(0, 1, 0)  # Out 0 sum
        self.connect_output(1, 1, 1)  # Out 1 carry
        self.inner_components = [XorGate(), FullAdder()]


class EightBit2sComplementAdderSubtractor(Component):

    def __init__(self):
        super().__init__()
        self.connect_input(0, 7, 0)  # Inp 0 to Adder 7 Inp 0
        self.connect_input(1, 6, 0)  # Inp 1 to Adder 6 Inp 0
        self.connect_input(2, 5, 0)  # Inp 2 to Adder 5 Inp 0
        self.connect_input(3, 4, 0)  # Inp 3 to Adder 4 Inp 0
        self.connect_input(4, 3, 0)  # Inp 4 to Adder 3 Inp 0
        self.connect_input(5, 2, 0)  # Inp 5 to Adder 2 Inp 0
        self.connect_input(6, 1, 0)  # Inp 6 to Adder 1 Inp 0
        self.connect_input(7, 0, 0)  # Inp 7 to Adder 0 Inp 0
        self.connect_input(8, 7, 1)  # Inp 8 to Adder 7 Inp 1
        self.connect_input(9, 6, 1)  # Inp 9 to Adder 6 Inp 1
        self.connect_input(10, 5, 1)  # Inp 10 to Adder 5 Inp 1
        self.connect_input(11, 4, 1)  # Inp 11 to Adder 4 Inp 1
        self.connect_input(12, 3, 1)  # Inp 12 to Adder 3 Inp 1
        self.connect_input(13, 2, 1)  # Inp 13 to Adder 2 Inp 1
        self.connect_input(14, 1, 1)  # Inp 14 to Adder 1 Inp 1
        self.connect_input(15, 0, 1)  # Inp 15 to Adder 0 Inp 1
        self.connect_input(16, 7, 2)  # Inp 16 to Adder 7 Inp 2
        self.connect_input(16, 6, 2)  # Inp 16 to Adder 6 Inp 2
        self.connect_input(16, 5, 2)  # Inp 16 to Adder 5 Inp 2
        self.connect_input(16, 4, 2)  # Inp 16 to Adder 4 Inp 2
        self.connect_input(16, 3, 2)  # Inp 16 to Adder 3 Inp 2
        self.connect_input(16, 2, 2)  # Inp 16 to Adder 2 Inp 2
        self.connect_input(16, 1, 2)  # Inp 16 to Adder 1 Inp 2
        self.connect_input(16, 0, 2)  # Inp 16 to Adder 0 Inp 2
        self.connect_input(16, 0, 3)  # Inp 16 to Adder 0 Inp 3
        self.connect_inner_components(0, 1, 1, 3)  # Adder 0 carry to Adder 1 carry inp
        self.connect_inner_components(1, 1, 2, 3)  # Adder 1 carry to Adder 2 carry inp
        self.connect_inner_components(2, 1, 3, 3)  # Adder 2 carry to Adder 3 carry inp
        self.connect_inner_components(3, 1, 4, 3)  # Adder 3 carry to Adder 4 carry inp
        self.connect_inner_components(4, 1, 5, 3)  # Adder 4 carry to Adder 5 carry inp
        self.connect_inner_components(5, 1, 6, 3)  # Adder 5 carry to Adder 6 carry inp
        self.connect_inner_components(6, 1, 7, 3)  # Adder 5 carry to Adder 6 carry inp
        self.connect_output(0, 7, 1)  # Out 0 to Adder 0 carry
        self.connect_output(1, 7, 0)  # Out 1 to Adder 7 sum
        self.connect_output(2, 6, 0)  # Out 2 to Adder 6 sum
        self.connect_output(3, 5, 0)  # Out 3 to Adder 5 sum
        self.connect_output(4, 4, 0)  # Out 4 to Adder 4 sum
        self.connect_output(5, 3, 0)  # Out 5 to Adder 3 sum
        self.connect_output(6, 2, 0)  # Out 6 to Adder 2 sum
        self.connect_output(7, 1, 0)  # Out 7 to Adder 1 sum
        self.connect_output(8, 0, 0)  # Out 8 to Adder 0 sum
        self.inner_components = [TwoBit2sComplementAdderSubtractor(), TwoBit2sComplementAdderSubtractor(), TwoBit2sComplementAdderSubtractor(),
                                 TwoBit2sComplementAdderSubtractor(), TwoBit2sComplementAdderSubtractor(), TwoBit2sComplementAdderSubtractor(),
                                 TwoBit2sComplementAdderSubtractor(), TwoBit2sComplementAdderSubtractor()]


if __name__ == "__main__":
    and_gate = AndGate()
    assert and_gate.get_output(0) == 0
    and_gate.set_input(0, 1)
    and_gate.set_input(1, 1)
    and_gate.evaluate()
    assert and_gate.get_output(0) == 1
    and_gate.set_input(0, 0)
    and_gate.set_input(1, 1)
    and_gate.evaluate()
    assert and_gate.get_output(0) == 0
    and_gate.set_input(0, 1)
    and_gate.set_input(1, 0)
    and_gate.evaluate()
    assert and_gate.get_output(0) == 0
    and_gate.set_input(0, 0)
    and_gate.set_input(1, 0)
    and_gate.evaluate()
    assert and_gate.get_output(0) == 0

    or_gate = OrGate()
    assert or_gate.get_output(0) == 0
    or_gate.set_input(0, 1)
    or_gate.set_input(1, 1)
    or_gate.evaluate()
    assert or_gate.get_output(0) == 1
    or_gate.set_input(0, 1)
    or_gate.set_input(1, 0)
    or_gate.evaluate()
    assert or_gate.get_output(0) == 1
    or_gate.set_input(0, 0)
    or_gate.set_input(1, 1)
    or_gate.evaluate()
    assert or_gate.get_output(0) == 1
    or_gate.set_input(0, 0)
    or_gate.set_input(1, 0)
    or_gate.evaluate()
    assert or_gate.get_output(0) == 0

    not_gate = NotGate()
    assert not_gate.get_output(0) == 1
    not_gate.set_input(0, 1)
    not_gate.evaluate()
    assert not_gate.get_output(0) == 0
    not_gate.set_input(0, 0)
    not_gate.evaluate()
    assert not_gate.get_output(0) == 1

    nand_gate = NandGate()
    assert nand_gate.get_output(0) == 1
    nand_gate.set_input(0, 1)
    nand_gate.set_input(1, 1)
    nand_gate.evaluate()
    assert nand_gate.get_output(0) == 0
    nand_gate.set_input(0, 0)
    nand_gate.set_input(1, 1)
    nand_gate.evaluate()
    assert nand_gate.get_output(0) == 1
    nand_gate.set_input(0, 1)
    nand_gate.set_input(1, 0)
    nand_gate.evaluate()
    assert nand_gate.get_output(0) == 1
    nand_gate.set_input(0, 0)
    nand_gate.set_input(1, 0)
    nand_gate.evaluate()
    assert nand_gate.get_output(0) == 1

    nor_gate = NorGate()
    assert nor_gate.get_output(0) == 1
    nor_gate.set_input(0, 1)
    nor_gate.set_input(1, 1)
    nor_gate.evaluate()
    assert nor_gate.get_output(0) == 0
    nor_gate.set_input(0, 0)
    nor_gate.set_input(1, 1)
    nor_gate.evaluate()
    assert nor_gate.get_output(0) == 0
    nor_gate.set_input(0, 1)
    nor_gate.set_input(1, 0)
    nor_gate.evaluate()
    assert nor_gate.get_output(0) == 0
    nor_gate.set_input(0, 0)
    nor_gate.set_input(1, 0)
    nor_gate.evaluate()
    assert nor_gate.get_output(0) == 1

    xor_gate = XorGate()
    assert xor_gate.get_output(0) == 0
    xor_gate.set_input(0, 1)
    xor_gate.set_input(1, 1)
    xor_gate.evaluate()
    assert xor_gate.get_output(0) == 0
    xor_gate.set_input(0, 0)
    xor_gate.set_input(1, 0)
    xor_gate.evaluate()
    assert xor_gate.get_output(0) == 0
    xor_gate.set_input(0, 0)
    xor_gate.set_input(1, 1)
    xor_gate.evaluate()
    assert xor_gate.get_output(0) == 1
    xor_gate.set_input(0, 1)
    xor_gate.set_input(1, 0)
    xor_gate.evaluate()
    assert xor_gate.get_output(0) == 1

    half_adder = HalfAdder()
    assert half_adder.get_output(0) == 0  # sum
    assert half_adder.get_output(1) == 0  # carry
    half_adder.set_input(0, 1)
    half_adder.set_input(1, 1)
    half_adder.evaluate()
    assert half_adder.get_output(0) == 0
    assert half_adder.get_output(1) == 1
    half_adder.set_input(0, 0)
    half_adder.set_input(1, 1)
    half_adder.evaluate()
    assert half_adder.get_output(0) == 1
    assert half_adder.get_output(1) == 0
    half_adder.set_input(0, 1)
    half_adder.set_input(1, 0)
    half_adder.evaluate()
    assert half_adder.get_output(0) == 1
    assert half_adder.get_output(1) == 0
    half_adder.set_input(0, 0)
    half_adder.set_input(1, 0)
    half_adder.evaluate()
    assert half_adder.get_output(0) == 0
    assert half_adder.get_output(1) == 0

    address_decoder = TwoBitAddressDecoder()
    address_decoder.set_input(0, 0)
    address_decoder.set_input(1, 0)
    address_decoder.evaluate()
    assert address_decoder.get_output(0) == 0
    assert address_decoder.get_output(1) == 0
    assert address_decoder.get_output(2) == 0
    assert address_decoder.get_output(3) == 1
    address_decoder.set_input(0, 1)
    address_decoder.set_input(1, 0)
    address_decoder.evaluate()
    assert address_decoder.get_output(0) == 0
    assert address_decoder.get_output(1) == 1
    assert address_decoder.get_output(2) == 0
    assert address_decoder.get_output(3) == 0
    address_decoder.set_input(0, 0)
    address_decoder.set_input(1, 1)
    address_decoder.evaluate()
    assert address_decoder.get_output(0) == 0
    assert address_decoder.get_output(1) == 0
    assert address_decoder.get_output(2) == 1
    assert address_decoder.get_output(3) == 0
    address_decoder.set_input(0, 1)
    address_decoder.set_input(1, 1)
    address_decoder.evaluate()
    assert address_decoder.get_output(0) == 1
    assert address_decoder.get_output(1) == 0
    assert address_decoder.get_output(2) == 0
    assert address_decoder.get_output(3) == 0

    multiplexer2to1 = TwoToOneMultiplexer()
    multiplexer2to1.set_input(0, 0)
    multiplexer2to1.set_input(1, 0)
    multiplexer2to1.set_input(2, 1)  # Selector bit
    multiplexer2to1.evaluate()
    assert multiplexer2to1.get_output(0) == 0
    multiplexer2to1.set_input(0, 0)
    multiplexer2to1.set_input(1, 1)
    multiplexer2to1.set_input(2, 1)  # Selector bit
    multiplexer2to1.evaluate()
    assert multiplexer2to1.get_output(0) == 0
    multiplexer2to1.set_input(0, 1)
    multiplexer2to1.set_input(1, 0)
    multiplexer2to1.set_input(2, 1)  # Selector bit
    multiplexer2to1.evaluate()
    assert multiplexer2to1.get_output(0) == 1
    multiplexer2to1.set_input(0, 1)
    multiplexer2to1.set_input(1, 1)
    multiplexer2to1.set_input(2, 1)  # Selector bit
    multiplexer2to1.evaluate()
    assert multiplexer2to1.get_output(0) == 1
    multiplexer2to1.set_input(0, 0)
    multiplexer2to1.set_input(1, 0)
    multiplexer2to1.set_input(2, 0)  # Selector bit
    multiplexer2to1.evaluate()
    assert multiplexer2to1.get_output(0) == 0
    multiplexer2to1.set_input(0, 1)
    multiplexer2to1.set_input(1, 0)
    multiplexer2to1.set_input(2, 0)  # Selector bit
    multiplexer2to1.evaluate()
    assert multiplexer2to1.get_output(0) == 0
    multiplexer2to1.set_input(0, 0)
    multiplexer2to1.set_input(1, 1)
    multiplexer2to1.set_input(2, 0)  # Selector bit
    multiplexer2to1.evaluate()
    assert multiplexer2to1.get_output(0) == 1
    multiplexer2to1.set_input(0, 1)
    multiplexer2to1.set_input(1, 1)
    multiplexer2to1.set_input(2, 0)  # Selector bit
    multiplexer2to1.evaluate()
    assert multiplexer2to1.get_output(0) == 1

    full_adder = FullAdder()
    full_adder.set_input(0, 0)
    full_adder.set_input(1, 0)
    full_adder.set_input(2, 0)
    full_adder.evaluate()
    assert full_adder.get_output(0) == 0  # sum
    assert full_adder.get_output(1) == 0  # carry
    full_adder.set_input(0, 0)
    full_adder.set_input(1, 0)
    full_adder.set_input(2, 1)
    full_adder.evaluate()
    assert full_adder.get_output(0) == 1  # sum
    assert full_adder.get_output(1) == 0  # carry
    full_adder.set_input(0, 0)
    full_adder.set_input(1, 1)
    full_adder.set_input(2, 0)
    full_adder.evaluate()
    assert full_adder.get_output(0) == 1  # sum
    assert full_adder.get_output(1) == 0  # carry
    full_adder.set_input(0, 1)
    full_adder.set_input(1, 0)
    full_adder.set_input(2, 0)
    full_adder.evaluate()
    assert full_adder.get_output(0) == 1  # sum
    assert full_adder.get_output(1) == 0  # carry
    full_adder.set_input(0, 0)
    full_adder.set_input(1, 1)
    full_adder.set_input(2, 1)
    full_adder.evaluate()
    assert full_adder.get_output(0) == 0  # sum
    assert full_adder.get_output(1) == 1  # carry
    full_adder.set_input(0, 1)
    full_adder.set_input(1, 0)
    full_adder.set_input(2, 1)
    full_adder.evaluate()
    assert full_adder.get_output(0) == 0  # sum
    assert full_adder.get_output(1) == 1  # carry
    full_adder.set_input(0, 1)
    full_adder.set_input(1, 1)
    full_adder.set_input(2, 0)
    full_adder.evaluate()
    assert full_adder.get_output(0) == 0  # sum
    assert full_adder.get_output(1) == 1  # carry
    full_adder.set_input(0, 1)
    full_adder.set_input(1, 1)
    full_adder.set_input(2, 1)
    full_adder.evaluate()
    assert full_adder.get_output(0) == 1  # sum
    assert full_adder.get_output(1) == 1  # carry

    binary_adder = EightBitBinaryAdder()
    # Add 00000000 + 00000000
    binary_adder.set_inputs_from_array([0 for i in range(0, 16)])
    binary_adder.evaluate()
    assert binary_adder.get_all_outputs() == [0, 0, 0, 0, 0, 0, 0, 0, 0]
    # Add 00000000 + 00000001
    binary_adder.set_inputs_from_array([0, 0, 0, 0, 0, 0, 0, 0,
                                        0, 0, 0, 0, 0, 0, 0, 1])
    binary_adder.evaluate()
    assert binary_adder.get_all_outputs() == [0, 0, 0, 0, 0, 0, 0, 0, 1]
    # Add 00000001 + 00000001
    binary_adder.set_inputs_from_array([0, 0, 0, 0, 0, 0, 0, 1,
                                        0, 0, 0, 0, 0, 0, 0, 1])
    binary_adder.evaluate()
    assert binary_adder.get_all_outputs() == [0, 0, 0, 0, 0, 0, 0, 1, 0]
    # Add 10101010 + 11001100
    binary_adder.set_inputs_from_array([1, 0, 1, 0, 1, 0, 1, 0,
                                        1, 1, 0, 0, 1, 1, 0, 0])
    binary_adder.evaluate()
    assert binary_adder.get_all_outputs() == [1, 0, 1, 1, 1, 0, 1, 1, 0]
    # Add 11111111 + 11111111
    binary_adder.set_inputs_from_array([1, 1, 1, 1, 1, 1, 1, 1,
                                        1, 1, 1, 1, 1, 1, 1, 1])
    binary_adder.evaluate()
    assert binary_adder.get_all_outputs() == [1, 1, 1, 1, 1, 1, 1, 1, 0]

    basic_adder_subtractor = TwoBit2sComplementAdderSubtractor()
    basic_adder_subtractor.set_input(0, 0)
    basic_adder_subtractor.set_input(1, 0)
    basic_adder_subtractor.set_input(2, 0)  # Subtract bit 1 = subtract, 0 = add
    basic_adder_subtractor.set_input(3, 0)  # These 2 should be the same, in the basic version they are connected, in the n-bit version they are different inputs
    basic_adder_subtractor.evaluate()
    assert basic_adder_subtractor.get_output(0) == 0  # Sum
    assert basic_adder_subtractor.get_output(1) == 0  # Carry
    basic_adder_subtractor.set_input(0, 1)
    basic_adder_subtractor.set_input(1, 0)
    basic_adder_subtractor.set_input(2, 0)  # Subtract bit 1 = subtract, 0 = add
    basic_adder_subtractor.set_input(3, 0)
    basic_adder_subtractor.evaluate()
    assert basic_adder_subtractor.get_output(0) == 1  # Sum
    assert basic_adder_subtractor.get_output(1) == 0  # Carry
    basic_adder_subtractor.set_input(0, 0)
    basic_adder_subtractor.set_input(1, 1)
    basic_adder_subtractor.set_input(2, 0)  # Subtract bit 1 = subtract, 0 = add
    basic_adder_subtractor.set_input(3, 0)
    basic_adder_subtractor.evaluate()
    assert basic_adder_subtractor.get_output(0) == 1  # Sum
    assert basic_adder_subtractor.get_output(1) == 0  # Carry
    basic_adder_subtractor.set_input(0, 1)
    basic_adder_subtractor.set_input(1, 1)
    basic_adder_subtractor.set_input(2, 0)  # Subtract bit 1 = subtract, 0 = add
    basic_adder_subtractor.set_input(3, 0)
    basic_adder_subtractor.evaluate()
    assert basic_adder_subtractor.get_output(0) == 0  # Sum
    assert basic_adder_subtractor.get_output(1) == 1  # Carry
    basic_adder_subtractor.set_input(0, 0)
    basic_adder_subtractor.set_input(1, 0)
    basic_adder_subtractor.set_input(2, 1)  # Subtract bit 1 = subtract, 0 = add
    basic_adder_subtractor.set_input(3, 1)
    basic_adder_subtractor.evaluate()
    assert basic_adder_subtractor.get_output(0) == 0  # Sum
    assert basic_adder_subtractor.get_output(1) == 1  # Carry
    basic_adder_subtractor.set_input(0, 1)
    basic_adder_subtractor.set_input(1, 0)
    basic_adder_subtractor.set_input(2, 1)  # Subtract bit 1 = subtract, 0 = add
    basic_adder_subtractor.set_input(3, 1)
    basic_adder_subtractor.evaluate()
    assert basic_adder_subtractor.get_output(0) == 1  # Sum
    assert basic_adder_subtractor.get_output(1) == 1  # Carry
    basic_adder_subtractor.set_input(0, 0)
    basic_adder_subtractor.set_input(1, 1)
    basic_adder_subtractor.set_input(2, 1)  # Subtract bit 1 = subtract, 0 = add
    basic_adder_subtractor.set_input(3, 1)
    basic_adder_subtractor.evaluate()
    assert basic_adder_subtractor.get_output(0) == 1  # Sum
    assert basic_adder_subtractor.get_output(1) == 0  # Carry
    basic_adder_subtractor.set_input(0, 1)
    basic_adder_subtractor.set_input(1, 1)
    basic_adder_subtractor.set_input(2, 1)  # Subtract bit 1 = subtract, 0 = add
    basic_adder_subtractor.set_input(3, 1)
    basic_adder_subtractor.evaluate()
    assert basic_adder_subtractor.get_output(0) == 0  # Sum
    assert basic_adder_subtractor.get_output(1) == 1  # Carry

    adder_subtractor = EightBit2sComplementAdderSubtractor()
    # 0 + 0
    adder_subtractor.set_inputs_from_array([0, 0, 0, 0, 0, 0, 0, 0,
                                            0, 0, 0, 0, 0, 0, 0, 0,
                                            0])  # Last bit is subtract signal
    adder_subtractor.evaluate()
    assert adder_subtractor.get_all_outputs() == [0, 0, 0, 0, 0, 0, 0, 0, 0]
    # 1 + 0
    adder_subtractor.set_inputs_from_array([0, 0, 0, 0, 0, 0, 0, 1,
                                            0, 0, 0, 0, 0, 0, 0, 0,
                                            0])  # Last bit is subtract signal
    adder_subtractor.evaluate()
    assert adder_subtractor.get_all_outputs() == [0, 0, 0, 0, 0, 0, 0, 0, 1]
    # 1 + 1
    adder_subtractor.set_inputs_from_array([0, 0, 0, 0, 0, 0, 0, 1,
                                            0, 0, 0, 0, 0, 0, 0, 1,
                                            0])  # Last bit is subtract signal
    adder_subtractor.evaluate()
    assert adder_subtractor.get_all_outputs() == [0, 0, 0, 0, 0, 0, 0, 1, 0]
    # 0 - 0
    adder_subtractor.set_inputs_from_array([0, 0, 0, 0, 0, 0, 0, 0,
                                            0, 0, 0, 0, 0, 0, 0, 0,
                                            1])  # Last bit is subtract signal
    adder_subtractor.evaluate()
    assert adder_subtractor.get_all_outputs() == [1, 0, 0, 0, 0, 0, 0, 0, 0]
    # 1 - 0
    adder_subtractor.set_inputs_from_array([0, 0, 0, 0, 0, 0, 0, 1,
                                            0, 0, 0, 0, 0, 0, 0, 0,
                                            1])  # Last bit is subtract signal
    adder_subtractor.evaluate()
    assert adder_subtractor.get_all_outputs() == [1, 0, 0, 0, 0, 0, 0, 0, 1]
    # 0 - 1
    adder_subtractor.set_inputs_from_array([0, 0, 0, 0, 0, 0, 0, 0,
                                            0, 0, 0, 0, 0, 0, 0, 1,
                                            1])  # Last bit is subtract signal
    adder_subtractor.evaluate()
    assert adder_subtractor.get_all_outputs() == [0, 1, 1, 1, 1, 1, 1, 1, 1]
    # 1 - 1
    adder_subtractor.set_inputs_from_array([0, 0, 0, 0, 0, 0, 0, 1,
                                            0, 0, 0, 0, 0, 0, 0, 1,
                                            1])  # Last bit is subtract signal
    adder_subtractor.evaluate()
    assert adder_subtractor.get_all_outputs() == [1, 0, 0, 0, 0, 0, 0, 0, 0]
    # 96 + 5 = 101
    adder_subtractor.set_inputs_from_array([0, 1, 1, 0, 0, 0, 0, 0,
                                            0, 0, 0, 0, 0, 1, 0, 1,
                                            0])  # Last bit is subtract signal
    adder_subtractor.evaluate()
    assert adder_subtractor.get_all_outputs() == [0, 0, 1, 1, 0, 0, 1, 0, 1]
    # 96 - 5
    adder_subtractor.set_inputs_from_array([0, 1, 1, 0, 0, 0, 0, 0,
                                            0, 0, 0, 0, 0, 1, 0, 1,
                                            1])  # Last bit is subtract signal
    adder_subtractor.evaluate()
    assert adder_subtractor.get_all_outputs() == [1, 0, 1, 0, 1, 1, 0, 1, 1]
    # 5 - 96
    adder_subtractor.set_inputs_from_array([0, 0, 0, 0, 0, 1, 0, 1,
                                            0, 1, 1, 0, 0, 0, 0, 0,
                                            1])  # Last bit is subtract signal
    adder_subtractor.evaluate()
    assert adder_subtractor.get_all_outputs() == [0, 1, 0, 1, 0, 0, 1, 0, 1]


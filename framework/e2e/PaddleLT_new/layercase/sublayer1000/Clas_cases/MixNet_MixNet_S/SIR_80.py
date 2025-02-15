# api:paddle.tensor.manipulation.split||api:paddle.tensor.manipulation.split||api:paddle.nn.functional.conv._conv_nd||api:paddle.nn.functional.conv._conv_nd||api:paddle.nn.functional.conv._conv_nd||api:paddle.tensor.manipulation.concat
import paddle
import unittest
import numpy as np


class LayerCase(paddle.nn.Layer):
    def __init__(self):
        super().__init__()
        self.parameter_0 = self.create_parameter(
           shape=[160, 1, 3, 3],
           dtype=paddle.float32,
        )
        self.parameter_1 = self.create_parameter(
           shape=[160, 1, 5, 5],
           dtype=paddle.float32,
        )
        self.parameter_2 = self.create_parameter(
           shape=[160, 1, 7, 7],
           dtype=paddle.float32,
        )
    def forward(
        self,
        var_0,    # (shape: [22, 480, 14, 14], dtype: paddle.float32, stop_gradient: False)
    ):
        out = paddle.tensor.manipulation.split(var_0, [160, 160, 160], axis=1)
        var_1 = out[0]
        var_2 = out[1]
        var_3 = out[2]
        out = paddle.tensor.manipulation.split(var_0, [160, 160, 160], axis=1)
        var_4 = out[0]
        var_5 = out[1]
        var_6 = out[2]
        var_7 = paddle.nn.functional.conv._conv_nd(var_4, self.parameter_0, bias=None, stride=[1, 1], padding=[1, 1], padding_algorithm='EXPLICIT', dilation=[1, 1], groups=160, data_format='NCHW', channel_dim=1, op_type='depthwise_conv2d', use_cudnn=False)
        var_8 = paddle.nn.functional.conv._conv_nd(var_5, self.parameter_1, bias=None, stride=[1, 1], padding=[2, 2], padding_algorithm='EXPLICIT', dilation=[1, 1], groups=160, data_format='NCHW', channel_dim=1, op_type='depthwise_conv2d', use_cudnn=False)
        var_9 = paddle.nn.functional.conv._conv_nd(var_6, self.parameter_2, bias=None, stride=[1, 1], padding=[3, 3], padding_algorithm='EXPLICIT', dilation=[1, 1], groups=160, data_format='NCHW', channel_dim=1, op_type='depthwise_conv2d', use_cudnn=False)
        var_10 = paddle.tensor.manipulation.concat((var_7, var_8, var_9,), axis=1)
        return var_10



def create_inputspec(): 
    inputspec = ( 
        paddle.static.InputSpec(shape=(-1, 480, -1, -1), dtype=paddle.float32, stop_gradient=False), 
    )
    return inputspec

def create_tensor_inputs():
    inputs = (
        paddle.rand(shape=[22, 480, 14, 14], dtype=paddle.float32),
    )
    return inputs


def create_numpy_inputs():
    inputs = (
        np.random.random(size=[22, 480, 14, 14]).astype('float32'),
    )
    return inputs


class TestLayer(unittest.TestCase):
    def setUp(self):
        self.inputs = create_tensor_inputs()
        self.net = LayerCase()
    def train(self, net, to_static, with_prim=False, with_cinn=False):
        if to_static:
            paddle.set_flags({'FLAGS_prim_all': with_prim})
            if with_cinn:
                build_strategy = paddle.static.BuildStrategy()
                build_strategy.build_cinn_pass = True
                net = paddle.jit.to_static(net, build_strategy=build_strategy, full_graph=True)
            else:
                net = paddle.jit.to_static(net, full_graph=True)
        paddle.seed(123)
        outs = net(*self.inputs)
        return outs
    def test_ast_prim_cinn(self):
        st_out = self.train(self.net, to_static=True)
        cinn_out = self.train(self.net, to_static=True, with_prim=True, with_cinn=True)
        for st, cinn in zip(paddle.utils.flatten(st_out), paddle.utils.flatten(cinn_out)):
            np.testing.assert_allclose(st.numpy(), cinn.numpy(), atol=1e-8)


if __name__ == '__main__':
    unittest.main()
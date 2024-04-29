import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: expand_as_base
    api简介: 根据 y 的形状扩展 x ，扩展后， x 的形状和 y 的形状相同
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, x, y, ):
        """
        forward
        """
        out = paddle.expand_as(x, y,  )
        return out


def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (paddle.to_tensor(-1 + (1 - -1) * np.random.random([2, 3, 1, 3, 1]).astype('float32'), dtype='float32', stop_gradient=False), paddle.to_tensor(-1 + (1 - -1) * np.random.random([2, 3, 4, 3, 5]).astype('float32'), dtype='float32', stop_gradient=False), )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (-1 + (1 - -1) * np.random.random([2, 3, 1, 3, 1]).astype('float32'), -1 + (1 - -1) * np.random.random([2, 3, 4, 3, 5]).astype('float32'), )
    return inputs

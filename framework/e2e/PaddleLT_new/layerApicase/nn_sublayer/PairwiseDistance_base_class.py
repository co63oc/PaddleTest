import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: PairwiseDistance_base
    api简介: 计算两个tensor之间pairwise的距离
    """

    def __init__(self):
        super(LayerCase, self).__init__()
        self.func = paddle.nn.PairwiseDistance(p=2.0, )

    def forward(self, data0, data1, ):
        """
        forward
        """
        out = self.func(data0, data1, )
        return out


def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (paddle.to_tensor(-1 + (1 - -1) * np.random.random([2, 3]).astype('float32'), dtype='float32', stop_gradient=False), paddle.to_tensor(-1 + (1 - -1) * np.random.random([2, 3]).astype('float32'), dtype='float32', stop_gradient=False), )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (-1 + (1 - -1) * np.random.random([2, 3]).astype('float32'), -1 + (1 - -1) * np.random.random([2, 3]).astype('float32'), )
    return inputs

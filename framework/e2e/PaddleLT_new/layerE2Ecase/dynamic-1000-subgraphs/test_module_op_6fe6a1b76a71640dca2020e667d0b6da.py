import os
os.environ['FLAGS_cinn_new_group_scheduler'] = '1'
os.environ['FLAGS_group_schedule_tiling_first'] = '1'
os.environ['FLAGS_enable_pir_api'] = '1'
os.environ['FLAGS_cinn_bucket_compile'] = '1'
import sys
import unittest
import numpy as np
from dataclasses import dataclass
import typing as t

@dataclass
class Stage:
    name: str
    env_vars: t.Dict[str, str]

cinn_stages = [
    Stage(
        name="dynamic_to_static",
        env_vars=dict(
            PADDLE_DEBUG_ENABLE_CINN=False,
            FLAGS_prim_all=False,
            FLAGS_prim_enable_dynamic=False,
        ),
    ),
    Stage(
        name="prim",
        env_vars=dict(
            PADDLE_DEBUG_ENABLE_CINN=False,
            FLAGS_prim_all=True,
            FLAGS_prim_enable_dynamic=True,
        ),
    ),
    Stage(
        name="infer_symbolic",
        env_vars=dict(
            PADDLE_DEBUG_ENABLE_CINN=True,
            FLAGS_prim_all=True,
            FLAGS_prim_enable_dynamic=True,
            FLAGS_use_cinn=False,
            FLAGS_check_infer_symbolic=True,
        ),
    ),
	Stage(
        name="frontend",
        env_vars=dict(
            PADDLE_DEBUG_ENABLE_CINN=True,
            FLAGS_prim_all=True,
            FLAGS_prim_enable_dynamic=True,
            FLAGS_use_cinn=True,
            FLAGS_check_infer_symbolic=False,
            FLAGS_enable_fusion_fallback=True,
        ), 
    ),
    Stage(
        name="backend",
        env_vars=dict(
            PADDLE_DEBUG_ENABLE_CINN=True,
            FLAGS_prim_all=True,
            FLAGS_prim_enable_dynamic=True,
            FLAGS_use_cinn=True,
            FLAGS_check_infer_symbolic=False,
            FLAGS_enable_fusion_fallback=False,
        ), 
    ),
]

def GetCinnStageByName(name):
    for stage in cinn_stages:
        if stage.name == name:
            return stage
    return None

def GetCurrentCinnStage():
    name = os.getenv('PADDLE_DEBUG_CINN_STAGE_NAME')
    if name is None:
        return None
    stage_names = [stage.name for stage in cinn_stages]
    assert name in stage_names, (
        f"PADDLE_DEBUG_CINN_STAGE_NAME should be in {stage_names}"
    )
    return GetCinnStageByName(name)

def GetPrevCinnStage(stage):
    for i in range(1, len(cinn_stages)):
        if stage is cinn_stages[i]:
            return cinn_stages[i - 1]
    return None

def IsCinnStageEnableDiff():
    value = os.getenv('PADDLE_DEBUG_CINN_STAGE_ENABLE_DIFF')
    enabled = value in {
        '1',
        'true',
        'True',
    }
    if enabled:
        assert GetCurrentCinnStage() is not None
    return enabled

last_cinn_stage_exit_code = None
def LastCINNStageFailed():
    global last_cinn_stage_exit_code
    if last_cinn_stage_exit_code is not None:
        return last_cinn_stage_exit_code != 0
    last_stage = GetPrevCinnStage(GetCurrentCinnStage())
    if last_stage is None:
        return False
    env_vars = dict(
        PADDLE_DEBUG_CINN_STAGE_NAME=last_stage.name,
        PADDLE_DEBUG_CINN_STAGE_ENABLE_DIFF='0',
    )
    env_vars_str = " ".join(
        f"{env_var}={value}"
        for env_var, value in env_vars.items()
    )
    last_cinn_stage_exit_code = os.system(
        f"{env_vars_str} {sys.executable} {__file__} > /dev/null 2>&1"
    )
    return last_cinn_stage_exit_code != 0

def SetDefaultEnv(**env_var2value):
    for env_var, value in env_var2value.items():
        if os.getenv(env_var) is None:
            os.environ[env_var] = str(value)

SetDefaultEnv(
    PADDLE_DEBUG_ENABLE_CINN=True,
    FLAGS_enable_pir_api=True,
    FLAGS_prim_all=True,
    FLAGS_prim_enable_dynamic=True,
    FLAGS_use_cinn=False,
    FLAGS_check_infer_symbolic=False,
    FLAGS_enable_fusion_fallback=False,
)

import paddle

def SetEnvVar(env_var2value):
    for env_var, value in env_var2value.items():
        os.environ[env_var] = str(value)
    paddle.set_flags({
        env_var:value
        for env_var, value in env_var2value.items()
        if env_var.startswith('FLAGS_')
    })

if GetCurrentCinnStage() is not None:
    SetEnvVar(GetCurrentCinnStage().env_vars)

def NumOperationsInBlock(block_idx):
    return [12][block_idx] - 1 # number-of-ops-in-block

def GetPaddleDebugNumAllowedOps():
    try:
        return int(os.getenv('PADDLE_DEBUG_NUM_ALLOWED_OPS'))
    except:
        return None

paddle_debug_num_allowed_ops = GetPaddleDebugNumAllowedOps()


if type(paddle_debug_num_allowed_ops) is not int:
    def EarlyReturn(block_idx, op_idx):
        return False      
else:
    def EarlyReturn(block_idx, op_idx):
        return op_idx >= paddle_debug_num_allowed_ops

class BlockEntries:

    def builtin_module_0_0_0(self, parameter_0, parameter_1, data_0):

        # pd_op.full_int_array: (2xi64) <- ()
        full_int_array_0 = [20, 20]

        # pd_op.full: (1xi32) <- ()
        full_0 = paddle._C_ops.full([1], 1, paddle.int32, paddle.core.CPUPlace())

        # pd_op.assign: (1xi32) <- (1xi32)
        assign_0 = full_0

        # pd_op.assign: (1xi32) <- (1xi32)
        assign_1 = full_0

        # pd_op.split: ([-1x20x-1x-1xf32, -1x20x-1x-1xf32]) <- (-1x40x-1x-1xf32, 2xi64, 1xi32)
        split_0 = paddle.split(data_0, full_int_array_0, full_0)

        # builtin.split: (-1x20x-1x-1xf32, -1x20x-1x-1xf32) <- ([-1x20x-1x-1xf32, -1x20x-1x-1xf32])
        split_1, split_2, = split_0

        # pd_op.assign: (-1x20x-1x-1xf32) <- (-1x20x-1x-1xf32)
        assign_2 = split_2

        # pd_op.assign: (-1x20x-1x-1xf32) <- (-1x20x-1x-1xf32)
        assign_3 = split_1

        # pd_op.conv2d: (-1x120x-1x-1xf32) <- (-1x20x-1x-1xf32, 120x20x1x1xf32)
        conv2d_0 = paddle._C_ops.conv2d(assign_3, parameter_0, [1, 1], [0, 0], 'EXPLICIT', [1, 1], 1, 'NCHW')

        # pd_op.conv2d: (-1x120x-1x-1xf32) <- (-1x20x-1x-1xf32, 120x20x1x1xf32)
        conv2d_1 = paddle._C_ops.conv2d(assign_2, parameter_1, [1, 1], [0, 0], 'EXPLICIT', [1, 1], 1, 'NCHW')

        # builtin.combine: ([-1x120x-1x-1xf32, -1x120x-1x-1xf32]) <- (-1x120x-1x-1xf32, -1x120x-1x-1xf32)
        combine_0 = [conv2d_0, conv2d_1]

        # pd_op.concat: (-1x240x-1x-1xf32) <- ([-1x120x-1x-1xf32, -1x120x-1x-1xf32], 1xi32)
        concat_0 = paddle._C_ops.concat(combine_0, assign_0)
        return assign_1, assign_3, assign_2, conv2d_0, conv2d_1, assign_0, concat_0



def GetEnvVarEnableJit():
    enable_jit = os.getenv('PADDLE_DEBUG_ENABLE_JIT')
    return enable_jit not in {
        "0",
        "False",
        "false",
        "OFF",
    }

def GetEnvVarEnableCinn():
    enable_cinn = os.getenv('PADDLE_DEBUG_ENABLE_CINN')
    return enable_cinn not in {
        "0",
        "False",
        "false",
        "OFF",
    }


def GetTolerance(dtype):
    if dtype == np.float16:
        return GetFloat16Tolerance()
    if dtype == np.float32:
        return GetFloat32Tolerance()
    return 1e-6

def GetFloat16Tolerance():
    try:
        return float(os.getenv('PADDLE_DEBUG_FLOAT16_TOL'))
    except:
        return 1e-3

def GetFloat32Tolerance():
    try:
        return float(os.getenv('PADDLE_DEBUG_FLOAT32_TOL'))
    except:
        return 1e-6

def IsInteger(dtype):
    return np.dtype(dtype).char in np.typecodes['AllInteger']


class CinnTestBase:
    def setUp(self):
        paddle.seed(2024)
        self.prepare_data()

    def test_train(self):
        dy_outs = self.train(use_cinn=False)
        cinn_outs = self.train(use_cinn=GetEnvVarEnableCinn())

        for cinn_out, dy_out in zip(cinn_outs, dy_outs):
          if type(cinn_out) is list and type(dy_out) is list:
            for x, y in zip(cinn_out, dy_out):
              self.assert_all_close(x, y)
          else:
            self.assert_all_close(cinn_out, dy_out)

    def assert_all_close(self, x, y):
        if (hasattr(x, "numpy") and hasattr(y, "numpy")):
            x_numpy = x.numpy()
            y_numpy = y.numpy()
            assert x_numpy.dtype == y_numpy.dtype
            if IsInteger(x_numpy.dtype):
                np.testing.assert_equal(x_numpy, y_numpy)
            else:
                tol = GetTolerance(x_numpy.dtype)
                np.testing.assert_allclose(x_numpy, y_numpy, atol=tol, rtol=tol)
        else:
            assert x == y

class Block_builtin_module_0_0_0(paddle.nn.Layer, BlockEntries):
    def __init__(self):
        super().__init__()

    def forward(self, parameter_0, parameter_1, data_0):
        args = [parameter_0, parameter_1, data_0]
        for op_idx, op_func in enumerate(self.get_op_funcs()):
            if EarlyReturn(0, op_idx):
                return args
            args = op_func(*args)
        return args

    def get_op_funcs(self):
        return [
            self.op_full_int_array_0,
            self.op_full_0,
            self.op_assign_0,
            self.op_assign_1,
            self.op_split_0,
            self.op_split_1,
            self.op_assign_2,
            self.op_assign_3,
            self.op_conv2d_0,
            self.op_conv2d_1,
            self.op_combine_0,
            self.op_concat_0,
        ]

    def op_full_int_array_0(self, parameter_0, parameter_1, data_0):
    
        # EarlyReturn(0, 0)

        # pd_op.full_int_array: (2xi64) <- ()
        full_int_array_0 = [20, 20]

        return [parameter_0, parameter_1, data_0, full_int_array_0]

    def op_full_0(self, parameter_0, parameter_1, data_0, full_int_array_0):
    
        # EarlyReturn(0, 1)

        # pd_op.full: (1xi32) <- ()
        full_0 = paddle._C_ops.full([1], 1, paddle.int32, paddle.core.CPUPlace())

        return [parameter_0, parameter_1, data_0, full_int_array_0, full_0]

    def op_assign_0(self, parameter_0, parameter_1, data_0, full_int_array_0, full_0):
    
        # EarlyReturn(0, 2)

        # pd_op.assign: (1xi32) <- (1xi32)
        assign_0 = full_0

        return [parameter_0, parameter_1, data_0, full_int_array_0, full_0, assign_0]

    def op_assign_1(self, parameter_0, parameter_1, data_0, full_int_array_0, full_0, assign_0):
    
        # EarlyReturn(0, 3)

        # pd_op.assign: (1xi32) <- (1xi32)
        assign_1 = full_0

        return [parameter_0, parameter_1, data_0, full_int_array_0, full_0, assign_0, assign_1]

    def op_split_0(self, parameter_0, parameter_1, data_0, full_int_array_0, full_0, assign_0, assign_1):
    
        # EarlyReturn(0, 4)

        # pd_op.split: ([-1x20x-1x-1xf32, -1x20x-1x-1xf32]) <- (-1x40x-1x-1xf32, 2xi64, 1xi32)
        split_0 = paddle.split(data_0, full_int_array_0, full_0)

        return [parameter_0, parameter_1, assign_0, assign_1, split_0]

    def op_split_1(self, parameter_0, parameter_1, assign_0, assign_1, split_0):
    
        # EarlyReturn(0, 5)

        # builtin.split: (-1x20x-1x-1xf32, -1x20x-1x-1xf32) <- ([-1x20x-1x-1xf32, -1x20x-1x-1xf32])
        split_1, split_2, = split_0

        return [parameter_0, parameter_1, assign_0, assign_1, split_1, split_2]

    def op_assign_2(self, parameter_0, parameter_1, assign_0, assign_1, split_1, split_2):
    
        # EarlyReturn(0, 6)

        # pd_op.assign: (-1x20x-1x-1xf32) <- (-1x20x-1x-1xf32)
        assign_2 = split_2

        return [parameter_0, parameter_1, assign_0, assign_1, split_1, assign_2]

    def op_assign_3(self, parameter_0, parameter_1, assign_0, assign_1, split_1, assign_2):
    
        # EarlyReturn(0, 7)

        # pd_op.assign: (-1x20x-1x-1xf32) <- (-1x20x-1x-1xf32)
        assign_3 = split_1

        return [parameter_0, parameter_1, assign_0, assign_1, assign_2, assign_3]

    def op_conv2d_0(self, parameter_0, parameter_1, assign_0, assign_1, assign_2, assign_3):
    
        # EarlyReturn(0, 8)

        # pd_op.conv2d: (-1x120x-1x-1xf32) <- (-1x20x-1x-1xf32, 120x20x1x1xf32)
        conv2d_0 = paddle._C_ops.conv2d(assign_3, parameter_0, [1, 1], [0, 0], 'EXPLICIT', [1, 1], 1, 'NCHW')

        return [parameter_1, assign_0, assign_1, assign_2, assign_3, conv2d_0]

    def op_conv2d_1(self, parameter_1, assign_0, assign_1, assign_2, assign_3, conv2d_0):
    
        # EarlyReturn(0, 9)

        # pd_op.conv2d: (-1x120x-1x-1xf32) <- (-1x20x-1x-1xf32, 120x20x1x1xf32)
        conv2d_1 = paddle._C_ops.conv2d(assign_2, parameter_1, [1, 1], [0, 0], 'EXPLICIT', [1, 1], 1, 'NCHW')

        return [assign_0, assign_1, assign_2, assign_3, conv2d_0, conv2d_1]

    def op_combine_0(self, assign_0, assign_1, assign_2, assign_3, conv2d_0, conv2d_1):
    
        # EarlyReturn(0, 10)

        # builtin.combine: ([-1x120x-1x-1xf32, -1x120x-1x-1xf32]) <- (-1x120x-1x-1xf32, -1x120x-1x-1xf32)
        combine_0 = [conv2d_0, conv2d_1]

        return [assign_0, assign_1, assign_2, assign_3, conv2d_0, conv2d_1, combine_0]

    def op_concat_0(self, assign_0, assign_1, assign_2, assign_3, conv2d_0, conv2d_1, combine_0):
    
        # EarlyReturn(0, 11)

        # pd_op.concat: (-1x240x-1x-1xf32) <- ([-1x120x-1x-1xf32, -1x120x-1x-1xf32], 1xi32)
        concat_0 = paddle._C_ops.concat(combine_0, assign_0)

        return [assign_1, assign_3, assign_2, conv2d_0, conv2d_1, assign_0, concat_0]

if True and not (IsCinnStageEnableDiff() and LastCINNStageFailed()):

    class Test_builtin_module_0_0_0(CinnTestBase, unittest.TestCase):
        def prepare_data(self):
            self.inputs = [
                # parameter_0
                paddle.uniform([120, 20, 1, 1], dtype='float32', min=0, max=0.5),
                # parameter_1
                paddle.uniform([120, 20, 1, 1], dtype='float32', min=0, max=0.5),
                # data_0
                paddle.uniform([22, 40, 28, 28], dtype='float32', min=0, max=0.5),
            ]
            for input in self.inputs:
                input.stop_gradient = True

        def apply_to_static(self, net, use_cinn):
            build_strategy = paddle.static.BuildStrategy()
            input_spec = [
                # parameter_0
                paddle.static.InputSpec(shape=[120, 20, 1, 1], dtype='float32'),
                # parameter_1
                paddle.static.InputSpec(shape=[120, 20, 1, 1], dtype='float32'),
                # data_0
                paddle.static.InputSpec(shape=[None, 40, None, None], dtype='float32'),
            ]
            build_strategy.build_cinn_pass = use_cinn
            return paddle.jit.to_static(
                net,
                input_spec=input_spec,
                build_strategy=build_strategy,
                full_graph=True,
            )

        def train(self, use_cinn):
            net = Block_builtin_module_0_0_0()
            if GetEnvVarEnableJit():
                net = self.apply_to_static(net, use_cinn)
            paddle.seed(2024)
            out = net(*self.inputs)
            return out

if __name__ == '__main__':
    unittest.main()
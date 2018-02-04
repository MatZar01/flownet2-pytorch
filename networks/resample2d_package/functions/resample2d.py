from torch.autograd import Function, Variable
from .._ext import resample2d


class Resample2dFunction(Function):

    @staticmethod
    def forward(ctx, input1, input2, kernel_size=1):
        assert input1.is_contiguous()
        assert input2.is_contiguous()

        ctx.save_for_backward(input1, input2)
        ctx.kernel_size = kernel_size

        _, d, _, _ = input1.size()
        b, _, h, w = input2.size()
        output = input1.new().resize_(b, d, h, w).zero_()

        resample2d.Resample2d_cuda_forward(input1, input2, output, kernel_size)

        return output

    @staticmethod
    def backward(ctx, grad_output):
        assert grad_output.is_contiguous()

        input1, input2 = ctx.saved_tensors

        grad_input1 = Variable(input1.new(input1.size()).zero_())
        grad_input2 = Variable(input1.new(input2.size()).zero_())

        resample2d.Resample2d_cuda_backward(input1, input2, grad_output.data,
                                            grad_input1.data, grad_input2.data,
                                            ctx.kernel_size)

        return grad_input1, grad_input2, None

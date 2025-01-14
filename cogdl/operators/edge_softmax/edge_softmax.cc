#include <torch/extension.h>
#include <iostream>
#include <vector>
#include <pybind11/pybind11.h>
#include <c10/cuda/CUDAGuard.h>
#include "../backend.h"
torch::Tensor edge_softmax_cuda(
    torch::Tensor rowptr,
    torch::Tensor weight);

torch::Tensor edge_softmax_backward_cuda(
torch::Tensor rowptr,
torch::Tensor softmax,
torch::Tensor grad);

torch::Tensor edge_softmax(
    torch::Tensor rowptr,
    torch::Tensor weight)
{   if (backend()==0){
    assert(rowptr.device().type() == torch::kCUDA);
    assert(weight.device().type() == torch::kCUDA);}
    assert(rowptr.is_contiguous());
    assert(weight.is_contiguous());
    assert(rowptr.dtype() == torch::kInt32);
    assert(weight.dtype() == torch::kFloat32);
    const at::cuda::OptionalCUDAGuard device_guard1(device_of(rowptr));
    const at::cuda::OptionalCUDAGuard device_guard2(device_of(weight));
    return edge_softmax_cuda(rowptr, weight);
}

torch::Tensor edge_softmax_backward(
    torch::Tensor rowptr,
    torch::Tensor softmax,
    torch::Tensor grad)
{   if (backend()==0){
    assert(rowptr.device().type() == torch::kCUDA);
    assert(softmax.device().type() == torch::kCUDA);
    assert(grad.device().type() == torch::kCUDA);}
    assert(rowptr.is_contiguous());
    assert(softmax.is_contiguous());
    assert(grad.is_contiguous()); 
    assert(rowptr.dtype() == torch::kInt32);
    assert(softmax.dtype() == torch::kFloat32);
    assert(grad.dtype() == torch::kFloat32);
    const at::cuda::OptionalCUDAGuard device_guard1(device_of(rowptr));
    const at::cuda::OptionalCUDAGuard device_guard2(device_of(softmax));
    const at::cuda::OptionalCUDAGuard device_guard3(device_of(grad));
    return edge_softmax_backward_cuda(rowptr, softmax, grad);
}

PYBIND11_MODULE(edge_softmax, m)
{
    m.doc() = "edgeSoftmax in CSR format. ";
    m.def("edge_softmax", &edge_softmax, "CSR edgeSoftmax");
    m.def("edge_softmax_backward", &edge_softmax_backward, "CSR edgeSoftmax backward");
}
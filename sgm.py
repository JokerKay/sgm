#!/usr/bin/env python

"""
    sgm.py
    
    Agnostic SGM implementation
"""

import sys
import json
from time import time

def sgm(A, P, B, eye, compute_grad, solve_lap, num_iters, tolerance, prod_sum, verbose=True):
    grad, grad_offset = compute_grad(A, P, B)
    
    stop = False
    for i in range(num_iters):
        iter_start_time = time()
        
        lap_start_time = time()
        T = solve_lap(grad, grad_offset, eye=eye)
        lap_time = time() - lap_start_time
        
        grad_t, grad_t_offset = compute_grad(A, T, B)
        
        c = prod_sum(grad, P) + prod_sum(grad_offset, P)
        d = prod_sum(grad_t, P) + prod_sum(grad_t_offset, P) + prod_sum(grad, T) + prod_sum(grad_offset, T)
        e = prod_sum(grad_t, T) + prod_sum(grad_t_offset, T)
        
        if (c - d + e == 0) and (d - 2 * e == 0):
            alpha = 0
        else:
            if (c - d + e == 0):
                alpha = float('inf')
            else:
                alpha = -(d - 2 * e) / (2 * (c - d + e))
        
        f1     = c - e
        falpha = (c - d + e) * alpha ** 2 + (d - 2 * e) * alpha
        
        if (alpha < tolerance) and (alpha > 0) and (falpha > 0) and (falpha > f1):
            P           = (alpha * P)           + (1 - alpha) * T
            grad        = (alpha * grad)        + (1 - alpha) * grad_t
            grad_offset = (alpha * grad_offset) + (1 - alpha) * grad_t_offset
        elif f1 < 0:
            P           = T
            grad        = grad_t
            grad_offset = grad_t_offset
        else:
            stop = True
        
        if verbose:
            iter_time = time() - iter_start_time
            print(json.dumps({
                "iter"          : i,
                "lap_time"      : lap_time,
                "nolap_time"    : iter_time - lap_time,
            }))
        
        if stop:
            break
    
    return solve_lap(P, 0, eye=eye)
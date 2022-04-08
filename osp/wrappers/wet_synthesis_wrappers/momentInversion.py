import math
import numpy as np
import scipy.linalg as linalg
import osp.wrappers.wet_synthesis_wrappers.exceptions as exceptions


def wheeler(m):

    n = int(math.floor(len(m) / 2))

    sigma = np.zeros([2*n + 1, 2*n + 1])

    for i in range(1, 2*n + 1):
        sigma[1, i] = m[i-1]

    a = np.zeros(n)
    b = np.zeros(n)

    a[0] = m[1]/m[0]

    b[0] = 0

    for i in range(2, n+1):
        for j in range(i, 2*n - i + 2):
            sigma[i, j] = sigma[i - 1, j + 1] - a[i - 2]*sigma[i - 1, j] \
                - b[i - 2]*sigma[i - 2, j]

        a[i - 1] = sigma[i, i + 1]/sigma[i, i] \
            - sigma[i - 1, i]/sigma[i - 1, i - 1]
        b[i - 1] = sigma[i, i]/sigma[i - 1, i - 1]

    negSqrt_b = np.zeros(n-1)

    for i in range(0, n-1):
        b_i = b[i + 1]

        if b_i < 0:
            raise exceptions.RealizabilityErr(m)

        negSqrt_b[i] = -math.sqrt(b_i)

    D, V = linalg.eigh_tridiagonal(a, negSqrt_b)

    w = np.zeros(n)
    x = np.zeros(n)

    for i in range(0, n):
        w[i] = (V[0, i]**2)*m[0]
        if w[i] < 0:
            raise exceptions.RealizabilityErr(m)

        x[i] = D[i]
        if x[i] < 0:
            raise exceptions.RealizabilityErr(m, x[i], negNode=True)

    return w, x


if __name__ == "__main__":

    moments = [3.86403175e+00, 3.86403357e-09, 3.86403539e-18, 3.86403721e-27]
    moments = [4.77253617e+13, 1.08819180e+08, 2.99624644e+02, 9.09160310e-04]
    # moments = [0.0679532, 3.39766e-10, 1.69883e-18, 3.99208e-14]

    w, x = wheeler(moments)
    print('weights:', w)
    print('abscissas:', x)

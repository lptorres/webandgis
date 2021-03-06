# coding=utf-8
"""**Numerical tools**
"""

import numpy
from utilities import verify


def ensure_numeric(A, typecode=None):
    """Ensure that sequence is a numeric array.

    :param A: Is one of the following:

        * Sequence. If A is already a numeric array it will be returned
                    unaltered
                    If not, an attempt is made to convert it to a numeric
                    array
        * Scalar.   Return 0-dimensional array containing that value. Note
                    that a 0-dim array DOES NOT HAVE A LENGTH UNDER numpy.
        * String.   Array of ASCII values (numpy can't handle this)

    :param typecode: numeric type. If specified, use this in the conversion.
                    If not, let numeric package decide.
                    typecode will always be one of num.float, num.int, etc.

    :raises: Exception

    :returns: An array of A if it is found to be of a numeric type
    :rtype: numpy.ndarray

    .. note::
        that numpy.array(A, dtype) will sometimes copy.  Use 'copy=False' to
        copy only when required.

        This function is necessary as array(A) can cause memory overflow.
    """

    if isinstance(A, basestring):
        msg = 'Sorry, cannot handle strings in ensure_numeric()'
        # FIXME (Ole): Change this to whatever is the appropriate exception
        # for wrong input type
        raise Exception(msg)

    if typecode is None:
        if isinstance(A, numpy.ndarray):
            return A
        else:
            return numpy.array(A)
    else:
        return numpy.array(A, dtype=typecode, copy=False)


def nan_allclose(x, y, rtol=1.0e-5, atol=1.0e-8):
    """Does element comparison within a tolerance, excludes overlapped NaN.

    :param x: scalar or numpy array
    :type x: numpy.ndarray, float

    :param y: scalar or numpy array
    :type y: numpy.ndarray, float

    :param rtol: The relative tolerance parameter
    :type rtol: float

    :param atol: The absolute tolerance parameter
    :type atol: float

    :raises:

    :returns: The result of the allclose on non NaN elments
    :rtype: bool

    Note:
        Returns True if all non-nan elements pass.
    """

    xn = numpy.isnan(x)
    yn = numpy.isnan(y)
    if numpy.any(xn != yn):
        # Presence of NaNs is not the same in x and y
        return False

    if numpy.all(xn):
        # Everything is NaN.
        # This will also take care of x and y being NaN scalars
        return True

    # Filter NaN's out
    if numpy.any(xn):
        x = x[-xn]
        y = y[-yn]

    # Compare non NaN's and return
    return numpy.allclose(x, y, rtol=rtol, atol=atol)


def normal_cdf(x, mu=0, sigma=1):
    r"""Cumulative Normal Distribution Function

    :param x: scalar or array of real numbers
    :type x: numpy.ndarray, float

    :param mu: Mean value. Default 0
    :type mu: float, numpy.ndarray

    :param sigma: Standard deviation. Default 1
    :type sigma: float

    :returns: An approximation of the cdf of the normal
    :rtype: numpy.ndarray

    Note:
        CDF of the normal distribution is defined as
        \frac12 [1 + erf(\frac{x - \mu}{\sigma \sqrt{2}})], x \in \R

        Source: http://en.wikipedia.org/wiki/Normal_distribution
    """

    arg = (x - mu) / (sigma * numpy.sqrt(2))
    res = (1 + erf(arg)) / 2

    return res


def log_normal_cdf(x, median=1, sigma=1):
    r"""Cumulative Log Normal Distribution Function

    :param x: scalar or array of real numbers
    :type x: numpy.ndarray, float

    :param median: Median (exp(mean of log(x)). Default 1
    :type median: float

    :param sigma: Log normal standard deviation. Default 1
    :type sigma: float

    :returns: An approximation of the cdf of the normal
    :rtype: numpy.ndarray

    .. note::
        CDF of the normal distribution is defined as
        \frac12 [1 + erf(\frac{x - \mu}{\sigma \sqrt{2}})], x \in \R

        Source: http://en.wikipedia.org/wiki/Normal_distribution
    """

    return normal_cdf(numpy.log(x), mu=numpy.log(median), sigma=sigma)


# noinspection PyUnresolvedReferences
def erf(z):
    """Approximation to ERF

    :param z: input array or scalar to perform erf on
    :type z: numpy.ndarray, float

    :returns: the approximate error
    :rtype: numpy.ndarray, float

    Note:
        from:
        http://www.cs.princeton.edu/introcs/21function/ErrorFunction.java.html
        Implements the Gauss error function.
        erf(z) = 2 / sqrt(pi) * integral(exp(-t*t), t = 0..z)

        Fractional error in math formula less than 1.2 * 10 ^ -7.
        although subject to catastrophic cancellation when z in very close to 0
        from Chebyshev fitting formula for erf(z) from Numerical Recipes, 6.2

        Source:
        http://stackoverflow.com/questions/457408/
        is-there-an-easily-available-implementation-of-erf-for-python
    """

    # Input check
    try:
        len(z)
    except TypeError:
        scalar = True
        z = [z]
    else:
        scalar = False

    z = numpy.array(z)

    # Begin algorithm
    t = 1.0 / (1.0 + 0.5 * numpy.abs(z))

    # Use Horner's method
    ans = 1 - t * numpy.exp(-z * z - 1.26551223 +
                           t * (1.00002368 +
                           t * (0.37409196 +
                           t * (0.09678418 +
                           t * (-0.18628806 +
                           t * (0.27886807 +
                           t * (-1.13520398 +
                           t * (1.48851587 +
                           t * (-0.82215223 +
                           t * 0.17087277)))))))))

    neg = (z < 0.0)  # Mask for negative input values
    ans[neg] = -ans[neg]

    if scalar:
        return ans[0]
    else:
        return ans


def axes_to_points(x, y):
    """Generate all combinations of grid point coordinates from x and y axes

    :param x: x coordinates (array)
    :type x: numpy.ndarray

    :param y: y coordinates (array)
    :type y: numpy.ndarray

    :returns:
        * P: Nx2 array consisting of coordinates for all
             grid points defined by x and y axes. The x coordinate
             will vary the fastest to match the way 2D numpy
             arrays are laid out by default ('C' order). That way,
             the x and y coordinates will match a corresponding
             2D array A when flattened (A.flat[:] or A.reshape(-1))

    Note:
        Example

        x = [1, 2, 3]
        y = [10, 20]

        P = [[1, 10],
             [2, 10],
             [3, 10],
             [1, 20],
             [2, 20],
             [3, 20]]
    """

    # Reverse y coordinates to have them start at bottom of array
    y = numpy.flipud(y)

    # Repeat x coordinates for each y (fastest varying)
    # noinspection PyTypeChecker
    X = numpy.kron(numpy.ones(len(y)), x)

    # Repeat y coordinates for each x (slowest varying)
    Y = numpy.kron(y, numpy.ones(len(x)))

    # Check
    N = len(X)
    verify(len(Y) == N)

    # Create Nx2 array of x and y coordinates
    X = numpy.reshape(X, (N, 1))
    Y = numpy.reshape(Y, (N, 1))
    P = numpy.concatenate((X, Y), axis=1)

    # Return
    return P


def grid_to_points(A, x, y):
    """Convert grid data to point data

    :param A: Array of pixel values
    :type A: numpy.ndarray

    :param x: Longitudes corresponding to columns in A (west->east)
    :type x: numpy.ndarray

    :param y: Latitudes corresponding to rows in A (south->north)
    :type y: numpy.ndarray

    Returns:
        * P: Nx2 array of point coordinates
        * V: N array of point values
    """

    msg = ('Longitudes must be increasing (west to east). I got %s' % str(x))
    verify(x[0] < x[1], msg)

    msg = ('Latitudes must be increasing (south to north). I got %s' % str(y))
    verify(y[0] < y[1], msg)

    # Create Nx2 array of x, y points corresponding to each
    # element in A.
    points = axes_to_points(x, y)

    # Create flat 1D row-major view of A cast as
    # one column vector of length MxN where M, N = A.shape
    #values = A.reshape((-1, 1))
    values = A.reshape(-1)

    # Return Nx3 array with rows: x, y, value
    return points, values


def geotransform_to_axes(G, nx, ny):
    """Convert geotransform to coordinate axes

    :param G: GDAL geotransform (6-tuple).
        (top left x, w-e pixel resolution, rotation,
        top left y, rotation, n-s pixel resolution).
    :type G: tuple

    :param nx: Number of cells in the w-e direction
    :type nx: int

    :param ny: Number of cells in the n-s direction
    :type nx: int


    :returns: Two vectors (longitudes and latitudes) representing the grid
        defined by the geotransform.

        The values are offset by half a pixel size to correspond to
        pixel registration.

        I.e. If the grid origin (top left corner) is (105, 10) and the
        resolution is 1 degrees in each direction, then the vectors will
        take the form

        longitudes = [100.5, 101.5, ..., 109.5]
        latitudes = [0.5, 1.5, ..., 9.5]
    """

    lon_ul = float(G[0])  # Longitude of upper left corner
    lat_ul = float(G[3])  # Latitude of upper left corner
    dx = float(G[1])      # Longitudinal resolution
    dy = - float(G[5])    # Latitudinal resolution (always(?) negative)

    verify(dx > 0)
    verify(dy > 0)

    # Coordinates of lower left corner
    lon_ll = lon_ul
    lat_ll = lat_ul - ny * dy

    # Coordinates of upper right corner
    lon_ur = lon_ul + nx * dx

    # Define pixel centers along each directions
    # This is to achieve pixel registration rather
    # than gridline registration
    dx2 = dx / 2
    dy2 = dy / 2

    # Define longitudes and latitudes for each axes
    x = numpy.linspace(lon_ll + dx2,
                       lon_ur - dx2, nx)
    y = numpy.linspace(lat_ll + dy2,
                       lat_ul - dy2, ny)

    # Return
    return x, y

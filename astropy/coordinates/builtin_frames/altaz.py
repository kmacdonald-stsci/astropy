# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import (absolute_import, unicode_literals, division,
                        print_function)

import numpy as np

from ... import units as u
from ..representation import (CartesianDifferential,
                              SphericalRepresentation,
                              UnitSphericalRepresentation,
                              SphericalCosLatDifferential,
                              UnitSphericalCosLatDifferential)
from ..baseframe import BaseCoordinateFrame, RepresentationMapping
from ..frame_attributes import (FrameAttribute, TimeFrameAttribute,
                                QuantityFrameAttribute, EarthLocationAttribute)

_90DEG = 90*u.deg


class AltAz(BaseCoordinateFrame):
    """
    A coordinate or frame in the Altitude-Azimuth system (Horizontal
    coordinates).  Azimuth is oriented East of North (i.e., N=0, E=90 degrees).

    This frame is assumed to *include* refraction effects if the ``pressure``
    frame attribute is non-zero.

    This frame has the following frame attributes, which are necessary for
    transforming from AltAz to some other system:

    * ``obstime``
        The time at which the observation is taken.  Used for determining the
        position and orientation of the Earth.
    * ``location``
        The location on the Earth.  This can be specified either as an
        `~astropy.coordinates.EarthLocation` object or as anything that can be
        transformed to an `~astropy.coordinates.ITRS` frame.
    * ``pressure``
        The atmospheric pressure as an `~astropy.units.Quantity` with pressure
        units.  This is necessary for performing refraction corrections.
        Setting this to 0 (the default) will disable refraction calculations
        when transforming to/from this frame.
    * ``temperature``
        The ground-level temperature as an `~astropy.units.Quantity` in
        deg C.  This is necessary for performing refraction corrections.
    * ``relative_humidity``
        The relative humidity as a number from 0 to 1.  This is necessary for
        performing refraction corrections.
    * ``obswl``
        The average wavelength of observations as an `~astropy.units.Quantity`
         with length units.  This is necessary for performing refraction
         corrections.

    Parameters
    ----------
    representation : `BaseRepresentation` or None
        A representation object or None to have no data (or use the other keywords)
    az : `Angle`, optional, must be keyword
        The Azimuth for this object (``alt`` must also be given and
        ``representation`` must be None).
    alt : `Angle`, optional, must be keyword
        The Altitude for this object (``az`` must also be given and
        ``representation`` must be None).
    distance : :class:`~astropy.units.Quantity`, optional, must be keyword
        The Distance for this object along the line-of-sight.
    pm_az : :class:`~astropy.units.Quantity`, optional, must be keyword
        The proper motion in azimuth for this object (``pm_alt`` must also be
        given).
    pm_alt : :class:`~astropy.units.Quantity`, optional, must be keyword
        The proper motion in altitude for this object (``pm_az`` must also be
        given).
    radial_velocity : :class:`~astropy.units.Quantity`, optional, must be keyword
        The radial velocity of this object.
    copy : bool, optional
        If `True` (default), make copies of the input coordinate arrays.
        Can only be passed in as a keyword argument.

    Notes
    -----
    The refraction model is based on that implemented in ERFA, which is fast
    but becomes inaccurate for altitudes below about 5 degrees.  Near and below
    altitudes of 0, it can even give meaningless answers, and in this case
    transforming to AltAz and back to another frame can give highly discrepent
    results.  For much better numerical stability, leaving the ``pressure`` at
    ``0`` (the default), disabling the refraction correction (yielding
    "topocentric" horizontal coordinates).

    """

    frame_specific_representation_info = {
        SphericalRepresentation: [
            RepresentationMapping('lon', 'az'),
            RepresentationMapping('lat', 'alt')
        ],
        SphericalCosLatDifferential: [
            RepresentationMapping('d_lon_coslat', 'pm_az', u.mas/u.yr),
            RepresentationMapping('d_lat', 'pm_alt', u.mas/u.yr),
            RepresentationMapping('d_distance', 'radial_velocity', u.km/u.s),
        ],
        CartesianDifferential: [
            RepresentationMapping('d_x', 'v_x', u.km/u.s),
            RepresentationMapping('d_y', 'v_y', u.km/u.s),
            RepresentationMapping('d_z', 'v_z', u.km/u.s),
        ],
    }
    frame_specific_representation_info[UnitSphericalRepresentation] = \
        frame_specific_representation_info[SphericalRepresentation]
    frame_specific_representation_info[UnitSphericalCosLatDifferential] = \
        frame_specific_representation_info[SphericalCosLatDifferential]

    default_representation = SphericalRepresentation
    default_differential = SphericalCosLatDifferential

    obstime = TimeFrameAttribute(default=None)
    location = EarthLocationAttribute(default=None)
    pressure = QuantityFrameAttribute(default=0, unit=u.hPa)
    temperature = QuantityFrameAttribute(default=0, unit=u.deg_C)
    relative_humidity = FrameAttribute(default=0)
    obswl = QuantityFrameAttribute(default=1*u.micron, unit=u.micron)

    def __init__(self, *args, **kwargs):
        super(AltAz, self).__init__(*args, **kwargs)

    @property
    def secz(self):
        """
        Secant if the zenith angle for this coordinate, a common estimate of the
        airmass.
        """
        return 1/np.sin(self.alt)

    @property
    def zen(self):
        """
        The zenith angle for this coordinate
        """
        return _90DEG.to(self.alt.unit) - self.alt


#self-transform defined in cirs_observed_transforms.py

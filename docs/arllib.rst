.. ARL documentation master file


:index:`Algorithm Reference Library`
************************************

The Algorithm Reference Library is used to capture radio interferometry calibration and imaging algorithms in a
reference form for use by SDP contractors. The interfaces all operate with familiar data structures such as image,
visibility table, gaintable, etc.

See also :doc:`Algorithm Reference Library Goals<arllib_goals>`

The functions as arranged as in the folowing image:

.. image:: ./Calibrate_and_Image.png
      :width: 1024px


.. toctree::
   :name: mastertoc
   :maxdepth: 2

:index:`ARL-based Notebooks`
----------------------------

.. toctree::
   :name: mastertoc
   :maxdepth: 2

   Imaging Demonstration<arl/imaging>


:index:`ARL API`
----------------

Define Visibility
+++++++++++++++++

.. automodule:: arl.define_visibility
   :members:

Simulate Visibility
+++++++++++++++++++

.. automodule:: arl.simulate_visibility
   :members:

Calibrate Visibility
++++++++++++++++++++

.. automodule:: arl.calibrate_visibility
   :members:

Fourier Transform
+++++++++++++++++

.. automodule:: arl.fourier_transform
   :members:

Deconvolve Image
++++++++++++++++

.. automodule:: arl.deconvolve_image
   :members:

Define Image
++++++++++++

.. automodule:: arl.define_image
   :members:

Polarisation
++++++++++++

.. automodule:: arl.polarisation
   :members:

Define SkyModel
+++++++++++++++

.. automodule:: arl.define_skymodel
   :members:

Solve Combinations
++++++++++++++++++

.. automodule:: arl.solve_combinations
   :members:

Assess Quality
++++++++++++++

.. automodule:: arl.assess_quality
   :members:



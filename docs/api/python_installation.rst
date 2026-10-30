.. _PythonInstallation:

.. title:: Python Installation Guide

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Python Installation</span>
         </h1>

      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>pip install hades-obol</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Installation
======================

This page covers installing the ``hades-obol`` Python package, which provides programmatic access to the Hades computational backend.

If you are looking to install the Hades desktop application instead, see :doc:`/overview/installation`.

Hades' Python API enables you to automate workflows without the GUI and perform more powerful analyses. You can run thousands of models to explore the parameter space in more detail and understand the interplay between different parameters and their effect on the results.

.. tip::
   New to Python? If you don't have Python installed, you can run and edit all of our example scripts in a free online environment like [Google Colab](https://colab.research.google.com/). With Colab, you can also upload your own datasets and run Hades without installing anything locally.

Prerequisites
-------------
* **Python 3.10 or higher** is required.
* Primary dependencies include `numpy`, `matplotlib`, and `scipy`. 

Install the Package
-------------------

.. tab-set::

   .. tab-item:: via pip (Recommended)

      This is the standard and recommended way to install the latest stable version of Hades.
      
      .. code-block:: bash

         pip install hades-obol

      ``pip`` will automatically install all required dependencies and install the relevant ``hades-obol`` distribution for your operating system and Python version.

   .. tab-item:: from source

      You can install directly from our GitHub repository:

      .. code-block:: bash

         Coming soon

Verify the Installation
-----------------------
To ensure everything was installed properly, open a Python terminal and try importing the package:

.. code-block:: python

   import hades
   print(hades.__version__)

You should see the current version number (0.9.0).

You can always check if you are running the latest version of Hades by running:

.. code-block:: python

   from hades import check_for_updates
   check_for_updates()

Upgrading the Package
-----------------------

If you already have an older version of the package installed, you can upgrade to the latest version using pip:

.. code-block:: bash

   pip install --upgrade hades-obol

Or download the latest release from GitHub and install manually, as above.

Next Steps
----------
Now that you have the package installed, see the :doc:`quickstart` to run your first analysis with Hades in under two minutes.

Alternatively, visit the :doc:`API Reference <../api/index>` for detailed documentation on all available classes and functions.









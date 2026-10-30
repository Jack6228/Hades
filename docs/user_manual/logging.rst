.. _Logs:

.. title:: Logs | User Guide

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Logs</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>User Guide</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Logs
====================

Both Hades software and the ``hades-obol`` Python package keep logs of their operations, which can be useful for verifying operations, debugging, and providing aid for troubleshooting. 

Hades saves up to five log files, in the ``Logs`` directory of the ``Hades`` folder in your system's ``AppData\Local`` directory. The log files are named with the date and time of their creation, for example: ``hades_2026-10-17_15-00-00.log``. Each log file contains information about the operations performed by Hades, including any errors or warnings that occurred during execution.

Note that for the windows application, a new log is created each time the application is started, whereas the Python package creates a new log file each time the package is imported. The log files are automatically rotated, with the oldest log file being deleted when a new log file is created and there are already five log files present.
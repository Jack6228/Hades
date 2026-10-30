.. _HadesInstallation:

.. title:: Installing Hades

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Installing Hades</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>Standalone Windows Application</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Installation
======================

Hades is available in two formats: a standalone **Desktop Application** with a graphical user interface, and a **Python Package** for advanced scripting and automation. This page is for the Hades desktop application; see the :doc:`Python Installation Guide </api/python_installation>` for installing the Python package.

----

Desktop Application
-------------------

The standalone desktop application requires no coding knowledge, simply follow the instructions below:

.. tab-set::

   .. tab-item:: Windows (Available)
      :sync: windows

      .. note::
         As Hades is a free, open-source project, we do not currently pay a corporate fee to Microsoft for an official software publisher certificate. Because of this, Windows may try to block or warn you when you open the installer.

         We are working to acquire a certificate, but in the meantime, you may see a blue warning screen that says "Windows protected your PC" when you try to run the installer; if this happens, see the alternative installation methods below.

      **Download the Installer**
      
      The latest Windows installer is only available from the offical `Hades GitHub Releases <https://github.com/Jack6228/Hades/releases>`_ page. 

      Click the ``HadesInstallerV0.9.0.exe`` file to download the installer. The latest version is recommended, but you can also download older versions if needed.

      **Run the Installer**
       
      1. Locate the downloaded file (e.g., ``HadesInstallerV0.9.0.exe``).
      2. Double-click the file to run it. 
      3. If Windows displays a "Windows protected your PC" warning, click **More info** > **Run anyway**.
      4. Follow the on-screen instructions to complete the installation.

      **Launch the App**
      
      You can now launch Hades from your Windows Start Menu or Desktop shortcut.


      .. dropdown:: Alternative Installation Methods
         :animate: fade-in
         :icon: info

         **Option A: Run as Administrator**

         1. Right-click the installer file you downloaded, such as ``HadesInstallerV0.9.0.exe``.
         2. Select **Run as administrator** from the context menu.

         **Option B: Run via Command Prompt**

         If you do not see a "Run anyway" button, you can run the installer through Command Prompt:

         1. Open the Start Menu (e.g., click the Windows icon in the bottom left corner of your screen or press the Windows key on your keyboard).
         2. Type ``cmd`` and press Enter. A black Command Prompt window will open.
         3. Type the following command and press Enter to go to your Downloads folder:

            .. code-block:: bash

               cd %HOMEPATH%\Downloads 

         4. Type the name of your installer and press Enter to start it. You can type the first few letters and press Tab to complete the name: 

            .. code-block:: bash

               HadesInstallerV0.9.0.exe

   .. tab-item:: macOS & Linux
      :sync: maclinux

      The Hades desktop application is currently only available for Windows. 
      
      If you are using macOS or Linux, please use the :doc:`Python Installation Guide </api/python_installation>` to install Hades as a Python package.

.. note::
    **Want to use Hades in Python?** If you want to automate workflows, run batch analyses, or integrate Hades into your own scripts, see the :doc:`Python Installation Guide </api/python_installation>` or :doc:`Python Quickstart </api/quickstart>` for a minimal example.

----

Troubleshooting
---------------

*Common issues during installation will be added here as they are discovered.*

.. **The installer fails with a permissions error**
..    Right-click the installer and select **Run as administrator**, then
..    retry the installation.

.. **Hades opens but immediately closes**
..    ...
   .. This can occur if a required Visual C++ runtime is missing. Download and
   install the `Microsoft Visual C++ Redistributable
   <https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist>`_
   and then relaunch Hades.

If your issue is not listed here, open a report on GitHub using the `issue tracker <[https://github.com/Jack6228//Hades/issues]>`_. Please include your operating system version, Hades version, and any error messages you received. The more information you provide, the easier it will be for us to fix!

----

Next Steps
----------

Hades is installed and ready to use. Head to the :doc:`quickstart` to run your first analysis or understand how to use Hades.

The :doc:`/user_manual/index` is also available for a thorough explanation of all aspects of the desktop software.

If you work in Python and want to automate your workflows, the Hades Python API is available separately. See :doc:`Python Installation </api/python_installation>` to get started.

----

.. Install from Source
.. -------------------

.. If you prefer to install Hades directly from its source, clone the GitHub repository and build the .exe yourself:

.. .. code-block:: bash

..    example code here

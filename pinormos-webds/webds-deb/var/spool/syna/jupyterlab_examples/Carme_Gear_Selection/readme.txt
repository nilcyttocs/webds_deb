This example code makes use of Prompter and JupyterDash to create a gear selection wizard for the Carme NSM. The entry point is the wizard.ipynb IPython notebook. Running the notebook launches the wizard.

By default, the wizard is configured to do sweeps of 10 integration durations starting from 24 and incrementing by 1 for each step of the sweep. The wizard is also configured to cover 5 different noise conditions. These configurations are set at the top of wizard.ipynb (int_durs and test_conditions).

The wizard makes use of JupyterDash through 3 separate ports. The following port forwarding commands need to be issued first from the host computer this browser is running on before running the wizard.
  adb forward tcp:8050 tcp:8050
  adb forward tcp:8051 tcp:8051
  adb forward tcp:8052 tcp:8052

The wizard is set up to work with PR3696805 for Keys. As such, the wizard requires that the private config JSON file of PR3696805 (renamed as config_private.json) be placed in the Packrat directory in the file browser in the left sidebar (/Packrat/3696805/config_private.json).

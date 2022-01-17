# Welcome to WebDS

---

WebDS is a web-based implementation of Design Studio. It is integrated into the JupyterLab environment where you accessed this README document.

On the JupyterLab launcher page you can find three categories.
- IPython
- WebDS
- Other

The **IPython** category is where you can create IPython notebooks (.ipynb files) and start IPython console sessions for interactive Python scripting.

The **WebDS** category contains the WebDS features added to the JupyterLab environment.

The **Other** category contains various tools including Terminal for CLI operations on the Raspberry Pi and tools for creating text (.txt), Markdown (.md), and Python (.py) files as well as opening a contextual help window for additional information on Python functions.

### IPython

From within an IPython notebook or an IPython console, you can access the TouchComm device connected to the Raspberry Pi by making use of the TouchComm and AsicProgrammer Python modules already residing in the Raspbery Pi file system. The TouchComm Python module is for performing operations outlined in the TouchComm protocol specification on the device. The AsicProgrammer Python module is for performing erase and program on the device.

The path to the TouchComm and AsicProgrammer Python modules has already been configured in the IPython environment. From within an IPython notebook or an IPython console, you can import the TouchComm Python module as follows.
```python
from touchcomm import TouchComm
```
On the other hand, you can import the AsicProgrammer Python module as follows.
```python
from programmer import AsicProgrammer
```
The user guides of the TouchComm and AsicProgrammer Python modules containing detailed usage and API information can be found in the Documentation section of the WebDS category.

### WebDS

The WebDS features are in active development and will continue to be rolled out as they become available in future PinormOS releases.

Presently, WebDS offers the following features.
- README - This document.
- Documentation - This is where you can find the user guides of the TouchComm and AsicProgrammer Python modules.
- Software Update - This is where you can do PinormOS system update on the Raspberry Pi.
- ADC Data - This is where you can view real-time heatmap plots of delta and raw image reports.
- Erase and Program - This is where you can do chip reprogram with a .hex file.

### Workspace

The JupyterLab workspace is located in /home/pi/jupyter/workspace on the Raspberry Pi. It is shown as the root directory in the file browser in the left sidebar of JupyterLab. In the workspace you can find a Synaptics directory. This is a read-only directory containing useful reference materials. The reference materials include the following.

- TouchComm protocol specification
- User guides of TouchComm and AsicProgrammer Python modules
- This REAME file
- Various Python sample code

The structure of the Synaptics directory is as follows.
```
Synaptics/
    |
    |___Documentation/
    |   |
    |   |___Specifications/
    |   |   |
    |   |   |___TouchComm_Protocol/
    |   |       |
    |   |       |___511-000746-01_RevL_TouchComm.pdf
    |   |
    |   |___User_Guides/
    |       |
    |       |___AsicProgrammer/
    |       |   |
    |       |   |___AsicProgrammer User Guide (HTML)
    |       |
    |       |___TouchComm/
    |           |
    |           |___TouchComm User Guide (HTML)
    |
    |___readme.md
    |
    |___Sample_Code/
        |
        |___capture_reports.ipynb
        |
        |___erase_and_program.ipynb
        |
        |___identify.ipynb
        |
        |___reflash.ipynb
```

# Welcome to WebDS

---

WebDS is a web-based implementation of Design Studio. It is integrated into the JupyterLab environment where you accessed this README document.

On the JupyterLab launcher page you can the following categories.
- **Favourites**&nbsp;&nbsp;&nbsp;Individual widgets from the other categories can be added to the Favourites category by right-clicking on the widget to add. Widgets can be removed from the Favourites category also by right-clicking on the widget to remove.
- **Firmware Install**&nbsp;&nbsp;&nbsp;This category contains widgets for updating the firmware running on the connected TouchComm device.
- **Touch - Assessment**&nbsp;&nbsp;&nbsp; This category contains widgets for exploring and assessing details about the connected TouchComm device.
- **Touch - Configuration**&nbsp;&nbsp;&nbsp; This category contains widgets for updating various configuration settings on the connected TouchComm device.
- **Touch - Development**&nbsp;&nbsp;&nbsp; This category contains widgets for performing development and evaluation tasks and include those for creating IPython notebooks (.ipynb files) and starting Ipython console sessions for interactive Python scripting.
- **DSDK - Applications**&nbsp;&nbsp;&nbsp; This category contains widgets for accessing reference documentation and performing various setup and configuration tasks on the DSDK.

### IPython

From within an IPython notebook or an IPython console, you can access the TouchComm device connected to the DSDK by making use of the TouchComm and AsicProgrammer Python modules already residing in the file system on the DSDK. The TouchComm Python module is for performing operations outlined in the TouchComm protocol specification on the device. The AsicProgrammer Python module is for performing erase and program on the device.

The path to the TouchComm and AsicProgrammer Python modules has already been configured in the IPython environment. From within an IPython notebook or an IPython console, you can import the TouchComm Python module as follows.
```python
from touchcomm import TouchComm
```
On the other hand, you can import the AsicProgrammer Python module as follows.
```python
from programmer import AsicProgrammer
```
The user guides for the TouchComm and AsicProgrammer Python modules containing detailed usage and API information can be found in the *Documentation* section of the *DSDK - Applications* category.


### Workspace

The JupyterLab workspace is located at /home/dsdkuser/jupyter/workspace on the DSDK. It is shown as the root directory in the file browser in the left sidebar of JupyterLab. In the workspace you can find a Synaptics directory. This is a read-only directory containing useful reference materials. The reference materials include the following.

- TouchComm protocol specification
- User guides for TouchComm and AsicProgrammer Python modules
- This REAME file
- Various IPython sample code

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
    |   |   |
    |   |   |___AsicProgrammer/
    |   |   |   |
    |   |   |   |___AsicProgrammer User Guide (HTML)
    |   |   |
    |   |   |___TouchComm/
    |   |       |
    |   |       |___TouchComm User Guide (HTML)
    |   |
    |   |___WebDS_API/
    |       |
    |       |___webds_api.yaml
    |
    |___readme.md
    |
    |___Sample_Code/
        |
        |___Carme_Gear_Selection/
        |   |
        |   |___readme.txt
        |   |
        |   |___wizard.ipynb
        |
        |___adc_plot.ipynb
        |
        |___capture_reports.ipynb
        |
        |___data_playback.ipynb
        |
        |___erase_and_program.ipynb
        |
        |___identify.ipynb
        |
        |___prototyping.ipynb
        |
        |___reflash.ipynb
        |
        |___touch_plot.ipynb
```

The workspace also contains a Packrat directory for the placement of Packrat files for use by WebDS and IPython notebooks. The structure of the Packrat directory follows that of the Packrat cache. For example, the Packrat files for PR1234567 should be placed in the /Packrat/1234567 directory in the workspace.

---

#### Note
The AsicProgrammer Python module and its associated user guide are available only in the internal version of WebDS.
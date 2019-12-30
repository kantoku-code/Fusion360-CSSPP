#FusionAPI_python Addin Closed Space Sphere Packing Problem Ver0.0.1
#Author-kantoku
#Description-Closed Space Sphere Packing Problem

#using Fusion360AddinSkeleton
#https://github.com/tapnair/Fusion360AddinSkeleton
#Special thanks:Patrick Rainsberry

import adsk.core

from .CreateCube import CreateCube
from .ContactCheck import ContactCheck
from .CloseAllDocs import CloseAllDocs

commands = []
command_definitions = []

# Set to True to display various useful messages when debugging your app
debug = False

# create panel info
TABNAME = 'SolidTab'
PANELNAME = 'CSSPP'

def run(context):

    # create cube
    cmd = {
        'cmd_name': '立方体作成',
        'cmd_description': '立方体作成',
        'cmd_id': 'create_cube',
        'cmd_resources': './resources/CreateCube',
        'workspace': 'FusionSolidEnvironment',
        'toolbar_panel_id': PANELNAME,
        'class': CreateCube
    }
    command_definitions.append(cmd)

    # Cube-Sphere Contact Check
    cmd = {
        'cmd_name': '接触チェック',
        'cmd_description': '接触チェック',
        'cmd_id': 'contact_check',
        'cmd_resources': './resources/ContactCheck',
        'workspace': 'FusionSolidEnvironment',
        'toolbar_panel_id': PANELNAME,
        'class': ContactCheck
    }
    command_definitions.append(cmd)

    # close All Document
    cmd = {
        'cmd_name': '全て閉じる',
        'cmd_description': '全て閉じる',
        'cmd_id': 'close_all_doc',
        'cmd_resources': './resources/CloseAllDocs',
        'workspace': 'FusionSolidEnvironment',
        'toolbar_panel_id': PANELNAME,
        'class': CloseAllDocs
    }
    command_definitions.append(cmd)


    # create panel
    panel = initPanel(TABNAME,PANELNAME)
    if not panel:
        return

    # Don't change anything below here:
    for cmd_def in command_definitions:
        command = cmd_def['class'](cmd_def, debug)
        commands.append(command)

        for run_command in commands:
            run_command.on_run()

    # panel promote -index
    panelControls = panel.controls
    pControl = panelControls.item(1)
    pControl.isPromoted = True


def stop(context):
    for stop_command in commands:
        stop_command.on_stop()

def initPanel(
    tabName :str,
    panelName :str
    ) -> adsk.core.ToolbarPanel:

    try:
        app  :adsk.core.Application = adsk.core.Application.get()
        ui   :adsk.core.UserInterface = app.userInterface

        if not ui.isTabbedToolbarUI:
            return

        allDesignTabs = ui.toolbarTabsByProductType('DesignProductType')
        if allDesignTabs.count < 1:
            return

        toolsTab = allDesignTabs.itemById(tabName)
        if not toolsTab:
            return

        allToolsTabPanels = toolsTab.toolbarPanels
        newPanel = None
        newPanel = allToolsTabPanels.itemById(panelName)
        if not newPanel:
            newPanel = allToolsTabPanels.add(panelName, panelName)

        if newPanel:
            newPanel.isVisible = True
        else:
            return

        return newPanel
    except:
        return
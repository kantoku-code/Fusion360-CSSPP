# FusionAPI_python Addin CreateCube
# Author-kantoku
# Description-Create a cube with a side length of 100

import adsk.core, adsk.fusion, traceback
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase

class CreateCube(Fusion360CommandBase):
    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        adsk.terminate()

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        cf = cubeFactry()
        cf.exec()

class cubeFactry():
    def __init__(self):
        pass

    def exec(self):
        ui = None
        try:
            app  :adsk.core.Application = adsk.core.Application.get()
            ui   :adsk.core.UserInterface = app.userInterface

            # create Doc - direct mode
            app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            des  :adsk.fusion.Design = app.activeProduct
            desTypes = adsk.fusion.DesignTypes
            des.designType = desTypes.DirectDesignType

            root :adsk.fusion.Component = des.rootComponent

            # set 100
            unit100 = self.unitConv(100)

            # create box
            pnt3D = adsk.core.Point3D
            vec3D = adsk.core.Vector3D
            pnt = pnt3D.create(0.0, 0.0, 0.0)
            lVec = vec3D.create(1.0, 0.0, 0.0)
            wVec= vec3D.create(0.0, 1.0, 0.0)

            bouBox3D = adsk.core.OrientedBoundingBox3D
            box = bouBox3D.create(pnt, lVec, wVec, unit100, unit100, unit100)

            tmpBrMgr = adsk.fusion.TemporaryBRepManager.get()
            cube :adsk.fusion.BRepBody = root.bRepBodies.add(tmpBrMgr.createBox(box))
            cube.opacity = 0.5
            cube.name = 'cube100'
            
            # parametric mode
            des.designType = desTypes.ParametricDesignType

            msg = "Let's enjoy!!"
            ui.messageBox(msg)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def unitConv(
        self,
        value :float,
        def2itr :bool = True
        ) -> float:

        app  :adsk.core.Application =  adsk.core.Application.get()
        des  :adsk.fusion.Design = app.activeProduct

        um = des.unitsManager
        if def2itr:
            return um.convert(value, um.defaultLengthUnits, um.internalUnits)
        else:
            return um.convert(value, um.internalUnits, um.defaultLengthUnits)
# FusionAPI_python Addin ContactCheck var0.0.2
# Author-kantoku
# Description-接触チェック

import adsk.core, adsk.fusion, traceback
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase

class ContactCheck(Fusion360CommandBase):
    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        cf = ContactFactry()
        cf.exec()

import adsk.core, adsk.fusion, traceback
import math

_tolerance = 0.01
class ContactFactry():
    def __init__(self):
        pass

    def exec(self):

        ui = None
        try:
            app  :adsk.core.Application = adsk.core.Application.get()
            ui   :adsk.core.UserInterface = app.userInterface
            des  :adsk.fusion.Design = app.activeProduct

            # 確認用トレランス設定
            global _tolerance
            _tolerance = self.unitConv(_tolerance)

            # 拡張
            setExtensionMethods()

            # データ収集
            showBodies = self.getShowBody(des)
            cubes = [bd for bd in showBodies if bd.isCube()]
            spheres = [bd for bd in showBodies if bd.isSphere()]

            # 実行チェック
            msg = self.canExecute(cubes, spheres)
            if len(msg) > 0:
                ui.messageBox(msg)
                return

            # 交差を取得
            ints = []
            for sp in spheres:
                for cb in cubes:
                    ints.extend(sp.tryIntersect(cb))

            for idx, sp1 in enumerate(spheres):
                for sp2 in spheres[idx + 1:]:
                    ints.extend(sp1.tryIntersect(sp2))

            if len(ints) < 1:
                msg  = '交差はありません!'
                ui.messageBox(msg)
                return
            
            # 可視化
            skt = self.initRootSketch()
            skt.name = 'ContactCheck'

            skt.arePointsShown = False
            skt.isComputeDeferred = True
            [i.drawSkt(skt) for i in  ints if i]
            skt.isComputeDeferred = False

            # 干渉チェック
            if skt.isCollision():
                skt.name += '_is_Collision!!'
                msg = '干渉有り!!'
            else:
                msg = '干渉無し!'

            # おしまい
            app.activeViewport.refresh()
            ui.messageBox(msg)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def canExecute(
        self,
        cubes :list,
        spheres :list) -> str:

        msgLst = []
        
        # 立方体チェック
        if len(cubes) < 1:
            msgLst.append('表示された正方形が、みつかりません!')
        elif len(cubes) > 1:
            msgLst.append('表示する正方形は、1個にして下さい!')

        # 球体チェック
        if len(spheres) < 1:
            msgLst.append('表示された球体が、みつかりません!')

        rads = set(self.getAllRadius(spheres))
        if len(rads) > 1:
            msg = '\n'.join([str(self.unitConv(r, False)) for r in rads])
            msgLst.append('表示された球体の半径が複数有るため中止します!!\n' + msg)

        return '\n'.join(msgLst)
    
    # 桁数指定四捨五入
    # https://qiita.com/sak_2/items/b2dd8bd1c4e4b0788e9a
    def round_tol(self, x):
        tol = str(_tolerance)
        decimal = tol.find('.')
        p=10**(len(tol)-decimal)
        return (x*p*2+1)//2/p

    def initRootSketch(
        self) -> adsk.fusion.Sketch:
        
        app  :adsk.core.Application = adsk.core.Application.get()
        des  :adsk.fusion.Design = app.activeProduct
        root :adsk.fusion.Component = des.rootComponent

        return root.sketches.add(root.xYConstructionPlane)

    def getShowBody(
        self,
        des :adsk.fusion.Design) -> list:

        return [bBody
            for comp in des.allComponents if comp.isBodiesFolderLightBulbOn
            for bBody in comp.bRepBodies if bBody.isLightBulbOn & bBody.isVisible]

    def getAllRadius(
        self,
        spheres :list) -> list:

        lst = []
        for brep in spheres:
            for face in brep.faces:
                lst.append(self.round_tol(face.geometry.radius))

        return lst

    def unitConv(
        self,
        value :float,
        def2itr :bool = True) -> float:

        app  :adsk.core.Application = adsk.core.Application.get()
        des  :adsk.fusion.Design = app.activeProduct

        um = des.unitsManager
        if def2itr:
            return um.convert(value, um.defaultLengthUnits, um.internalUnits)
        else:
            return um.convert(value, um.internalUnits, um.defaultLengthUnits)

def setExtensionMethods():
    adsk.fusion.BRepBody.isCube = isCube
    adsk.fusion.BRepBody.isSphere = isSphere
    adsk.fusion.BRepBody.tryIntersect = tryIntersect
    adsk.fusion.BRepBody.rootMatrix = getRootMatrix
    adsk.fusion.Sketch.isCollision = isCollision
    adsk.core.Point3D.midPoint = midPoint3D

    adsk.core.ObjectCollection.drawSkt = drawSketchCurve
    adsk.core.Point3D.drawSkt = drawSketchPoint
    adsk.core.Circle3D.drawSkt = drawSketchCircle

def drawSketchCircle(
    self :adsk.core.ObjectCollection,
    skt :adsk.fusion.Sketch):

    skt.sketchCurves.sketchFittedSplines.addByNurbsCurve(self.asNurbsCurve)

def drawSketchCurve(
    self :adsk.core.ObjectCollection,
    skt :adsk.fusion.Sketch):

    skt.sketchCurves.sketchFittedSplines.add(self)

def drawSketchPoint(
    self :adsk.core.Point3D,
    skt :adsk.fusion.Sketch):

    skt.sketchPoints.add(self)

def isCollision(
    self :adsk.fusion.Sketch) -> bool:

    if self.sketchCurves.count > 0:
        return True
    else:
        return False

def isSphere(
    self :adsk.fusion.BRepBody) -> bool:

    # すべて球面か?
    sr = adsk.core.SurfaceTypes.SphereSurfaceType
    if len([fc for fc in self.faces if fc.geometry.surfaceType != sr]) > 0:
        return False

    # 半径は一致しているか?
    if len(set([round(fc.geometry.radius, 4) for fc in self.faces])) > 1:
        return False

    # 面積は正しいか?
    r = self.faces.item(0).geometry.radius
    if abs(4 * math.pi * r * r - self.area) > 0.001:
        return False

    return True

def isCube(
    self :adsk.fusion.BRepBody) -> bool:

    # 頂点・エッジ・面数正しい?
    if self.faces.count != 6 or self.edges.count != 12 or self.vertices.count != 8:
        return False
    
    # 各面積は同じか?
    if len(set([round(fc.area, 4) for fc in self.faces])) > 1:
        return False
    
    # すべて平面か?
    flat = adsk.core.SurfaceTypes.PlaneSurfaceType
    if len([fc for fc in self.faces if fc.geometry.surfaceType != flat]) > 0:
        return False

    return True

def tryIntersect(
    self :adsk.fusion.BRepBody,
    tgt :adsk.fusion.BRepBody):

    spSurfs = self.faces
    spMat = self.rootMatrix()

    tgtSurfs = tgt.faces
    tgtMat = tgt.rootMatrix()

    app  :adsk.core.Application = adsk.core.Application.get()
    measMgr = app.measureManager

    ints = []
    for spSurf in spSurfs:
        spGeo = adsk.core.Sphere.cast(spSurf.geometry)
        spGeo.transformBy(spMat)

        for tgtSurf in tgtSurfs:
            if tgt.isCube():
                # cube
                tgtGeo = adsk.core.Plane.cast(tgtSurf.geometry)
                tgtGeo.transformBy(tgtMat)
                tgtEva :adsk.core.SurfaceEvaluator = tgtSurf.evaluator
                interLst = tgtGeo.intersectWithSurface(spGeo)

                if interLst.count > 0:
                    # 干渉
                    inter = interLst.item(0)
                    crvEva = inter.evaluator
                    _, startParameter, endParameter = crvEva.getParameterExtents()
                    _, pnts = crvEva.getStrokes(startParameter, endParameter, _tolerance)

                    onPnts = adsk.core.ObjectCollection.create()
                    for pnt in pnts:
                        _, prm = tgtEva.getParameterAtPoint(pnt)
                        if tgtEva.isParameterOnFace(prm):
                            onPnts.add(pnt)

                    if onPnts.count > 0:
                        ints.append(onPnts)
                else:
                    # 接触
                    minLength = measMgr.measureMinimumDistance(tgtGeo, spGeo.origin)
                    if abs(minLength.value - spGeo.radius) < _tolerance:
                        inf = adsk.core.InfiniteLine3D.create(spGeo.origin, tgtGeo.normal)
                        pnt = tgtGeo.intersectWithLine(inf)
                        _, prm = tgtEva.getParameterAtPoint(pnt)
                        if tgtEva.isParameterOnFace(prm):
                            ints.append(pnt)

            else:
                # sphere
                tgtGeo = adsk.core.Sphere.cast(tgtSurf.geometry)
                tgtGeo.transformBy(tgtMat)
                tgtOri :adsk.core.Point3D = tgtGeo.origin
                tgtRad = tgtGeo.radius

                if abs(spGeo.radius - tgtRad) > _tolerance:
                    return None
                
                spOri = spGeo.origin
                minLength = tgtOri.distanceTo(spOri)
                if minLength > tgtRad * 2:
                    # 干渉なし
                    continue
                
                if minLength < _tolerance:
                    # 同一
                    continue

                if abs(minLength - tgtRad * 2) < _tolerance:
                    # 接触
                    ints.append(spOri.midPoint(tgtOri))
                else:
                    # 干渉
                    vec = spOri.asVector()
                    vec.subtract(tgtOri.asVector())
                    ori = spOri.midPoint(tgtOri)
                    pln = adsk.core.Plane.create(ori, vec)

                    interLst = pln.intersectWithSurface(spGeo)
                    [ints.append(c) for c in interLst]

    return ints

def getRootMatrix(
    self :adsk.fusion.BRepBody) -> adsk.core.Matrix3D:

    comp = adsk.fusion.Component.cast(self.parentComponent)
    des = adsk.fusion.Design.cast(comp.parentDesign)
    root = des.rootComponent

    mat = adsk.core.Matrix3D.create()
  
    if comp == root:
        return mat

    occs = root.allOccurrencesByComponent(comp)
    if len(occs) < 1:
        return mat
    
    occ = occs[0]
    occ_names = occ.fullPathName.split('+')
    occs = [root.allOccurrences.itemByName(name) 
                for name in occ_names]
    mat3ds = [occ.transform for occ in occs]
    mat3ds.reverse()
    for mat3d in mat3ds:
        mat.transformBy(mat3d)

    return mat

def midPoint3D(
    self :adsk.core.Point3D,
    pnt :adsk.core.Point3D) -> adsk.core.Point3D:

    p = self.copy()
    p.setWithArray([(x + y) * 0.5 for (x, y) in zip(self.asArray(), pnt.asArray())])
    return p
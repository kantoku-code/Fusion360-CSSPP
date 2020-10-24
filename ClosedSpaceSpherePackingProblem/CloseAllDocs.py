# FusionAPI_python Addin CloseAllDocs
# Author-kantoku
# Description-Close all open files without saving

import adsk.core, traceback
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase

class CloseAllDocs(Fusion360CommandBase):
    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        adsk.terminate()
        
    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        cf = closeAllDocFactry()
        cf.run()

class closeAllDocFactry():
    def __init__(self):
        pass
    def run(self):
        ui = None
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            docs = app.documents
            msg = '{}個のファイルが開いています\n'.format(docs.count)
            msg += '全て保存せずにクローズしますがよろしいですか？'
            
            if not ui.messageBox(msg,'',1,3) == 0:
                return
                
            #逆からじゃないと全ては閉じない
            lst = [doc for doc in docs]
            [doc.close(False) for doc in lst]
            
            # ui.messageBox('Done')
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
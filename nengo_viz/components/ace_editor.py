import time

import nengo

from nengo_viz.components.component import Component, Template

class AceEditor(Component):
    def __init__(self, viz, config, uid, code):
        super(AceEditor, self).__init__(viz, config, uid)
        self.viz = viz
        self.code = code

    def javascript(self):
        return 'new VIZ.Ace(%s)' % self.code ##feed VIZ.Ace a single string of the code



    def message(self, msg):
        self.code = msg
from IPython.core.magic import Magics, magics_class, line_magic, needs_local_scope
import sys

@magics_class
class GlobalVals(Magics):
    @needs_local_scope
    @line_magic
    def globalvals(self, line, local_ns):
        '''
        '''
        myvars = line.split()
        globalns = self.shell.user_global_ns
        for v in myvars:
            local_ns[v] = globalns[v]


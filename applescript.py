from lint import Linter
import json
import platform

script = '''
import sys
from Foundation import NSAppleScript, NSConcreteValue, NSRange
import objc
import json

class CustomCodec(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, NSConcreteValue):
            if obj.objCType() == NSRange.__typestr__:
                r = obj.rangeValue()
                return (r.location, r.length)
        return json.JSONEncoder.default(self, obj)

def lint(code):
    code = code.decode('utf8')
    linter = NSAppleScript.alloc().initWithSource_(code)
    errors = dict(linter.compileAndReturnError_(None)[1] or {})
    objc.recycleAutoreleasePool()
    return CustomCodec().encode(errors)

if __name__ == '__main__':
    code = sys.stdin.read()
    print lint(code)
'''

class AppleScript(Linter):
    @classmethod
    def can_lint(cls, language):
        if platform.system() != 'Darwin':
            return
        return 'AppleScript' in language

    def lint(self):
        out = self.communicate(('/usr/bin/python', '-c', script), self.code)
        out = out.replace('\u2019', '\'')
        error = json.loads(out)
        if error:
            brief = error['NSAppleScriptErrorBriefMessage']
            # message = error['NSAppleScriptErrorMessage']
            start, end = error['NSAppleScriptErrorRange']

            line = self.code[:start].count('\n')
            offset = 0
            if line:
                offset = start - self.code[:start].rindex('\n')

            self.highlight.range(line, offset, end - offset)
            self.error(line, brief)

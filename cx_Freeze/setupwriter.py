import os
import sys
import subprocess

if sys.version_info[0] < 3:
    input = raw_input

class SetupWriter(object):
    bases = {
        "C" : "Console",
        "G" : "Win32GUI",
        "S" : "Win32Service"
    }

    @property
    def needWin32Options(self):
        return self.executableName or self.base.startswith("Win32")

    def __init__(self):
        self.name = self.GetValue("Project name")
        self.version = self.GetValue("Version", "1.0")
        self.description = self.GetValue("Description")
        self.script = self.GetValue("Python file to make executable from")
        defaultExecutableName, ext = os.path.splitext(self.script)
        self.executableName = self.GetValue("Executable file name",
                defaultExecutableName)
        if self.executableName == defaultExecutableName:
            self.executableName = None
        basesPrompt = "(C)onsole application, (G)UI application, or (S)ervice"
        while True:
            baseCode = self.GetValue(basesPrompt, "C")
            if baseCode in self.bases:
                self.base = self.bases[baseCode]
                break
        while True:
            self.setupFileName = self.GetValue("Save setup script to",
                    "setup.py")
            if not os.path.exists(self.setupFileName):
                break
            if self.GetBooleanValue("Overwrite %s" % self.setupFileName):
                break

    def GetBooleanValue(self, label, default = False):
        defaultResponse = default and "y" or "n"
        while True:
            response = self.GetValue(label, defaultResponse,
                    separator = "? ").lower()
            if response in ("y", "n", "yes", "no"):
                break
        return response in ("y", "yes")

    def GetValue(self, label, default = "", separator = ": "):
        if default:
            label += " [%s]" % default
        return input(label + separator).strip() or default

    def Write(self):
        output = open(self.setupFileName, "w")
        w = lambda s: output.write(s + "\n")

        w("from cx_Freeze import setup, Executable")
        if self.needWin32Options:
            w("import sys")
        w("")
        
        w("# Dependencies are automatically detected, but it might need")
        w("# fine tuning.")
        w("buildOptions = dict(packages = [], excludes = [])")
        w("")

        w("executables = [")
        if self.executableName is not None:
            w("    Executable(%r, %r, targetName = %r)" % \
                    (self.script, self.base, self.executableName))
        else:
            w("    Executable(%r, %r)" % (self.script, self.base))
        w("]")
        w("")
 
        w(("setup(name=%r,\n"
           "      version = %r,\n"
           "      description = %r,\n"
           "      options = dict(build_exe = buildOptions),\n"
           "      executables = executables)") % \
           (self.name, self.version, self.description))

def main():
    writer = SetupWriter()
    writer.Write()
    print("")
    print("Setup script written to %s; run it as:" % writer.setupFileName)
    print("    python %s build" % writer.setupFileName)
    if writer.GetBooleanValue("Run this now"):
        subprocess.call(["python", writer.setupFileName, "build"])


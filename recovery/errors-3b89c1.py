import os
import sys
import time
import json
import inspect
import requests
import Tkinter__Tkinter as mtk
from winmanage import quitWin
from PyEditAppBase import PyEditAppBase

import subprocess as commands  # Built in

EXIT_PANIC = 0x1


def lineno():
    callerframerecord = inspect.stack()[1]  # 0 represents this line
    # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    return info.lineno


def listDirectoryAt(d):
    return commands.getstatusoutput('ls -1 {}'.format(d))[1].split('\n')


def askForBugs(app):
    """Dependent on <app> argument being PyEdit. Not a good repurpose"""
    bug_report = mtk.Ttk("Bug Report")
    bug_report.protocol("WM_DELETE_WINDOW", lambda: quitWin(bug_report))
    bug_report.title("Submit a Bug")
    mtk.TLabel(bug_report, text="Enter a name: ").pack()
    name = mtk.Entry(bug_report)
    name.pack()
    mtk.TLabel(bug_report,
               text="Describe the steps to recreate the bug: ").pack()
    steps = mtk.Text(bug_report, width=40, height=10)
    steps.pack()
    mtk.TLabel(bug_report,
               text="Include any other additional"
                    "information that could help: ").pack()
    info = mtk.Text(bug_report, width=40, height=10)
    info.pack()
    qu = mtk.Button(bug_report, text="Next...",
                    command=lambda: askToSubmitBugs(name, steps, info, app,
                                                    bug_report))
    qu.pack()
    bug_report.mainloop()


class BugReport:
    def __init__(self, bugtime, platform, version, pyv, name, steps, info, preferences, logfile, appname):
        self.created = bugtime
        self.platform = platform
        self.version = version
        self.pyv = pyv
        self.name = name
        self.steps = steps
        self.info = info
        self.preferences = preferences
        self.logfile = logfile
        self.appname = appname

    def toJson(self):
        return {
            "parameters": {
                "created": self.created,
                "platform": self.platform,
                "version": self.version,
                "pyversion": str(self.pyv)
            },
            'user': {
                "user": self.name,
                "steps": self.steps,
                "info": self.info
            },
            'app': {
                "preferences": self.preferences,
                "logfile": self.logfile,
                'appname': self.appname
            }
        }


def writeBugReport(name, steps, info, app):
    """Extremely versitile. Takes a name, steps, info and class object
    and formats an error report. <app> can be None when it is not called
    for an instance of a class"""
    bugtime = time.ctime()
    platform = os.sys.platform
    version = os.sys.version
    pyeditv = app.version if app else 'N/A'
    appname = app.getName() if app else "App"

    if app is not None:
        logfile = open(app.logFileLocation)
        logtext = logfile.read()
        preffiles = app.preferencesfile
        preffile = open(os.path.realpath(preffiles.name))
        prefs = preffile.read()

        report = BugReport(bugtime, platform, version, pyeditv,
                           name, steps, info, prefs, logtext, appname)
    else:
        report = BugReport(bugtime, platform, version, pyeditv,
                           name, steps, info, None, None, appname)

    return report


def askToSubmitBugs(name, steps, info, app, br):
    br.quit()
    _name = name.get()
    _steps = steps.get(0.0, mtk.END)
    _info = info.get(0.0, mtk.END)
    br.destroy()
    error_report = writeBugReport(_name, _steps, _info, app)
    tosend = mtk.Ttk("To Send")
    tosend.title("Bug Report")
    mtk.TLabel(tosend,
               text="The following information will be submitted \n"
                    "(no personally identifiable information is sent) ").pack()
    a = mtk.Text(tosend, width=125, height=30)
    a.insert(0.0, error_report)
    a.pack()
    can = mtk.Button(tosend, text='Cancel', command=lambda: quitWin(tosend))
    can.pack()
    qu = mtk.Button(tosend, text="Go",
                    command=lambda: sendReport(error_report, tosend))
    qu.pack()
    tosend.mainloop()


def sendReport(report, win):
    win.destroy()
    win.quit()

    if os.environ['PY_EDIT_DEBUG']:
        r = requests.post('http://localhost:8099/bug-report', json=report.toJson());
    else:
        r = requests.post('https://pyeditbugserver.herokuapp.com/bug-report', json=report.toJson())
    if (r.status_code != 200):
        al = mtk.Ttk("Bug Send Error Win")
        al.title("Error")
        mtk.Label(al,
                  text=r.reason).pack()
        mtk.Button(al, text='ok', command=lambda: quitWin(al)).pack()
        al.mainloop()
    else:
        al = mtk.Ttk("Bug Report Successfully Sent")
        al.
        al.title("Success!")
        mtk.Button(al, text='ok', command=lambda: quitWin(al)).pack()
        al.mainloop()


def truncateLog(path, linestokeep=16348):
    """Opens a log file at <path> and truncates the first (total - linestokeep)
    lines thus trimming the file at <path> to being the last <linestokeep>
    number of lines in the original file"""
    lfile = open(path)

    text = lfile.readlines()

    if len(text) > linestokeep:
        trunctext = text[-linestokeep:]
    else:
        trunctext = text

    texttowrite = "".join(trunctext)  # Cannot Write a list, needs a string

    wlfile = open(path, "w")  # Open 'w' after reading to prevent erased file
    wlfile.write(texttowrite)
    lfile.close()
    wlfile.close()


def log(app_or_path, facility=0, severity=7,
        message="Generic Log Msg", lineno=lineno(), source=__file__, last_call=False):
    """Takes a class object and severity (int), message (str) and source (str)
    and writes it to the "writelog" file of the <app_or_path>. If <app_or_path>
    is a string then it opens the file at path <app_or_path> and writes to it

    facility is 0-main; 1-procedure; 2-class; 3-method
    severity is the same as SYSLOG

    """
    logmessage = \
        "{}: FACILITY={} [Level: {}] -> {} at line #{} from {}\n".format(time.ctime(),
                                                                         facility,
                                                                         severity, message,
                                                                         lineno, source)
    if isinstance(app_or_path, str):
        f = open(app_or_path, 'a')
        f.write(logmessage)
        f.flush()
        os.fsync(f.fileno())
        if last_call:
            f.close()
    else:
        if isinstance(app_or_path, PyEditAppBase):
            if not app_or_path.writelog.closed:
                app_or_path.writelog.write(logmessage)
                app_or_path.writelog.flush()
                os.fsync(app_or_path.writelog.fileno())
                if last_call:
                    app_or_path.writelog.close()
            else:
                f = open(app_or_path.writelog.name, 'a')
                f.write(logmessage)
                f.flush()
                os.fsync(f.fileno())
                if last_call:
                    f.close()
        else:
            raise TypeError(
                "First argument to log function must be app instance or path to file (in: {})".format(__file__))


def pyedit_panic():
    raise SystemExit(EXIT_PANIC)


def exit_on_error(traceback, fatal=False):
    # Note that nothing is being called on app.
    # This is because the __main__ file as a try/except/finally
    # and the finally called app.halt()
    # Since we are raising SystemExit, finally *WILL*
    # take place before the system quits. Therefore,
    # it is redundant (and dangerous since app.halt() closes files)
    # to call end twice. Therefore, when you raise SystemExit
    # app.halt() is called in the finally clause of the
    # __main__.py file
    alert = mtk.Ttk("alert win in CLS: HandleError")
    alert.title("Fatal Error")
    alertlabel = mtk.TLabel(alert,
                            text="Something went wrong and PyEdit needs to"
                                 "close.\nYou may lose unsaved changes."
                                 "\nWe Apologize for the inconvenience.")
    alerterror = mtk.TLabel(alert, text="\n\n{}\n\n".format(traceback))
    if fatal:
        alertbutton = mtk.Button(alert, text="Quit",
                                 command=pyedit_panic)
    else:
        alertbutton = mtk.Button(alert, text="Quit",
                                 command=alert.destroy)
    alertlabel.pack()
    alerterror.pack()
    alertbutton.pack()
    alert.mainloop()


class UnicodeException(Exception):
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Presence of Unicode Characters"

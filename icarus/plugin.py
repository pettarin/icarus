#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
import datetime
import os
import re
import sys
import tempfile
import zipfile
if sys.version_info[0] == 2:
    import Tkinter as tkinter
    import ttk as tkinter_ttk
    import tkFileDialog as tkinter_filedialog
    import Tkconstants as tkinter_constants
    import ScrolledText as tkinter_scrolledtext
else:
    import tkinter
    import tkinter.ttk as tkinter_ttk
    import tkinter.filedialog as tkinter_filedialog
    import tkinter.constants as tkinter_constants
    import tkinter.scrolledtext as tkinter_scrolledtext

from moedit import MOEdit

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "0.0.2"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

PLUGIN_NAME = "icarus"

ROOT_MIN_WIDTH = 800
ROOT_MIN_HEIGHT = 600

class MainGUI(tkinter.Frame):
    DEFAULT_GUI_MIN_WIDTH = 800
    DEFAULT_GUI_MIN_HEIGHT = 600
    DEFAULT_ID_FORMAT = "f%06d"
    DEFAULT_ID_REGEX = r"f[0-9]{6}"
    DEFAULT_MO_CLASS = "mo"
    DEFAULT_NOMO_CLASS = "nomo"
    DEFAULT_EXISTING_IDS_ONLY = 0
    DEFAULT_SAVE_DIRECTORY = os.path.expanduser("~")
    DEFAULT_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "li", "p", "q"]

    OPERATION_ADD = "add"
    OPERATION_REMOVE = "remove"
    OPERATION_REMOVE_MO_CLASS = "remove_mo_class"

    REQUIRED_PREF_KEYS = [
        "id_format",
        "id_regex",
        "mo_class",
        "nomo_class",
        "existing_ids_only",
        "save_directory",
        "tags",
        "window_geometry"
    ]
    SMIL_DIRECTORY = "Misc"
    
    SMIL_HEADER = """<smil xmlns="http://www.w3.org/ns/SMIL" xmlns:epub="http://www.idpf.org/2007/ops" version="3.0">
 <body>
  <seq id="seq1" epub:textref="../%s">"""
    SMIL_ROW = """   <par id="%s"><text src="../%s#%s"/><audio clipBegin="%s" clipEnd="%s" src="../%s"/></par>"""
    SMIL_FOOTER = """  </seq>
 </body>
</smil>"""

    def __init__(self, parent, bk):
        tkinter.Frame.__init__(self, parent, border=5)
        self.parent = parent
        self.bk = bk
        self.prefs = bk.getPrefs()
        if not self.has_all_required_pref_keys():
            self.apply_defaults()
        self.initialize_ui()
        self.populate_pairs()
        parent.protocol("WM_DELETE_WINDOW", self.quit)

    def has_all_required_pref_keys(self):
        """
        Return True if and only if the preferences
        have all the required keys.

        :rtype: bool
        """
        for key in self.REQUIRED_PREF_KEYS:
            if not key in self.prefs:
                return False
        return True

    def populate_pairs(self):
        """
        Get matching (text, audio) pairs
        and populate the Text element.
        """
        def href_to_number(href):
            """
            Extract the first number appearing
            in the basename (without extension)
            of the file with given href,
            and return the corresponding string,
            padded up to 6 zeros.
            If no number appears in the basename
            (without extension),
            return the basename (without extension).

            :param href: the href path
            :type  href: str
            :rtype: str
            """
            base = os.path.basename(href)
            if "." in base:
                base = ".".join(base.split(".")[:-1])
            numbers = re.findall(r"\d+", base)
            if len(numbers) > 0:
                base = str(numbers[0]).zfill(6)
            return base
        pairs = []
        text_files = {}
        for mid, href in self.bk.text_iter():
            num = href_to_number(href)
            text_files[num] = href
        for mid, href, mediatype in self.bk.media_iter():
            num = href_to_number(href)
            if num in text_files:
                pairs.append((text_files[num], href))
        self.pairs_text.delete("1.0", tkinter.END)
        if len(pairs) > 0: 
            self.pairs_text.insert(tkinter.INSERT, "\n".join(["%s <-> %s" % (p[0], p[1]) for p in pairs]))
        else:
            msg = []
            msg.append("No (text, audio) pairs found.")
            msg.append("")
            msg.append("Please make sure that:")
            msg.append("  1. you added the MO attributes (use the panel above); and")
            msg.append("  2. you imported the audio files; and")
            msg.append("  3. the text/audio file names are pairable.")
            self.pairs_text.insert(tkinter.INSERT, "\n".join(msg))

    def quit(self):
        """
        Close the plugin GUI.
        """
        # store other prefs
        self.save()
        # closing window
        self.parent.destroy()
        self.quit()

    def save(self):
        """
        Save the preferences.
        """
        # store window geometry
        self.prefs["window_geometry"] = self.parent.geometry()
        # store other preferences
        tags = sorted([tag for tag in set(self.tags_var.get().split(" ")) if len(tag) > 0])
        self.prefs["tags"] = tags
        self.prefs["mo_class"] = self.mo_class_var.get().strip()
        self.prefs["nomo_class"] = self.nomo_class_var.get().strip()
        self.prefs["id_regex"] = self.id_regex_var.get().strip()
        self.prefs["id_format"] = self.id_format_var.get().strip()
        self.prefs["existing_ids_only"] = self.existing_ids_only.get()
        self.prefs["save_directory"] = self.save_directory_var.get().strip()
        # save preferences
        self.bk.savePrefs(self.prefs)

    def apply_defaults(self):
        """
        Apply the default values to the preferences.
        """
        # reset window geometry
        self.parent.update_idletasks()
        w = self.parent.winfo_screenwidth()
        h = self.parent.winfo_screenheight()
        rootsize = (self.DEFAULT_GUI_MIN_WIDTH, self.DEFAULT_GUI_MIN_HEIGHT)
        x = w / 2 - rootsize[0] / 2
        y = h / 2 - rootsize[1] / 2
        self.prefs["window_geometry"] = "%dx%d+%d+%d" % (rootsize + (x, y))
        # reset tags
        self.prefs["tags"] = self.DEFAULT_TAGS
        self.prefs["mo_class"] = self.DEFAULT_MO_CLASS
        self.prefs["nomo_class"] = self.DEFAULT_NOMO_CLASS
        self.prefs["id_regex"] = self.DEFAULT_ID_REGEX
        self.prefs["id_format"] = self.DEFAULT_ID_FORMAT
        self.prefs["existing_ids_only"] = self.DEFAULT_EXISTING_IDS_ONLY
        self.prefs["save_directory"] = self.DEFAULT_SAVE_DIRECTORY

    def initialize_ui(self):
        """
        Initialize the plugin UI, creating its elements.
        The window geometry is loaded from the preferences.
        """
        self.parent.title(PLUGIN_NAME)
        
        body = tkinter.Frame(self)
        body.pack(fill=tkinter_constants.BOTH, expand=True)

        frameAddRemove = tkinter.LabelFrame(body, bd=2, padx=10, pady=10, relief=tkinter_constants.GROOVE, text="Step 1: add MO attributes")
        frameAddRemove.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        frame1 = tkinter.Frame(frameAddRemove)
        frame1.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)
        tkinter.Label(frame1, text="Tags to process: ").pack(side=tkinter_constants.LEFT)
        self.tags_var = tkinter.StringVar()
        self.tags_var.set(" ".join(self.prefs["tags"]))
        tags_entry = tkinter.Entry(frame1, textvariable=self.tags_var)
        tags_entry.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH, expand=1)

        frame2 = tkinter.Frame(frameAddRemove)
        frame2.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)
        tkinter.Label(frame2, text="Don't process if tag has class: ").pack(side=tkinter_constants.LEFT)
        self.nomo_class_var = tkinter.StringVar()
        self.nomo_class_var.set(self.prefs["nomo_class"])
        nomo_class_entry = tkinter.Entry(frame2, textvariable=self.nomo_class_var)
        nomo_class_entry.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH, expand=1)

        frame3 = tkinter.Frame(frameAddRemove)
        frame3.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)
        tkinter.Label(frame3, text="Add class to MO tags: ").pack(side=tkinter_constants.LEFT)
        self.mo_class_var = tkinter.StringVar()
        self.mo_class_var.set(self.prefs["mo_class"])
        mo_class_entry = tkinter.Entry(frame3, textvariable=self.mo_class_var)
        mo_class_entry.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH, expand=1)

        frame4 = tkinter.Frame(frameAddRemove)
        frame4.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)
        tkinter.Label(frame4, text="MO ID regex: ").pack(side=tkinter_constants.LEFT)
        self.id_regex_var = tkinter.StringVar()
        self.id_regex_var.set(self.prefs["id_regex"])
        id_regex_entry = tkinter.Entry(frame4, textvariable=self.id_regex_var)
        id_regex_entry.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH, expand=1)

        frame5 = tkinter.Frame(frameAddRemove)
        frame5.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)
        tkinter.Label(frame5, text="MO ID format: ").pack(side=tkinter_constants.LEFT)
        self.id_format_var = tkinter.StringVar()
        self.id_format_var.set(self.prefs["id_format"])
        id_format_entry = tkinter.Entry(frame5, textvariable=self.id_format_var)
        id_format_entry.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH, expand=1)

        frame6 = tkinter.Frame(frameAddRemove)
        frame6.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)
        self.existing_ids_only = tkinter.IntVar()
        self.existing_ids_only.set(self.prefs["existing_ids_only"])
        existing_ids_only_checkbox = tkinter.Checkbutton(frame6, text="Add MO class only to tags with existing MO ID attribute", variable=self.existing_ids_only)
        existing_ids_only_checkbox.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH)

        frame7 = tkinter.Frame(frameAddRemove)
        frame7.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)
        self.remove_mo_class_button = tkinter.Button(frame7, text="Remove MO class only", command=self.cmd_remove_mo_class)
        self.remove_mo_class_button.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.X, expand=1)
        self.remove_button = tkinter.Button(frame7, text="Remove MO class and id", command=self.cmd_remove)
        self.remove_button.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.X, expand=1)
        self.add_button = tkinter.Button(frame7, text="Add MO class and id", command=self.cmd_add)
        self.add_button.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.X, expand=1)
        
        frameGenerate = tkinter.LabelFrame(body, bd=2, padx=10, pady=10, relief=tkinter_constants.GROOVE, text="Step 2: export aeneas job ZIP file")
        frameGenerate.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH, expand=1)

        frameA = tkinter.Frame(frameGenerate)
        frameA.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH, expand=1)
        #self.pairs_text = tkinter.Text(frameA, height=10)
        self.pairs_text = tkinter_scrolledtext.ScrolledText(frameA, height=10)
        self.pairs_text.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH, expand=1)

        frameC = tkinter.Frame(frameGenerate)
        frameC.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.BOTH)
        self.export_button = tkinter.Button(frameC, text="Export aeneas job ZIP file", command=self.cmd_export)
        self.export_button.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.X, expand=1)

        frameB = tkinter.Frame(frameGenerate)
        frameB.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.BOTH)
        tkinter.Label(frameB, text="Export ZIP file to: ").pack(side=tkinter_constants.LEFT)
        self.save_directory_var = tkinter.StringVar()
        self.save_directory_var.set(self.prefs["save_directory"])
        save_directory_entry = tkinter.Entry(frameB, textvariable=self.save_directory_var)
        save_directory_entry.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH, expand=1)
        self.dir_button = tkinter.Button(frameB, text="...", command=self.cmd_cd)
        self.dir_button.pack(side=tkinter_constants.RIGHT, fill=tkinter_constants.X, expand=1)

        frameImport = tkinter.LabelFrame(body, bd=2, padx=10, pady=10, relief=tkinter_constants.GROOVE, text="Step 3: import SMIL files")
        frameImport.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)
        self.import_button = tkinter.Button(frameImport, text="Import SMIL files", command=self.cmd_import)
        self.import_button.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.X, expand=1)

        frameButtons = tkinter.Frame(body)
        frameButtons.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.BOTH)
        self.default_button = tkinter.Button(frameButtons, text="Reset defaults", command=self.cmd_reset)
        self.default_button.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.X, expand=1)
        self.quit_button = tkinter.Button(frameButtons, text="Quit", command=self.quit)
        self.quit_button.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.X, expand=1)

        self.parent.geometry(self.prefs["window_geometry"])


    def cmd_reset(self):
        """
        Reset the settings to their default values.
        """
        self.apply_defaults()
        self.tags_var.set(" ".join(self.prefs["tags"]))
        self.mo_class_var.set(self.prefs["mo_class"])
        self.nomo_class_var.set(self.prefs["nomo_class"])
        self.id_regex_var.set(self.prefs["id_regex"])
        self.id_format_var.set(self.prefs["id_format"])
        self.existing_ids_only.set(self.prefs["existing_ids_only"])
        self.save_directory_var.set(self.prefs["save_directory"])
        self.save()

    def cmd_remove(self):
        """
        The user clicked the "Remove MO class and id" button.
        Perform the corresponding action.
        """
        self.save()
        self.add_remove(self.OPERATION_REMOVE)
        self.quit()

    def cmd_remove_mo_class(self):
        """
        The user clicked the "Remove MO class only" button.
        Perform the corresponding action.
        """
        self.save()
        self.add_remove(self.OPERATION_REMOVE_MO_CLASS)
        self.quit()

    def cmd_add(self):
        """
        The user clicked the "Add MO class and id" button.
        Perform the corresponding action.
        """
        self.save()
        self.add_remove(self.OPERATION_ADD)
        self.quit()

    def cmd_cd(self):
        """
        The user clicked the button to change the output directory.
        Show the corresponding dialog and save the resulting path. 
        """
        path = tkinter_filedialog.askdirectory(
            initialdir=self.prefs["save_directory"],
            parent=self,
            title="Select directory",
            mustexist=True
        )
        if (path is not None) and (len(path) > 0):
            self.prefs["save_directory"] = path
            self.save_directory_var.set(path)

    def cmd_export(self):
        """
        The user clicked the button to export the aeneas job ZIP file. 
        Process the current contents of the pairs Text element,
        and, if there is at least one valid (text, audio) pair,
        create the requested ZIP file.
        """
        self.save()
        pairs = []
        data = self.pairs_text.get("1.0", tkinter.END)
        for line in data.split("\n"):
            if "<->" in line:
                arr = line.split("<->")
                if len(arr) == 2:
                    t_href = arr[0].strip()
                    a_href = arr[1].strip()
                    t_mid = self.bk.href_to_id(t_href, ow=None)
                    a_mid = self.bk.href_to_id(a_href, ow=None)
                    if (t_mid is not None) and (a_mid is not None):
                        pairs.append(((t_href, t_mid), (a_href, a_mid)))
        if len(pairs) > 0:
            self.create_aeneas_job(pairs)
        else:
            print("ERROR: no (text, audio) files found. No aeneas job file was generated.")
        self.quit()

    def cmd_import(self):
        """
        The user clicked the button to import SMIL files.
        Show the corresponding dialog and import the specified single SMIL file
        or the SMIL files inside the specified ZIP file.
        """
        self.save()
        path = tkinter_filedialog.askopenfilename(
            initialdir=self.prefs["save_directory"],
            filetypes=[("aeneas output ZIP file", ".zip"), ("SMIL file", ".smil")],
            parent=self,
            title="Select aeneas output (SMIL or ZIP of SMILs)"
        )
        if (path is not None) and (len(path) > 0) and (os.path.isfile(path)):
            if path.endswith(".zip"):
                self.import_zip_file(path)
            elif path.endswith(".smil"):
                self.import_smil_file(path)
        self.quit()


    def add_remove(self, operation):
        """
        Add or remove MO class and/or id attributes
        to the XHTML files selected in the Book View panel.

        :param operation: the requested operation 
        :type  operation: str
        """
        issues = []
        for (id_type, mid) in self.bk.selected_iter():
            if id_type == "manifest":
                href = self.bk.id_to_href(mid, ow=None)
                mime = self.bk.id_to_mime(mid, ow=None)
                if mime == "application/xhtml+xml":
                    print("File %s\n" % href)
                    
                    data = self.bk.readfile(mid).encode("utf-8")
                    moedit = MOEdit(
                        tags=self.prefs["tags"],
                        mo_class=self.prefs["mo_class"],
                        nomo_class=self.prefs["nomo_class"],
                        id_regex=self.prefs["id_regex"],
                        id_format=self.prefs["id_format"],
                        existing_ids_only=self.prefs["existing_ids_only"]
                    )
                    
                    if operation == self.OPERATION_ADD:
                        msgs, data = moedit.add_mo_attributes(data)
                    elif operation == self.OPERATION_REMOVE:
                        msgs, data = moedit.remove_mo_attributes(data, remove_class=True, remove_id=True)
                    elif operation == self.OPERATION_REMOVE_MO_CLASS:
                        msgs, data = moedit.remove_mo_attributes(data, remove_class=True, remove_id=False)
                    else:
                        msgs, data = ([], None)
                    
                    if data is not None:
                        self.bk.writefile(mid, data)
                    
                    for msg_type, msg_text in msgs:
                        print("    %s: %s" % (msg_type, msg_text))
                        if msg_type != "INFO":
                            issues.append((href, msg_type, msg_text))
                    
                    print("\n=====================\n")
        
        # print issues only, if any
        if len(issues) > 0:
            print("ISSUES FOUND:\n")
            for issue in issues:
                print("File %s : %s : %s" % issue)
        else:
            print("NO ISSUES FOUND")


    def create_aeneas_job(self, pairs):
        def now_str():
            """
            Return a string with the current date/time,
            formatted like this: "20151216_180203".

            :rtype: str
            """
            now = datetime.datetime.now()
            return "%d%02d%02d_%02d%02d%02d" % (
                now.year,
                now.month,
                now.day,
                now.hour,
                now.minute,
                now.second
            )
        
        def file_extension(href):
            """
            Return the file extension (including the leading ".")
            of the file pointed by the given href path,
            or "" if the given href does not have an extension.
            For example, "audio.mp3" produces ".mp3",
            while "audio" returns "".

            :param href: a file path
            :type  href: str
            :rtype: str
            """
            base = os.path.basename(href)
            if "." in base:
                return ".%s" % base.split(".")[-1]
            return ""

        now = now_str()
        zip_name = "%s_aeneas_job.zip" % (now)
        zip_name_proc = "%s_aeneas_job.output.zip" % (now)
        zip_path = os.path.join(self.prefs["save_directory"], zip_name)

        config_name = "config.xml"
        config_language = self.get_metadatum_value(name="language", default=None)
        if config_language is None:
            config_language = "en"
            print("WARNING: unable to determine the language from the OPF file, using '%s' instead" % (config_language))
        else:
            print("INFO: detected language '%s' in the OPF file" % (config_language))
        config = []
        config.append('<?xml version = "1.0" encoding="UTF-8" standalone="no"?>')
        config.append('<job>')
        config.append(' <job_language>%s</job_language>' % (config_language))
        config.append(' <job_description>Job from Sigil</job_description>')
        config.append(' <os_job_file_name>%s</os_job_file_name>' % (zip_name_proc))
        config.append(' <os_job_file_container>zip</os_job_file_container>')
        config.append(' <os_job_file_hierarchy_type>flat</os_job_file_hierarchy_type>')
        config.append(' <os_job_file_hierarchy_prefix>OEBPS/%s</os_job_file_hierarchy_prefix>' % (self.SMIL_DIRECTORY))
        config.append(' <tasks>')

        zip_obj = zipfile.ZipFile(zip_path, mode="w")
        i = 1
        for pair in pairs:
            (t_href, t_mid), (a_href, a_mid) = pair
            t_data = self.bk.readfile(t_mid).encode("utf-8")
            t_name = "t%06d.xhtml" % (i)
            zip_obj.writestr(t_name, t_data)
            a_data = self.bk.readfile(a_mid)
            a_name = "a%06d%s" % (i, file_extension(a_href))
            zip_obj.writestr(a_name, a_data)
            s_name = self.smil_name_from_t_href(t_href)
            config.append('  <task>')
            config.append('   <task_language>%s</task_language>' % (config_language))
            config.append('   <task_description>Task %s</task_description>' % (t_name))
            config.append('   <task_custom_id>%s</task_custom_id>' % (t_name))
            config.append('   <is_text_file>%s</is_text_file>' % (t_name))
            config.append('   <is_text_type>unparsed</is_text_type>')
            # NOTE not specifying the id regex, to allow pre-existing ids
            #      aeneas will select fragments using the MO class alone
            #config.append('   <is_text_unparsed_id_regex>%s</is_text_unparsed_id_regex>' % (self.prefs["id_regex"]))
            # NOTE elements with multiple classes (with one of them being the MO class)
            #      are handled by aeneas as well
            config.append('   <is_text_unparsed_class_regex>%s</is_text_unparsed_class_regex>' % (self.prefs["mo_class"]))
            # NOTE specifying unsorted to allow pre-existing ids
            #      that might be get shuffled by numeric or lexicographic
            config.append('   <is_text_unparsed_id_sort>unsorted</is_text_unparsed_id_sort>')
            config.append('   <is_audio_file>%s</is_audio_file>' % (a_name))
            config.append('   <os_task_file_name>%s</os_task_file_name>' % (s_name))
            config.append('   <os_task_file_format>smil</os_task_file_format>')
            config.append('   <os_task_file_smil_page_ref>../%s</os_task_file_smil_page_ref>' % (t_href))
            config.append('   <os_task_file_smil_audio_ref>../%s</os_task_file_smil_audio_ref>' % (a_href))
            config.append('  </task>')
            i += 1
        config.append(' </tasks>')
        config.append('</job>')
        zip_obj.writestr(config_name, "\n".join(config).encode("utf-8"))
        zip_obj.close()
        print("INFO: created aeneas job file '%s'" % (zip_path))
        print("INFO: you can upload it to http://aeneasweb.org or process it locally:")
        print()
        print("$ python -m aeneas.tools.execute_job %s %s" % (zip_path, self.prefs["save_directory"]))
        print()


    def create_dummy_smil_file(self, t_href, t_mid, a_href, smil_mid):
        """
        This function is not currently used.
        """
        import sigil_gumbo_bs4_adapter as gumbo_bs4
        ret = None
        xhtml_data = self.bk.readfile(t_mid).encode("utf-8")
        soup = gumbo_bs4.parse(xhtml_data)
        attributes = {
            "class": re.compile(r".*\b" + self.prefs["mo_class"] + r"\b.*"),
            "id": re.compile(r".*\b" + self.prefs["id_regex"] + r"\b.*")
        }
        s_ids = [node.attrs["id"] for node in soup.find_all(attrs=attributes)]
        if len(s_ids) > 0:
            s_name = self.smil_name_from_t_href(t_href)
            s_href = os.path.join(self.SMIL_DIRECTORY, s_name)
            mid = self.bk.href_to_id(s_href)
            if mid is not None:
                print("INFO: file '%s' exists, removing it" % (s_href))
                self.bk.deletefile(mid)
            i = 1
            data = []
            data.append(self.SMIL_HEADER % (t_href))
            for s_id in s_ids:
                p_id = "%06d" % (i)
                i += 1
                data.append(self.SMIL_ROW % (p_id, t_href, s_id, "0.000", "0.000", a_href))
            data.append(self.SMIL_FOOTER)
            data = ("\n".join(data)).encode("utf-8")
            self.bk.addfile(smil_mid, s_name, data, mime="application/smil+xml", properties=None)
            print("INFO: created file '%s'" % (s_href))
            ret = s_href
        else:
            print("ERROR: no SMIL elements in file '%s'" % (t_href))
            ret = None
        print()
        return ret


    def import_zip_file(self, path):
        """
        Import SMIL files from a ZIP file at path.
        The SMIL files are matched if their name inside the ZIP container
        ends with ".smil" (after being lowercased).

        :param path: the path to the ZIP file
        :type  path: str
        """
        try:
            zip_obj = zipfile.ZipFile(path, "r")
            smils = sorted([name for name in zip_obj.namelist() if name.lower().endswith(".smil")])
            if len(smils) > 0:
                for name in smils:
                    basename = os.path.basename(name)
                    smil_mid = "smil.%s" % basename
                    data = zip_obj.read(name)
                    self.bk.addfile(smil_mid, basename, data, mime="application/smil+xml", properties=None)
                    print("INFO: file '%s' added" % (basename))
                    extracted = True
            else:
                print("WARNING: no SMIL files found in '%s'" % (path))
            zip_obj.close()
        except:
            print("ERROR: unable to import SMIL files from '%s'" % (path))


    def import_smil_file(self, path):
        """
        Import a single SMIL file, located at path.
        """
        try:
            basename = os.path.basename(path)
            smil_mid = "smil.%s" % basename
            with open(path, "rb") as file_obj:
                data = file_obj.read()
                self.bk.addfile(smil_mid, basename, data, mime="application/smil+xml", properties=None)
            print("INFO: file '%s' added" % (path))
        except:
            print("ERROR: unable to add file '%s'" % (path))


    def smil_name_from_t_href(self, t_href):
        """
        Return the name for the SMIL file associated with
        a text file with path t_href.

        :param t_href: the path of the text file
        :type  t_href: str
        :rtype: str
        """
        return os.path.basename(t_href).replace(".xhtml", "") + ".smil"


    def get_metadatum_value(self, name, default="", first=True):
        """
        Return the value of the metadatum name, if present in the OPF,
        otherwise return the specified default value.
        If first is True, return only the first value found;
        otherwise, return the list of values found.

        :param name: the name of the metadatum to look for
        :type  name: str
        :param default: the default value to be returned if the search fails
        :type  default: str or None
        :param first: if True, return only the first value found; otherwise,
                      return the list of values found
        :type  first: bool
        :rtype: str or list of str
        """
        try:
            ps = self.bk.qp
            ps.setContent(self.bk.getmetadataxml())
            ret = []
            capture_text = False
            for text, tagprefix, tagname, tagtype, tagattr in ps.parse_iter():
                if (capture_text) and (text is not None):
                    ret.append(text)
                    capture_text = False
                elif (tagname is not None) and (tagname.endswith(name)):
                    # TODO improve on this, considering namespaces
                    # tagname might be "dc:language"
                    # so we check with endswith()
                    capture_text = True
                else:
                    capture_text = False
            if len(ret) == 0:
                return default
            elif first:
                return ret[0]
            return ret
        except:
            return default



def run(bk):
    """
    Plugin entry point
    """
    root = tkinter.Tk()
    root.title(PLUGIN_NAME)
    root.resizable(True, True)
    root.minsize(ROOT_MIN_WIDTH, ROOT_MIN_HEIGHT)
    MainGUI(root, bk).pack(fill=tkinter_constants.BOTH, expand=True)
    root.mainloop()
    return 0

def main():
    return -1
    
if __name__ == "__main__":
    sys.exit(main())


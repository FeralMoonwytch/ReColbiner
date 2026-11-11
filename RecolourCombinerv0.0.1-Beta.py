import os
import sys
import tkinter as tk
from tkinter import filedialog


def resource_path(relative_path):
    """Get path to a bundled resource, works both in dev and compiled .exe"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# ---------------- Sims-style theme constants ----------------

SIMS_FONT = ("Comic Sans MS", 10, "bold")
DARK_BLUE = "#000052"
BUTTON_BLUE = "#2d74ae"
TEXT_COLOR = "#ffffff"

# ---------------- Recolour Combiner Main Code ----------------

class ReColbinerApp:

    # ---------------- Instruction Window Text ----------------

    HELP_TEXT = (
        "RECOLBINER - v0.0.2-Beta\n"
        "The Sims 1 Recolour Combining Tool\n"
        "\n"
        "Combine several CC items' IFF files into one Multi-Object file "
        "that cycles through the graphics of the originals in game. "
        "Basically, proxy-recolour functionality for the Sims 1 - fewer "
        "files, fewer ID conflicts, and a lot more room in your Downloads "
        "folder for more CC.\n"
        "\n"
        "This is a super beta release, so expect a few hijinks and "
        "shenanigans along the way. Full notes, known limitations and "
        "bug reporting info are on the Patreon post:\n"
        "https://www.patreon.com/cw/FeralMoonwytch\n"
        "\n"
        "------------------------------\n"
        "INSTRUCTIONS\n"
        "------------------------------\n"
        "1. Backup your Downloads folder. Whole thing, make a copy "
        "somewhere else, just in case.\n"
        "2. Select the folder where the CC to combine is located.\n"
        "3. Choose the save path for your new combined files. It "
        "defaults to the folder you're in. Create a new folder for your "
        "combined items to keep them quarantined from your original CC.\n"
        "4. Select the items you want to combine from the list. The "
        "first item you choose will be the Main File. Hold CTRL to "
        "select multiple, or drag down the list.\n"
        "5. Update the catalogue name and new file name if you want to.\n"
        "6. Hit Combine - repeat steps 4-6 until all your desired files "
        "are combined.\n"
        "7. From your Downloads folder, you must, at minimum, move out "
        "all the files that were Main Files. Your new Multi-Object items "
        "have inherited those files' GUIDs and will conflict with them.\n"
        "8. Boot the game and test your new objects.\n"
        "9. To cycle the graphic, re-select and place the object in "
        "Build Mode. Once the desired colour is reached, it can be "
        "safely moved around in Buy Mode without changing again.\n"
        "10. Download even more custom content.\n"
        "\n"
        "------------------------------\n"
        "LICENCE / USAGE TERMS\n"
        "------------------------------\n"
        "ReColbiner is and always will be free to download and use. "
        "Please don't pay anyone for it or resell it.\n"
        "\n"
        "At this stage ReColbiner is closed-source - the compiled tool "
        "is available for download, but the code isn't public yet while "
        "I work towards a few specific goals. Once I've reached a stable "
        "point, I plan to release the full source on GitHub under a free "
        "and open licence.\n"
        "\n"
        "Until then:\n"
        "- Free to use for personal, non-commercial purposes.\n"
        "- Please don't decompile, reverse-engineer, or redistribute "
        "modified versions of the tool.\n"
        "- Please don't repackage or rehost ReColbiner elsewhere - link "
        "back to the Patreon page instead so everyone gets the latest "
        "version.\n"
        "- Any objects/CC you create using ReColbiner are entirely yours "
        "to share, sell, or use as you like - this only covers the tool "
        "itself, not what you make with it.\n"
    )

    # ---------------- CTSS (Catalogue string) constants ----------------

    CATALOG_ENCODING = "cp1252"  # US (lang 1) & International (lang 2) text
    DESC_SUFFIX = "\r\n\r\nTo cycle graphic pick up and place item in Build Mode - Added with ReColbiner"

    # --------------------- App Code --------------------------

    def __init__(self, root_master):
        self.root = root_master

        # -------------- App Attributes ---------------
        self.fileContents_list = []
        self.fileName_list = []
        self.mainIdx = 0
        self.oriCatalogue_name = ""
        self.save_path = ""

        self.folder_dir = ""
        self.folder_files = []       # All .iff filenames found in the selected folder
        self.prev_selection = set()  # Tracks listbox selection between events

        self.output_has_entries = False  # tracks whether the output panel already has content

        self.root.title("ReColbiner: The Sims 1 Recolour Combiner - Version 0.0.1-Beta")
        self.root.iconbitmap(resource_path("recolbiner_C4_dresser.ico"))
        self.root.geometry("650x450")
        self.root.configure(bg=DARK_BLUE)

        # ---------------- Top button bar ----------------

        # Button Frame to held buttons at the top of widget
        button_frame = tk.Frame(root_master, bg=DARK_BLUE, bd=4, relief="ridge", padx=5, pady=5)
        button_frame.pack(side="top", fill="x")

        # Help button - pinned to the right edge
        # Packed before button_group so it claims space first (button_group then centers in what remains)
        help_size = 32
        help_btn = tk.Canvas(
            button_frame, width=help_size, height=help_size,
            bg=DARK_BLUE, highlightthickness=0, cursor="hand2"
        )
        pad = 3
        help_btn.create_oval(
            pad, pad, help_size - pad, help_size - pad,
            outline=TEXT_COLOR, width=2, fill=BUTTON_BLUE
        )
        help_btn.create_text(
            help_size / 2, help_size / 2, text="?",
            font=("Comic Sans MS", 14, "bold"), fill=TEXT_COLOR
        )
        help_btn.bind("<Button-1>", self.on_help)
        help_btn.pack(side="right", padx=10)

        # Button Group to group main buttons in the centre of Button Frame
        button_group = tk.Frame(button_frame, bg=DARK_BLUE)
        button_group.pack()  # No side/fill = centers itself in button_frame

        select_btn = tk.Button(
            button_group, text="Select Folder", command=self.on_select_folder,
            font=SIMS_FONT, bg=BUTTON_BLUE, fg=TEXT_COLOR,
            activebackground=BUTTON_BLUE, relief="raised", bd=3,
            padx=10, pady=4, width=10
        )
        select_btn.pack(side="left", padx=5)

        clear_btn = tk.Button(
            button_group, text="Clear Files", command=self.on_clear_files,
            font=SIMS_FONT, bg=BUTTON_BLUE, fg=TEXT_COLOR,
            activebackground=BUTTON_BLUE, relief="raised", bd=3,
            padx=10, pady=4, width=10
        )
        clear_btn.pack(side="left", padx=5)

        change_save_path_btn = tk.Button(
            button_group, text="Save Path", command=self.on_change_save_path,
            font=SIMS_FONT, bg=BUTTON_BLUE, fg=TEXT_COLOR,
            activebackground=BUTTON_BLUE, relief="raised", bd=3,
            padx=10, pady=4, width=10
        )
        change_save_path_btn.pack(side="left", padx=5)

        combine_btn = tk.Button(
            button_group, text="Combine Files", command=self.on_combine_files,
            font=SIMS_FONT, bg=BUTTON_BLUE, fg=TEXT_COLOR,
            activebackground=BUTTON_BLUE, relief="raised", bd=3,
            padx=10, pady=4, width=10
        )
        combine_btn.pack(side="left", padx=5)

        # ---------------- Panels frame ----------------

        panels_frame = tk.Frame(root_master, bg=DARK_BLUE, padx=5, pady=5)
        panels_frame.pack(side="top", fill="both", expand=True)

        panels_frame.columnconfigure(0, weight=1, uniform="panels")
        panels_frame.columnconfigure(1, weight=1, uniform="panels")
        panels_frame.rowconfigure(7, weight=1)

        # Top panel: Main file (single-line height, spans both columns)
        main_file_label = tk.Label(
            panels_frame, text="Main File",
            font=SIMS_FONT, bg=DARK_BLUE, fg=TEXT_COLOR
        )
        main_file_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 0))

        main_file_container = tk.Frame(panels_frame, bg=DARK_BLUE, bd=4, relief="ridge")
        main_file_container.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        main_file_container.columnconfigure(0, weight=1)

        self.main_file_display = tk.Label(
            main_file_container, text="", anchor="w",
            font=SIMS_FONT, bg=BUTTON_BLUE, fg=TEXT_COLOR,
            padx=5, pady=3
        )
        self.main_file_display.grid(row=0, column=0, sticky="ew")

        # Save Path panel: Same dimensions/style as Main File (single-line, spans both columns)
        save_path_label = tk.Label(
            panels_frame, text="Save Path",
            font=SIMS_FONT, bg=DARK_BLUE, fg=TEXT_COLOR
        )
        save_path_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 0))

        save_path_container = tk.Frame(panels_frame, bg=DARK_BLUE, bd=4, relief="ridge")
        save_path_container.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        save_path_container.columnconfigure(0, weight=1)

        self.save_path_display = tk.Label(
            save_path_container, text="", anchor="w",
            font=SIMS_FONT, bg=BUTTON_BLUE, fg=TEXT_COLOR,
            padx=5, pady=3
        )
        self.save_path_display.grid(row=0, column=0, sticky="ew")

        # Catalogue Name and New File Name: Editable single-line entries, one per column
        catalogue_label = tk.Label(
            panels_frame, text="Catalogue Name",
            font=SIMS_FONT, bg=DARK_BLUE, fg=TEXT_COLOR
        )
        catalogue_label.grid(row=4, column=0, sticky="w", padx=5, pady=(0, 0))

        new_file_name_label = tk.Label(
            panels_frame, text="New File Name",
            font=SIMS_FONT, bg=DARK_BLUE, fg=TEXT_COLOR
        )
        new_file_name_label.grid(row=4, column=1, sticky="w", padx=5, pady=(0, 0))

        self.catalogue_name_var = tk.StringVar()
        catalogue_entry_container = tk.Frame(panels_frame, bg=DARK_BLUE, bd=4, relief="ridge")
        catalogue_entry_container.grid(row=5, column=0, sticky="ew", padx=5, pady=(0, 5))
        catalogue_entry_container.columnconfigure(0, weight=1)

        self.catalogue_name_entry = tk.Entry(
            catalogue_entry_container, textvariable=self.catalogue_name_var,
            font=SIMS_FONT, bg=BUTTON_BLUE, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR, relief="flat", bd=0
        )
        self.catalogue_name_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=3)

        self.new_file_name_var = tk.StringVar()
        new_file_name_container = tk.Frame(panels_frame, bg=DARK_BLUE, bd=4, relief="ridge")
        new_file_name_container.grid(row=5, column=1, sticky="ew", padx=5, pady=(0, 5))
        new_file_name_container.columnconfigure(0, weight=1)

        self.new_file_name_entry = tk.Entry(
            new_file_name_container, textvariable=self.new_file_name_var,
            font=SIMS_FONT, bg=BUTTON_BLUE, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR, relief="flat", bd=0
        )
        self.new_file_name_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=3)

        # Left panel: Selected files list
        left_label = tk.Label(
            panels_frame, text="Select Files To Combine",
            font=SIMS_FONT, bg=DARK_BLUE, fg=TEXT_COLOR
        )
        left_label.grid(row=6, column=0, sticky="w", padx=5, pady=(0, 0))

        left_container = tk.Frame(panels_frame, bg=DARK_BLUE, bd=4, relief="ridge")
        left_container.grid(row=7, column=0, sticky="nsew", padx=5)
        left_container.rowconfigure(0, weight=1)
        left_container.columnconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(
            left_container, selectmode="extended", exportselection=False,
            font=SIMS_FONT, bg=BUTTON_BLUE, fg=TEXT_COLOR,
            selectbackground="#ffffff", selectforeground=DARK_BLUE,
            bd=0, highlightthickness=0
        )
        self.file_listbox.grid(row=0, column=0, sticky="nsew")

        left_scrollbar = tk.Scrollbar(
            left_container, orient="vertical", command=self.file_listbox.yview
        )
        left_scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.configure(yscrollcommand=left_scrollbar.set)

        self.file_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        # Right panel: Output
        right_label = tk.Label(
            panels_frame, text="Combined File Output",
            font=SIMS_FONT, bg=DARK_BLUE, fg=TEXT_COLOR
        )
        right_label.grid(row=6, column=1, sticky="w", padx=5, pady=(0, 0))

        right_container = tk.Frame(panels_frame, bg=DARK_BLUE, bd=4, relief="ridge")
        right_container.grid(row=7, column=1, sticky="nsew", padx=5)
        right_container.rowconfigure(0, weight=1)
        right_container.columnconfigure(0, weight=1)

        self.output_text = tk.Text(
            right_container, wrap="word", state="disabled", width=1,
            font=SIMS_FONT, bg=BUTTON_BLUE, fg=TEXT_COLOR,
            bd=0, highlightthickness=0
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")

        right_scrollbar = tk.Scrollbar(
            right_container, orient="vertical", command=self.output_text.yview
        )
        right_scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=right_scrollbar.set)


    # ---------------- File Handling Methods ----------

    def Select_Folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if not folder_path:
            return

        try:
            all_files = os.listdir(folder_path)
        except OSError:
            self.append_output(
                f"Error: Could not open folder '{folder_path}'", is_error=True)
            return

        self.folder_dir = folder_path
        self.folder_files = sorted(
            f for f in all_files
            if f.lower().endswith(".iff") and os.path.isfile(os.path.join(folder_path, f))
        )

        # A new folder means a fresh combine list - old picks no longer apply
        self.fileName_list = []
        self.fileContents_list = []
        self.prev_selection = set()
        self.mainIdx = 0
        self.oriCatalogue_name = ""
        self.main_file_display.configure(text="")

        # Default save path to the folder itself - user can still override via Change Save Path
        self.save_path = folder_path
        self.update_save_path_display()

        if not self.folder_files:
            self.append_output(f"No IFF files found in: '{folder_path}'.")


    def Read_File_Contents(self, filename):
        # Reads one file's bytes on demand - only called when it's selected for combining
        # Raises OSError if the file can no longer be read
        # Caller is responsible for catching this and showing a friendly message
        path = os.path.join(self.folder_dir, filename)
        with open(path, "rb") as f:
            return bytearray(f.read())


    def Clear_Files(self):
        self.fileName_list = []
        self.fileContents_list = []
        self.prev_selection = set()
        self.mainIdx = 0
        self.oriCatalogue_name = ""
        self.main_file_display.configure(text="")
        self.file_listbox.selection_clear(0, "end")


    def Assign_MainFile(self):
        selected_names = self.get_selected_file_names()
        if len(selected_names) == 1 and selected_names[0] in self.fileName_list:
            idx = self.fileName_list.index(selected_names[0])
            self.mainIdx = idx


    # ---------------- CTSS Catalogue Helpers ----------------

    def Read_Catalogue_Name(self):

        # Walks chunk headers to find the first CTSS chunk in a file's bytes, or None
        headerSize = 64
        chunkHeaderSize = 76
        pos = headerSize
        chunk = bytearray()
        main_fileContents = self.fileContents_list[0]
        while pos < len(main_fileContents):
            if pos + 8 > len(main_fileContents):
                raise ValueError("File ends in the middle of a chunk header - it may be corrupted or truncated.")

            chunkType = bytes(main_fileContents[pos:pos + 4])
            chunkSize = int.from_bytes(main_fileContents[pos + 4:pos + 8], byteorder="big")
            chunkEnd = pos + chunkSize

            if chunkSize <= 0:
                raise ValueError("File contains an invalid chunk size - it may be corrupted.")

            if chunkType == b"CTSS":
                chunk = main_fileContents[pos:chunkEnd]

            pos = chunkEnd

        if not chunk:
            return ""

        # Reads the International Catalogue Name (language code 2) from a CTSS chunk (FD FF format only)
        # Falls back to the US Catalogue Name (language code 1) if no International name pair is present
        # Returns '' if unsupported or not found - never raises error as this is just for populating the display
        ctss_body = chunk[chunkHeaderSize:]
        version = int.from_bytes(ctss_body[0:2], byteorder="little", signed=True)
        if version != -3:
            return ""

        count = int.from_bytes(ctss_body[2:4], byteorder="little")
        offset = 4
        us_name = ""
        us_name_found = False
        for _ in range(count):
            lang = ctss_body[offset]
            offset += 1
            end1 = ctss_body.index(0, offset)
            str1 = bytes(ctss_body[offset:end1])
            offset = end1 + 1
            end2 = ctss_body.index(0, offset)
            offset = end2 + 1

            # Searches for International lang-2 pair
            if lang == 2:
                return str1.decode(self.CATALOG_ENCODING, errors="replace")

            # First lang-1 pair seen is the US Name - remember it in case there's no lang 2 at all
            if lang == 1 and not us_name_found:
                us_name = str1.decode(self.CATALOG_ENCODING, errors="replace")
                us_name_found = True

        # No International pair found in this chunk - fall back to whatever US name we captured
        return us_name


    # -------------- Combine Files Method ----------------------

    def MainFile_Copy(self):

        # -------------- Main File Copy Variable ----------------------

        main_fileContents = self.fileContents_list[self.mainIdx]
        cutSize = 0
        headerSize = 64
        chunkHeaderSize = 76
        pos = headerSize

        # Header version 2.0 does not require rsmp
        TS1_IFFheader = (
            "49 46 46 20 46 49 4C 45 20 32 2E 30 3A 54 59 50"
            "45 20 46 4F 4C 4C 4F 57 45 44 20 42 59 20 53 49"
            "5A 45 00 20 4A 41 4D 49 45 20 44 4F 4F 52 4E 42"
            "4F 53 20 26 20 4D 41 58 49 53 20 31 39 39 36 00"
        )

        Main_copiedContent = bytearray.fromhex(TS1_IFFheader.replace(" ", ""))

        UncopiedChunk_Types = {b"CTSS", b"DGRP", b"SPR2", b"OBJD", b"OBJf", b"PALT", b"rsmp"}

        # BHAV that iterates through graphics by a step of 1
        # BHAV_chunkHEX = (
        #     "42 48 41 56 00 00 00 B8 1B BC 00 10 63 68 61 6E"
        #     "67 65 20 74 6F 20 6E 65 78 74 20 67 72 61 70 68"
        #     "69 63 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
        #     "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
        #     "00 00 00 00 00 00 00 00 00 00 00 00 02 80 08 00"
        #     "16 04 02 00 11 00 00 00 02 00 01 FF 13 00 01 00"
        #     "00 02 06 07 02 00 02 FD 00 00 0B 00 00 05 0A 03"
        #     "02 00 03 FD 00 00 00 00 00 05 19 03 02 00 04 FD"
        #     "00 00 01 00 00 03 19 07 02 00 05 06 00 00 04 00"
        #     "74 0E 19 15 02 00 06 FD 00 00 00 00 00 05 19 07"
        #     "02 00 07 FD 00 00 00 00 00 05 03 19 07 00 FE FD"
        #     "00 00 00 00 00 00 00 00"
        # )

        # BHAV that iterates through graphics by a step of 1000
        BHAV_chunkHEX = (
            "42 48 41 56 00 00 00 B8 1B BC 00 10 63 68 61 6E"
            "67 65 20 74 6F 20 6E 65 78 74 20 67 72 61 70 68"
            "69 63 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
            "00 00 00 00 00 00 00 00 00 00 00 00 02 80 08 00"
            "16 04 02 00 11 00 00 00 02 00 01 FF 13 00 01 00"
            "00 02 06 07 02 00 02 FD 00 00 0B 00 00 05 0A 03"
            "02 00 03 FD 00 00 00 00 00 05 19 03 02 00 04 FD"
            "00 00 E8 03 00 03 19 07 02 00 05 06 00 00 04 00"
            "74 0E 19 15 02 00 06 FD 00 00 00 00 00 05 19 07"
            "02 00 07 FD 00 00 00 00 00 05 03 19 07 00 FE FD"
            "00 00 00 00 00 00 00 00"
        )


        BHAVid_list = []
        BHAV_chunk = bytearray.fromhex(BHAV_chunkHEX.replace(" ", ""))
        BHAV_ID = BHAV_chunk[8:10] # bytearray(b'\x1b\xbc') Big Endian

        PALT_chunks = []
        SPR2_chunks = []
        DGRP_chunks = []

        mainFile_OBJD = []
        mainFile_OBJf = []
        mainFile_CTSS = []

        # -------------- Main File Copy ----------------------

        # Copies all data from main file that won't need to be altered into Main_copiedContent
        # Collects BHAV IDs in a list to check for conflicts with BHAV_ID
        # Collects main file OBJD and OBJf in a list for updating later
        while pos < len(main_fileContents):

            if pos + 8 > len(main_fileContents):
                raise ValueError(f"'{self.fileName_list[self.mainIdx]}' File ends in the middle of a chunk header.")

            chunkType = bytes(main_fileContents[pos:pos + 4])
            chunkSize = int.from_bytes(main_fileContents[pos + 4:pos + 8], byteorder="big")
            chunkEnd = pos + chunkSize

            if chunkSize <= 0:
                raise ValueError(
                    f"'{self.fileName_list[self.mainIdx]}' Contains an invalid chunk and may be corrupted."
                )

            if chunkType not in UncopiedChunk_Types:
                if chunkType == b"BHAV":
                    BHAVid = bytes(main_fileContents[pos + 8:pos + 10])
                    BHAVid_list.append(BHAVid)
                Main_copiedContent += main_fileContents[pos:chunkEnd]

            elif chunkType == b"CTSS":
                mainFile_CTSS.append(main_fileContents[pos:chunkEnd])
                cutSize += chunkSize
            elif chunkType == b"OBJD":
                mainFile_OBJD.append(main_fileContents[pos:chunkEnd])
                cutSize += chunkSize
            elif chunkType == b"OBJf":
                mainFile_OBJf.append(main_fileContents[pos:chunkEnd])
                cutSize += chunkSize
            else:
                cutSize += chunkSize

            pos = chunkEnd

        # -------------- BHAV ID Checker ----------------------

        # Changes BHAV_ID from default 7100 if that ID is already in use
        # Only act if BHAV_ID collides with something already in BHAVid_list
        if BHAV_ID in BHAVid_list:
            new_id = 4999
            while True:
                new_id += 1
                new_id_bytes = bytearray(new_id.to_bytes(2, byteorder='big'))
                if new_id_bytes not in BHAVid_list:
                    BHAV_ID = new_id_bytes
                    break
                if new_id >= 7500:
                    raise ValueError("No free BHAV ID was available in range 5000-7500.")
            assert len(BHAV_ID) == 2, "BHAV_ID must be exactly 2 bytes"
            BHAV_chunk[8:10] = BHAV_ID

        Main_copiedContent += BHAV_chunk

        # ----------------- Chunk Getter ---------------------

        # Iterates through every Selected File and creates a nested list of chunks
        # Walks through fileContents to locate wanted types
        # Grabs data to the start of the next marker (or end of data)
        # Within the chunk type list the index of a files chunks will be the index of the file in fileContents_list

        for file_index, fileContents in enumerate(self.fileContents_list):
            file_DGRP = []
            file_PALT = []
            file_SPR2 = []

            pos = headerSize
            while pos < len(fileContents):

                if pos + 8 > len(fileContents):
                    raise ValueError(f"'{self.fileName_list[file_index]}' File ends in the middle of chunk header.")

                chunkType = bytes(fileContents[pos:pos + 4])
                chunkSize = int.from_bytes(fileContents[pos + 4:pos + 8], byteorder="big")
                chunkEnd = pos + chunkSize

                if chunkSize <= 0:
                    raise ValueError(
                        f"'{self.fileName_list[file_index]}' Contains an invalid chunk and may be corrupted."
                    )

                if chunkType == b"DGRP":
                    file_DGRP.append(fileContents[pos:chunkEnd])
                if chunkType == b"PALT":
                    file_PALT.append(fileContents[pos:chunkEnd])
                if chunkType == b"SPR2":
                    file_SPR2.append(fileContents[pos:chunkEnd])

                pos = chunkEnd

            DGRP_chunks.append(file_DGRP)
            PALT_chunks.append(file_PALT)
            SPR2_chunks.append(file_SPR2)

        # ----------------- Multi-Graphic File Scanner ---------------------

        # Pre-scan mainFile_OBJD (Main File only. Flat list like DGRP_chunks[0])
        # To check if any object is multi-graphic (Animated)
        # If so, the WHOLE file's DGRP numbering switches to sequential (+1)
        # Instead of the default step of +1000 used for multi-tile objects

        is_multiGraphic_file = False
        for chunk in mainFile_OBJD:
            numGraphics = int.from_bytes(chunk[chunkHeaderSize + 8:chunkHeaderSize + 10], byteorder="little")
            if numGraphics > 1:
                is_multiGraphic_file = True
                break

        # ----------------- File Offset Calculator ---------------------

        # PALT, SPR2 and DGRP each get their OWN independent offset per
        # file and their own running "next free ID" cursor. These are
        # separate ID namespaces - cross-references between them are
        # already resolved through the ID_map dictionaries built below,
        # not by any arithmetic relationship between their raw values -
        # so pooling them together (as an earlier version of this did)
        # only inflates each file's apparent footprint to the union of
        # three unrelated numbering ranges instead of each type's real one.
        #
        # Within a single type, a file's own internal relative spacing
        # between its chunks IS preserved (anchored on that file's own
        # min/max for that type).
        #
        # File 0 (the Main File) always gets offset 0 for every type -
        # its IDs are left completely untouched, since it's the only file
        # whose own BHAVs/OBJf/etc still run and may reference its own
        # graphic IDs elsewhere in the file.

        def type_bounds(chunks_by_file, file_index):
            ids = [int.from_bytes(chunk[8:10], byteorder='big') for chunk in chunks_by_file[file_index]]
            return (min(ids), max(ids)) if ids else None

        def build_file_offsets(chunks_by_file):
            offsets = [0]
            main_bounds = type_bounds(chunks_by_file, 0)
            next_free_id = (main_bounds[1] + 1) if main_bounds else 1

            for file_index in range(1, len(chunks_by_file)):
                bounds = type_bounds(chunks_by_file, file_index)
                if bounds is None:
                    offsets.append(0)  # File contributed no chunks of this type - nothing to shift
                    continue
                local_min, local_max = bounds
                offset = next_free_id - local_min
                offsets.append(offset)
                next_free_id = local_max + offset + 1

            return offsets

        PALT_file_offsets = build_file_offsets(PALT_chunks)
        SPR2_file_offsets = build_file_offsets(SPR2_chunks)
        DGRP_file_offsets = build_file_offsets(DGRP_chunks)


        # ----------------- PALT_Changer ---------------------

        # PALT ID changing - Iterate through list items - ID Generated by enumerate counter
        # Builds an old-ID ---> new-ID map per file in PALT_IDmaps a list of dictionaries
        # SPR2 can correctly repoint to their original PALT instead of assuming matching list position
        # PALT_IDmaps[file_index][old_PALT_id] = new_PALT_id

        PALT_IDmaps = []

        for file_index, file_PALT in enumerate(PALT_chunks):
            ID_map = {}
            offset = PALT_file_offsets[file_index]   # was: file_offsets[file_index]

            for chunk_index, chunk in enumerate(file_PALT):

                oldPALT_ID = int.from_bytes(chunk[8:10], byteorder='big')
                newPALT_ID = oldPALT_ID + offset

                # if is_multiGraphic_file:
                #     #newPALT_ID = 100 + (chunk_index * 1) + (file_index * 100)
                #     #newPALT_ID = oldPALT_ID + (file_index * 100)
                #     #newPALT_ID = oldPALT_ID
                #     newPALT_ID = 100 + (chunk_index * 1) + (file_index * 1000)
                # else:
                #     #newPALT_ID = 100 + (chunk_index * 1000) + (file_index * 100)
                #     #newPALT_ID = oldPALT_ID + (chunk_index * 1000)
                #     #newPALT_ID = oldPALT_ID
                #     newPALT_ID = 100 + (chunk_index * 1) + (file_index * 1000)

                ID_map[oldPALT_ID] = newPALT_ID

                if newPALT_ID > 65535:
                    self.append_output(
                        f"Error: PALT ID {newPALT_ID} out of bounds (max 65535) "
                        f"at file_index={file_index}, chunk_index={chunk_index}",
                        is_error=True)
                    return None


                # Header ID field in Big Endian - Fills from the back - Leading 00s
                chunk[8:10] = newPALT_ID.to_bytes(2, byteorder="big")

                Main_copiedContent += chunk

            PALT_IDmaps.append(ID_map)

        # ----------------- SPR2_Changer ---------------------

        # SPR2 ID changing - Iterate through list items - ID Generated by enumerate counter
        # Any PALT references inside the SPR2 are remapped through this file's PALT_IDmaps entry
        # So the SPR2 keeps pointing at the PALT palette it originally used
        # SPR2_IDmaps[file_index][old_SPR2_id] = new_SPR2_id

        SPR2_IDmaps = []
        NULL_PALT = 0xA3A3  # "Use default palette" marker - never a real PALT ID, leave untouched

        for file_index, file_SPR2 in enumerate(SPR2_chunks):
            ID_map = {}
            offset = SPR2_file_offsets[file_index]   # was: file_offsets[file_index]
            filePALT_map = PALT_IDmaps[file_index] if file_index < len(PALT_IDmaps) else {}

            for chunk_index, chunk in enumerate(file_SPR2):

                oldSPR2_ID = int.from_bytes(chunk[8:10], byteorder='big')
                newSPR2_ID = oldSPR2_ID + offset

                # if is_multiGraphic_file:
                #     #newSPR2_ID = 100 + (chunk_index * 1) + (file_index * 100)
                #     #newSPR2_ID = oldSPR2_ID + (file_index * 100)
                #     #newSPR2_ID = oldSPR2_ID
                #     newSPR2_ID = 100 + (chunk_index * 1) + (file_index * 1000)
                # else:
                #     #newSPR2_ID = 100 + (chunk_index * 1000) + (file_index * 100)
                #     #newSPR2_ID = oldSPR2_ID + (chunk_index * 1000)
                #     #newSPR2_ID = oldSPR2_ID
                #     newSPR2_ID = 100 + (chunk_index * 1) + (file_index * 1000)



                ID_map[oldSPR2_ID] = newSPR2_ID

                if newSPR2_ID > 65535:
                    self.append_output(
                        f"Error: SPR2 ID {newSPR2_ID} out of bounds (max 65535) "
                        f"at file_index={file_index}, chunk_index={chunk_index}",
                        is_error=True)
                    return None

                # Header ID field in Big Endian - Fills from the back - Leading 00s
                chunk[8:10] = newSPR2_ID.to_bytes(2, byteorder="big")

                version = int.from_bytes(chunk[chunkHeaderSize:chunkHeaderSize + 4], byteorder='little')

                if version == 1000:
                    sprite_count = int.from_bytes(chunk[chunkHeaderSize + 4:chunkHeaderSize + 8], byteorder='little')
                    offset_table = []
                    offsetT_pos = chunkHeaderSize + 12  # Location of Offset Table

                    # Default PALT ID - 4 byte - remap using the ORIGINAL ID this field held
                    oldDefault_PALT = int.from_bytes(chunk[chunkHeaderSize +8:chunkHeaderSize +12], byteorder="little")
                    newDefault_PALT = filePALT_map.get(oldDefault_PALT, oldDefault_PALT)
                    chunk[chunkHeaderSize + 8:chunkHeaderSize + 12] = newDefault_PALT.to_bytes(4, byteorder="little")

                    # PALT IDs for each sprite - 2 bytes
                    # Minimum 3 Sprites - single rotation. One for each of three zoom level
                    # Maximum 12 Sprites - four cardinal rotation for each of three zoom levels
                    for i in range(sprite_count):
                        offset_table.append(int.from_bytes(chunk[offsetT_pos:offsetT_pos + 4], byteorder='little'))
                        offsetT_pos += 4

                        PALT_IDpos = chunkHeaderSize + offset_table[i] + 8  # Skip Width(2)+Height(2)+Flags(4)
                        oldSprite_PALT = int.from_bytes(chunk[PALT_IDpos:PALT_IDpos + 2], byteorder='little')

                        if oldSprite_PALT == NULL_PALT:
                            newSprite_PALT = NULL_PALT
                        else:
                            newSprite_PALT = filePALT_map.get(oldSprite_PALT, oldSprite_PALT)

                        chunk[PALT_IDpos:PALT_IDpos + 2] = newSprite_PALT.to_bytes(2, byteorder="little")

                elif version == 1001:
                    # Field order is swapped vs 1000: Default palette comes before Sprite count
                    oldDefault_PALT = int.from_bytes(chunk[chunkHeaderSize +4:chunkHeaderSize +8], byteorder="little")
                    newDefault_PALT = filePALT_map.get(oldDefault_PALT, oldDefault_PALT)
                    chunk[chunkHeaderSize + 4:chunkHeaderSize + 8] = newDefault_PALT.to_bytes(4, byteorder="little")

                    sprite_count = int.from_bytes(chunk[chunkHeaderSize + 8:chunkHeaderSize + 12], byteorder='little')

                    # No offset table in 1001
                    # Sprites are walked sequentially using each sprite's own "Sprite size" field
                    # Sprite size (Version 1001) - 4-byte integer specifying the size of sprite in bytes
                    # Sprite size excludes the Sprite version + Sprite size fields (each 4 bytes)
                    # So next sprite = this sprite's start + 8 + size
                    pos = chunkHeaderSize + 12
                    for i in range(sprite_count):
                        sprite_start = pos
                        sprite_size = int.from_bytes(chunk[pos + 4:pos + 8], byteorder='little')

                        # Palette sits after Sprite version(4) + Sprite size(4) + Width(2) + Height(2) + Flags(4)
                        PALT_IDpos = sprite_start + 16
                        oldSprite_PALT = int.from_bytes(chunk[PALT_IDpos:PALT_IDpos + 2], byteorder='little')

                        if oldSprite_PALT == NULL_PALT:
                            newSprite_PALT = NULL_PALT
                        else:
                            newSprite_PALT = filePALT_map.get(oldSprite_PALT, oldSprite_PALT)

                        chunk[PALT_IDpos:PALT_IDpos + 2] = newSprite_PALT.to_bytes(2, byteorder="little")

                        pos = sprite_start + 8 + sprite_size

                else:
                    raise ValueError(f"'{self.fileName_list[file_index]}': Unsupported SPR2 version {version}")

                Main_copiedContent += chunk

            SPR2_IDmaps.append(ID_map)


        # ----------------- DGRP_Changer ---------------------

        # DGRP ID changing - Iterate through list items - ID Generated by enumerate counter
        # Builds an old-ID ---> new-ID map per file in DGRP_IDmaps a list of dictionaries
        # So the DGRP keeps pointing at the SPR2 sprite it originally used
        # DGRP_IDmaps[file_index][old_DGRP_id] = new_DGRP_id

        DGRP_IDmaps = []
        overall_max_DGRP_id = 0 # <-- new: tracks the true ceiling across the whole combine

        for file_index, file_DGRP in enumerate(DGRP_chunks):
            fileSPR2_map = SPR2_IDmaps[file_index] if file_index < len(SPR2_IDmaps) else {}
            offset = DGRP_file_offsets[file_index]   # was: file_offsets[file_index]

            ID_map = {}

            for chunk_index, chunk in enumerate(file_DGRP):

                oldDGRP_ID = int.from_bytes(chunk[8:10], byteorder='big')
                newDGRP_ID = oldDGRP_ID + offset

                # if is_multiGraphic_file:
                #     #newDGRP_ID = 100 + (chunk_index * 1) + (file_index * 100)
                #     #newDGRP_ID = oldDGRP_ID + (file_index * 100)
                #     #newDGRP_ID = oldDGRP_ID
                #     newDGRP_ID = 100 + (chunk_index * 1) + (file_index * 1000)
                # else:
                #     #newDGRP_ID = 100 + (chunk_index * 1000) + (file_index * 100)
                #     #newDGRP_ID = oldDGRP_ID + (chunk_index * 1000)
                #     #newDGRP_ID = oldDGRP_ID
                #     newDGRP_ID = 100 + (chunk_index * 1) + (file_index * 1000)

                ID_map[oldDGRP_ID] = newDGRP_ID
                overall_max_DGRP_id = max(overall_max_DGRP_id, newDGRP_ID)  # <-- new

                if newDGRP_ID > 65535:
                    self.append_output(
                        f"Error: DGRP ID {newDGRP_ID} out of bounds (max 65535) "
                        f"at file_index={file_index}, chunk_index={chunk_index}",
                        is_error=True)
                    return None


                # Header ID field in Big Endian - Fills from the back - Leading 00s
                chunk[8:10] = newDGRP_ID.to_bytes(2, byteorder="big")

                pos = chunkHeaderSize
                version = int.from_bytes(chunk[pos:pos + 2], byteorder="little")
                pos += 2

                if version in (20000, 20001):
                    image_count = int.from_bytes(chunk[pos:pos + 2], byteorder="little")
                    pos += 2
                elif version in (20003, 20004):
                    image_count = int.from_bytes(chunk[pos:pos + 4], byteorder="little")
                    pos += 4
                else:
                    raise ValueError(f"'{self.fileName_list[file_index]}': Unsupported DGRP version {version}")

                for i in range(image_count):

                    if version in (20000, 20001):
                        sprite_count = int.from_bytes(chunk[pos:pos + 2], byteorder="little")
                        pos += 2 + 1 + 1 # Sprite count(2) + Direction flags(1) + Zoom level(1)
                    else:  # 20003, 20004
                        pos += 4 + 4  # Direction flags(4) + Zoom level(4)
                        sprite_count = int.from_bytes(chunk[pos:pos + 4], byteorder="little")
                        pos += 4  # Sprite count(4)

                    for j in range(sprite_count):

                        if version in (20000, 20001):
                            pos += 2  # Type(2)
                            spr_idpos = pos
                            spr_idsize = 2
                            pos += spr_idsize  # SPR chunk ID
                            pos += 2 + 2 + 2 + 2
                            # SPR frame number(2) + Flags(2) + Sprite X offset(2) + Sprite Y offset(2)

                            if version == 20001:
                                pos += 4  # Object Z offset(4)

                        else:  # 20003, 20004
                            spr_idpos = pos
                            spr_idsize = 4
                            pos += spr_idsize  # SPR chunk ID
                            pos += 4 + 4 + 4 + 4 + 4
                            # SPR frame num(4) + Sprite X off(4) + Sprite Y off(4) + Object Z off(4) + Flags(4)

                            if version == 20004:
                                pos += 4 + 4  # Object X offset(4) + Object Y offset(4)

                        oldSPR2_ref = int.from_bytes(chunk[spr_idpos:spr_idpos + spr_idsize], byteorder="little")
                        newSPR2_ref = fileSPR2_map.get(oldSPR2_ref, oldSPR2_ref)
                        chunk[spr_idpos:spr_idpos + spr_idsize] = newSPR2_ref.to_bytes(spr_idsize, byteorder="little")

                Main_copiedContent += chunk

            DGRP_IDmaps.append(ID_map)


        # ----------------- OBJD_Changer ---------------------

        # OBJD is only ever taken from the Main File
        # So only the Main File's DGRP map (index 0) is relevant for remapping Base Graphic ID
        # Map is effectively an identity map kept for consistency/clarity rather than strict necessity
        # Main File's offset is always 0

        main_file_DGRP_map = DGRP_IDmaps[0] if DGRP_IDmaps else {}

        for chunk_index, chunk in enumerate(mainFile_OBJD):

            old_base_graphic_id = int.from_bytes(chunk[chunkHeaderSize + 6:chunkHeaderSize + 8], byteorder="little")

            if old_base_graphic_id == 0:
                # Catalogue Only OBJD - some multi-tile objects carry this. No matching DGRP - leave as 0
                new_base_graphic_id = 0
                numGraphics = 0
            else:
                new_base_graphic_id = main_file_DGRP_map.get(old_base_graphic_id, old_base_graphic_id)

                # numGraphics must cover every ID any merged file's states could ever occupy,
                # starting from this segment's own Base Graphic ID, up to the real highest
                # DGRP ID assigned anywhere in the combine.
                numGraphics = (overall_max_DGRP_id - new_base_graphic_id) + 1

                if numGraphics < 1:
                    self.append_output(
                        f"Error: Segment Base Graphic ID {new_base_graphic_id} is higher than "
                        f"the highest assigned DGRP ID ({overall_max_DGRP_id}) - "
                        f"'{self.fileName_list[self.mainIdx]}' may have an unusual OBJD/DGRP layout.",
                        is_error=True)
                    return None

                if numGraphics > 65535:
                    self.append_output(
                        f"Error: Number of Graphics {numGraphics} out of bounds (max 65535) "
                        f"for segment {chunk_index}",
                        is_error=True)
                    return None

            chunk[chunkHeaderSize + 6:chunkHeaderSize + 8] = new_base_graphic_id.to_bytes(2, byteorder="little")
            chunk[chunkHeaderSize + 8:chunkHeaderSize + 10] = numGraphics.to_bytes(2, byteorder="little")

            Main_copiedContent += chunk

        # ----------------- OBJf_Changer ---------------------

        # Updating OBJf to call BHAV on user placement
        # Bytes 138 and 139 are location of User Placement Tree
        # OBJf data in Little Endian - BHAV_ID in Big Endian - Converts to Little Endian

        for chunk in mainFile_OBJf:
            BHAV_int = int.from_bytes(BHAV_ID, byteorder="big")  # Returns int value of BHAV_ID eg.7100
            BHAV_IDle = BHAV_int.to_bytes(2, byteorder="little")  # bytes(b'\xbc\x1b') Little Endian
            chunk[138:140] = BHAV_IDle

            Main_copiedContent += chunk

        # ----------------- CTSS_Changer ---------------------

        # Rewrites a CTSS chunk (FD FF format)
        # Sets the US/International Catalogue Name to new_name
        # Appends DESC_SUFFIX to the US/International Description
        # Leaves every other language pair untouched. Returns the rebuilt chunk bytes

        newCatalogue_name = self.catalogue_name_var.get().strip() or self.oriCatalogue_name

        for chunk in mainFile_CTSS:
            ctss_header = bytes(chunk[:chunkHeaderSize])
            ctss_body = chunk[chunkHeaderSize:]
            version = int.from_bytes(ctss_body[0:2], byteorder="little", signed=True)
            if version != -3:
                raise ValueError(f"'{self.fileName_list[self.mainIdx]}' Unsupported CTSS version {version}")

            count = int.from_bytes(ctss_body[2:4], byteorder="little")
            pairs = []
            offset = 4
            for _ in range(count):
                lang = ctss_body[offset]
                offset += 1
                end1 = ctss_body.index(0, offset)
                str1 = bytes(ctss_body[offset:end1])
                offset = end1 + 1
                end2 = ctss_body.index(0, offset)
                str2 = bytes(ctss_body[offset:end2])
                offset = end2 + 1
                pairs.append([lang, str1, str2])
            trailer = bytes(ctss_body[offset:])

            name_bytes = newCatalogue_name.encode(self.CATALOG_ENCODING)
            suffix_bytes = self.DESC_SUFFIX.encode(self.CATALOG_ENCODING)

            # First str1 of US (1) or International (2) pair seen is the Name - Second str1 is the Description
            # Format for pairs is nested list: pairs = [[lang, str1, str2], [lang, str1, str2], etc...]
            # Where lang = Language Code Integer, str1 = Name or Desc String, str2 = Comment String (Often Blank)
            # pairs = [[1, b"US Name", b""],[1, b"US Description", b""],[2, b"Int Name", b""],...]
            # Where pairs[0] is US Name and pairs[1] is US Description etc...
            seen_count = {}
            int_name_pair = []
            int_desc_pair = []
            us_name_pair = []
            us_desc_pair = []
            for pair in pairs:
                lang = pair[0]
                if lang not in (1, 2):
                    continue
                idx = seen_count.get(lang, 0)
                seen_count[lang] = idx + 1
                # Name
                if idx == 0:
                    pair[1] = name_bytes
                    if lang == 1:
                        us_name_pair = pair
                    if lang == 2:
                        int_name_pair = pair
                # Description
                elif idx == 1:
                    pair[1] = pair[1] + suffix_bytes
                    if lang == 1:
                        us_desc_pair = pair
                    if lang == 2:
                        int_desc_pair = pair

            # Code requires US and International Languages at minimum
            # So pairs minimum final length should be 4 with US Name, US Description, Int Name, Int Description
            # If US or International code not found code below copies what data we do have into them

            # No US (lang 1) pair existed
            # Duplicate the (already-updated) Int Name and Description as new lang-1 pairs so both entries are present
            if 1 not in seen_count and int_name_pair and int_desc_pair:
                pairs.append([1, int_name_pair[1], int_name_pair[2]])
                pairs.append([1, int_desc_pair[1], int_desc_pair[2]])

            # No International (lang 2) pair existed
            # Duplicate the (already-updated) US Name and Description as new lang-2 pairs so both entries are present
            if 2 not in seen_count and us_name_pair and us_desc_pair:
                pairs.append([2, us_name_pair[1], us_name_pair[2]])
                pairs.append([2, us_desc_pair[1], us_desc_pair[2]])

            # Builds new CTSS to correct new bounds and size with new Catalogue Name and Description
            new_body = bytearray()
            new_body += (-3).to_bytes(2, byteorder="little", signed=True)
            new_body += len(pairs).to_bytes(2, byteorder="little")
            for lang, str1, str2 in pairs:
                new_body += bytes([lang]) + str1 + b"\x00" + str2 + b"\x00"
            new_body += trailer

            new_header = bytearray(ctss_header)
            new_header[4:8] = (chunkHeaderSize + len(new_body)).to_bytes(4, byteorder="big")

            chunk = bytes(new_header) + bytes(new_body)

            Main_copiedContent += chunk


        # ----------------- Write Completed File ---------------------

        # Output name comes from the "New File Name" entry (falls back to NewMulti.iff)
        output_filename = self.new_file_name_var.get().strip() or "NewMulti.iff"
        if not output_filename.lower().endswith(".iff"):
            output_filename += ".iff"

        # Output directory comes from the "Save Path" panel (falls back to cwd)
        output_dir = self.save_path if self.save_path else os.getcwd()
        output_path = os.path.join(output_dir, output_filename)

        # Writing is where invalid save paths, missing permissions, or a full disk would surface
        # Raised as OSError and translated to a friendly message by the caller (on_combine_files)
        with open(output_path, "wb") as f:
            f.write(Main_copiedContent)

        return output_path


    # ---------------- Helper methods ----------------

    def refresh_file_listbox(self):
        """Repopulates the listbox from the currently browsed folder's .iff files."""
        self.file_listbox.delete(0, "end")
        for name in self.folder_files:
            self.file_listbox.insert("end", name)

    def get_selected_file_names(self):
        """Returns the file names currently highlighted in the listbox."""
        selected_indices = self.file_listbox.curselection()
        return [self.file_listbox.get(i) for i in selected_indices]

    def append_output(self, text, is_error=False):
        """Adds a new entry to the Combined File Output panel. Entries stay listed until the app is closed."""
        prefix = "Error: " if is_error and not str(text).startswith("Error:") else ""
        entry = f"{prefix}{text}"

        self.output_text.configure(state="normal")
        if self.output_has_entries:
            self.output_text.insert("end", "\n\n")
        self.output_text.insert("end", entry)
        self.output_has_entries = True
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def update_save_path_display(self):
        """Refreshes the Save Path panel label from self.save_path."""
        self.save_path_display.configure(text=self.save_path)

    def update_main_file(self):
        """Main file is always index 0 of the current selection; refreshes display + default name."""
        if self.fileName_list:
            self.mainIdx = 0
            main_file_name = self.fileName_list[0]
            self.main_file_display.configure(text=main_file_name)

            # Default Catalogue Name = "Multi - " + International Name in main file's CTSS
            try:
                self.oriCatalogue_name = "Multi - " + self.Read_Catalogue_Name()
            except (ValueError, IndexError):
                self.oriCatalogue_name = "Multi - Type Name Here"
                self.append_output(f"Could not read catalogue name from '{main_file_name}'", is_error=True)
            self.catalogue_name_var.set(self.oriCatalogue_name)

            # Only set the default New File Name the moment the list goes 0 ---> 1 items
            if len(self.fileName_list) == 1:
                base_name, _ext = os.path.splitext(main_file_name)
                self.new_file_name_var.set(base_name + "Multi")

        else:
            self.main_file_display.configure(text="")
            self.oriCatalogue_name = ""
            self.catalogue_name_var.set("")
            self.new_file_name_var.set("")

    def get_catalogue_name(self):
        """Returns the current text typed into the Catalogue Name box."""
        return self.catalogue_name_var.get()

    def get_new_file_name(self):
        """Returns the current text typed into the New File Name box."""
        return self.new_file_name_var.get()

    # ---------------- Button callbacks ----------------

    def on_select_folder(self):
        self.Select_Folder()
        self.update_main_file()
        self.refresh_file_listbox()

    def on_clear_files(self):
        self.Clear_Files()
        self.update_main_file()
        self.refresh_file_listbox()

    def on_listbox_select(self, _event):
        current_selection = set(self.file_listbox.curselection())
        newly_selected = current_selection - self.prev_selection
        newly_deselected = self.prev_selection - current_selection

        failed_indices = set()
        for idx in sorted(newly_selected):
            filename = self.folder_files[idx]
            try:
                contents = self.Read_File_Contents(filename)
            except OSError:
                self.append_output(f"Could not read: '{filename}'", is_error=True)
                failed_indices.add(idx)
                continue
            self.fileName_list.append(filename)
            self.fileContents_list.append(contents)

        for idx in newly_deselected:
            filename = self.folder_files[idx]
            if filename in self.fileName_list:
                list_idx = self.fileName_list.index(filename)
                self.fileName_list.pop(list_idx)
                self.fileContents_list.pop(list_idx)

        # Files that failed to read shouldn't stay highlighted as if they were selected
        if failed_indices:
            for idx in failed_indices:
                self.file_listbox.selection_clear(idx)
            current_selection -= failed_indices

        self.prev_selection = current_selection
        self.update_main_file()

    def on_change_save_path(self):
        new_path = filedialog.askdirectory(
            title="Select Save Path",
            initialdir=self.save_path if self.save_path else os.getcwd()
        )
        if new_path:
            self.save_path = new_path
            self.update_save_path_display()

    def on_combine_files(self):
        if not self.fileContents_list:
            self.append_output("No Files Selected - choose at least one IFF file to combine.", is_error=True)
            return

        # noinspection PyBroadException
        try:
            result = self.MainFile_Copy()
        except ValueError as e:
            # Deliberately raised for known, explainable problems
            # Corrupt/unsupported files, no free BHAV ID, etc
            # Pythons ValueError message is already written to be user-facing
            self.append_output(str(e), is_error=True)
        except (IndexError, KeyError):
            # Unexpected byte-layout problems, almost always from a malformed or unsupported .iff file
            self.append_output(
                "Failed to combine files - selected files may be corrupted or in an unsupported format.",
                is_error=True
            )
        except PermissionError:
            self.append_output(
                "Could not save the combined file - check permission to write to the selected save path.",
                is_error=True
            )
        except OSError:
            self.append_output(
                "Could not save the combined file - check that save path is valid and has room for the file.",
                is_error=True
            )
        except Exception:
            self.append_output("Something went wrong while combining the files.", is_error=True)
        else:
            self.append_output(f"Combined file saved to: {result}")

    def on_help(self, _event=None):
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("400x400")
        help_window.configure(bg=DARK_BLUE)

        help_container = tk.Frame(help_window, bg=DARK_BLUE, bd=4, relief="ridge")
        help_container.pack(fill="both", expand=True, padx=10, pady=10)
        help_container.rowconfigure(0, weight=1)
        help_container.columnconfigure(0, weight=1)

        help_text_widget = tk.Text(
            help_container, wrap="word",
            font=SIMS_FONT, bg=BUTTON_BLUE, fg=TEXT_COLOR,
            bd=0, highlightthickness=0
        )
        help_text_widget.grid(row=0, column=0, sticky="nsew")
        help_text_widget.insert("1.0", self.HELP_TEXT)
        help_text_widget.configure(state="disabled")

        help_scrollbar = tk.Scrollbar(
            help_container, orient="vertical", command=help_text_widget.yview
        )
        help_scrollbar.grid(row=0, column=1, sticky="ns")
        help_text_widget.configure(yscrollcommand=help_scrollbar.set)


if __name__ == "__main__":
    root = tk.Tk()
    app = ReColbinerApp(root)
    root.mainloop()
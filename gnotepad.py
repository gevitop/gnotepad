import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, font as tkFont
from PIL import Image, ImageTk
import os
import re
from typing import Optional
import webbrowser
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ICON_SIZE = (20, 20)


def set_main_app_icon(window, icon_path):
    if not os.path.exists(icon_path):
        try:
            blank_icon = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
            photo = ImageTk.PhotoImage(blank_icon)
            window.iconphoto(True, photo)
            window._icon = photo
        except:
            pass
        return

    try:
        window.iconbitmap(icon_path)
        return
    except tk.TclError:
        pass

    try:
        img = Image.open(icon_path)
        photo = ImageTk.PhotoImage(img)
        window.iconphoto(True, photo)
        window._icon = photo
        return
    except Exception:
        pass

    window.after(100, lambda: set_main_app_icon_delayed(window, icon_path))


def set_main_app_icon_delayed(window, icon_path):
    try:
        img = Image.open(icon_path)
        photo = ImageTk.PhotoImage(img)
        window.iconphoto(True, photo)
        window._icon = photo
    except Exception:
        pass


def apply_dark_titlebar(window):

    try:
        if os.name != "nt":
            return
        import ctypes
        from ctypes import wintypes

        hwnd = wintypes.HWND(window.winfo_id())
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19

        def _set_attr(attr, value=1):
            value = ctypes.c_int(value)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, ctypes.c_int(attr),
                ctypes.byref(value),
                ctypes.sizeof(value)
            )

        _set_attr(DWMWA_USE_IMMERSIVE_DARK_MODE, 1)
        _set_attr(DWMWA_USE_IMMERSIVE_DARK_MODE_OLD, 1)
    except Exception:
        pass


def load_ctk_icon(path: str, size=ICON_SIZE):
    try:
        img = Image.open(path)
        return ctk.CTkImage(img, size=size)
    except Exception:
        return None


def center_over_parent(window, parent):
    try:
        window.update_idletasks()
        if parent is None:
            return
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        win_w = window.winfo_width()
        win_h = window.winfo_height()
        x = parent_x + (parent_w // 2) - (win_w // 2)
        y = parent_y + (parent_h // 2) - (win_h // 2)
        window.geometry(f"+{x}+{y}")
    except Exception:
        pass


_OriginalToplevel = tk.Toplevel


class _PatchedToplevel(_OriginalToplevel):

    def __init__(self, *args, **kwargs):
        parent = args[0] if args else kwargs.get('master', None)
        super().__init__(*args, **kwargs)
        self._patched_parent = parent

        def _on_map(event=None):
            try:
                apply_dark_titlebar(self)
            except Exception:
                pass
            try:
                center_over_parent(self, self._patched_parent)
            except Exception:
                pass

            try:
                self.unbind("<Map>", _on_map_id)
            except Exception:
                pass

        _on_map_id = self.bind("<Map>", _on_map)



tk.Toplevel = _PatchedToplevel



class UndoRedoManager:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.undo_stack = []
        self.redo_stack = []
        self.current_text = ""
        self.max_stack_size = 100
        
    def save_state(self):

        current = self.text_widget.get("1.0", "end-1c")
        if current != self.current_text:
            if len(self.undo_stack) >= self.max_stack_size:
                self.undo_stack.pop(0)
            self.undo_stack.append(self.current_text)
            self.current_text = current
            self.redo_stack.clear()
    
    def undo(self):

        if self.undo_stack:
            self.redo_stack.append(self.current_text)
            self.current_text = self.undo_stack.pop()
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", self.current_text)
    
    def redo(self):

        if self.redo_stack:
            self.undo_stack.append(self.current_text)
            self.current_text = self.redo_stack.pop()
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", self.current_text)


class NotepadClone:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Gnotepad")
        self.root.geometry("1000x700")
        
        set_main_app_icon(self.root, "logo.ico")
        
        self.root.after(500, lambda: set_main_app_icon(self.root, "logo.ico"))
    
        self.current_file = None
        self.is_modified = False
        self.original_content = ""  
        
        self.search_index = "1.0"
        self.search_matches = []
        self.current_match = 0
        
        self.font_family = "Consolas"
        self.font_size = 11
        self.font_style = "normal"

        self.setup_ui()
        self.setup_bindings()
        
        self.undo_manager = UndoRedoManager(self.text_area)
        
        self.text_area.bind("<KeyPress>", self.on_key_press)
        self.text_area.bind("<Button-1>", self.on_text_change)
        
        self.update_title()
        self.set_windows_taskbar_icon()

    def set_windows_taskbar_icon(self):

        try:
            import ctypes
            from ctypes import wintypes
            

            myappid = 'gevitop.gnotepad.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
            if hasattr(self.root, 'tk') and hasattr(self.root.tk(), 'wm_iconphoto'):
                try:
                    img = Image.open("logo.ico")
                    photo = ImageTk.PhotoImage(img)
                    self.root.tk().wm_iconphoto(True, photo)
                    self.root._icon = photo
                except:
                    pass
        except Exception as e:
            pass


    def setup_ui(self):
        self.toolbar_frame = ctk.CTkFrame(self.root, height=50)
        self.toolbar_frame.pack(fill="x", padx=5, pady=(5, 0))
        self.toolbar_frame.pack_propagate(False)
        
        self.left_buttons_frame = ctk.CTkFrame(self.toolbar_frame, fg_color="transparent")
        self.left_buttons_frame.pack(side="left", fill="y", padx=10)
        
        self.create_menu_buttons()
        
        self.right_buttons_frame = ctk.CTkFrame(self.toolbar_frame, fg_color="transparent")
        self.right_buttons_frame.pack(side="right", fill="y", padx=10)

        copy_icon = load_ctk_icon("copy.png", ICON_SIZE)
        undo_icon = load_ctk_icon("undo.png", ICON_SIZE)
        redo_icon = load_ctk_icon("redo.png", ICON_SIZE)

        self.copy_btn = ctk.CTkButton(
            self.right_buttons_frame,
            image=copy_icon if copy_icon else None,
            text="" if copy_icon else "📋",
            width=40,
            height=30,
            command=self.copy_text,
            font=("Arial", 16) if not copy_icon else None
        )
        self.copy_btn.pack(side="right", padx=2)
        
        self.search_frame = ctk.CTkFrame(self.right_buttons_frame, fg_color="transparent")
        self.search_frame.pack(side="right", padx=5)
        
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Search...",
            width=150,
            height=30
        )
        self.search_entry.pack(side="top")
        self.search_entry.bind("<KeyRelease>", self.on_search)
        self.search_entry.bind("<Return>", self.find_next)
        
        self.undo_btn = ctk.CTkButton(
            self.right_buttons_frame,
            image=undo_icon if undo_icon else None,
            text="" if undo_icon else "↶",
            width=40,
            height=30,
            command=self.undo,
            font=("Arial", 16) if not undo_icon else None
        )
        self.undo_btn.pack(side="right", padx=2)
        

        self.redo_btn = ctk.CTkButton(
            self.right_buttons_frame,
            image=redo_icon if redo_icon else None,
            text="" if redo_icon else "↷",
            width=40,
            height=30,
            command=self.redo,
            font=("Arial", 16) if not redo_icon else None
        )
        self.redo_btn.pack(side="right", padx=2)
        
        self.text_frame = ctk.CTkFrame(self.root)
        self.text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        

        self.text_area = tk.Text(
            self.text_frame,
            wrap="none",
            bg="#212121",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#264F78", 
            selectforeground="#ffffff",
            font=(self.font_family, self.font_size),
            undo=False,
            relief="flat",
            borderwidth=0,
            selectborderwidth=0,
            inactiveselectbackground="#264F78", 
            highlightthickness=0, 
            padx=10, 
            pady=10
        )
        

        self.text_area.tag_configure("sel", 
                                   background="#264F78", 
                                   foreground="#ffffff",
                                   borderwidth=0,
                                   relief="flat")
        
        self.v_scrollbar = ctk.CTkScrollbar(self.text_frame, command=self.text_area.yview)
        self.h_scrollbar = ctk.CTkScrollbar(self.text_frame, command=self.text_area.xview, orientation="horizontal")
        
        self.text_area.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.text_area.pack(fill="both", expand=True)
        

        self.context_menu = tk.Menu(self.text_area, tearoff=0, bg="#2b2b2b", fg="white", activebackground="#404040", activeforeground="white", borderwidth=0, relief="flat")
        self.context_menu.add_command(label="Cut                Ctrl+X", command=self.cut_text)
        self.context_menu.add_command(label="Copy               Ctrl+C", command=self.copy_text)
        self.context_menu.add_command(label="Paste              Ctrl+V", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All         Ctrl+A", command=self.select_all)
        self.context_menu.add_command(label="Undo               Ctrl+Z", command=self.undo)
        self.context_menu.add_command(label="Redo               Ctrl+Y", command=self.redo)
        
        self.text_area.bind("<Button-3>", self.show_context_menu)
        

        self.status_bar = ctk.CTkFrame(self.root, height=25)
        self.status_bar.pack(fill="x", side="bottom", padx=5, pady=(0, 5))
        self.status_bar.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready", anchor="w")
        self.status_label.pack(side="left", padx=10)
        
        self.cursor_pos_label = ctk.CTkLabel(self.status_bar, text="Ln 1, Col 1")
        self.cursor_pos_label.pack(side="right", padx=10)
    
    def create_menu_buttons(self):

        menu_options = [
            ("File", self.show_file_menu),
            ("Edit", self.show_edit_menu),
            ("Format", self.show_format_menu),
            ("View", self.show_view_menu),
            ("Support me", self.open_github_link)
        ]
        
        for text, command in menu_options:
            btn = ctk.CTkButton(
                self.left_buttons_frame,
                text=text,
                width=60,
                height=30,
                command=command,
                fg_color="transparent",
                hover_color="#2b2b2b"
            )
            btn.pack(side="left", padx=2)
    
    def show_context_menu(self, event):

        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def show_file_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg="#2b2b2b", fg="white", activebackground="#404040", activeforeground="white", borderwidth=0, relief="flat")
        menu.add_command(label="New                 Ctrl+N", command=self.new_file)
        menu.add_command(label="Open...             Ctrl+O", command=self.open_file)
        menu.add_command(label="Save                Ctrl+S", command=self.save_file)
        menu.add_command(label="Save As...          Ctrl+Shift+S", command=self.save_as_file)
        menu.add_separator()
        menu.add_command(label="Exit                Alt+F4", command=self.exit_app)
        
        btn = self.left_buttons_frame.winfo_children()[0]
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        menu.tk_popup(x, y)
    
    def show_edit_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg="#2b2b2b", fg="white", activebackground="#404040", activeforeground="white", borderwidth=0, relief="flat")
        menu.add_command(label="Undo                Ctrl+Z", command=self.undo)
        menu.add_command(label="Redo                Ctrl+Y", command=self.redo)
        menu.add_command(label="Redo                Ctrl+Shift+Z", command=self.redo)
        menu.add_separator()
        menu.add_command(label="Cut                 Ctrl+X", command=self.cut_text)
        menu.add_command(label="Copy                Ctrl+C", command=self.copy_text)
        menu.add_command(label="Paste               Ctrl+V", command=self.paste_text)
        menu.add_command(label="Select All          Ctrl+A", command=self.select_all)
        menu.add_separator()
        menu.add_command(label="Find                Ctrl+F", command=self.focus_search)
        menu.add_command(label="Find Next           F3", command=self.find_next)
        menu.add_command(label="Replace             Ctrl+H", command=self.show_replace_dialog)
        
        btn = self.left_buttons_frame.winfo_children()[1]
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        menu.tk_popup(x, y)
    
    def show_format_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg="#2b2b2b", fg="white", activebackground="#404040", activeforeground="white", borderwidth=0, relief="flat")
        menu.add_command(label="Word Wrap", command=self.toggle_word_wrap)
        menu.add_command(label="Font...", command=self.choose_font)
        
        btn = self.left_buttons_frame.winfo_children()[2]
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        menu.tk_popup(x, y)
    
    def show_view_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg="#2b2b2b", fg="white", activebackground="#404040", activeforeground="white", borderwidth=0, relief="flat")
        menu.add_command(label="Zoom In             Ctrl++", command=self.zoom_in)
        menu.add_command(label="Zoom Out            Ctrl+-", command=self.zoom_out)
        menu.add_command(label="Restore Default Zoom Ctrl+0", command=self.reset_zoom)
        menu.add_separator()
        menu.add_command(label="Status Bar", command=self.toggle_status_bar)
        
        btn = self.left_buttons_frame.winfo_children()[3]
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        menu.tk_popup(x, y)
    
    def open_github_link(self):
        webbrowser.open("https://github.com/gevitop/")

    def setup_bindings(self):

        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as_file())
        

        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-Shift-Z>", lambda e: self.redo())
        self.root.bind("<Control-x>", lambda e: self.cut_text())
        self.root.bind("<Control-c>", lambda e: self.copy_text())
        

        self.text_area.bind("<Control-v>", self.paste_text)
        self.root.bind("<Control-a>", lambda e: self.select_all())
        

        self.root.bind("<Control-f>", lambda e: self.focus_search())
        self.root.bind("<F3>", lambda e: self.find_next())
        self.root.bind("<Control-h>", lambda e: self.show_replace_dialog())
        

        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-equal>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-0>", lambda e: self.reset_zoom())
        

        self.text_area.bind("<Control-MouseWheel>", self.on_mouse_wheel)
        

        self.text_area.bind("<KeyRelease>", self.on_text_change)
        self.text_area.bind("<Button-1>", self.update_cursor_position)
        self.text_area.bind("<KeyPress>", self.update_cursor_position)
        

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
    
    def on_mouse_wheel(self, event):

        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def on_key_press(self, event):

        if event.keysym in ['Return', 'BackSpace', 'Delete', 'Tab']:
            self.undo_manager.save_state()
        elif event.char and event.char.isprintable():

            if len(self.text_area.get("1.0", "end-1c")) % 10 == 0:
                self.undo_manager.save_state()
    
    def on_text_change(self, event=None):
        current_text = self.text_area.get("1.0", "end-1c")
        
        if self.current_file is None:
            self.is_modified = (current_text != "")
        else:
            self.is_modified = (current_text != self.original_content)
            
        self.update_title()
        self.update_status()
        self.update_cursor_position()
    
    def update_cursor_position(self, event=None):
        self.root.after(1, self._update_cursor_pos)
    
    def _update_cursor_pos(self):
        cursor_pos = self.text_area.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.cursor_pos_label.configure(text=f"Ln {line}, Col {int(col) + 1}")
    
    def update_title(self):
        filename = os.path.basename(self.current_file) if self.current_file else "Untitled"
        modified = "*" if self.is_modified else ""
        self.root.title(f"{modified}{filename} - Gnotepad")
    
    def update_status(self):
        char_count = len(self.text_area.get("1.0", "end-1c"))
        self.status_label.configure(text=f"Characters: {char_count}")
    

    def new_file(self):
        if self.is_modified:
            if not self.ask_save_changes():
                return
        
        self.text_area.delete("1.0", tk.END)
        self.current_file = None
        self.is_modified = False
        self.original_content = ""
        self.undo_manager = UndoRedoManager(self.text_area)
        self.update_title()
        self.update_status()
    
    def open_file(self):
        if self.is_modified:
            if not self.ask_save_changes():
                return
        
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.current_file = file_path
                self.original_content = content
                self.is_modified = False
                self.undo_manager = UndoRedoManager(self.text_area)
                self.undo_manager.current_text = content
                self.update_title()
                self.update_status()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get("1.0", "end-1c")
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.is_modified = False
                self.original_content = content
                self.update_title()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                content = self.text_area.get("1.0", "end-1c")
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.current_file = file_path
                self.is_modified = False
                self.original_content = content
                self.update_title()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def ask_save_changes(self):
        if self.is_modified:
            response = messagebox.askyesnocancel("Save Changes", "Do you want to save changes to this document?")
            if response is True:
                self.save_file()
                return not self.is_modified
            elif response is False:
                return True
            else:
                return False
        return True
    

    def undo(self):

        self.undo_manager.undo()
        self.on_text_change()
    
    def redo(self):

        self.undo_manager.redo()
        self.on_text_change()
    
    def cut_text(self):

        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.on_text_change()
        except tk.TclError:
            pass
    
    def copy_text(self):

        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:

            full_text = self.text_area.get("1.0", "end-1c")
            self.root.clipboard_clear()
            self.root.clipboard_append(full_text)
    
    def paste_text(self, event=None):

        try:
            clipboard_content = self.root.clipboard_get()
            self.text_area.insert(tk.INSERT, clipboard_content)
            self.on_text_change()
            return "break"
        except tk.TclError:
            pass
    
    def select_all(self):
        content = self.text_area.get("1.0", "end-1c")
        self.text_area.tag_remove("sel", "1.0", "end")
        

        self.text_area.tag_add("sel", "1.0", f"1.0+{len(content)}c")
        self.text_area.focus_set()
    

    def focus_search(self):
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)
    
    def on_search(self, event=None):
        query = self.search_entry.get()
        if not query:
            self.clear_search_highlights()
            return
        
        self.search_text(query)
    
    def search_text(self, query):
        self.clear_search_highlights()
        
        if not query:
            return
        
        self.search_matches = []
        start = "1.0"
        
        while True:
            pos = self.text_area.search(query, start, tk.END, nocase=True)
            if not pos:
                break
            
            end = f"{pos}+{len(query)}c"
            self.search_matches.append((pos, end))
            self.text_area.tag_add("search_highlight", pos, end)
            start = end
        

        self.text_area.tag_config("search_highlight", background="#404040", foreground="#ffff00")
        
        if self.search_matches:
            self.current_match = 0
            self.highlight_current_match()
    
    def find_next(self, event=None):
        if not self.search_matches:
            return
        
        self.current_match = (self.current_match + 1) % len(self.search_matches)
        self.highlight_current_match()
    
    def highlight_current_match(self):
        if not self.search_matches:
            return
        

        self.text_area.tag_remove("current_match", "1.0", tk.END)
        

        pos, end = self.search_matches[self.current_match]
        self.text_area.tag_add("current_match", pos, end)
        self.text_area.tag_config("current_match", background="#1f538d", foreground="#ffffff")
        

        self.text_area.see(pos)
    
    def clear_search_highlights(self):
        self.text_area.tag_remove("search_highlight", "1.0", tk.END)
        self.text_area.tag_remove("current_match", "1.0", tk.END)
        self.search_matches = []
        self.current_match = 0


    def show_replace_dialog(self):
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Replace")
        replace_window.geometry("650x280")
        replace_window.transient(self.root)
        replace_window.grab_set()
        replace_window.configure(bg="#2b2b2b")
        replace_window.iconbitmap('')

        try:
            img = Image.open("logo.ico")
            photo = ImageTk.PhotoImage(img)
            replace_window.iconphoto(False, photo)
        except:
            pass


        main_frame = ctk.CTkFrame(replace_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        

        ctk.CTkLabel(main_frame, text="Find what:").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        find_entry = ctk.CTkEntry(main_frame, width=300)
        find_entry.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="ew")
        

        ctk.CTkLabel(main_frame, text="Replace with:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        replace_entry = ctk.CTkEntry(main_frame, width=300)
        replace_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        

        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=10)
        
        match_case = tk.BooleanVar()
        wrap_around = tk.BooleanVar(value=True)
        
        ctk.CTkCheckBox(options_frame, text="Match case", variable=match_case).pack(anchor="w")
        ctk.CTkCheckBox(options_frame, text="Wrap around", variable=wrap_around).pack(anchor="w")
        

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        def find_next_action():
            find_text = find_entry.get()
            if find_text:
                self.search_entry.delete(0, tk.END)
                self.search_entry.insert(0, find_text)
                self.search_text(find_text)
                self.find_next()
        
        def replace_action():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            if find_text and self.search_matches:
                selected_text = self.text_area.get("sel.first", "sel.last")
                if selected_text == find_text:
                    self.text_area.delete("sel.first", "sel.last")
                    self.text_area.insert("sel.first", replace_text)
                find_next_action()
        
        def replace_all_action():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            if find_text:
                content = self.text_area.get("1.0", "end-1c")
                if match_case.get():
                    new_content = content.replace(find_text, replace_text)
                else:
                    pattern = re.compile(re.escape(find_text), re.IGNORECASE)
                    new_content = pattern.sub(replace_text, content)
                
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", new_content)
                self.on_text_change()
        
        ctk.CTkButton(button_frame, text="Find Next", command=find_next_action, width=100).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Replace", command=replace_action, width=100).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Replace All", command=replace_all_action, width=100).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=replace_window.destroy, width=100).pack(side="left", padx=5)
        

        main_frame.columnconfigure(1, weight=1)
        
        find_entry.focus_set()
    

    def toggle_word_wrap(self):
        current_wrap = self.text_area.cget("wrap")
        new_wrap = "word" if current_wrap == "none" else "none"
        self.text_area.configure(wrap=new_wrap)
    
    def choose_font(self):
        font_window = tk.Toplevel(self.root)
        font_window.title("Font")
        font_window.geometry("500x650")
        font_window.transient(self.root)
        font_window.grab_set()
        font_window.configure(bg="#343333")
        font_window.iconbitmap('')
        try:
            img = Image.open("logo.ico")
            photo = ImageTk.PhotoImage(img)
            font_window.iconphoto(False, photo)
        except:
            pass


        main_frame = ctk.CTkFrame(font_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(main_frame, text="Font:").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        font_list_frame = ctk.CTkFrame(main_frame)
        font_list_frame.grid(row=0, column=1, sticky="w", padx=10, pady=(10, 5))
        
        font_listbox = tk.Listbox(
            font_list_frame,
            selectmode="single",
            exportselection=0,
            bg="#212121",
            fg="white",
            selectbackground="#1f538d",
            selectforeground="#ffffff",
            relief="flat",
            borderwidth=0,
            height=6
        )
        font_listbox.pack(side="left", fill="both", expand=True)
        
        font_scrollbar = ctk.CTkScrollbar(font_list_frame, command=font_listbox.yview)
        font_scrollbar.pack(side="right", fill="y")
        font_listbox.configure(yscrollcommand=font_scrollbar.set)
        
        all_fonts = sorted(tkFont.families())
        for font in all_fonts:
            font_listbox.insert(tk.END, font)
        

        if self.font_family in all_fonts:
            index = all_fonts.index(self.font_family)
            font_listbox.selection_set(index)
            font_listbox.see(index)
        

        ctk.CTkLabel(main_frame, text="Font style:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        style_var = ctk.StringVar(value=self.font_style.replace("normal", "Regular").replace("bold", "Bold").replace("italic", "Italic").title())
        style_dropdown = ctk.CTkOptionMenu(
            main_frame, 
            variable=style_var,
            values=["Regular", "Bold", "Italic", "Bold Italic"],
            width=200
        )
        style_dropdown.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(main_frame, text="Size:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        size_var = ctk.StringVar(value=str(self.font_size))
        size_dropdown = ctk.CTkOptionMenu(
            main_frame, 
            variable=size_var,
            values=["8", "9", "10", "11", "12", "14", "16", "18", "20", "22", "24", "26", "28", "36", "48", "72"],
            width=200
        )
        size_dropdown.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        sample_frame = ctk.CTkFrame(main_frame, height=100)
        sample_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        sample_frame.grid_rowconfigure(1, weight=1)
        sample_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(sample_frame, text="Sample", anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
        
        sample_text = tk.Text(
            sample_frame, 
            height=4, 
            bg="#2b2b2b", 
            fg="white", 
            relief="flat",
            wrap="word"
        )
        sample_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))
        sample_text.insert("1.0", "AaBbYyZz")
        sample_text.config(state="disabled")

        button_frame = ctk.CTkFrame(font_window, fg_color="transparent")
        button_frame.pack(fill="x", side="bottom", padx=20, pady=10)
        
        def update_sample():
            try:
                font_index = font_listbox.curselection()
                font_family = font_listbox.get(font_index) if font_index else self.font_family
                font_style_str = style_var.get()
                font_size = int(size_var.get())
                
                weight = "bold" if "Bold" in font_style_str else "normal"
                slant = "italic" if "Italic" in font_style_str else "roman"
                
                sample_text.config(state="normal")
                sample_text.delete("1.0", "end")
                sample_text.insert("1.0", "AaBbYyZz")
                sample_text.tag_add("sample", "1.0", "end")
                sample_text.tag_config("sample", font=(font_family, font_size, weight, slant))
                sample_text.config(state="disabled")
            except (ValueError, tk.TclError):
                pass

        def apply_font():
            try:
                font_index = font_listbox.curselection()
                if not font_index:
                    return
                font_family = font_listbox.get(font_index)
                font_size = int(size_var.get())
                font_style_str = style_var.get()
                
                weight = "bold" if "Bold" in font_style_str else "normal"
                slant = "italic" if "Italic" in font_style_str else "roman"
                
                self.font_family = font_family
                self.font_size = font_size
                self.font_style = font_style_str
                
                self.text_area.configure(font=(self.font_family, self.font_size, weight, slant))
                font_window.destroy()
            except (ValueError, tk.TclError):
                messagebox.showerror("Error", "Invalid font selection.")

        font_listbox.bind("<<ListboxSelect>>", lambda e: update_sample())
        style_var.trace("w", lambda *args: update_sample())
        size_var.trace("w", lambda *args: update_sample())
        
        update_sample()

        ctk.CTkButton(button_frame, text="OK", command=apply_font).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=font_window.destroy).pack(side="right", padx=5)

    def zoom_in(self):
        self.font_size = min(self.font_size + 1, 72)
        self.update_font()
    
    def zoom_out(self):
        self.font_size = max(self.font_size - 1, 6)
        self.update_font()
    
    def update_font(self):
        weight = "bold" if "Bold" in self.font_style else "normal"
        slant = "italic" if "Italic" in self.font_style else "roman"
        self.text_area.configure(font=(self.font_family, self.font_size, weight, slant))
    
    def reset_zoom(self):
        self.font_size = 11
        self.update_font()
    
    def toggle_status_bar(self):
        if self.status_bar.winfo_viewable():
            self.status_bar.pack_forget()
        else:
            self.status_bar.pack(fill="x", side="bottom", padx=5, pady=(0, 5))
    
    def show_about(self):
        messagebox.showinfo("About", "Gnotepad\nBuilt with Love\nA modern, feature-rich text editor")
    
    def exit_app(self):
        if self.ask_save_changes():
            self.root.quit()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NotepadClone()
    app.run()
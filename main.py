#!/usr/bin/env python
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio
from gi.repository import GdkPixbuf
import os
import stat
import sys
import time


builder = Gtk.Builder()
builder.add_from_file("ui.glade")
HOME=os.environ.get('HOME')
DEFAULT_SAVE_PATH=HOME+"/.local/share/applications/"

listbox_recents = builder.get_object("listboxRecents")

#recents manager
recent_manager = Gtk.RecentManager()
recents = recent_manager.get_items()
recents_count = len(recents)
act_recents_count = 0
desktop_recents_path = []
desktop_recents_name = []
#get_row_at_index
def refreshRecents():
	global act_recents_count
	global desktop_recents_name
	global desktop_recents_name
	global recents
	recents = recent_manager.get_items()
	j=0
	while j<act_recents_count:
		listbox_recents.remove(listbox_recents.get_row_at_index(0))
		j+=1
	i=0
	desktop_recents_path = []
	desktop_recents_name = []
	while i<recents_count and len(desktop_recents_path) < 5:
		if recents[i].get_uri()[-8:] == ".desktop" and recents[i].get_uri()[:7]=="file://" and os.path.isfile(recents[i].get_uri()[7:]):
			desktop_recents_path.append(recents[i].get_uri()[7:])
			desktop_recents_name.append(recents[i].get_display_name())
		i+=1
	act_recents_count=len(desktop_recents_name)
	i=0
	while i<act_recents_count:
		box= Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		labelName= Gtk.Label()
		labelPath= Gtk.Label()
		labelName.set_xalign(0)
		labelPath.set_xalign(0)
		labelPath.set_opacity(0.5)
		box.set_spacing(6)
		labelName.set_text(desktop_recents_name[i])
		labelPath.set_text(desktop_recents_path[i])
		box.pack_end(labelPath, True, True, 0)
		box.pack_end(labelName, True, True, 0)
		row=Gtk.ListBoxRow()
		row.add(box)
		listbox_recents.add(row)
		i+=1
	
refreshRecents()

class App(Gtk.Application):
	def __init__(self):
		Gtk.Application.__init__(self, application_id="com.gabmus.mlauncher", flags=Gio.ApplicationFlags.FLAGS_NONE)

		self.connect("activate", self.activateCb)
		
		
	def do_startup(self):
	# start the application
		Gtk.Application.do_startup(self)
		
	def activateCb(self, app):
		window = builder.get_object("window1")
		window.set_wmclass("mLauncher", "mLauncher")
		app.add_window(window)
		appMenu=Gio.Menu()
		appMenu.append("About", "app.about")
		appMenu.append("Quit", "app.quit")
		about_action = Gio.SimpleAction.new("about", None)
		about_action.connect("activate", self.on_about_activate)
		app.add_action(about_action)
		quit_action = Gio.SimpleAction.new("quit", None)
		quit_action.connect("activate", self.on_quit_activate)
		app.add_action(quit_action)
		app.set_app_menu(appMenu)
		window.show_all()
		
	def on_about_activate(self, *agrs):
		builder.get_object("aboutdialog").show()
		
	def on_quit_activate(self, *args):
		self.quit()


def wait(time_lapse):
	time_start = time.time()
	time_end = (time_start + time_lapse)
 
	while time_end > time.time():
		while Gtk.events_pending():
			Gtk.main_iteration()

class Handler:

	iconPath="icon"
	infobarButtonsActionCode=0
	savePath=DEFAULT_SAVE_PATH+"default-mLauncher.desktop"
	untouchableLines= "\n"
	customSavePath= None

	def __init__(self):
		self.updateRadios()
		
	def showInfo(self, message, buttons, reHide=False, buttonsAction=None):
		buttonOk=builder.get_object("buttonInfobarOk")
		buttonCancel=builder.get_object("buttonInfobarCancel")
		infobar=builder.get_object("infobar")
		labelInfobar=builder.get_object("labelInfobar")
		if buttons:
			buttonOk.show()
			buttonCancel.show()
			self.infobarButtonsActionCode=buttonsAction
		else:
			buttonOk.hide()
			buttonCancel.hide()
		labelInfobar.set_text(message)
		infobar.show()
		if reHide:
			wait(5)
			infobar.hide()
		
				
	def updateRadios(self):
		radio_iconName = builder.get_object("radiobuttonIconName")
		entry_iconName = builder.get_object("entryIconName")
		filechooser_iconName = builder.get_object("filechooserbuttonIconPath")
		if radio_iconName.get_active():
			entry_iconName.set_sensitive(True)
			filechooser_iconName.set_sensitive(False)
			builder.get_object("filechooserbuttonIconPath").unselect_all()
		else:
			entry_iconName.set_sensitive(False)
			filechooser_iconName.set_sensitive(True)
		builder.get_object("imageIcon").set_from_icon_name("gnome-panel-launcher", Gtk.IconSize.DIALOG)
		self.iconPath="icon"
		entry_iconName.set_text("")
		
	def on_entryIconName_insert_text(self, entry):
		iconName = builder.get_object("entryIconName").get_text().strip()
		builder.get_object("imageIcon").set_from_icon_name(iconName, Gtk.IconSize.DIALOG)
		self.iconPath=iconName
		
	def on_radiobuttonIcon_group_changed(self, button):
		self.updateRadios()
	
	def onDeleteWindow(self, *args):
		Gtk.main_quit(*args)

	def buttonSave_clicked_cb(self, button):
		name=builder.get_object("entryName").get_text().strip()
		executable=builder.get_object("entryExec").get_text().strip()
		path=builder.get_object("entryPath").get_text().strip()
		category=builder.get_object("comboboxtext-entry").get_text()
		terminal=builder.get_object("switchTerminal").get_state()
		#check if the name contains nothing or only spaces
		if name and executable:
			if path and not os.path.isdir(path):
				self.showInfo("Your path is invalid! Clear or correct it!", False, True)
			else:
				#build string
				launcherString="[Desktop Entry]\n"
				launcherString+="Encoding=UTF-8\n"
				launcherString+="Type=Application\n"
				launcherString+="Categories="+category+"\n"
				launcherString+="Terminal="
				if terminal:
					launcherString+="true\n"
				else:
					launcherString+="false\n"
				launcherString+="Exec="+executable+"\n"
				if path:
					launcherString+="Path="+path+"\n"
				launcherString+="Name="+name+"\n"
				launcherString+="Icon="+self.iconPath
				launcherString+=self.untouchableLines
				if self.customSavePath:
					self.savePath=self.customSavePath
				else:
					self.savePath=DEFAULT_SAVE_PATH+name+".desktop"
				
				if not os.path.isfile(self.savePath):
					out_file = open(self.savePath,"w")
					out_file.write(launcherString)
					out_file.close()
					st= os.stat(self.savePath)
					os.chmod(self.savePath, st.st_mode | stat.S_IEXEC)
					recent_manager.add_item("file://"+self.savePath)
					print("\n\nDebug:\n"+launcherString)
					self.showInfo("File saved ("+self.savePath+")", False, True)
				else:
					#the infobar has to delete the file and recall this method
					self.showInfo("The file "+self.savePath+" already exists. Do you want to replace it?", True, False, 1)
		else:
			self.showInfo("Missing name and/or executable! Fix it!", False, True)
			
	def scale_image(self, filename):
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 48, 48)
		return pixbuf
			
	def on_filechooserbuttonIcon_file_set(self, button):
		imgObj=builder.get_object("imageIcon")
		self.iconPath=button.get_filename()
		pixbuf=self.scale_image(button.get_filename())
		imgObj.set_from_pixbuf(pixbuf)
			
	def on_filechooserbuttonExecutable_file_set(self, button):
		entry_exec=builder.get_object("entryExec")
		execFileName=button.get_filename()
		processedFileName=""
		i=0
		while i<len(execFileName):
			if execFileName[i] == " ":
				processedFileName+="\\ "
			elif execFileName[i] == "\\":
				processedFileName+="\\\\"
			else:
				processedFileName+=execFileName[i]
			i+=1
		entry_exec.set_text(processedFileName)
		
	def on_filechooserbuttonPath_file_set(self, button):
		entry_path=builder.get_object("entryPath")
		pathFileName=button.get_filename()
		entry_path.set_text(pathFileName)
		
	def on_buttonInfobarClose_clicked(self, infobar, closebutton):
		infobar.hide()
		
	def on_buttonInfobarCancel_clicked(self, button):
		builder.get_object("infobar").hide()
		
	def on_buttonInfobarOk_clicked(self, button):
		if self.infobarButtonsActionCode == 1:
			os.remove(self.savePath)
			self.buttonSave_clicked_cb(button)
		else:
			print("Infobar action code was "+self.infobarButtonsActionCode+". Tell the programmer something's wrong!")
			
	def on_buttonOpen_clicked(self, button):
		if popover.get_visible():
			popover.hide()
		else:
			refreshRecents()
			popover.show_all()
			
	def resetUI(self):
		builder.get_object("entryName").set_text("")
		builder.get_object("entryExec").set_text("")
		builder.get_object("entryPath").set_text("")
		builder.get_object("comboboxtext-entry").set_text("")
		builder.get_object("switchTerminal").set_state(False)
			
	def processFile(self, path):
		try:
			with open(path) as f:
				lines = f.readlines()
		
			self.customSavePath=path
		
			name=builder.get_object("entryName")
			executable=builder.get_object("entryExec")
			path=builder.get_object("entryPath")
			category=builder.get_object("comboboxtext-entry")
			terminal=builder.get_object("switchTerminal")
		
			self.resetUI()
		
			i=0
			self.untouchableLines= "\n"
			skip = [False, False, False, False, False, False]
			while len(lines)>0:
				if lines[i].strip() == "[Desktop Entry]":
					lines.pop(i)
				elif lines[i].strip()[:9] == "Encoding=":
					lines.pop(i)
				elif lines[i].strip() == "Type=Application":
					lines.pop(i)
				elif lines[i].strip()[:9] == "Terminal=" and not skip[0]:
					if "true" in lines[i]:
						terminal.set_state(True)
					else:
						terminal.set_state(False)
					lines.pop(i)
					skip[0]=True
				elif lines[i].strip()[:5] == "Exec=" and not skip[1]:
					executable.set_text(lines[i].strip()[5:])
					lines.pop(i)
					skip[1]=True
				elif lines[i].strip()[:5] == "Name=" and not skip[2]:
					name.set_text(lines[i].strip()[5:])
					lines.pop(i)
					skip[2]=True
				elif lines[i].strip()[:5] == "Name[":
					lines.pop(i)
				elif lines[i].strip()[:5] == "Icon=" and not skip[3]:
					mIcon=lines[i].strip()[5:]
					print(os.path.isfile(mIcon))
					if os.path.isfile(mIcon):
						builder.get_object("radiobuttonIconPath").set_active(True)
						builder.get_object("radiobuttonIconName").set_active(False)
						builder.get_object("filechooserbuttonIconPath").set_filename(mIcon)
						#self.updateRadios()
					else:
						builder.get_object("radiobuttonIconPath").set_active(False)
						builder.get_object("radiobuttonIconName").set_active(True)
						builder.get_object("entryIconName").set_text(mIcon)
						#self.updateRadios()
					self.iconPath=mIcon
					lines.pop(i)
					skip[3]=True
				elif lines[i].strip()[:5] == "Path=" and not skip[4]:
					path.set_text(lines[i].strip()[5:])
					lines.pop(i)
					skip[4]=True
				elif lines[i].strip()[:11] == "Categories=" and not skip[5]:
					category.set_text(lines[i].strip()[11:])
					lines.pop(i)
					skip[5]=True
				else:
					self.untouchableLines+=lines.pop(i)
		except:
			self.customSavePath= None
			print("ERR: File not found")
			self.showInfo("The file does not exist! Maybe you deleted it?", False, True)
		popover.hide()
									
		
			
	def on_listboxRecents_row_activated(self, listbox, row):
		selectedFilePath=row.get_children()[0].get_children()[1].get_text()
		self.processFile(selectedFilePath)
		
	def on_buttonOpenBrowse_clicked(self, button):
		builder.get_object("filechooserdialogOpenBrowse").set_current_folder_uri("file://"+HOME)
		builder.get_object("filechooserdialogOpenBrowse").show_all()
		popover.hide()
		
	
	def on_buttonDesktopChooserOk_clicked(self, button):
		self.on_filechooserdialogOpenBrowse_file_activated(builder.get_object("filechooserdialogOpenBrowse"))
		
		
	def on_filechooserdialogOpenBrowse_file_activated(self, dialog):
		if dialog.get_filename()[-8:] == ".desktop":
			self.processFile(dialog.get_filename())
		else:
			self.showInfo("The file selected is not valid. Look for one with a .desktop extension.", False, True)
		dialog.hide()
	
	
	def on_buttonDesktopChooserCancel_clicked(self, button):
		builder.get_object("filechooserdialogOpenBrowse").hide()
	
	def on_buttonSaveAsChooserCancel_clicked(self, button):
		builder.get_object("filechooserdialogSaveAs").hide()
	
	def on_buttonDesktopChooserOpenDefaultFolder_clicked(self, button):
		builder.get_object("filechooserdialogOpenBrowse").set_current_folder_uri("file://"+HOME+"/.local/share/applications")
		
	def on_buttonSaveAsChooserOpenDefaultFolder_clicked(self, button):
		builder.get_object("filechooserdialogSaveAs").set_current_folder_uri("file://"+HOME+"/.local/share/applications")
		
	def on_buttonSaveAs_clicked(self, button):
		builder.get_object("filechooserdialogSaveAs").set_current_folder_uri("file://"+HOME)
		builder.get_object("filechooserdialogSaveAs").show_all()
		
	def on_buttonSaveAsChooserOk_clicked(self, button):
		path=builder.get_object("filechooserdialogSaveAs").get_filename()
		if path[-8:] != ".desktop":
			path+=".desktop"
		self.customSavePath=path
		builder.get_object("filechooserdialogSaveAs").hide()
		self.buttonSave_clicked_cb(button)
		
			
			

popover = Gtk.Popover.new(builder.get_object("buttonOpen"))
popover.add(builder.get_object("openerWidget"))
builder.connect_signals(Handler())


if __name__ == "__main__":
	app= App()
	app.run(sys.argv)
#Gtk.main()

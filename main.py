#!/usr/bin/env python
from gi.repository import Gtk
from gi.repository import GdkPixbuf
import os
from os import path as ospath
from os import environ as osenviron
from os import remove as osremove
import stat
from os import stat as osstat
from os import chmod as oschmod


builder = Gtk.Builder()
builder.add_from_file("ui.glade")
HOME=os.environ.get('HOME')
DEFAULT_SAVE_PATH=HOME+"/.local/share/applications/"

class Handler:

	iconPath="icon"
	infobarButtonsActionCode=0
	savePath=DEFAULT_SAVE_PATH+"default-mLauncher.desktop"
	

	def __init__(self):
		self.updateRadios()
		
	def showInfo(self, message, buttons, buttonsAction=None):
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
		
				
	def updateRadios(self):
		radio_iconName = builder.get_object("radiobuttonIconName")
		radio_iconPath = builder.get_object("radiobuttonIconPath")
		entry_iconName = builder.get_object("entryIconName")
		button_load = builder.get_object("buttonLoadIconByName")
		filechooser_iconName = builder.get_object("filechooserbuttonIconPath")
		if radio_iconName.get_active():
			entry_iconName.set_sensitive(True)
			button_load.set_sensitive(True)
			filechooser_iconName.set_sensitive(False)
			builder.get_object("filechooserbuttonIconPath").unselect_all()
		else:
			entry_iconName.set_sensitive(False)
			button_load.set_sensitive(False)
			filechooser_iconName.set_sensitive(True)
		builder.get_object("imageIcon").set_from_icon_name("gnome-panel-launcher", Gtk.IconSize.DIALOG)
		self.iconPath="icon"
		entry_iconName.set_text("")
		
	def on_buttonLoadIconByName_clicked(self, button):
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
		category=builder.get_object("comboboxtextCategory").get_active_text()
		terminal=builder.get_object("switchTerminal").get_state()
		#check if the name contains nothing or only spaces
		if name and executable:
			if path and not os.path.isdir(path):
				self.showInfo("Your path is invalid! Clear or correct it!", False)
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
				self.savePath=DEFAULT_SAVE_PATH+name+"-mLauncher.desktop"
				
				if not os.path.isfile(self.savePath):
					out_file = open(self.savePath,"w")
					out_file.write(launcherString)
					out_file.close()
					st= os.stat(self.savePath)
					os.chmod(self.savePath, st.st_mode | stat.S_IEXEC)
					print("\n\nDebug:\n"+launcherString)
					self.showInfo("File saved in the default launchers path (~/.local/share/applications/)", False)
				else:
					#the infobar has to replace and save
					self.showInfo("The file "+self.savePath+" already exists. Do you want to replace it?", True, 1)
		else:
			self.showInfo("Missing name and/or executable! Fix it!", False)
			
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
		i=0
		processedFileName=""
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

builder.connect_signals(Handler())
window = builder.get_object("window1")
window.show_all()

Gtk.main()

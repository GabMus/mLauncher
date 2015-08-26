#!/usr/bin/env python
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from os import path as ospath
from os import environ as osenviron


builder = Gtk.Builder()
builder.add_from_file("ui.glade")
HOME=osenviron.get('HOME')
DEFAULT_SAVE_PATH=HOME+"/.local/share/applications/"

class Handler:

	iconPath="icon"

	def __init__(self):
		self.updateRadios()
		
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
		infobar=builder.get_object("infobar")
		label_infobar=builder.get_object("labelInfobar")
		#check if the name contains nothing or only spaces
		if name and executable:
			if path and not ospath.isdir(path):
				label_infobar.set_text("Your path is invalid! Clear or correct it!")
				infobar.show()
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
				out_file = open(DEFAULT_SAVE_PATH+name+"-mLauncher.desktop","w")
				out_file.write(launcherString)
				out_file.close()
				print("\n\nDebug:\n"+launcherString)
				label_infobar.set_text("File saved in the default launchers path (~/.local/share/applications/)")
				infobar.show()
		else:
			label_infobar.set_text("Missing name and/or executable! Fix it!")
			infobar.show()
			
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

builder.connect_signals(Handler())
window = builder.get_object("window1")
window.show_all()

Gtk.main()

import pygtk
pygtk.require('2.0')
import gtk
icon_theme = gtk.icon_theme_get_default()
icons=icon_theme.list_icons()
for icon in icons:
       print icon
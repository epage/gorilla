import os

__pretty_app_name__ = "Gorilla"
__app_name__ = "gorilla"
__version__ = "0.1.5"
__build__ = 0
__app_magic__ = 0xdeadbeef
_data_path_ = os.path.join(os.path.expanduser("~"), ".%s" % __app_name__)
_user_settings_ = "%s/settings.ini" % _data_path_
_user_logpath_ = "%s/%s.log" % (_data_path_, __app_name__)
IS_MAEMO = True

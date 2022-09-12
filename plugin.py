from pluginlib import Parent

# Plugin Base

@Parent("Plugin")
class PluginTemplate(object):
    ''' Plugin Template '''

    def on_open(self, ws): 
        return

    def on_close(self, ws, close_status_code, close_msg): 
        return

    def on_error(self, ws, error): 
        return

    def on_recv(self, ws, data, type, continuous): 
        return

    def on_send(self, ws, data, opcode): 
        return

    def on_ping(self, ws, message): 
        return

    def on_pong(self, ws, message): 
        return

# Plugin Manager

from pluginlib import PluginLoader, PluginImportError

_plugins = None

def initialize():
    global _plugins
    if _plugins is None:
        loader = PluginLoader(modules=["plugins"])
        try:
            _plugins = loader.plugins
        except PluginImportError as e:
            print(e)

def plugins():
    global _plugins
    return None if _plugins is None else _plugins.Plugin.values()

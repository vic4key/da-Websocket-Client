from plugin import PluginTemplate

class Sample(PluginTemplate):
  _alias_ = "Sample"
  _version_ = "1.0"
  # _skipload_ = True

  @staticmethod
  def _skipload_():
    from sys import version_info
    if version_info[:2] < (3, 6):
      return True, "Only support Python 3.6 or higher"
    return False

  def on_open(self, ws):
    print("WS openned  =>", ws)

  def on_close(self, ws, close_status_code, close_msg):
    print("WS closed   =>", ws, close_status_code, close_msg)

  def on_recv(self, ws, data, type, continuous):
    print("WS received =>", ws, "<data>", type, continuous)

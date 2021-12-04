bl_info = {
    "name": "Media Info Extractor",
    "description": "Get Media Info and insert it in the Text Editor",
    "author": "Tintwotin",
    "version": (1, 2),
    "blender": (2, 90, 0),
    "location": "Sequencer > Sidebar > Strip > Source > Media Info to Text Editor",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Sequencer",
}
from collections import ChainMap
import bpy, subprocess, os, sys
#from bpy.types import Operator
#from bpy.props import (
#    IntProperty,
#    BoolProperty,
#    EnumProperty,
#    StringProperty,
#    FloatProperty,
#)
import site


class SEQUENCE_OT_media_info_to_text_editor(bpy.types.Operator):
    """Extract Media Info and insert it in the Text Editor"""

    bl_label = "Media Info to Text Editor"
    bl_idname = "sequencer.media_info_to_text_editor"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        layout = layout.box()
        layout = layout.column(align=True)

        if collected_info:
            for i in collected_info.splitlines()[:-1]:
                layout.label(text=i)
        return

    def execute(self, context):
        global collected_info
        strip = bpy.context.scene.sequence_editor.active_strip
        # get the active strip
        seq_active = context.scene.sequence_editor.active_strip
        if seq_active.type == None or seq_active.type in [
            "MASK",
            "CLIP",
            "SCENE",
            "COLOR",
            "CROSS",
            "ADD",
            "SUBTRACT",
            "ALPHA_OVER",
            "ALPHA_UNDER",
            "GAMMA_CROSS",
            "MULTIPLY",
            "OVER_DROP",
            "WIPE",
            "GLOW",
            "TRANSFORM",
            "COLOR",
            "SPEED",
            "MULTICAM",
            "ADJUSTMENT",
            "GAUSSIAN_BLUR",
            "TEXT",
        ]:
            self.report(
                {"ERROR"}, "Active strip must be a video with inherent resolution"
            )
            return {"CANCELLED"}
        if seq_active.type == "SOUND":
            file_path = bpy.path.abspath(seq_active.sound.filepath)
        if seq_active.type == "IMAGE":
            strip_dirname = os.path.dirname(seq_active.directory)
            file_path = bpy.path.abspath(os.path.join(strip_dirname, seq_active.name))
        if seq_active.type == "MOVIE":
            file_path = bpy.path.abspath(
                (str(seq_active.filepath))
            )  # convert to absolute path
        file_path = file_path.replace("\\", "\\\\")
        print(file_path)
        filename = os.path.basename(file_path)

        app_path = site.USER_SITE
        if app_path not in sys.path:
            sys.path.append(app_path)
        pybin = sys.executable  # bpy.app.binary_path_python # Use for 2.83

        try:
            subprocess.call([pybin, "-m", "ensurepip"])
        except ImportError:
            pass
        try:
            from infomedia import InfoMedia
        except ImportError:
            subprocess.check_call([pybin, "-m", "pip", "install", "infomedia"])
        try:
            from infomedia import mediainfo
        except ImportError:
            print("Installation of the Media Info module failed")
        data = mediainfo(file_path)
        # print("Duration = {}".format(data['format']['duration']))
        chain_data = ChainMap(data)
        collected_info = "File: " + file_path + "\n"

        for item, value in chain_data.items():
            item = (item.replace(" ", "")).title()
            item = (item.replace("_", " ")).title()
            collected_info = collected_info + ("\n" + item + ": " + "\n")
            for items, values in value.items():
                items = (items.replace(" ", "")).title()
                items = (items.replace("_", " ")).title()
                values = (str(values).replace("_", " ")).title()
                collected_info = collected_info + (items + ": " + values + "\n")
        print(collected_info)  # Print to system console

        filename = "MediaInfo_" + filename[:50][:-4] + ".txt"
        if filename not in bpy.data.texts:
            bpy.data.texts.new(filename)  # New document in Text Editor
        else:
            bpy.data.texts[filename].clear()  # Clear existing text
        bpy.data.texts[filename].write(
            collected_info + chr(10)
        )  # Insert in Text Editor
        self.report({"INFO"}, "Media Info added to Text Editor")

        return {"FINISHED"}


def panel_append(self, context):  # add button
    self.layout.operator(SEQUENCE_OT_media_info_to_text_editor.bl_idname)


def register():
    bpy.types.SEQUENCER_PT_source.append(panel_append)
    bpy.utils.register_class(SEQUENCE_OT_media_info_to_text_editor)


def unregister():
    bpy.types.SEQUENCER_PT_source.remove(panel_append)
    bpy.utils.unregister_class(SEQUENCE_OT_media_info_to_text_editor)


if __name__ == "__main__":
    register()
# unregister()

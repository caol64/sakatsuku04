import ctypes
import platform
import importlib.resources
from ctypes import c_void_p, c_uint, c_ulong, c_char, c_bool


# we get the correct library extension per os
lib="libpine_c"
cur_os = platform.system()
if(cur_os == "Linux"):
    lib="libpine_c.so"
elif(cur_os == "Windows"):
    lib="libpine_c.dll"
elif(cur_os == "Darwin"):
    lib="libpine_c.dylib"


# we load the library, this will require it to be in the same folder
# refer to bindings/c to build the library.
with importlib.resources.path("sakatsuku04.libs", lib) as file_path:
    libipc = ctypes.CDLL(file_path)

libipc.pine_pcsx2_new.restype = c_void_p

libipc.pine_read.argtypes = [c_void_p, c_uint, c_char, c_bool]
libipc.pine_read.restype = c_ulong

libipc.pine_get_error.argtypes = [c_void_p]
libipc.pine_get_error.restype = c_uint

libipc.pine_pcsx2_delete.argtypes = [c_void_p]
libipc.pine_pcsx2_delete.restype = None

libipc.pine_write.argtypes = [c_void_p, c_uint, c_ulong, c_char, c_bool]
libipc.pine_write.restype = None

ipc = libipc.pine_pcsx2_new()
value = libipc.pine_read(ipc, 0x703D58, c_char(2), False)
print("Read:", value)
libipc.pine_write(ipc, 0x703D58, c_ulong(11500), c_char(6), False)
print("Error:", libipc.pine_get_error(ipc))
libipc.pine_pcsx2_delete(ipc)

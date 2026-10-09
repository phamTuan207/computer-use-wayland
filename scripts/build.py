#!/usr/bin/env python3
"""Rebuild only the local Wayland pointer; no downloads."""
from pathlib import Path
import subprocess
p=Path(__file__).resolve().parents[1]/'native'
subprocess.run(['wayland-scanner','client-header',str(p/'pointer.xml'),str(p/'pointer-protocol.h')],check=True)
subprocess.run(['wayland-scanner','private-code',str(p/'pointer.xml'),str(p/'pointer-protocol.c')],check=True)
subprocess.run(['cc','-Wall','-Wextra','-Werror','-O2','-o',str(p/'pointer'),str(p/'pointer.c'),str(p/'pointer-protocol.c'),'-lwayland-client','-lm'],check=True)
print('pointer built')

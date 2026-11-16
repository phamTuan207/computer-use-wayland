#!/usr/bin/env python3
"""Build the local Wayland pointer and session indicator; no downloads."""
from pathlib import Path
import subprocess
p=Path(__file__).resolve().parents[1]/'native'
subprocess.run(['wayland-scanner','client-header',str(p/'pointer.xml'),str(p/'pointer-protocol.h')],check=True)
subprocess.run(['wayland-scanner','private-code',str(p/'pointer.xml'),str(p/'pointer-protocol.c')],check=True)
subprocess.run(['cc','-Wall','-Wextra','-Werror','-O2','-o',str(p/'pointer'),str(p/'pointer.c'),str(p/'pointer-protocol.c'),'-lwayland-client','-lm'],check=True)
print('pointer built')
flags=subprocess.check_output(['pkg-config','--cflags','--libs','gtk4-layer-shell-0','gtk4','wayland-client'],text=True).split()
protocols=Path(subprocess.check_output(['pkg-config','--variable=pkgdatadir','wayland-protocols'],text=True).strip())
presentation=protocols/'stable/presentation-time/presentation-time.xml'
background=protocols/'staging/ext-background-effect/ext-background-effect-v1.xml'
subprocess.run(['wayland-scanner','client-header',str(background),str(p/'background-effect-protocol.h')],check=True)
subprocess.run(['wayland-scanner','private-code',str(background),str(p/'background-effect-protocol.c')],check=True)
subprocess.run(['wayland-scanner','client-header',str(presentation),str(p/'presentation-protocol.h')],check=True)
subprocess.run(['wayland-scanner','private-code',str(presentation),str(p/'presentation-protocol.c')],check=True)
subprocess.run(['cc','-Wall','-Wextra','-Werror','-O2','-o',str(p/'indicator'),str(p/'indicator.c'),str(p/'presentation-protocol.c'),str(p/'background-effect-protocol.c'),*flags,'-lm'],check=True)
print('indicator built')
subprocess.run(['wayland-scanner','client-header',str(p/'keyboard.xml'),str(p/'keyboard-protocol.h')],check=True)
subprocess.run(['wayland-scanner','private-code',str(p/'keyboard.xml'),str(p/'keyboard-protocol.c')],check=True)
subprocess.run(['cc','-Wall','-Wextra','-Werror','-O2','-o',str(p/'modifiers'),str(p/'modifiers.c'),str(p/'keyboard-protocol.c'),'-lwayland-client','-lxkbcommon'],check=True)
print('modifiers built')
# Vendored corrected wtype helper (keyboard correction): apply the pinned
# v0.4 patch in a temporary directory and build the private native/wtype.
import tempfile
_vendored = p / 'vendor' / 'wtype'
with tempfile.TemporaryDirectory(prefix='wtype-build-') as _td:
    _patched = Path(_td) / 'main.c'
    subprocess.run(['patch', '--batch', '--fuzz=0', '--output', str(_patched),
                    str(_vendored / 'main.c'),
                    str(_vendored / 'keyboard-correction.patch')], check=True)
    _wtype_flags = subprocess.check_output(
        ['pkg-config', '--cflags', '--libs', 'wayland-client', 'xkbcommon'],
        text=True).split()
    subprocess.run(['cc', '-Wall', '-Wextra', '-O2', '-I', str(p),
                    '-o', str(p / 'wtype'), str(_patched),
                    str(p / 'keyboard-protocol.c'), *_wtype_flags], check=True)
print('wtype built')

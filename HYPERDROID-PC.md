# HyperDroid PC Launcher branch

This branch replaces the previous PocketLinux direction with an Android launcher based on the Winlator execution engine.

## What this first build does

- registers as an Android HOME launcher;
- shows installed Android applications in a desktop-style grid;
- opens Windows shortcuts through Winlator;
- keeps Winlator container, Wine, Box64, DXVK/VKD3D and controller functionality;
- can open the HyperDroid Store/Aptoide package (`cm.aptoide.pt`) when it is installed;
- contains no PocketLinux, Debian desktop, XFCE, VNC or PRoot UI.

Winlator uses a minimal internal rootfs/glibc runtime. Removing that internal runtime would break Wine/Box64, so it is intentionally kept hidden as an engine implementation detail.

Upstream Winlator source: https://github.com/brunodev85/winlator

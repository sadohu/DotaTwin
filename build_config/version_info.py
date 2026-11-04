# -*- coding: utf-8 -*-
"""
Información de versión para el ejecutable de DotaTwin.
Este archivo ayuda a reducir las alertas de Windows SmartScreen.
"""

VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(3, 1, 1, 0),
        prodvers=(3, 1, 1, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    '040904B0',  # English (US)
                    [
                        StringStruct('CompanyName', 'Sadohu'),
                        StringStruct('FileDescription', 'DotaTwin - Dota 2 Configuration Manager'),
                        StringStruct('FileVersion', '3.1.1.0'),
                        StringStruct('InternalName', 'DotaTwin'),
                        StringStruct('LegalCopyright', u'© 2025 Sadohu. All rights reserved.'),
                        StringStruct('OriginalFilename', 'DotaTwin_v3.1.1.exe'),
                        StringStruct('ProductName', 'DotaTwin'),
                        StringStruct('ProductVersion', '3.1.1.0'),
                        StringStruct('Comments', 'Twin your Dota experience - Safe configuration manager for Dota 2'),
                        StringStruct('LegalTrademarks', '')
                    ]
                )
            ]
        ),
        VarFileInfo([VarStruct('Translation', [1033, 1200])])
    ]
)

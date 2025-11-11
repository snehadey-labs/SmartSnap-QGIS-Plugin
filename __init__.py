def classFactory(iface):
    from .smartsnap import SmartSnap
    return SmartSnap(iface)


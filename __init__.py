from .nens_dependency_loader import NenSDependencyLoader

def classFactory(iface):
    return NenSDependencyLoader(iface)

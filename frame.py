

# Typescript definition for Fame
# class Frame extends LicensedItem {
#   private _mechtype: MechType[]
#   private _y_pos: number
#   private _mounts: MountType[]
#   private _stats: IFrameStats
#   private _traits: FrameTrait[]
#   private _core_system: CoreSystem
class Frame:
    """Class for frame data"""
    def __init__(self):
        self.mechtype = []
        self.mounts = []
        self.stats = None
        self.traits = []
        self.core_system = None

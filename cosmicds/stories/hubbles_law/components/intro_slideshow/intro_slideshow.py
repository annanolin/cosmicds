import ipyvuetify as v
import astropy.units as u
from astropy.coordinates import SkyCoord
from traitlets import Int, Bool, Unicode
from cosmicds.utils import load_template
from cosmicds.stories.hubbles_law.utils import GALAXY_FOV
from cosmicds.stories.hubbles_law.components.exploration_tool import ExplorationTool

#theme_colors()

class IntroSlideshow(v.VuetifyTemplate):
    template = load_template("intro_slideshow.vue", __file__, traitlet=True).tag(sync=True)
    step = Int(0).tag(sync=True)
    length = Int(7).tag(sync=True)
    dialog = Bool(False).tag(sync=True)
    currentTitle = Unicode("").tag(sync=True)
    exploration_complete = Bool(False).tag(sync=True)
    intro_complete = Bool(False).tag(sync=True)

    _titles = [
        "Hubble Data Story",
        "1920's Astronomy",
        "Explore the Night Sky",
        "What Are Nebulae?",
        "Spiral Nebulae",
        "Henrietta Leavitt's Discovery",
        "Vesto Slipher and Spectra"
    ]
    _default_title = "Hubble Data Story"

    def __init__(self, *args, **kwargs):
        exploration_tool = ExplorationTool()
        exploration_tool2 = ExplorationTool()
        exploration_tool3 = ExplorationTool()
        self.components = {
            'c-exploration-tool': exploration_tool,
            'c-exploration-tool2': exploration_tool2,
            'c-exploration-tool3': exploration_tool3
        }
        self.currentTitle = self._default_title

        def update_title(change):
            index = change["new"]
            if index in range(len(self._titles)):
                self.currentTitle = self._titles[index]
            else:
                self.currentTitle = self._default_title

        self.observe(update_title, names=["step"])

        def update_exploration_complete(change):
            self.exploration_complete = change["new"]
        exploration_tool.observe(update_exploration_complete, names=["exploration_complete"])

        super().__init__(*args, **kwargs)

    def go_to_location(self, wwt_label, args):
        wwt = self.components[wwt_label].widget
        coordinates = SkyCoord(args["ra"] * u.deg, args["dec"] * u.deg, frame='icrs')
        instant = args.get("instant") or False
        fov_as = args.get("fov", None)
        fov = fov_as * u.arcsec if fov_as else GALAXY_FOV
        wwt.center_on_coordinates(coordinates, fov=fov, instant=instant)

    def vue_go_to_location_tool2(self, args):
        self.go_to_location('c-exploration-tool2', args)

    def vue_go_to_location_tool3(self, args):
        self.go_to_location('c-exploration-tool3', args)
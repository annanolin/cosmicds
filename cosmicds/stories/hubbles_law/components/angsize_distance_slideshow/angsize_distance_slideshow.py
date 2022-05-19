import ipyvuetify as v
from pathlib import Path
from traitlets import Int, Bool, Unicode, List
from cosmicds.utils import load_template
from glue_jupyter.state_traitlets_helpers import GlueState


# theme_colors()

class Angsize_SlideShow(v.VuetifyTemplate):
    template = load_template(
        "angsize_distance_slideshow.vue", __file__, traitlet=True).tag(sync=True)
    step = Int(0).tag(sync=True)
    length = Int(13).tag(sync=True)
    dialog = Bool(False).tag(sync=True)
    currentTitle = Unicode("").tag(sync=True)
    state = GlueState().tag(sync=True)
    max_step_completed = Int(0).tag(sync=True)
    interact_steps = List([7, 9]).tag(sync=True)
    #exploration_complete = Bool(False).tag(sync=True)
    #intro_complete = Bool(False).tag(sync=True)

    _titles = [
        "1920's Astronomy",
        "1920's Astronomy",
        "How can we know how far away something is?",
        "How can we know how far away something is?",
        "How can we know how far away something is?",
        "How can we know how far away something is?",
        "Galaxy Distances",
        "Galaxy Distances",
        "Galaxy Distances",
        "Galaxy Distances",
        "Galaxy Distances",
        "Galaxy Distances",        
        "Galaxy Distances"
    ]
    _default_title = "1920's Astronomy"

    def __init__(self, story_state, *args, **kwargs):
        self.state = story_state
        self.currentTitle = self._default_title

        def update_title(change):
            index = change["new"]
            if index in range(len(self._titles)):
                self.currentTitle = self._titles[index]
            else:
                self.currentTitle = self._default_title

        self.observe(update_title, names=["step"])

        super().__init__(*args, **kwargs)
<template>
  <span>
    <slot>
      <v-icon
        @click="speak"
      >
        {{ speaking ? 'mdi-stop' : 'mdi-voice' }}
      </v-icon>
    </slot>
  </span>
</template>

<script>
module.exports = {
  props: {
    selectors: {
      type: Array,
      default: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', ':not(mjx-assistive-mml) > mjx-container']
    },
    stopOnClose: {
      type: Boolean,
      default: true
    },
    root: {
      type: [Object, Function],
      default: null
    }
  },
  data: function () {
    return {
      speaking: false,
      intervalID: 0,
      rootElement: null,
      iconNameMap: {
        'cached': 'reset'
      }
    };
  },
  destroyed() {
    if (this.stopOnClose && this.speaking) {
      clearInterval(this.intervalID);
      window.speechSynthesis.cancel();
    }
  },
  methods: {
    elementText(element) {

      // Replace any MDI icons with text representing their name
      const clone = element.cloneNode(true);
      const mdiPrefix = "mdi-";
      const icons = clone.querySelectorAll(`[class*='${mdiPrefix}']`);
      icons.forEach(icon => {
        const classes = [...icon.classList].filter(cls => cls.startsWith(mdiPrefix));
        if (classes.length === 0) {
          icon.remove();
        } else {
          const txt = document.createElement("text");
          const cls = classes[0];
          let iconName = cls.slice(mdiPrefix.length);
          txt.textContent = this.iconNameMap[iconName] ?? iconName.replace("-", " ");
          icon.parentNode?.replaceChild(txt, icon);
        }
      });

      // Replace any MathJax with its semantic speech text
      if (clone.tagName === "mjx-container") {
        const speechText = clone.getAttribute("aria-label");
        if (speechText) {
          const txt = document.createElement("text");
          txt.textContent = speechText;
          clone.parentNode?.replaceChild(txt, clone);
        } else {
          clone.remove();
        }
      }

      return clone.textContent.trim();

    },
    makeUtterance(text) {
      const utterance = new SpeechSynthesisUtterance(text);

      // The interval is to work around this issue:
      // https://bugs.chromium.org/p/chromium/issues/detail?id=679437
      //
      // We could just use one interval for the entire block of text items
      // but the pause-resume is sometimes slightly audible, so better to minimize that.
      // Note that the pause-resume won't happen if the text takes longer than 14 seconds to say
      utterance.onstart = (_event) => {
        this.intervalID = setInterval(() => {
          window.speechSynthesis.pause();
          window.speechSynthesis.resume();
        }, 14000);
      }
      utterance.onend = (_event) => {
        clearInterval(this.intervalID);
      }

      return utterance;
    },
    findRootElement() {
      if (this.root instanceof Element) {
        this.rootElement = this.root;
      } else if (this.root instanceof Function) {
        this.rootElement = this.root();
      } else {
        this.rootElement = this.$parent.$el;
      }
    },
    
    // Taken from https://www.geeksforgeeks.org/how-to-check-if-an-element-is-visible-in-dom/
    // TODO: Is there a better way to check?
    //
    // Note that element.checkVisibility() doesn't work on Safari:
    // https://caniuse.com/mdn-api_element_checkvisibility
    isElementVisible(element) {
      return element.offsetWidth || 
             element.offsetHeight || 
             element.getClientRects().length;
    },
    getSpeechItems() {
      if (this.rootElement === null) {
        this.findRootElement();
      }
      const selectedElements = this.rootElement.querySelectorAll(this.selectors.join(","));
      const elements = [].concat(...selectedElements).filter(this.isElementVisible);
      const items = elements.map(element => this.elementText(element)).filter(text => text.length > 0);
      return items;
    },
    speak() {
      const synth = window.speechSynthesis;
      if (synth.speaking) {
        synth.cancel();
        if (this.speaking) {
          clearInterval(this.intervalID);
          this.speaking = false;
          return;
        }
      } else {
        this.speaking = false;
      }

      // We say each speech item as its own utterance
      // This gives a nice pause between paragraphs
      this.speaking = true;
      const items = this.getSpeechItems();
      const utterances = items.map(this.makeUtterance);
      const lastUtterance = utterances[utterances.length - 1];
      const lastOnEnd = lastUtterance.onend;
      utterances[utterances.length - 1].onend = (event) => {
        lastOnEnd(event);
        this.speaking = false;
      }
      utterances.forEach((utterance) => synth.speak(utterance));
    }
  }
}
</script>

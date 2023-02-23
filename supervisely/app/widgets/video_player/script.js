Vue.component("html-video", {
  props: ["time_to_set", "url", "mime_type", "is_playing", "mask_path"],
  template: `
<div style="position: relative;">
    <video ref="video"
        width="100%"
        height="auto"
        controls
        @timeupdate="$emit('timeupdate', $refs['video'].currentTime)"
        @play="$emit('update:is_playing', true)"
        @pause="$emit('update:is_playing', false)"
    >
        <source ref="video-data" :src="url" :type="mime_type">
    </video>
    <div v-if="mask_path"
        ref="mask"
        style="
            opacity: 0.4;
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            pointer-events: none;
            background-size: contain;
        " 
        :style="overlayStyle">
    </div>
</div>
`,
  computed: {
    overlayStyle() {
      return {
        backgroundImage: `url("${this.mask_path}")`,
      };
    },
  },
  watch: {
    time_to_set(time) {
      if (Number.isFinite(time)) {
        this.$refs["video"].currentTime = time;
        this.$emit("update:time_to_set", null);
      }
    },
    url: {
      handler() {
        this.update_video_src();
      },
      immediate: true,
    },
    mime_type: {
      handler() {
        this.update_video_src();
      },
      immediate: true,
    },
    is_playing: {
      handler(value) {
        this.play_pause(value);
      },
    },
  },
  mounted() {
    if (this.is_playing) {
      this.$emit("update:is_playing", false);
    }
  },
  methods: {
    update_video_src() {
      const video = this.$refs["video"];
      const source = this.$refs["video-data"];

      if (!this.url || !this.mime_type || !video) {
        return;
      }
      video.pause();
      source.setAttribute("src", this.url);
      source.setAttribute("type", this.mime_type);
      video.load();
    },
    play_pause() {
      const video = this.$refs["video"];
      if (!video) {
        return;
      }
      this.is_playing ? video.play() : video.pause();
    },
  },
});

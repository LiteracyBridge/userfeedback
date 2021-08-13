<template>
  <div>
  <button @click="setupModal" class="button">Instructions</button>
  <div id="modal" >
    <transition name="fade" appear>
      <div class="modal-overlay" v-if="showModal" @click="showModal = false"/>
    </transition>
    <transition name="pop" appear>
      <div class="modal" role="dialog" v-if="showModal">
        <h1>Instructions</h1>
        <p>This page is composed of two parts: an audio player and a data entry form.</p>   
        <h2>Controlling the Audio Player </h2>
        <p>A new audio file is loaded each time the page is refreshed or the form is submitted. Use the following keys to play/pause, quickly move forward and backward, change speed, 
          and loop a section of audio to help with transcription:</p>
        <table>
          <tr>
            <th>Play/Pause:</th><td><span class="keybig">P</span></td>
            <th>Faster</th><td><span class="keybig">F</span></td>
            <th>Slower</th><td><span class="keybig">S</span></td>
          </tr>
          <tr>
            <th>Ahead 10s:</th><td><span class="keybig">&#8594;</span></td>
            <th>Back 10s:</th><td><span class="keybig">&#8592;</span></td>
            <th>Back 5s:</th><td><span class="keybig">/</span></td>
          </tr>
          <tr>
            <th>Set Loop Start</th><td><span class="keybig"> [ </span></td>
            <th>Set Loop End</th><td><span class="keybig"> ] </span></td>
            <th>Stop Loop</th><td><span class="keybig"> \ </span></td>
          </tr>
        </table>
        <h2>Moving Around the Form</h2>
        <p>You can also use the keyboard to move around, enter, and submit your data.</p>
        <table>
          <tr>
            <th>Control Audio Player:</th><td><span class="keybig">{esc}</span></td>
            <th>Next Quetion:</th><td><span class="keybig">{tab}</span></td>
            <th>Prev Question:</th><td><span class="keybig">{shift}</span> <span class="keybig">{tab}</span></td>
          </tr>
          <tr>
            <th>Click a Button:</th><td><span class="keybig">{space}</span> or <span class="keybig">{enter}</span></td>
            <th>Choose Option:</th><td><span class="keybig">{up/down}</span></td>
            <th>Select a Box:</th><td><span class="keybig">{tab}</span> and <span class="keybig">{space}</span></td>
          </tr>
        </table>
        <button @click="showModal = false" tabindex="0" ref="closeModal" class="button">Close</button>
      </div>
    </transition>
  </div>
  </div> 
</template>

<script>
export default {
  name: "Instructions",
  data() {
    return {
      showModal: false    
    }
  },
  methods: {
    escape() {
      if (this.showModal) {
        this.showModal = false;
      }
    },
    setupModal() {
      this.showModal = true;
      this.$nextTick(() => {
        this.$refs.closeModal.focus();
      })
    } 
  }
}
</script>

<style scoped>

</style>
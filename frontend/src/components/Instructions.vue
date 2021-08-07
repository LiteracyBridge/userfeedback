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
.modal {
  position: absolute;
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  margin: auto;
  text-align: center;
  width: fit-content;
  height: fit-content;
  max-width: 60em;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 5px 5px rgba(0, 0, 0, 0.2);
  background: #FFF;
  z-index: 999;
  transform: none;
}
.modal h1 {
  margin: 0 0 1rem;
}

.modal-overlay {
  content: '';
  position: absolute;
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 998;
  background: #2c3e50;
  opacity: 0.6;
  cursor: pointer;
}

/* ---------------------------------- */
.fade-enter-active,
.fade-leave-active {
  transition: opacity .4s linear;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.pop-enter-active,
.pop-leave-active {
  transition: transform 0.4s cubic-bezier(0.5, 0, 0.5, 1), opacity 0.4s linear;
}

.pop-enter,
.pop-leave-to {
  opacity: 0;
  transform: scale(0.3) translateY(-50%);
}
</style>
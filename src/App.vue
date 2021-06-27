<template>
  <div id="app" ref="top" @keydown.esc="escape">
    <img alt="Amplio logo" src="./assets/logo.png" width="256" height="40" />

    <div id="modal">
      <p>{{signedIn}}</p>
      <p>{{user_email}}</p>
      <button @click="setupModal" class="button">Click for Instructions</button>
      <transition name="fade" appear>
        <div class="modal-overlay" 
            v-if="showModal" 
            @click="showModal = false"></div>
      </transition>
      <transition name="pop" appear>
        <div class="modal" role="dialog" v-if="showModal">
          <h1>Instructions</h1>
          <p>This page is composed of two parts: an audio player and a data entry form. <span style="font-style:italic; color:red">It does not yet save any data.</span></p>   
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
          <button @click="showModal = false" ref="closeModal" class="button">Close</button>
        </div>
      </transition>
    </div>


    <div id="modalsubmit">
      <transition name="fade" appear>
        <div class="modal-overlay" v-if="showSubmitModal"></div>
      </transition>
      <transition name="pop" appear>
        <div class="modal" role="dialog" v-if="showSubmitModal">
          <h1>Submitted!</h1>
        </div>
      </transition>
    </div>



    <latest-audio ref="audio" />
    <div>
      <table style="text-align:left ">
        <tr>
          <td colspan="2" style="align: middle">
            <button type="button" class="button_warning" @click="handleSubmit">
            Mark as "Not Feedback"
            </button>
          </td>
        </tr>
        <tr>
          <td colspan="2"> 
            <p>Transcription</p>
            <textarea width="100%"
              id="transcripton"
              name="transcription"
              rows="5" 
              v-model="transcription"
            />
          </td>
        </tr>
        <td class="pad">
          <p class="question">Is the person speaking offering a...</p>
          <input
            type="radio"
            name="sentiment"
            id="comment"
            value="comment"
            v-model="sentiment"
          />
          <label for="comment">Comment</label>
          <br />
          <input
            type="radio"
            name="sentiment"
            id="complaint"
            value="complaint"
            v-model="sentiment"
          />
          <label for="complaint">Complaint</label>
          <br />
          <input
            type="radio"
            name="sentiment"
            id="endorsement"
            value="endorsement"
            v-model="sentiment"
          />
          <label for="endorsement">Endorsement</label>
          <br />
          <input
            type="radio"
            name="sentiment"
            id="question"
            value="question"
            v-model="sentiment"
          />
          <label for="question">Question</label>
          <br />
          <input
            type="radio"
            name="sentiment"
            id="suggestion"
            value="suggestion"
            v-model="sentiment"
          />
          <label for="suggestion">Suggestion</label>
        </td>
        <td class="pad">
          <p class="question">Is a child protection issue discussed?</p>
          <input type="radio" name="cp" id="cp-yes" value="yes" v-model="cp" />
          <label for="cp-yes">Yes</label>
          <br />
          <input type="radio" name="cp" id="cp-no" value="no" v-model="cp" />
          <label for="cp-no">No</label>
          <br />
          <input type="radio" name="cp" id="cp-maybe" value="maybe" v-model="cp" />
          <label for="cp-maybe">Maybe / Unsure</label>
        </td>
        <tr>
          <td class="pad">
            <p class="question">What is the topic of the message?</p>
            <input
              type="radio" name="topic"
              id="diarrhea"
              value="diarrhea"
              v-model="topic"
            />
            <label for="diarrhea">Diarrhea Management</label>
            <br />
            <input type="radio" name="topic" id="malaria" value="malaria" v-model="topic" />
            <label for="malaria">Malaria Prevention</label>
            <br />
            <input
              type="radio" name="topic"
              id="handwashing"
              value="handwashing"
              v-model="topic"
            />
            <label for="handwashing">Handwashing</label>
            <br />
            <input
              type="radio" name="topic"
              id="delivery"
              value="delivery"
              v-model="topic"
            />
            <label for="delivery">Safe Delivery</label>
            <br />
            <input
              type="radio" name="topic"
              id="breastfeeding"
              value="breastfeeding"
              v-model="topic"
            />
            <label for="breastfeeding">Breastfeeding</label>
          </td>
          <td class="pad">
            <p class="question">What sub-topics are discussed?</p>
            <div v-if="topic=='diarrhea'">
            <input type="checkbox" name="subtopics" id="ors" value="ors" v-model="subtopics">
            <label for="ors">ORS</label><br/>
            <input type="checkbox" name="subtopics" id="zinc" value="zinc" v-model="subtopics">
            <label for="zinc">Zinc</label><br/>
            <input type="checkbox" name="subtopics" id="diarrhea" value="diarrhea" v-model="subtopics">
            <label for="diarrhea">Signs of Diarrhea</label><br/>
            <input type="checkbox" name="subtopics" id="feeding" value="feeding" v-model="subtopics">
            <label for="feeding">Feeding and Drinking</label><br/>
            <br>
            </div>
            <div v-else-if="topic=='malaria'">
            <input type="checkbox" name="subtopics" id="llin" value="llin" v-model="subtopics">
            <label for="llin">LLINs</label><br/>
            <input type="checkbox" name="subtopics" id="signs" value="signs" v-model="subtopics">
            <label for="signs">Signs and Symptoms</label><br/>
            <input type="checkbox" name="subtopics" id="myths" value="myths" v-model="subtopics">
            <label for="myths">Myths about Malaria</label><br/>
            <input type="checkbox" name="subtopics" id="water" value="water" v-model="subtopics">
            <label for="water">Hygiene and Sitting Water</label><br/>
            <br>
            </div>
            <div v-else-if="topic=='handwashing'">
            <input type="checkbox" name="subtopics" id="tippy" value="tippy" v-model="subtopics">
            <label for="tippy">Use of a Tippy-Tap</label><br/>
            <input type="checkbox" name="subtopics" id="soap" value="soap" v-model="subtopics">
            <label for="soap">Buying vs. Making Soap</label><br/>
            <input type="checkbox" name="subtopics" id="technique" value="technique" v-model="subtopics">
            <label for="technique">Handwashing Technique</label><br/>
            <input type="checkbox" name="subtopics" id="when" value="when" v-model="subtopics">
            <label for="when">Times for Handwashing</label><br/>
            <br>
            </div>
            <div v-else-if="topic=='delivery'">
            <input type="checkbox" name="subtopics" id="skilled" value="skilled" v-model="subtopics">
            <label for="skilled">Use of Skilled Attendants</label><br/>
            <input type="checkbox" name="subtopics" id="ANC" value="ANC" v-model="subtopics">
            <label for="ANC">Importance of ANC</label><br/>
            <input type="checkbox" name="subtopics" id="dangersigns" value="dangersigns" v-model="subtopics">
            <label for="dangersigns">When to Call a Doctor</label><br/>
            <input type="checkbox" name="subtopics" id="planning" value="planning" v-model="subtopics">
            <label for="planning">Planning for Delivery</label><br/>
            <br>
            </div>
            <div v-else-if="topic=='breastfeeding'">
            <input type="checkbox" name="subtopics" id="nofood" value="nofood" v-model="subtopics">
            <label for="nofood">No Food or Water for 6 Months</label><br/>
            <input type="checkbox" name="subtopics" id="nutrition" value="nutrition" v-model="subtopics">
            <label for="nutrition">Best Foods after 6 Months</label><br/>
            <input type="checkbox" name="subtopics" id="colostrum" value="colostrum" v-model="subtopics">
            <label for="colostrum">First Breastmilk (Colostrum)</label><br/>
            <input type="checkbox" name="subtopics" id="latching" value="latching" v-model="subtopics">
            <label for="latching">Problems with Latching</label><br/>
            <br>
            </div>
          </td>
        </tr>
        <tr>
          <td class="pad">
            <p class="question">Does this recording prompt any action?</p>
            <input type="checkbox" name="action" id="action-msg" value="message" v-model="actions"/>
            <label for="action-msg">Answer question in a future message</label><br/>
            <input type="checkbox" name="action" id="action-guide" value="guidance" v-model="actions"/>
            <label for="action-guide">Provide guidance to community facilitator</label><br/>
            <input type="checkbox" name="action" id="action-clarify" value="clarify" v-model="actions"/>
            <label for="action-clarify">Clarify a confusing message</label><br/>
            <label for="action-other">Other: </label>
            <input type="text" class="text_input" name="otherAction" id="otherAction" v-model="otherAction"/>
          </td>
          <td style="vertical-align: middle">
            <br/>
            <input type="button" class="button_submit" value="SUBMIT" @click="handleSubmit"/>
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script>
import { Auth } from 'aws-amplify';
import LatestAudio from "./components/LatestAudio.vue";

export default {
  name: "App",
  components: {
    LatestAudio,
  },
  data() {
    return {
      signedIn: false,
      user_email:"",
      showModal: false,
      showSubmitModal: false,
      sentiment: "",
      transcription: "",
      cp: "",
      topic: "",
      subtopics: [],
      actions:[],
      otherAction:''
    };
  },
  methods: {
    async isUserSignedIn() {
      try {
          const userObj = await Auth.currentAuthenticatedUser();
          this.user_email=userObj['attributes']['email'];
          this.signedIn = true;
      }
      catch (err) {
          this.signedIn = false;
          console.log(err);
          }
    },  
    handleSubmit() {
      //Submit values somewhere
      this.showSubmitModal = true;

      //there's got to be an easier way! but form.reset() didn't do it
      this.sentiment='';
      this.transcription='';
      this.cp='';
      this.topic='';
      this.subtopics=[];
      this.actions=[];
      this.otherAction='';
      console.log("try to call updateUrl");
      this.$refs.audio.updateUrl();
      setTimeout(()=> {
        this.showSubmitModal = false;
      },1000);
    },
    escape() {
      if (this.showModal) {
        this.showModal = false;
      }
      this.$refs.audio.setAudioFocus();
    },
    setupModal() {
      this.showModal = true;
      this.$refs.closeModal.focus();
    }
  },
  created() {
    this.isUserSignedIn();
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

textarea {
	-webkit-box-sizing: border-box;
	-moz-box-sizing: border-box;
	box-sizing: border-box;
	width: 100%;
}
table {
  margin-left: auto;
  margin-right: auto;
}
td.pad {
  padding: 15px;
  padding-top: 0px;
  padding-left: 0px;
  vertical-align: top;
}

.key {
  font-weight:bold;
  padding: 0px;
  background: #e7e8e9;
  font-size: 1.0em;
}

.keybig {
  font-weight:bold;
  padding: 1px;
  background: #e7e8e9;
  font-size: 1.1em;
}

th {
  text-align: right;
  border-bottom: 1px solid #ddd;
}

td {
  padding: 3px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

ul {
  list-style-type: none;
}

.text_input {
  border-color: transparent;
  border-bottom: 2px solid;
  outline:none;
}

.question {
  font-weight:bold;
}

/* For Modal */
html {
  height: 100%;
  background: #FFF;
  color: #000;
  font-size: 62.5%;
}

body {
  min-height: 100%;
  margin: 0;
  display: grid;
  place-items: center;
  font-size: 1.4rem;
}

.button {
  border: none;
  color: #FFF;
  background: #2629c0;
  appearance: none;
  font: inherit;
  font-size: 1.2rem;
  padding: .5em 1em;
  border-radius: .3em;
  cursor: pointer;
  margin: 15px;
}

.button_warning {
  border: none;
  color: #FFF;
  background: #ac2121;
  appearance: none;
  font: inherit;
  font-size: 1.2rem;
  padding: .5em 1em;
  border-radius: .3em;
  cursor: pointer;
}


.button_submit {
  border: none;
  color: #FFF;
  background: #23b60f;
  appearance: none;
  font: inherit;
  font-size: 1.2rem;
  padding: .5em 1em;
  border-radius: .3em;
  cursor: pointer;
  margin: 40px;
}

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
 
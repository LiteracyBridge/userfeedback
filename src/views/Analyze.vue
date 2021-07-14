<template>
<div width="100%"  @keydown.esc="escape" >
<div width="100%" class="navbar">
  <span>AMPLIO</span>
  <span>Analysis</span>
  <span>
    <select v-model="selectedProgramCode" @change="newProgram">
      <option v-for="program in programs" :value="program.code" :key="program.code">
        <span> {{program.name}}</span>
      </option>
    </select>
    <a @click="logout">Logout</a>
  </span>
</div>
<div id="modal" >
  <transition name="fade" appear>
    <div class="modal-overlay" 
        v-if="showModal" 
        @click="showModal = false"></div>
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

<table width="600">
  <tr  v-if="!connected"><td style="color:red; font-size:1.5em; font-weight:bolder; text-align:center; padding: 0px">
     No Connection!
  </td></tr>
  <tr><td style="text-align:center">
  </td></tr>
  <tr  style="padding: 0px">
    <td  style="padding: 0px">
      <table width="100%" style="padding: 0px">
        <tr>
          <td>
            Deployment <select v-model="selectedDeployment" @change="loadQuestions">
              <option v-for="deployment in deployments" :value="deployment" :key="deployment">
                <span> {{deployment}}</span>
              </option>
            </select>
          </td>
          <td>
            Language <select v-model="selectedLanguageCode" @change="loadQuestions">
              <option v-for="language in languages" :value="language.code" :key="language.code">
                <span> {{language.name}}</span>
              </option>
            </select>
          </td>
          <td style="float:right;padding: 0px">
              <button @click="setupModal" class="button">Instructions</button>
          </td>
        </tr>
      </table>      
    </td>
  </tr>
  <tr><td>
      <latest-audio @network="updateConnected" @handleUseless="handleUseless" ref="audio" :userEmail="this.$route.query.email" :deployment="selectedDeployment" :program="selectedProgramCode" :language="selectedLanguageCode"/>
  </td></tr>
  <tr><td>
      <div ref="top">
        Feedback Form
        <table width="100%" style="text-align:left;border: 2px solid #ddd;padding: 5px"">
          <tr v-for="(question,count) in questions" :key="question.id">
              <td class="pad">
                  <p class="question">{{count+1}}. {{question.question_label}}
                      <span v-if="question.required" style="color: red">*</span>   
                  </p>
                  <div v-if="question.type=='textarea'">
                    <textarea width="100%" rows="5" :name="question.name" v-model="form.responses[question.data]"/>
                  </div>
                  <div v-for="choice in question.choices" :key="choice.choice_id">
                      <input @click="uncheckSubChoices(choice.data)" :type="question.type" :name="question.name" :id="choice.choice_id" :ref="choice.choice_id" :value="choice.value" v-model="form.responses[question.data]" />
                      <label :for="choice.choice_id">{{choice.choice_label}}</label>
                      <span v-if="choice.data_other">
                          <input type="text" class="text_input" name="question.name+'other'" id="choice.choice_id+'other'" v-model="form.responses[choice.data_other]"/>
                      </span>
                      <br />
                      <div  v-if="choice.choices && String(form.responses[question.data]).includes(choice.value)">
                        <label>{{choice.question_label}}</label><span v-if="choice.required" style="color: red">*</span>   
                        <div v-for="subchoice in choice.choices" :key="subchoice.choice_id" style="text-indent: 20px">
                            <input :type="choice.type" :name="choice.name" :id="choice.question_id" :value="subchoice.value" v-model="form.responses[choice.data]"/>
                            <label :for="subchoice.id">{{subchoice.choice_label}}</label>
                            <span v-if="subchoice.data_other">
                                <input type="text" class="text_input" name="choice.name+'other'" id="subchoice.choice_id+'other'" v-model="form.responses[subchoice.data_other]"/>
                            </span>                    
                        </div>
                      </div>
                  </div>
              </td>
          </tr>
          <tr>
            <td style="text-align: right">
              <input type="button" class="button_submit" value="SUBMIT" @click="handleSubmit"/>
            </td>
          </tr>
        </table>
      </div>
    </td></tr>
  </table>
  <p>Need help? Contact us at support@amplio.org</p>

  <!-- <p>Responses:<br/>{{JSON.stringify(form.responses)}}</p> -->
  <!-- <p>Questions:<br/>{{JSON.stringify(questions)}}</p> -->
  </div>
</template>

<script>
import LatestAudio from "../components/LatestAudio.vue";
//import Question from "../components/Question.vue";
import { Auth } from 'aws-amplify';

//TODO: Code for axios copied from LatestAudio.vue.  Could all axios call be put somewhere else for both components to call?
import axios from 'axios'
import Vue from 'vue'
import VueAxios from 'vue-axios'
Vue.use(VueAxios,axios)

export default {
  name: "Home",
  components: {
    LatestAudio   //,Question
  },
  data() {
    return {
      connected: true,
      showModal: false,
      showSubmitModal: false,
      questions: [],
    form: {
        uuid: '',
        user_email: '',
        useless: false,
        responses: {
          // explicity list keys that need to be arrays for multiple responses
          resp_01:[],
          resp_02:[],
          resp_03:[],
          resp_04:[],
          resp_05:[],
          resp_06:[],
          resp_07:[],
          resp_08:[],
          resp_09:[],
          resp_10:[],
          resp_11:[],
          resp_12:[],
          resp_13:[],
          resp_14:[],
          resp_15:[],
          resp_16:[],
          resp_17:[],
          resp_18:[],
          resp_19:[],
          resp_20:[]
         }
      },
      programs: [{
        code:"CARE-ETH-GIRLS",
        name:"CARE Ethiopia Girls",
        languages:[{
          code:"aar",
          name:"Afar af"
        }],
        deployments:[1]
      },{
        code:"CARE-ETH-BOYS",
        name:"CARE Ethiopia Boys",
        languages:[{
          code:"aar",
          name:"Afar af"
        },{
          code:"en",
          name:"English"
        }],
        deployments:[1,2]
      }],
      selectedProgramCode:"CARE-ETH-GIRLS",
      selectedDeployment:1,
      selectedLanguageCode:"aar"
    }
  },
  methods: {
    async logout() {
      try {
          await Auth.signOut();
          this.$router.push('Login');
      } catch (error) {
          alert(error.message);
      }
    },
    updateConnected(isConnected) {
      this.connected = isConnected;
    },
    uncheckSubChoices(responsecode) {
      if(responsecode) {
        //console.log(responsecode);
        var a = this.form.responses[responsecode]=[];
      }
    },
    handleUseless() {
      this.form.useless = true;
      this.handleSubmit();
    },
    handleSubmit() {
      //First, add UUID and email to the form data before we submit it.
      this.form.user_email = this.$route.query.email;
      this.form.uuid = this.$refs.audio.getUUID();

      //Submit values somewhere
      //const action = "https://b71ce224-55b2-4565-b217-0a98ed7fbea6.mock.pstmn.io";
      const action = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufProcess";      
      Vue.axios.post(action,this.form, {headers: {'Authorization': `${this.$token}`}})
      .then(response=>{
          console.log(response.data);
          //TODO: What if Lambda function says it wasn't submitted properly
          //this.audioMetadata = response.data;
          //this.url=this.audioMetadata.url;
          //this.filename = unescape(this.url.substring(this.url.lastIndexOf('/')+1)); 
          //this.fullyLoaded = false;
          //this.$refs.audio.load();
          //this.setAudioFocus();
          this.showSubmitModal = true;
      })
      .catch (err => {
          //TODO: what if network just went away before hitting submit - is data lost? can it retry?
          console.log(err);
          this.connected = false;
      });

      //there's got to be an easier way! but form.reset() didn't do it
      this.form.uuid = '';
      this.form.useless = false;
      this.form.responses.transcription='';
      this.form.responses.resp_01=[];
      this.form.responses.resp_02=[];
      this.form.responses.resp_03=[];
      this.form.responses.resp_04=[];
      this.form.responses.resp_05=[];
      this.form.responses.resp_06=[];
      this.form.responses.resp_07=[];
      this.form.responses.resp_08=[];
      this.form.responses.resp_09=[];
      this.form.responses.resp_10=[];
      this.form.responses.resp_11=[];
      this.form.responses.resp_12=[];
      this.form.responses.resp_13=[];
      this.form.responses.resp_14=[];
      this.form.responses.resp_15=[];
      this.form.responses.resp_16=[];
      this.form.responses.resp_17=[];
      this.form.responses.resp_18=[];
      this.form.responses.resp_19=[];
      this.form.responses.resp_20=[];

      this.sentiment='';
      this.transcription='';
      this.cp='';
      this.topic='';
      this.subtopics=[];
      this.actions=[];
      this.otherAction='';

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
      if (this.$refs.closeModal) {
        this.$refs.closeModal.focus();
      }
    },
    newProgram() {
      this.selectedLanguageCode = this.languages[0].code;
      this.selectedDeployment = this.deployments[0];
      this.loadQuestions();
    },
    loadQuestions() {
      //const original = '[{"id":"1","question_label":"Is the person speaking an adult or child?","name":"adult_child","type":"radio","data":"resp_01","required":false,"choices":[{"choice_id":"11","choice_label":"Adult","value":"adult"},{"choice_id":"12","choice_label":"Child","value":"child"},{"choice_id":"13","choice_label":"Unsure","value":"unsure"}]},{"id":"2","question_label":"Is the person speaking male or female?","name":"gender","type":"radio","data":"resp_02","required":false,"choices":[{"choice_id":"21","choice_label":"Male","value":"male"},{"choice_id":"22","choice_label":"Female","value":"female"},{"choice_id":"23","choice_label":"Unsure","value":"unsure"}]},{"id":"3","question_label":"Is the person speaking offering a...","name":"sentiment","type":"radio","data":"resp_03","required":true,"choices":[{"choice_id":"31","choice_label":"Comment","value":"comment"},{"choice_id":"32","choice_label":"Complaint","value":"complaint"},{"choice_id":"33","choice_label":"Endorsement","value":"endorsement"},{"choice_id":"34","choice_label":"Question","value":"question"},{"choice_id":"35","choice_label":"Suggestion","value":"suggestion"},{"choice_id":"36","choice_label":"Unsure","value":"unsure"}]},{"id":"10","question_label":"What is the topic of the message?","name":"topic","type":"checkbox","data":"resp_10","required":true,"choices":[{"id":"100","choice_label":"Diarrhea Management","value":"diarrhea","question_label":"Select subtopic(s)","type":"checkbox","name":"diarrhea","data":"resp_11","required":true,"choices":[{"choice_id":"101","choice_label":"ORS","value":"ors"},{"choice_id":"102","choice_label":"Zinc","value":"zinc"},{"choice_id":"103","choice_label":"Signs of Diarrhea","value":"signs"},{"choice_id":"104","choice_label":"Feeding and Drinkin","value":"feeding"}]},{"id":"110","choice_label":"Malaria Prevention","value":"malaria","question_label":"Select subtopic(s)","name":"malaria","type":"checkbox","data":"resp_12","required":true,"choices":[{"choice_id":"111","choice_label":"LLINs","value":"llins"},{"choice_id":"112","choice_label":"Signs and Symptoms","value":"signs"},{"choice_id":"113","choice_label":"Myths about Malaria","value":"myths"},{"choice_id":"114","choice_label":"Hygiene and Sitting Water","value":"hygiene"}]},{"id":"120","choice_label":"Handwashing","value":"handwashing","question_label":"Select subtopic(s)","type":"checkbox","name":"handwashing","data":"resp_13","required":true,"choices":[{"choice_id":"121","choice_label":"Use of a Tippy-Tap","value":"tippytap"},{"choice_id":"122","choice_label":"Buying vs. Making Soap","value":"makingsoap"},{"choice_id":"123","choice_label":"Handwashing Technique","value":"technique"},{"choice_id":"124","choice_label":"Times for Handwashing","value":"times"}]},{"id":"130","choice_label":"Safe Delivery","value":"delivery","question_label":"Select subtopic(s)","type":"checkbox","name":"delivery","data":"resp_14","required":true,"choices":[{"choice_id":"131","choice_label":"Use of SBAs","value":"sba"},{"choice_id":"132","choice_label":"Importance of ANC","value":"anc"},{"choice_id":"133","choice_label":"When to Call a Doctor","value":"calldoctor"},{"choice_id":"134","choice_label":"Planning for Delivery","value":"planning"}]},{"id":"140","choice_label":"Breastfeeding","value":"breastfeeding","question_label":"Select subtopic(s)","type":"checkbox","name":"breastfeeding","data":"resp_15","required":true,"choices":[{"choice_id":"141","choice_label":"No food or water for 6 months","value":"nofood6mos"},{"choice_id":"142","choice_label":"Introduction of solid foods","value":"solidfood"},{"choice_id":"143","choice_label":"First breastmilk","value":"firstmilk"},{"choice_id":"144","choice_label":"Problems with latching","value":"latching"}]}]},{"id":"4","question_label":"Is a child protection issue discussed?","name":"cp","type":"radio","data":"resp_04","required":true,"choices":[{"choice_id":"41","choice_label":"Yes","value":"yes"},{"choice_id":"42","choice_label":"No","value":"no"},{"choice_id":"43","choice_label":"Unsure","value":"unsure"}]},{"id":"5","question_label":"Does this User Feedback message prompt any action?","name":"action","type":"radio","data":"resp_05","required":true,"choices":[{"choice_id":"51","choice_label":"None","value":"none"},{"choice_id":"52","choice_label":"Answer question in a future message","value":"message"},{"choice_id":"53","choice_label":"Provide guidance to a community facilitator","value":"guidance"},{"choice_id":"54","choice_label":"Clarify a confusing message","value":"clarify"},{"choice_id":"55","choice_label":"Other","value":"other","data_other":"resp_06"}]}]';
      //const generated = '[{"id": 1, "name": "transcription", "question_label": "Transcription", "type": "textarea", "data": "transcription", "data_other": "", "required": false, "constraint": ""}, {"id": 2, "name": "adult_child", "question_label": "Is the person speaking an adult or child?", "type": "radio", "data": "resp_01", "data_other": "", "required": false, "constraint": "", "choices": [{"choice_id": 1, "choice_label": "Adult", "value": "adult"}, {"choice_id": 2, "choice_label": "Child", "value": "child"}, {"choice_id": 3, "choice_label": "Unsure", "value": "unsure"}]}, {"id": 3, "name": "gender", "question_label": "Is the person speaking male or female?", "type": "radio", "data": "resp_02", "data_other": "", "required": false, "constraint": "", "choices": [{"choice_id": 4, "choice_label": "Male", "value": "male"}, {"choice_id": 5, "choice_label": "Female", "value": "female"}, {"choice_id": 6, "choice_label": "Unsure", "value": "unsure"}]}, {"id": 4, "name": "sentiment", "question_label": "Is the person speaking offering a ...", "type": "radio", "data": "resp_03", "data_other": "", "required": true, "constraint": "", "choices": [{"choice_id": 7, "choice_label": "Comment", "value": "comment"}, {"choice_id": 8, "choice_label": "Complaint", "value": "complaint"}, {"choice_id": 9, "choice_label": "Endorsement", "value": "endorsement"}, {"choice_id": 10, "choice_label": "Question", "value": "question"}, {"choice_id": 11, "choice_label": "Suggestion", "value": "suggestion"}, {"choice_id": 12, "choice_label": "Unsure", "value": "unsure"}]}, {"id": 5, "name": "topic", "question_label": "What is the topic of the message?", "type": "checkbox", "data": "resp_04", "data_other": "", "required": true, "constraint": "", "choices": [{"choice_id": 13, "choice_label": "Diarrhea Management", "value": "diarrhea", "id": 6, "name": "diarrhea", "question_label": "Select subtopic(s)", "type": "checkbox", "data": "resp_05", "data_other": "", "required": true, "constraint": "", "choices": [{"choice_id": 18, "choice_label": "ORS", "value": "ors"}, {"choice_id": 19, "choice_label": "Zinc", "value": "zinc"}, {"choice_id": 20, "choice_label": "Signs of Diarrhea", "value": "signs"}, {"choice_id": 21, "choice_label": "Feeding and Drinking", "value": "feeding"}]}, {"choice_id": 14, "choice_label": "Malaria Prevention", "value": "malaria", "id": 7, "name": "malaria", "question_label": "Select subtopic(s)", "type": "checkbox", "data": "resp_06", "data_other": "", "required": true, "constraint": "", "choices": [{"choice_id": 22, "choice_label": "LLINs", "value": "llins"}, {"choice_id": 23, "choice_label": "Signs and Symptoms", "value": "signs"}, {"choice_id": 24, "choice_label": "Myths about Malaria", "value": "myths"}, {"choice_id": 25, "choice_label": "Hygiene and Sitting Water", "value": "hygiene"}]}, {"choice_id": 15, "choice_label": "Handwashing", "value": "handwashing", "id": 8, "name": "handwashing", "question_label": "Select subtopic(s)", "type": "checkbox", "data": "resp_07", "data_other": "", "required": true, "constraint": "", "choices": [{"choice_id": 26, "choice_label": "Use of a Tippy-Tap", "value": "tippytap"}, {"choice_id": 27, "choice_label": "Buying vs. Making Soap", "value": "makingsoap"}, {"choice_id": 28, "choice_label": "Handwashing Technique", "value": "technique"}, {"choice_id": 29, "choice_label": "Times for Handwashing", "value": "times"}]}, {"choice_id": 16, "choice_label": "Safe Delivery", "value": "delivery", "id": 9, "name": "delivery", "question_label": "Select subtopic(s)", "type": "checkbox", "data": "resp_08", "data_other": "", "required": true, "constraint": "", "choices": [{"choice_id": 30, "choice_label": "Use of SBAs", "value": "sba"}, {"choice_id": 31, "choice_label": "Importance of ANC", "value": "anc"}, {"choice_id": 32, "choice_label": "When to Call a Doctor", "value": "calldoctor"}, {"choice_id": 33, "choice_label": "Planning for Delivery", "value": "planning"}]}, {"choice_id": 17, "choice_label": "Breastfeeding", "value": "breastfeeding", "id": 10, "name": "breastfeeding", "question_label": "Select subtopic(s)", "type": "checkbox", "data": "resp_09", "data_other": "", "required": true, "constraint": "", "choices": [{"choice_id": 34, "choice_label": "No food or water for 6 months", "value": "nofood6mos"}, {"choice_id": 35, "choice_label": "Introduction of solid foods", "value": "solidfood"}, {"choice_id": 36, "choice_label": "First breastmilk", "value": "firstmilk"}, {"choice_id": 37, "choice_label": "Problems with latching", "value": "latching"}]}]}, {"id": 11, "name": "cp", "question_label": "Is a child protection issue discussed?", "type": "radio", "data": "resp_10", "data_other": "", "required": true, "constraint": "", "choices": [{"choice_id": 38, "choice_label": "Yes", "value": "yes"}, {"choice_id": 39, "choice_label": "No", "value": "no"}, {"choice_id": 40, "choice_label": "Unsure", "value": "unsure"}]}, {"id": 12, "name": "action", "question_label": "Does this User Feedback message prompt any action?", "type": "radio", "data": "resp_11", "data_other": "resp_12", "required": true, "constraint": "", "choices": [{"choice_id": 41, "choice_label": "None", "value": "none"}, {"choice_id": 42, "choice_label": "Answer question in a future message", "value": "message"}, {"choice_id": 43, "choice_label": "Provide guidance to a community facilitator", "value": "guidance"}, {"choice_id": 44, "choice_label": "Clarify a confusing message", "value": "clarify"}]}]';
      //this.questions=JSON.parse(generated);
      const request = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufQuestions?"
          + "&program=" + this.selectedProgramCode
          + "&deployment=" + this.selectedDeployment
          + "&language=" + this.selectedLanguageCode;
      // Vue.axios.interceptors.request.use(request => {
      //     console.log('Starting Request', JSON.stringify(request, null, 2))
      //     return request
      // });
      Vue.axios.get(request,{headers: {'Authorization': `${this.$token}`}})
      .then(response=>{
        console.log("got questions:");
        this.questions=response.data;
        if (!this.connected) {
            this.$emit('network',true);
            this.connected = true;
        }
        //console.log(response.data);
      }).catch(err => {
          console.log("caught:"+err)
          this.$emit('network',false);
          this.connected = false;
      })
    }
  },
  computed: {
    deployments() {
      var program = this.programs.filter((p)=>{
        return p.code==this.selectedProgramCode;
        });
      //console.log("deployments="+program[0].deployments);
      return program[0].deployments;
    },
    languages() {
      var program = this.programs.filter((p)=>{
        return p.code==this.selectedProgramCode;
        });
      //console.log("programcode="+this.selectedProgramCode);
      //console.log("languages"+ program[0].languages);
      return program[0].languages;
    }
  },
  mounted() {
  },
  created() {
    this.loadQuestions();
    //this.form.responses=JSON.parse('{"resp_10":[],"resp_11":[],"resp_12":[]}');
  }
};
</script>

<style>

.navbar {
  background-color:#289B6A;
  color:white;
  font-size:1.15em;
  font-weight:bolder;
  text-align:left;
  line-height:40px;
  vertical-align:middle;
}

.navbar select {
  width:150px;
  margin-right:25px;
  vertical-align:middle;
}

.navbar span {
  padding-left:5%;
  padding-right:5%;
  margin-bottom:20px;
  vertical-align:middle;
}

.navbar span:first-child {
  font-size:1.3em;
}

.navbar span:last-child {
  float:right;
  vertical-align:middle;
}

select {
  width:100px;
}

textarea {
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
td.stats {
  text-align: center;
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
  /* border-bottom: 1px solid #ddd; */
}

td {
  padding: 3px;
  text-align: left;
  /* border-bottom: 1px solid #ddd; */
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
  color:#58595B;
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
  background:dodgerblue;
  appearance: none;
  font: inherit;
  font-size: 1.2rem;
  font-weight:bolder;
  padding: .5em 1em;
  border-radius: .3em;
  cursor: pointer;
  margin: 3px;
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
  margin: 10px;
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
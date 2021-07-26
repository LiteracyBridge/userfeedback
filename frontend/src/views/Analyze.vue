<template>
<div width="100%"  @keydown.esc="escape" >
<div width="100%" class="navbar">
  <span>AMPLIO</span>
  <span class="text-2xl">Analysis</span>
  <span>
    <select v-model="context.selectedProgramCode" @change="newProgram" class="outline-grey text-black text-base">
      <option v-for="program in programs" :value="program.code" :key="program.code">
        <span> {{program.name}}</span>
      </option>
    </select>
    <a @click="logout" class="text-2xl text-white font-bold whitespace-nowrap rounded cursor-pointer hover:text-gray-500">Logout</a>
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
    <div class="modal-overlay" v-if="noMessages"></div>
  </transition>
  <transition name="pop" appear>
    <div class="modal" role="dialog" v-if="noMessages">
      <h1 style="color:red">
        <span v-if="context.totalReceivedMessages > 0">No more messages to process!</span>
        <span v-else>No messages are ready to process yet.</span>          
        </h1>
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
            Deployment <select v-model="context.selectedDeployment" @change="loadQuestions" class="outline-grey">
              <option v-for="deployment in deployments" :value="deployment" :key="deployment">
                <span> {{deployment}}</span>
              </option>
            </select>
          </td>
          <td>
            Language <select v-model="context.selectedLanguageCode" @change="loadQuestions" class="outline-grey">
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
      <latest-audio :key="audioKey" @no_messages="showNoMessages" @network="updateConnected" @handleUseless="handleUseless" ref="audio" 
      :userEmail="this.$route.query.email" :context="context" />
  </td></tr>
  <tr><td>
      <div ref="top">
        Feedback Form
        <table width="100%" style="text-align:left;border: 2px solid #ddd;padding: 5px">
          <tr v-for="(question,count) in questions" :key="question.question_id">
              <td class="pad">
                  <p><span class="question">{{count+1}}. {{question.question_label}}</span>
                      <!-- <span v-if="question.required" style="color: red">*</span>    -->
                      <span v-if="question.required"> (Required)</span>   
                      <span v-else> (Optional)</span>   
                  </p>
                  <div v-if="question.type=='textarea'">
                    <textarea width="100%" rows="5" class="outline-grey" :name="question.name" v-model="form.responses[question.data]"/>
                  </div>
                  <div v-if="question.type=='number'">
                    <p v-if="invalidResponse(question)" class="col-span-2 md:col-span-4 text-center text-red-500">
                      <font-awesome-icon icon="exclamation-circle" class="w-6 h-6" />
                      Invalid Number: {{question.constraint}}
                    </p>
                    <v-input :name="question.name" type="number" mx="mx-0" :value="Number(form.responses[question.data])"
                      @input="updateResponse(question.data,$event.target.value)"/>
                  </div>
                  <div v-if="question.type=='select'">
                    <select :name="question.name" mx="mx-0" v-model="form.responses[question.data]" class="outline-grey text-black text-base">
                      <option v-for="option in question.choices" :key="option.choice_id" :value="option.value">
                          {{option.choice_label}}
                      </option>
                    </select>
                  </div>
                  <!-- <div v-if="question.type=='select'">
                    <label for="question.id+'-input'">{{question.question_label}}</label>
                    <multiselect
                      :id="question.id + '-multi'"
                      :value="form.responses[question.data]"

                      :options="question.choices"
                      placeholder="Select an option"
                      aria-label="Select an option"
                      @select="$updateResponse(question.data,event.target.value)"
                    />
                  </div> -->

                  <div v-else v-for="choice in question.choices" :key="choice.choice_id">
                      <input class="mr-3" @change="clearOtherAndSubChoices
                      (choice,question)" :type="question.type" :name="question.name" :id="choice.choice_id" :ref="choice.choice_id" :value="choice.value" v-model="form.responses[question.data]" />
                      <label :for="choice.choice_id">{{choice.choice_label}}</label>
                      <br />
                      <div  v-if="choice.choices && String(form.responses[question.data]).includes(choice.value)">
                        <label>{{choice.question_label}}</label><span v-if="choice.required" style="color: red">*</span>   
                        <div v-for="subchoice in choice.choices" :key="subchoice.choice_id" style="text-indent: 20px">
                            <input class="mr-3" :type="choice.type" :name="choice.name" :id="choice.question_id" :value="subchoice.value" v-model="form.responses[choice.data]"/>
                            <label :for="subchoice.choice_id">{{subchoice.choice_label}}</label>
                        </div>
                      <div v-if="choice.data_other" style="text-indent: 20px">
                            <input class="mr-3" @change="clearOtherAndSubChoices(null,choice)" :type="choice.type" :name="choice.name" :id="choice.question_id+'-other'" value="other" v-model="form.responses[choice.data]"/>
                            <label :for="choice.choice_id+'-other'">Other</label>
                            <!-- <input class="ml-3 text_input" @focus="form.responses[choice.data].push('other')" type="text" :name="choice.name+'-othertxt'" :id="choice.choice_id+'-othertxt'" v-model="form.responses[choice.data_other]"/> -->
                            <div v-if="String(form.responses[choice.data]).includes('other')">
                              <textarea rows="2" @focus="form.responses[choice.data].push('other')" class="ml-16 w-auto outline-grey" :name="choice.name+'-othertxt'" :id="choice.choice_id+'-othertxt'" v-model="form.responses[choice.data_other]"/>
                            </div>
                      </div>

                      </div>
                  </div>
                  <!-- <div v-if="question.data_other" :key="question.question_id+'-other'"> -->
                  <div v-if="question.data_other">
                      <!-- <input class="mr-3" @change="clearOtherAndSubChoices(null,question)" :type="question.type" :name="question.name" :id="question.question_id+'-other'" :ref="question.question_id+'-other'" value="other" v-model="form.responses[question.data]" /> -->
                      <input class="mr-3" @change="clearOtherAndSubChoices(null,question)" :type="question.type" :name="question.name" :id="question.question_id+'-other'" value="other" v-model="form.responses[question.data]" />
                      <label :for="question.question_id+'-other'">Other</label>
                      <span >
                          <!-- <input class="ml-3 text_input" @focus="(Array.isArray(form.responses[question.data]) && form.responses[question.data].length > 0 ? form.responses[question.data].push('other') : form.responses[question.data]='other')" type="text" name="question.name+'-othertxt'" :id="question.question_id+'othertxt'" v-model="form.responses[question.data_other]"/> -->
                          <!-- <input class="ml-3 text_input" @focus="form.responses[question.data].push('other')" type="text" name="question.name+'-othertxt'" :id="question.question_id+'-othertxt'" v-model="form.responses[question.data_other]"/> -->
                          <div v-if="String(form.responses[question.data]).includes('other')">
                            <textarea rows="2" @focus="form.responses[question.data].push('other')" class="ml-16 w-auto outline-grey" :name="question.name+'-othertxt'" :id="question.choice_id+'-othertxt'" v-model="form.responses[question.data_other]"/>
                          </div>
                      </span>
                  </div>
              </td>
          </tr>
          <tr>
            <td style="text-align: right">
              <div class="float-right">
                <v-tooltip
                  v-if="requiredCompleted  != ''"
                  :text="'Questions still required:  #'+checkCompleted()"
                  position="right"
                  class="my-2 ml-2"
                  :width="200"
                >
                  <font-awesome-icon
                    class="text-orange-600"
                    icon="exclamation-circle"
                  />
                </v-tooltip>
                <VButton
                  label="SUBMIT"
                  variant="success"
                  :disabled="requiredCompleted != ''"
                  :iconL="submitStatus === 'submitting' ? 'spinner' : ''"
                  :iconLPulse="submitStatus === 'submitting'"
                  @click="handleSubmit"
                />
              </div>
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
import VTooltip from '@/components/VTooltip'
import VInput from '@/components/VInput'
import VButton from '@/components/VButton';
import uniqueId from 'lodash.uniqueid'
import Multiselect from 'vue-multiselect'

Vue.use(VueAxios,axios)

export default {
  name: "Home",
  components: {
    LatestAudio,   //,Question
    VTooltip,
    VInput,
    VButton,
    Multiselect
  },
  data() {
    return {
      connected: true,
      audioKey: 0,
      showModal: false,
      noMessages: false,
      showSubmitModal: false,
      submitStatus: null,
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
          resp_20:[],
          resp_21:[],
          resp_22:[],
          resp_23:[],
          resp_24:[],
          resp_25:[],
          resp_26:[],
          resp_27:[],
          resp_28:[],
          resp_29:[],
          resp_30:[],
          resp_01_o:[],
          resp_02_o:[],
          resp_03_o:[],
          resp_04_o:[],
          resp_05_o:[],
          resp_06_o:[],
          resp_07_o:[],
          resp_08_o:[],
          resp_09_o:[],
          resp_10_o:[],
          resp_11_o:[],
          resp_12_o:[],
          resp_13_o:[],
          resp_14_o:[],
          resp_15_o:[],
          resp_16_o:[],
          resp_17_o:[],
          resp_18_o:[],
          resp_19_o:[],
          resp_20_o:[],
          resp_21_o:[],
          resp_22_o:[],
          resp_23_o:[],
          resp_24_o:[],
          resp_25_o:[],
          resp_26_o:[],
          resp_27_o:[],
          resp_28_o:[],
          resp_29_o:[],
          resp_30_o:[],
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
        }],
        deployments:[1]
      }],
      context: {
        selectedProgramCode:"CARE-ETH-GIRLS",
        selectedDeployment:1,
        selectedLanguageCode:"aar",
        totalReceivedMessages: 123 
      }
    }
  },
  methods: {
    updateResponse(whichResponse,whatValue) {
      this.form.responses[whichResponse] = whatValue;
      console.log('['+whichResponse+']:'+whatValue);
      //this.getQuestionFromResponseCode(whichResponse);
    },
    invalidResponse(question) {
      const constraint='non-negative';//question.constraint  //this.getPropertyFromData(whichResponse,'constraint');
      const data=this.form.responses['resp_20'];//question.data //[whichResponse];
      var invalid = false;
      if (constraint =='non-negative') {
        if(isNaN(data[0]) || data[0]<0) {
          invalid = true;
        }
      };
      return invalid;      
    },
    getPropertyFromData(whichResponse,key) {
      // search the questions for data or data_other matching whichResponse
      console.log("in getProp:"+whichResponse)
      var target,question;
      // first search the top-level questions
      question = this.questions.filter((q)=>{
        return q.data==whichResponse || q.data_other==whichResponse;
      });
      if (question.length==1) {
        target = question[0]; 
      } else {
        // if not in top-level questions, it must be in a choice that has subchoices.
        question = this.questions.filter(q1=>q1.choices).map((q2)=>{
          return q2.choices.filter((c)=>{
            return c.data==whichResponse||c.data_other==whichResponse
          })
        }).filter(q3=>q3.length>0);
        target = question[0][0];
      }
      return target[key];
    },
    async logout() {
      try {
          await Auth.signOut();
          this.$router.push('Login');
      } catch (error) {
          console.log(error.message);
      }
    },
    updateConnected(isConnected) {
      this.connected = isConnected;
    },
    clearOtherAndSubChoices(choice,question) {
      if (question.data_other && !(String(this.form.responses[question.data]).includes('other'))) {
          this.form.responses[question.data_other] = '';
      }
      if (choice && choice.data) {
        this.form.responses[choice.data]=[];
        if (choice.data_other) {
          this.form.responses[choice.data_other] = '';
        }
      }
    },
    showNoMessages() {
          this.noMessages = true;
          setTimeout(()=> {
            this.noMessages = false;
          },4000);
    },
    handleUseless() {
      this.form.useless = true;
      this.handleSubmit();
    },
    handleSubmit() {
      this.submitStatus = 'submitting';
      //First, add UUID and email to the form data before we submit it.
      this.form.user_email = this.$route.query.email;
      this.form.uuid = this.$refs.audio.getUUID();

      //Submit values here:
      const action = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufProcess";      
      Vue.axios.post(action,this.form, {headers: {'Authorization': `${this.$token}`}})
      .then(response=>{
          console.log(response.data);
          //TODO: What if Lambda function says it wasn't submitted properly
          this.showSubmitModal = true;
          this.resetFormAndAudio();
          setTimeout(()=> {
            this.showSubmitModal = false;
          },1000);
      })
      .catch (err => {
          //TODO: what if network just went away before hitting submit - is data lost? can it retry?
          console.log(err);
          this.connected = false;
      });
      this.submitStatus = '';
    },
    resetFormAndAudio() {
      //there's got to be an easier way!
      this.form.uuid = '';
      this.form.useless = false;
      for (var i=1;i<=30;i++) {
        var field = i.toString();
        if (field.length==1) {
          field = '0'+field;
        }
        field = 'resp_' + field;
        // console.log(field);
        this.form.responses[field]=[];
        this.form.responses[field+'_o']=[];
      }
      this.setDefaults();
      if (this.$refs.audio) {
        this.$refs.audio.updateUrl();
      }
    },
    escape() {
      this.checkCompleted();
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
      this.context.selectedLanguageCode = this.languages[0].code;
      this.context.selectedDeployment = this.deployments[0];
      this.loadQuestions();
    },
    setDefaults() {
      for (var q of this.questions) {
        if (q.default && q.default != 'null') {
          if (q.type == 'select') {
            this.form.responses[q.data]=q.default;
          } else {
            this.form.responses[q.data]=[q.default];
          }
        }   
      }
    },
    loadQuestions() {
      const request = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufQuestions?"
          + "&program=" + this.context.selectedProgramCode
          + "&deployment=" + this.context.selectedDeployment
          + "&language=" + this.context.selectedLanguageCode;
      // Vue.axios.interceptors.request.use(request => {
      //     console.log('Starting Request', JSON.stringify(request, null, 2))
      //     return request
      // });
      Vue.axios.get(request,{headers: {'Authorization': `${this.$token}`}})
      .then(response=>{
        this.questions=response.data;
        this.setDefaults();
        this.hardcodeTotalReceived();
        if (!this.connected) {
            this.$emit('network',true);
            this.connected = true;
        }
        //console.log(response.data);
      }).catch(err => {
          console.log("caught:"+err)
          this.$emit('network',false);
          this.connected = false;
      });
      this.resetFormAndAudio();
    },
    hardcodeTotalReceived() {
        // Rabiya plans to write functionality to get programs/languages/deployments for the user
        // This should also include the total received UF messages that are applicable.
        // IMPORTANT: when doing this, be sure to exclude any messages less than 5 seconds, 
        // just as done by the lambda fct, ufDataService, when it gets the next uuid. 
        if (this.context.selectedProgramCode == 'CARE-ETH-GIRLS') {
          this.context.totalReceivedMessages = 104; //actual number of girls UF messages >= 5 seconds
        } else if (this.context.selectedLanguageCode == 'en') {
          this.context.totalReceivedMessages = 456;  // made-up number for made-up deployment 
        } else if (this.context.selectedDeployment == 1) {
          this.context.totalReceivedMessages = 123; //actual number of boys UF messages >= 5 seconds
        } else {
          this.context.totalReceivedMessages = 0; // made-up number for made-up deployment
        }
    },
    checkCompleted() {
        let completed = "";
        let questionNumber = 0;
        for (var q of this.questions) {
          questionNumber++;
          if (q.required) {
            if (this.form.responses[q.data].length == 0) {
              completed += String(questionNumber) + ",";
            }
          }  
          if (q.choices && q.choices.length > 0) {
            for (var c of q.choices) {
              //check if the subchoice would be required if its parent choice is checked 
              if (c.required && String(this.form.responses[q.data]).includes(c.value)) {
                //now check if this sub-choice has data
                if (this.form.responses[c.data].length == 0) {
                  completed += String(questionNumber) + "." + c.value + ",";
                }
              }
            }
          }
        }
        if (completed.length > 1) {
          completed = completed.substring(0, completed.length - 1);
        }
        return completed;
    },
  },
  computed: {
    requiredCompleted() {
      return this.checkCompleted();
    },
    deployments() {
      var program = this.programs.filter((p)=>{
        return p.code==this.context.selectedProgramCode;
        });
      //console.log("deployments="+program[0].deployments);
      return program[0].deployments;
    },
    languages() {
      var program = this.programs.filter((p)=>{
        return p.code==this.context.selectedProgramCode;
        });
      //console.log("programcode="+this.context.selectedProgramCode);
      //console.log("languages"+ program[0].languages);
      return program[0].languages;
    },
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
  border-bottom: 1px solid;
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

:disabled {
  background-color: #D8D8D8;
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
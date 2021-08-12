<template>
<div @keydown.esc="escape">
  <nav-bar :programs="programs" :selectedProgramCode="context.selectedProgramCode" :email="this.$route.query.email" @changed="updatedProgram"/>
  <div v-if="!connected" style="color:red; font-size:1.5em; font-weight:bolder; text-align:center; padding: 0px">No Connection!</div>    
  <div class="flex">
      <div v-if="nextUUID!=null" @click="$emit('all')" style="color:#0000ee;font-weight:bold" class="cursor-pointer text-2xl underline">View all responses</div>    
      <div>
        <span>
          <depl-lang-select :deployments="deployments" :languages="languages" 
            :selectedDeployment="context.selectedDeployment" :selectedLanguageCode="context.selectedLanguageCode" 
            @langChanged="updatedLanguage" @deplChanged="updatedDeployment"
          />
        </span>
      </div>
  </div>
  <div style="padding: 0px">
          <stats :progress="progress" />
  </div>
  <div class="absolute right-0">
    <instructions/>
  </div>
  <hr style="height:2px;border-width:0;background-color:gray">
  <div v-if="audioMetadata.url!=''">
      <audio-player :key="audioKey" @srcError="updateUrl" @network="updateConnected" @next="getNext" ref="audio" :audioMetadata="audioMetadata" />
  </div>
  <div v-if="audioMetadata.url!=''" >
      <survey :context="context" :uuid="audioMetadata.uuid" :submission="audioMetadata.submission" @next="getNext" @checkboxes="setCheckboxes" @network="updateConnected"/>
  </div>
  <div v-if="audioMetadata.url==''">
    <span style="color:red; text-align:center" v-html="showNoAudios"/>
  </div>
  <div>
    <br/>
    <p>Need help? Contact us at support@amplio.org</p>
  </div>
 </div>
</template>

<script>
import NavBar from "../components/NavBar.vue";
import DeplLangSelect from "../components/DeplLangSelect.vue"
import Instructions from "../components/Instructions.vue"
import Stats from "../components/Stats.vue";
import AudioPlayer from "../components/AudioPlayer.vue";
import Survey from "../components/Survey.vue";
import axios from 'axios'
import Vue from 'vue'
import VueAxios from 'vue-axios'

Vue.use(VueAxios,axios)

export default {
  name: "AnalyzeComp",
  props:{
    nextUUID: {
      default:null
    }
  },
  watch: {
    nextUUID (newUUID,oldUUID) {
      this.uuid = newUUID;
      if (newUUID != null) {
        this.updateUrl();
      }
    }
  },
  components: {
    NavBar,
    DeplLangSelect,
    Instructions,
    Stats,
    AudioPlayer,
    Survey
  },
  data() {
    return {
      uuid:'',
      previousSubmission: false,
      audioMetadata:{},
      progress:{totalReceivedMessages: -1},
      connected: true,
      audioKey: 0,
      showModal: false,
      message: '',
      checkboxes:[],
      form: {},
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
        selectedLanguageCode:"aar"
      }
    }
  },
  methods: {
    getNext() {
      if (this.nextUUID != null) {
        this.$emit("next");
      } else {
        this.uuid = null;
        this.updateUrl();
      }    
    },
    updateUrl() {  
      const request = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufTDataService?"
          + "email=" + this.$route.query.email
          + "&program=" + this.context.selectedProgramCode
          + "&deployment=" + this.context.selectedDeployment
          + "&language=" + this.context.selectedLanguageCode
          + ((this.uuid)?"&uuid="+this.uuid+"&array="+JSON.stringify(this.checkboxes):"")
      // Vue.axios.interceptors.request.use(request => {console.log('Starting Request', JSON.stringify(request, null, 2)) return request });
      console.log("updateUrl:"+request);
      Vue.axios.get(request,{headers: {'Authorization': `${this.$token}`}})
      .then(response=>{
          if (!this.connected) {
              this.connected = true;
          }
          this.uuid = response.data.audioMetadata.uuid;
          this.audioMetadata = response.data.audioMetadata;
          this.progress = response.data.progress;
          if (this.audioMetadata.url != '') {
              let filename = unescape(this.audioMetadata.url.substring(this.audioMetadata.url.lastIndexOf('/')+1));
              this.audioMetadata["filename"]=filename; 
              if (this.audioMetadata.submission) {
                this.previousSubmission = true;
              }
          }
          console.log("new URL:"+this.audioMetadata.url);
      }).catch(err => {
          console.log("caught:"+err)
          this.connected = false;
      })
    },
    setCheckboxes(list) {
      // this is used to pass to lambda fct when requesting a specific uuid form submission
      // some fields need to be in an array (checkboxes); while others should not (select boxes)
      this.checkboxes = list;
    },
    updateConnected(isConnected) {
      this.connected = isConnected;
    },
    escape() {
      this.$refs.audio.setAudioFocus();
    },
    updatedProgram(programCode) {
      this.context.selectedProgramCode = programCode;
      this.context.selectedLanguageCode = this.languages[0].code;
      this.context.selectedDeployment = this.deployments[0];
      this.updateUrl();
    },
    updatedLanguage(languageCode) {
      this.context.selectedLanguageCode = languageCode;
      this.updateUrl();
    },
    updatedDeployment(deployment) {
      this.context.selectedDeployment = deployment;
      this.updateUrl();
    }
  },
  computed: {
    deployments() {
      var program = this.programs.filter((p)=>{
        return p.code==this.context.selectedProgramCode;
        });
      return program[0].deployments;
    },
    languages() {
      var program = this.programs.filter((p)=>{
        return p.code==this.context.selectedProgramCode;
        });
      return program[0].languages;
    },
    showNoAudios() {
      let message="NONE";
      if (this.$route.path=='/responses' && this.uuid == null) {
        // Must be in Responses.vue, which is telling us that we are at the end of the list.
        message = "Finished!  There are no more responses to review.";
      } else {
        if (this.progress.totalReceivedMessages != -1) { // -1 indicated that this number hasn't been loaded yet.
          if(this.progress.totalReceivedMessages == 0) {
            message = "No messages are ready to process yet.";
          } else {
            let remaining = this.progress.totalReceivedMessages - (this.progress.others_recordings + this.progress.users_recordings);
            if (remaining == 0) {
              message = "Finished! There are no more messages to process!";          
            } else {
              var isAre;
              var itThey;
              if (remaining == 1) {
                isAre = 'is ';
                itThey = 'It ';
              } else {
                isAre = 'are ';
                itThey = 'They ';
              }
              message = "There " + isAre + String(remaining) + " remaining message" +((remaining>1)?"s":"")  + " still being processed by others.<BR/>" + itThey + "will be available for you to process within 5 minutes.";
            }
          }
        }
      }
      return message;
    }
  },
  mounted() {
    if(this.$route.path=='/analyze' || this.$route.path=='/responses') {
      this.uuid = this.nextUUID;
      this.updateUrl();
    }
  }
};
</script>

<style>
select {
  width:100px;
}

table {
  margin-left: auto;
  margin-right: auto;
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

select:focus {
  outline:1px solid #4D90FE; 
  border:1px solid #4D90FE;
 }


/* For Modal */
html {
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

:disabled {
  background-color: #D8D8D8;
}

</style>
<template>
<div class="grid grid-cols-10" @keydown.esc="escape">
  <div class="col-span-full row-start-1 row-end-2">
    <nav-bar :key="navKey" :allResponsesLink="nextUUID != null" @contextChanged="contextChanged" @all="$emit('all')"/>
  </div>
  <div class="col-start-3 col-span-6">
    <div v-if="!connected" style="color:red; font-size:1.5em; font-weight:bolder; text-align:center; padding: 0px">No Connection!</div>    
    <div class="float-right">
      <instructions/>
    </div>
    <div style="padding: 0px">
            <stats :progress="progress" />
    </div>
    <div v-if="audioMetadata.url!=''">
        <audio-player :key="audioKey" @srcError="updateUrl" @network="updateConnected" @next="getNext" ref="audio" :audioMetadata="audioMetadata" />
    </div>
    <br/>
    <div v-if="audioMetadata.url!=''" >
        <survey :key="surveyKey" :uuid="uuid" :submission="audioMetadata.submission" @next="getNext" @checkboxes="setCheckboxes" @network="updateConnected"/>
    </div>
    <div v-if="audioMetadata.url==''">
      <span style="color:red; text-align:center" v-html="showNoAudios"/>
    </div>
    <div>
      <br/>
      <p>Need help? Contact us at support@amplio.org</p>
    </div>
  </div>
 </div>
</template>

<script>
import NavBar from "../components/NavBar.vue";
import Instructions from "../components/Instructions.vue"
import Stats from "../components/Stats.vue";
import AudioPlayer from "../components/AudioPlayer.vue";
import Survey from "../components/Survey.vue";
import axios from 'axios'
import Vue from 'vue'
import VueAxios from 'vue-axios'
import {getters,mutations} from '../globalStore.js'

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
      if (newUUID != '') {
        this.updateUrl();
      } else {
        this.audioMetadata.url = '';
      }
    }
  },
  components: {
    NavBar,
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
      surveyKey: 0,
      navKey:0,
      showModal: false,
      message: '',
      checkboxes:[],
      form: {}
    }
  },
  methods: {
    ...mutations,
    getNext() {
      if (this.nextUUID != null) {
        this.$emit("next");
      } else {
        this.uuid = null;
        this.updateUrl();
      }    
    },
    updateUrl() {  
      const request = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufDataService?"
          + "email=" + this.email
          + "&program=" + this.context.selectedProgramCode
          + "&deployment=" + this.context.selectedDeployment
          + "&language=" + this.context.selectedLanguageCode
          + ((this.uuid)?"&uuid="+this.uuid:"")
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
          if (this.$refs.audio) {
            this.$refs.audio.setAudioFocus();
          }
          console.log("new URL:"+this.audioMetadata.url);
      }).catch(err => {
          console.log("caught:"+err)
          this.uuid="";
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
    contextChanged() {      
      this.uuid='';
      this.updateUrl();
      this.surveyKey += 1;
    },
  },
  computed: {
    ...getters,
    showNoAudios() {
      let message="NONE";
      if (this.$route.path=='/review' && ((this.uuid == '') || (this.uuid==null))) {
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
    console.log("mounted-AnalyzeComp");
    if(this.$route.path=='/analyze' || this.$route.path=='/review') {
      this.uuid = this.nextUUID;
      this.updateUrl();
    }
  },
   created() {
    if(this.$route.query.program) {
      this.setProgram(this.$route.query.program);
      this.setLanguage(this.$route.query.language);
      this.setDeployment(this.$route.query.deployment);
    }
  },
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
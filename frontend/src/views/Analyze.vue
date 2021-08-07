<template>
<div @keydown.esc="escape" >

  <nav-bar :programs="programs" :selectedProgramCode="context.selectedProgramCode" @changed="updatedProgram"/>

  <div>
      <div  v-if="!connected" style="color:red; font-size:1.5em; font-weight:bolder; text-align:center; padding: 0px">No Connection!</div>    
      <div>
        <span>
          <depl-lang-select :deployments="deployments" :languages="languages" 
            :selectedDeployment="context.selectedDeployment" :selectedLanguageCode="context.selectedLanguageCode" 
            @langChanged="updatedLanguage" @deplChanged="updatedDeployment"
          />
        </span>
        <span style="float:right">
          <instructions/>
        </span>
      </div>
      <div style="padding: 0px">
          <stats :progress="progress" />
      </div>

      <div v-if="audioMetadata.url!=''">
          <audio-player :key="audioKey" @srcError="updateUrl" @network="updateConnected" ref="audio" :audioMetadata="audioMetadata" />
      </div>
      <br/>
      <div v-if="audioMetadata.url!=''" >
          <survey :context="context" :uuid="audioMetadata.uuid" @submitted="updateUrl" @network="updateConnected"/>
      </div>

      <div v-if="audioMetadata.url==''"><td style="color:red; text-align:center" v-html="showNoAudios"/></div>
  </div>
  <br/>
  <p>Need help? Contact us at support@amplio.org</p>

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
  name: "Home",
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
      audioMetadata:{},
      progress:{totalReceivedMessages: -1},
      connected: true,
      audioKey: 0,
      showModal: false,
      message: '',
      questions: [],
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
    updateUrl() {    
      const request = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufTDataService?"
          + "email=" + this.$route.query.email
          + "&program=" + this.context.selectedProgramCode
          + "&deployment=" + this.context.selectedDeployment
          + "&language=" + this.context.selectedLanguageCode;
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
          }
          console.log("new URL:"+this.audioMetadata.url);
      }).catch(err => {
          console.log("caught:"+err)
          this.connected = false;
      })
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
      return message;
    }
  },
  mounted() {
    if(this.$route.path=='/app') {
      this.updateUrl();
    }
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

:disabled {
  background-color: #D8D8D8;
}

</style>
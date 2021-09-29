<template>
<div>
    <div class="row-start-1 row-end-2 col-span-full" >
         <nav-bar/>
    </div>
    <div v-if="context.selectedProgramCode=='DEMO'" class="mt-2 mb-5 ml-5">
        {{target}}: <VButton label='Delete Analysis' variant="button_warning" @click="deleteAnalysis"/>
        <br/>
        <span>{{deleteMessage}}</span>
    </div>
    <div v-if="loginEmail.search(/@amplio.org/)>0" class="ml-5 mt-48">
        <form @submit.prevent="viewAs">
            <v-input :value="emailInput" @input="emailInput = $event.target.value" type="text" name="emailAddress" label="Email address"  icon-left="user-circle"/>
            <button :disabled="invalidEmail" class="button">View As</button>
        </form>
    </div>
    <div v-if="noPrograms">
        <span style="color:red;font-weight:bolder">This user does not have access to a program with User Feedback messages.</span>
    </div>
</div>

</template>

<script>
import NavBar from "@/components/NavBar"
import VButton from '@/components/VButton';
import VInput from '@/components/VInput';
import Vue from 'vue'
import axios from 'axios'
import VueAxios from 'vue-axios'
import {getters,mutations,actions} from '../globalStore.js'
Vue.use(VueAxios,axios)

export default {
  name:"Admin",
  components: {
    NavBar,
    VButton,
    VInput
  },
  data() {
    return {
      connected: true,
      deleteMessage: "",
      emailInput:"",
      noPrograms:false
    }
  },
  methods: {
    ...mutations,
    ...actions,
    async viewAs() {
        console.log("ViewAs:"+this.emailInput);
        const previousEmail = this.email;
        this.setEmail(this.emailInput);    
        var atLeastOneProgram = await this.getProgramsAndContext();
        if (atLeastOneProgram) {
            this.$router.push({ path:'/analyze'})
        } else {
            this.setEmail(previousEmail);
            this.emailInput='';
            this.noPrograms = true;
            setTimeout(()=> {
                this.noPrograms = false;
            },5000);            
        }
    },
    deleteAnalysis() {
      this.deleteMessage = 'Deleting Analysis...';

      const request = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufProcess?"
          + "email=" + this.email
          + "&program=" + this.context.selectedProgramCode
          + "&deployment=" + this.context.selectedDeployment
          + "&language=" + this.context.selectedLanguageCode
      console.log("deleting analysis:"+request);
      Vue.axios.delete(request,{headers: {'Authorization': `${this.$token}`}})
      .then(response=>{
            if (!this.connected) {
                this.connected = true;
            }
            this.deleteMessage = 'Analysis data has been deleted for ' + this.target + '.';
            setTimeout(()=> {
                this.deleteMessage = '';
            },5000);
            console.log(response.data);
      }).catch(err => {
            console.log(err);
            this.connected = false;
            this.deleteMessage = 'There is no Internet connection right now.  Data may not have been cleared.';
            setTimeout(()=> {
                this.showSubmitModal = false;
                this.message = '';
            },5000);
      })
    }
   },

  computed: {
    ...getters,
    invalidEmail() {
        const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return !re.test(String(this.emailInput).toLowerCase());
    },
    target() {
        return this.context.selectedProgramCode + '/' + this.context.selectedDeployment + '/' + this.context.selectedLanguageCode
    }
   },
   mounted() {
        if (this.loginEmail != this.email) {
            this.emailInput = this.loginEmail; 
        }
   }
}
</script>
<style scoped>
.button_warning {
  border: none;
  color: #FFF;
  background: red;
  appearance: none;
  font: inherit;
  font-size: 1.2rem;
  font-weight:bolder;
  padding: .5em 1em;
  border-radius: .3em;
  cursor: pointer;
}
</style>
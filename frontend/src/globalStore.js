import Vue from 'vue'
import axios from 'axios'
import VueAxios from 'vue-axios'

export const store = Vue.observable(
    {context:{},
    programs:[],
    // context: {
    //     selectedProgramCode:"CARE-ETH-BOYS",
    //     selectedDeployment:1,
    //     selectedLanguageCode:"aar"
    // },
    // programs: [{
    //     code:"CARE-ETH-GIRLS",
    //     name:"CARE Ethiopia Girls",
    //     languages:[{
    //       code:"aar",
    //       name:"Afar af"
    //     }],
    //     deployments:[{
    //       number:1,
    //       languages:["aar"]
    //     }]
    //   },{
    //     code:"CARE-ETH-BOYS",
    //     name:"CARE Ethiopia Boys",
    //     languages:[{
    //       code:"aar",
    //       name:"Afar af"
    //     },{
    //       code:"en",
    //       name:"English"
    //     }],
    //     deployments:[{
    //       number:1,
    //       languages:["aar"]
    //     }, {
    //       number:2,
    //       languages:["en","aar"]
    //     },{
    //       number:3,
    //       languages:["en"]
    //     }]
    //   },{
    //     code:"DEMO",
    //     name:"Demo Program",
    //     languages:[{
    //       code:"en",
    //       name:"English"
    //     }],
    //     deployments:[{
    //       number:1,
    //       languages:["en"]
    //     }]
    //   }],
     email: "", // email used throughout app, can be changed with "View As" admin feature
     loginEmail: ""} // email used in cognito login
  )

export const getters = {
    context: ()=> store.context,
    programs: ()=> store.programs,
    email: ()=> store.email,
    loginEmail: ()=> store.loginEmail
}

export const mutations = {
    setProgram(programCode) {
        store.context["selectedProgramCode"] = programCode;
    },
    setDeployment(deployment) {
        store.context["selectedDeployment"] = deployment;
    },
    setLanguage(languageCode) {
        store.context["selectedLanguageCode"] = languageCode;
    },
    setContext(context) {
        store.context = context;
    },
    setLoginEmail(email) {
        store.loginEmail = email;
        store.email = email;
    },
    setEmail(email) {
        store.email = email;
    },
    setPrograms(programs) {
        store.programs = programs;
    }
}
export const actions = {
    async getProgramsAndContext() {
        var atLeastOneProgram = false;
        const request = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufDataService?"
            + "email=" + store.email + "&program=all";
        console.log("updateUrl:"+request);
        await axios.get(request,{headers: {'Authorization': `${this.$token}`}})
        .then(response=>{
            this.connected = true;
            if (response.data.programs) {
                // setting context to null will delay computed functions 
                this.setContext(null);
                this.setPrograms(response.data.programs);
                this.setContext(response.data.context);
                atLeastOneProgram = true;
            } 
        }).catch(err => {
            console.log("caught:"+err)
            this.connected = false;
        })
        return atLeastOneProgram;
    }         
}

Vue.prototype.$store = store
Vue.prototype.$actions = actions


<template>
  <div>
    <div class="navbar grid grid-cols-10 justify-items-start content-end">
      <span class="text-3xl col-start-2 col-span-1 row-start-1 row-span-1 pb-0">AMPLIO</span>
      <router-link class="pt-4 text-2xl col-start-3 col-span-1 row-start-1 row-span-1" to="/analyze">
        Analyze
      </router-link>
      <router-link class="pt-4 text-2xl col-start-4 col-span-1 row-start-1 row-span-1" to="/review">
        Review
      </router-link>
      <router-link class="pt-4 text-2xl col-start-5 col-span-1 row-start-1 row-span-1" to="/admin">
        Admin
      </router-link>
      <select :value="context.selectedProgramCode" @change="programChanged" class="col-start-7 col-span-2 justify-self-end my-4 outline-grey text-black text-lg w-64">
        <option v-for="program in programs" :value="program.code" :key="program.code">
          <span> {{program.name}}</span>
        </option>
      </select>
      <a @click="logout" class="col-start-9 col-end-11 justify-self-center pt-4 text-2xl text-white font-bold whitespace-nowrap rounded cursor-pointer hover:text-gray-500">Logout</a>
    </div>
    <div class="grid grid-cols-10 justify-items-start content-end pb-8">
      <div v-if="allResponsesLink" @click="$emit('all')" class="row-start-2 col-start-3 col-span-2 cursor-pointer pt-4 text-2xl underline" style="color:#0000ee;font-weight:bold" >
          View all    
      </div>
      <div v-if="email != loginEmail" class="row-start-2 col-start-4 col-span-1 cursor-pointer pt-4 text-small">
          {{email}}    
      </div>
      <div class="row-start-2 col-start-5 col-span-4 justify-self-end pt-4">
          Deployment 
          <select :value="context.selectedDeployment" class="outline-grey w-16 mr-8" @change="deploymentChanged">
              <option v-for="deployment in deployments" :value="deployment" :key="deployment"><span> {{deployment}}</span></option>
          </select>
          Language 
          <select :value="context.selectedLanguageCode" class="outline-grey" @change="languageChanged">
              <option v-for="language in languages" :value="language.code" :key="language.code"><span> {{language.name}}</span></option>
          </select>
      </div>          
    </div>
  </div>
</template>
<script>
import { Auth } from 'aws-amplify';
import {getters, mutations} from '../globalStore.js'
export default ({
    name: "NavBar",
    props: ["allResponsesLink"],
    data() {
      return {
        }
    },
    methods: {
        ...mutations,
        programChanged(programCode) {
          this.setProgram(programCode.target.value);
          this.setDeployment(this.deployments[0]);
          this.setLanguage(this.languages[0].code);
          this.$emit('contextChanged')
        },
        deploymentChanged(deployment) {
          this.setDeployment(deployment.target.value);
          if (!this.languages.map(l=>l.code).includes(this.context.selectedLanguageCode)) {
            this.context.selectedLanguageCode = this.languages[0].code;
          }
          this.$emit('contextChanged')
        },
        languageChanged(language) {
          this.setLanguage(language.target.value)
          this.$emit('contextChanged')
        },
        async logout() {
            try {
                await Auth.signOut();
                this.$router.push('Login');
            } catch (error) {
                console.log(error.message);
            }
        },

    },
    computed: {
        ...getters,
        deployments() {
          // console.log("deployments computed:");
          // console.log(this.programs);
          // console.log(this.context);
            let deployments = this.programs.filter(p=>p.code==this.context.selectedProgramCode)[0]
                                        .deployments.map(d=>d.number);
          return deployments;
        },
        languages() {
          let program = this.programs.filter(p=>p.code==this.context.selectedProgramCode)[0];
          let languageCodes = program.deployments.filter(d=>d.number==this.context.selectedDeployment)[0].languages;
          let languages = program.languages.filter(l=>languageCodes.includes(l.code));
          return languages;
        },
        navRoutes() {
            var navRoutes = [];
            for (var route of this.$router.options.routes) {
                if(route.hasOwnProperty('menu') & route.menu) {
                    if (this.$route.path==route.path) {
                        route.current = true;
                    }
                    navRoutes.push(route);
                }
            }
            return navRoutes;
        }
    }
})
</script>
<style scoped>

.navbar {
  background-color:#289B6A;
  color:white;
  font-size:1.15em;
  font-weight:bolder;
  text-align:left;
  line-height:40px;
  width:100vmax;
  vertical-align:middle;
}

.router-link-active {
    text-decoration: underline;
    text-decoration-thickness: 2px;
}
</style>
<template>
  <div>
    <div class="navbar grid grid-cols-10 justify-items-start content-end">
      <span class="text-3xl col-start-2 col-span-1 row-start-1 row-span-1 pb-0">AMPLIO</span>
      <router-link class="pt-4 text-2xl col-start-3 col-span-1 row-start-1 row-span-1" :to="'/analyze?email='+email+'&program='+programCode+'&language='+languageCode+'&deployment='+deployment">
        Analyze
      </router-link>
      <router-link class="pt-4 text-2xl col-start-4 col-span-1 row-start-1 row-span-1" :to="'/review?email='+email+'&program='+programCode+'&language='+languageCode+'&deployment='+deployment">
        Review
      </router-link>
      <select v-model="programCode" @change="$emit('progChanged',programCode)" class="col-start-7 col-span-2 justify-self-end my-4 outline-grey text-black text-lg w-64">
        <option v-for="program in programs" :value="program.code" :key="program.code">
          <span> {{program.name}}</span>
        </option>
      </select>
      <a @click="logout" class="col-start-9 col-end-11 justify-self-center pt-4 text-2xl text-white font-bold whitespace-nowrap rounded cursor-pointer hover:text-gray-500">Logout</a>
    </div>
    <div class="grid grid-cols-10 justify-items-start content-end pb-8">
      <div v-if="allResponsesLink" @click="$emit('all')" class="row-start-2 col-start-3 col-span-2 cursor-pointer pt-4 text-2xl underline" style="color:#0000ee;font-weight:bold" >
          View all responses    
      </div>
      <div class="row-start-2 col-start-5 col-span-4 justify-self-end pt-4">
          Deployment 
          <select v-model="deployment" class="outline-grey w-16 mr-8" @change="$emit('deplChanged',deployment)">
              <option v-for="deployment in deployments" :value="deployment" :key="deployment"><span> {{deployment}}</span></option>
          </select>
          Language 
          <select v-model="languageCode" class="outline-grey" @change="$emit('langChanged',languageCode)">
              <option v-for="language in languages" :value="language.code" :key="language.code"><span> {{language.name}}</span></option>
          </select>
      </div>          
    </div>
  </div>
</template>
<script>
import { Auth } from 'aws-amplify';

export default ({
    name: "NavBar",
    props: ["email","programs","selectedProgramCode","deployments","languages","selectedDeployment","selectedLanguageCode","allResponsesLink"],
    data() {
      return {
        programCode: '',      
        deployment:'',
        languageCode:''
        }
    },
    methods: {
        async logout() {
            try {
                await Auth.signOut();
                this.$router.push('Login');
            } catch (error) {
                console.log(error.message);
            }
        },

    },
    mounted() {
        this.programCode = this.selectedProgramCode;
        this.deployment = this.selectedDeployment;
        this.languageCode = this.selectedLanguageCode;
    },
    computed: {
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
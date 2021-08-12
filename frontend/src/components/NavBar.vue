<template>
  <div>
    <div class="navbar">
      <span class="text-3xl px-10">AMPLIO</span>
      <router-link class="px-20 text-2xl" v-for="route in navRoutes" :key="route.path" :to="route.path+'?email='+email+'&program='+programCode+'&language='+languageCode+'&deployment='+deployment">
        {{route.name}}
      </router-link>
      <span class="absolute right-10">
        <select v-model="programCode" @change="$emit('progChanged',programCode)" class="outline-grey text-black text-base mr-16 w-64">
          <option v-for="program in programs" :value="program.code" :key="program.code">
            <span> {{program.name}}</span>
          </option>
        </select>
        <a @click="logout" class="text-2xl text-white font-bold whitespace-nowrap rounded cursor-pointer hover:text-gray-500">Logout</a>
      </span>
    </div>    
    <div class="float-left">
        <div v-if="allResponses" @click="$emit('all')" style="color:#0000ee;font-weight:bold" class="cursor-pointer text-2xl underline">View all responses</div>    
    </div>
    <div class="float-right">
        Deployment 
        <select v-model="deployment" class="mt-3 mr-24 outline-grey" @change="$emit('deplChanged',deployment)">
            <option v-for="deployment in deployments" :value="deployment" :key="deployment"><span> {{deployment}}</span></option>
        </select>
        Language 
        <select v-model="languageCode" class="outline-grey" @change="$emit('langChanged',languageCode)">
            <option v-for="language in languages" :value="language.code" :key="language.code"><span> {{language.name}}</span></option>
        </select>
    </div>          
  </div>
</template>
<script>
import { Auth } from 'aws-amplify';

export default ({
    name: "NavBar",
    props: ["email","programs","selectedProgramCode","deployments","languages","selectedDeployment","selectedLanguageCode","allResponses"],
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
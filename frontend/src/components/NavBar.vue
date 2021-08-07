<template>
  <div class="navbar">
    <span>AMPLIO</span>
    <span class="text-2xl">Analysis</span>
    <span>
      <select v-model="programCode" @change="$emit('changed',programCode)" class="outline-grey text-black text-base">
        <option v-for="program in programs" :value="program.code" :key="program.code">
          <span> {{program.name}}</span>
        </option>
      </select>
      <a @click="logout" class="text-2xl text-white font-bold whitespace-nowrap rounded cursor-pointer hover:text-gray-500">Logout</a>
    </span>
  </div>
    
</template>
<script>
import { Auth } from 'aws-amplify';

export default ({
    name: "NavBar",
    props: ["programs","selectedProgramCode"],
    data() {
      return {
        programCode: ''      
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
    }

})
</script>

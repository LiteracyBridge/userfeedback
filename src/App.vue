<template>
  <div id="app">
    <img alt="Amplio logo" src="./assets/logo.png" width="256" height="40" />
    <router-view />
  </div>
</template>

<script>
import { Auth } from 'aws-amplify';

export default {
  name: "App",
  data() {
    return {
      signedIn: false,
      user_email:"",
    };
  },
  methods: {
    async isUserSignedIn() {
      try {
          const userObj = await Auth.currentAuthenticatedUser();
          this.user_email=userObj['attributes']['email'];
          this.signedIn = true;
          this.$router.push({ path: '/app', query: { email: this.user_email } })
      }
      catch (err) {
          this.signedIn = false;
          console.log(err);
          this.$router.push({ path: '/login' });
          }
    }
  },
  created() {
    this.isUserSignedIn();
  },  
  computed: {
    isLoggedIn() {
      return this.signedIn;
    }  
  }
};
</script>

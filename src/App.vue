<template>
  <div id="app">
    <img alt="Amplio logo" src="./assets/logo.png" width="256" height="40" />
    <router-view />
  </div>
</template>

<script>

export default {
  name: "App",
  created() {
    this.$router.push({ path: '/login' });
  },  
};
</script>

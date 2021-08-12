<template>
  <div id="app" width="100%">
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

<style>
#app {
  font-family: Helvetica, Avenir, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin: 0;
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


</style>
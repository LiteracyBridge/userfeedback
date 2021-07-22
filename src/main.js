import Vue from 'vue'
import App from './App.vue'
import './assets/main.css'

import Amplify from 'aws-amplify'
import awsconfig from './aws-exports';
import router from './router'

// Custom plugins
import './plugins/fontawesome'

try {
Amplify.configure(awsconfig);
} catch (err) {
  console.log(err);
}
Vue.config.productionTip = false

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')


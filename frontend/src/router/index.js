import Vue from 'vue'
import VueRouter from 'vue-router'
//import Home from '../views/Home.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/app',
    name: 'Analyze',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "analyze" */ '../views/Analyze.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () =>
        import(/* webpackChunkName: "login" */ '../views/Login.vue'),
},
{
  path: '/register',
  component: () => import(/* webpackChunkName: "sign-up" */ '../views/SignUp.vue'),
  meta: {
    layout: 'login'
  }
},
{
  path: '/password-reset',
  component: () => import(/* webpackChunkName: "password-reset" */ '../views/PasswordReset.vue'),
  meta: {
    layout: 'login'
  },
}
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router

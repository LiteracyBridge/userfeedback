<template>
    <div class="container" v-if="displayLogin">
        <form @submit.prevent="login">
            <h2>Login</h2>
            <input
                type="email"
                v-model="email"
                placeholder="Email address..."
            />
            <input
                type="password"
                v-model="password"
                placeholder="password..."
            />
            <button>Login</button>
        </form>
    </div>
</template>

<script>
import { Auth } from 'aws-amplify';
import Vue from 'vue'

export default {
    name: 'Login',
    data() {
        return {
            email: '',
            password: '',
            displayLogin: false
        };
    },
    methods: {
        async login() {
            try {
                const user = await Auth.signIn(this.email, this.password);
                console.log('user', user);
                this.isUserSignedIn();
            } catch (error) {
                alert(error.message);
            }
        },
        async isUserSignedIn() {
            try {
                const userObj = await Auth.currentAuthenticatedUser();
                this.$user_email = userObj['attributes']['email'];
                Vue.prototype.$token = userObj['signInUserSession']['idToken']['jwtToken']
                console.log('Token ending: '+this.$token.substr(this.$token.length-5,4));
                this.displayLogin = false;
                this.$router.push({ path: '/app', query: { email: this.$user_email } })
                console.log('User email: '+this.$user_email);
            }
            catch (err) {
                this.displayLogin = true;
                console.log(err);
            }
        }
    },
    created() {
        this.isUserSignedIn();
    }
};
</script>

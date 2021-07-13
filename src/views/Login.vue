<template>
    <div>
      <div class="login" v-if="displayLogin" width="100%">
        <table><tr><td><img alt="Amplio logo" src="../assets/logo.png" width="256" height="40" /></td></tr>
        <tr><td>
        <form @submit.prevent="login">
            <p style="font-size:1.5em">User Feedback Processing</p>
            <div>Email Address</div>
            <input
                type="email"
                v-model="email"
                placeholder="Email address..."
            /><div>Password</div>
            <input
                type="password"
                v-model="password"
                placeholder="password..."
            /><p/>
            <button>Login</button>
        </form>
        </td></tr>
        </table>
      </div>
      <div width="100%" class="bottombar">Copyright 2021 AMPLIO NETWORK</div>
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
                alert(err);
                console.log(err);
            }
        }
    },
    created() {
        this.isUserSignedIn();
    }
};
</script>

<style scoped>
.login {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 90vh;
    text-align:center;
}

.bottombar {
    background-color:#289B6A;
    color:white;
    font-size:0.6em;
    text-align:center;
    line-height:40px;
    vertical-align:middle;
}

</style>
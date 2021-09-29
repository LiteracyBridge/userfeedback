<template>
    <div>
      <div class="login" v-if="displayLogin" width="100%">
    <div class="mx-auto pt-20" style="max-width:300px;">
        <img alt="Amplio logo" src="../assets/logo.png" class="mx-auto" />
        <p class="mt-3"  style="font-size:1.5em">User Feedback Processing</p>
        <div class="mt-5 p-6 bg-white rounded-lg shadow-box">
        <form @submit.prevent="login">
                <v-input
                ref="user"
                type="text"
                icon-left="user-circle"
                name="emailAddress"
                label="Email address"
                class="my-6"
                :value="emailInput"
                @input="emailInput = $event.target.value"
                />
                <v-input
                type="password"
                name="password"
                label="Password"
                class="mt-6 mb-2"
                :value="password"
                @input="password = $event.target.value"
                />
                <p/>
                <VButton
                    type="submit"
                    label="Sign In"
                    variant="success full"
                    
                />
        </form>
        <div v-if="loginError">
            <span style="color:red;font-weight:bolder">Invalid email/password</span>
        </div>
        <div v-if="noPrograms">
            <span style="color:red;font-weight:bolder">Sorry, but you do not currently have access to a program that is configured for User Feedback Processing.</span>
        </div>

      </div>
      <!-- <p class="text-sm mt-4">
        No account? <router-link class="text-green font-bold" to="/register">Sign Up</router-link>
      </p> -->

    </div>
      </div>
      <div width="100%" class="bottombar">&copy; 2021 AMPLIO NETWORK</div>
    </div>
</template>

<script>
import { Auth } from 'aws-amplify';
import Vue from 'vue';
import VInput from '@/components/VInput';
import VButton from '@/components/VButton';
import {actions, getters,mutations} from '../globalStore.js'


export default {
    components: {
        VInput,
        VButton
    },        
    name: 'Login',
    data() {
        return {
            emailInput: '',
            password: '',
            displayLogin: false,
            loginError: false,
            noPrograms: false
        };
    },
    methods: {
        ...mutations,
        ...actions,
        async login() {
            try {
                console.log("signing in")
                const user = await Auth.signIn(this.emailInput, this.password);
                this.loginError = false;
                this.isUserSignedIn();
            } catch (error) {
                this.loginError = true;
                console.log("ERROR in login():");
                console.log(error.message);
            }
        },
        async isUserSignedIn() {
            try {
                const userObj = await Auth.currentAuthenticatedUser();
                this.setLoginEmail(userObj['attributes']['email']);
                Vue.prototype.$token = userObj['signInUserSession']['idToken']['jwtToken']
                this.displayLogin = false;
                var atLeastOneProgram = await this.getProgramsAndContext();
                if (atLeastOneProgram) {
                    this.$router.push({ path: '/analyze'})
                } else {
                    this.displayLogin = true;
                    this.noPrograms = true;
                    try {
                        await Auth.signOut();
                    } catch (error) {
                        console.log(error.message);
                    }
                    setTimeout(()=> {
                        this.noPrograms = false;
                    },5000);            
                }
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
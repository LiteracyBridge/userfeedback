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
                :value="email"
                @input="email = $event.target.value"
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
                    @click="login"
                />
        </form>
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


export default {
    components: {
        VInput,
        VButton
    },        
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
                this.isUserSignedIn();
            } catch (error) {
                console.log(error.message);
            }
        },
        async isUserSignedIn() {
            try {
                const userObj = await Auth.currentAuthenticatedUser();
                this.$user_email = userObj['attributes']['email'];
                Vue.prototype.$token = userObj['signInUserSession']['idToken']['jwtToken']
                // console.log('Token ending: '+this.$token.substr(this.$token.length-5,4));
                this.displayLogin = false;
                this.$router.push({ path: '/analyze', query: { email: this.$user_email } })
            }
            catch (err) {
                this.displayLogin = true;
                // alert(err);
                console.log(err);
            }
        }
    },
    created() {
        console.log(this.$route);
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
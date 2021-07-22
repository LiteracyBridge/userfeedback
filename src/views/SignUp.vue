<template>
  <main class="container mx-auto pt-4 text-center">
    <slot />

    <h1 class="visually_hidden">Register into Amplio-Suite</h1>

    <div class="mx-auto pt-20" style="max-width:300px;">
      <img src="/img/logo.png" alt="Amplio logo" class="mx-auto">

      <div class="mt-5 p-6 bg-white rounded-lg shadow-box">
        <form v-on:submit.prevent>
          <v-input
            ref="name"
            type="text"
            icon-left="user-circle"
            name="fullName"
            label="Full Name"
            class="my-0"
            :value="fullName"
            @input="fullName = $event.target.value"
          />

          <v-input
            type="email"
            name="email"
            label="Email"
            class="my-6"
            :value="email"
            @input="email = $event.target.value"
          />

          <v-input
            type="email"
            name="emailCorfimation"
            label="Email confirmation"
            class="my-6"
            :value="emailConfirmation"
            @input="emailConfirmation = $event.target.value"
          />

          <v-input
            type="password"
            name="password"
            label="Password"
            class="my-6"
            :value="password"
            @input="password = $event.target.value"
          />

          <VButton
            type="submit"
            label="Register"
            variant="success full"
            :iconL="status === 'loading' ? 'spinner' : ''"
            :iconLPulse="status === 'loading'"
            @click="handleRegister"
          />
        </form>
      </div>

      <p class="text-sm mt-4">
        Already have login and password? <router-link class="text-green font-bold" to="/login">Sign in</router-link>
      </p>
    </div>
  </main>
</template>

<script>
import { mapState, mapActions } from 'vuex'

import VButton from '@/components/VButton'
import VInput from '@/components/VInput'

export default {
  components: {
    VButton,
    VInput
  },
  computed: {
    ...mapState('account', [
      'status'
    ]),
  },
  data () {
    return {
      fullName: '',
      email: '',
      emailConfirmation: '',
      password: ''
    }
  },
  methods: {
    ...mapActions('ui', [
      'setNotification'
    ]),
    ...mapActions('account', [
      'register'
    ]),
    async handleRegister () {
      try {
        await this.register({ email: this.email, password: this.password })
        this.setNotification({ type: 'notice', text: 'Check your email and copy the validation code' })
        this.$router.push('/login')
      }
      catch (error) {
        this.fullName = ''
        this.email = ''
        this.emailConfirmation = ''
        this.password = ''

        if (error === 'Not fill') {
          this.setNotification({ type: 'alert', text: 'All fields are required' })
        } else if (error.code === 'InvalidPasswordException') {
          this.setNotification({ type: 'alert', text: error.message })
        } else if (error.code === 'UserLambdaValidationException') {
          this.setNotification({ type: 'alert', text: 'The email address provided does not match our records in the system. Please contact support@amplio.org' })
        } else {
          this.setNotification({ type: 'alert', text: error.message })
        }

        this.$refs.name.$el.children[1].focus()
      }
    }
  }
}
</script>

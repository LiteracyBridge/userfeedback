<template>
  <div :class="[isFocus ? 'focused' : '', mx]"  class="relative w-64 my-2 text-base bg-white field-wrapper">
    <div v-if="iconLeft" class="absolute left-0 pl-5 pt-2 pointer-events-none">
      <font-awesome-icon :icon="iconLeft" class="w-6 h-6 text-gray-500" />
    </div>
    <div v-if="iconRight" class="absolute right-0 pr-5 pt-2 pointer-events-none">
      <font-awesome-icon :icon="iconRight" class="w-6 h-6 text-gray-500" />
    </div>

    <label
      v-if="label"
      :for="name === '' ? false : name"
      :style="{ left: iconLeft ? '40px' : '10px' }"
      class="absolute inline-block px-2 bg-white text-label"
    >
      {{ label }}
    </label>
    <input
      :class="[iconLeft ? 'pl-12' : 'pl-5', iconRight ? 'pr-12' : 'pr-5']"
      class="w-full block py-2 rounded border border-solid border-gray-500 focus:outline-none focus:shadow-outline"
      :value="value"
      :name="name === '' ? false : name"
      :id="name === '' ? false : name"
      v-bind="$attrs"
      v-on="$listeners"
      @focus="isFocus = true"
      @blur="handleBlur"
    >
  </div>
</template>

<script>
export default {
  inheritAttrs: false,
  props: {
    value: [String, Number],
    iconLeft: {
      type: String,
      default: ''
    },
    iconRight: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: ''
    },
    name: {
      type: String,
      default: ''
    },
    mx: {
      type: String,
      default: 'mx-auto'
    }
  },
  data () {
    return {
      isFocus: false
    }
  },
  mounted () {
    if (this.value !== '') this.isFocus = true
  },
  watch: {
    value () {
      if (this.value !== '') this.isFocus = true
      else this.isFocus = false
    }
  },
  methods: {
    handleBlur () {
      if (!this.value) this.isFocus = false
    }
  }
}
</script>

<style scoped>
.field-wrapper.focused label {
  top: -20px;
  font-size: 0.8rem;
  color: black;
  transition: all .2s linear;
}

label {
  overflow: hidden;
  top: 2px;
  margin: 8px 5px;
  font-size: 1em;
  line-height: 1.4em;
  text-transform: capitalize;
  transition: all .2s linear;
}

input {
  filter: none;
}
</style>

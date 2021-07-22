<template>
  <component
    :is="tag"
    role="button"
    tabindex="0"
    :disabled="disabled"
    :aria-disabled="disabled"
    :aria-label="label ? label : ariaLabel"
    :class="[baseClass, variant, active ? 'active' : '', colors]"
    class="items-right"
    @click="handleClick"
    @keyup.enter="handleClick"
    @keyup.space="handleClick"
  >
    <font-awesome-icon
      v-if="iconL"
      :icon="iconL"
      :pulse="iconLPulse"
      :class="[label ? 'mr-2' : '']"
      class="w-6 h-6"
    />
    {{ label }}
    <font-awesome-icon
      v-if="iconR"
      :icon="iconR"
      :pulse="iconRPulse"
      :class="[label ? 'ml-2' : '']"
      class="w-6 h-6"
    />
  </component>
</template>

<script>
export default {
  props: {
    tag: {
      type: String,
      default: 'button',
    },
    variant: {
      type: String,
      default: 'default',
    },
    colors: {
      type: String,
      default: '',
    },
    label: {
      type: String,
      default: '',
    },
    ariaLabel: {
      type: String,
      default: '',
    },
    active: {
      type: Boolean,
      default: true
    },
    disabled: {
      type: Boolean,
      default: false
    },
    iconL: {
      type: String,
      default: '',
    },
    iconLPulse: {
      type: Boolean,
      default: false,
    },
    iconR: {
      type: String,
      default: '',
    },
    iconRPulse: {
      type: Boolean,
      default: false,
    }
  },
  computed: {
    baseClass () {
      return this.label === '' ? 'icon'
        : this.tag === 'button' ? 'button'
          : 'link'
    },
  },
  methods: {
    handleClick () {
      if (!this.disabled) this.$emit('click')
    }
  }
}
</script>

<style scoped>
.button,
.link,
.icon {
  @apply transition duration-200;
}

.button {
  @apply px-5 py-2 justify-center border rounded-lg;
}
/* .button:hover {
  @apply shadow-button;
} */
.button.full {
  @apply w-full;
}
.button.default {
  @apply text-black bg-transparent border-black;
}
.button.default:hover {
  @apply bg-gray-200;
}
.button.success {
  @apply text-white bg-green;
}
.button.submit {
  @apply text-white bg-blue;
}
.button.warning {
  @apply text-white bg-red-500;
}
.button.warning:hover {
  @apply bg-red-600;
}
.button.warning-ligth {
  @apply text-red-500 bg-transparent border-red-500;
}

.button:disabled,
.button[disabled],
.button:disabled:hover,
.button[disabled]:hover {
  box-shadow: none;
  @apply text-white bg-gray-400 border-gray-400 cursor-not-allowed;
}

.link {
  white-space: nowrap;
  @apply text-black font-semibold cursor-pointer;
}
.link.active {
  @apply text-blue;
}
.link:hover {
  @apply text-blue underline;
}

.icon {
  @apply w-12 h-10 justify-center border rounded-full;
}
.icon:hover {
  @apply bg-gray-200;
}
/* .icon:hover {
  @apply bg-gray-200 shadow-button;
} */
.icon.warning {
  @apply text-red-500;
}
</style>

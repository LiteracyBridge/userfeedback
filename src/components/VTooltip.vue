<template>
  <div class="relative inline-block text-center border-b border-black border-dotted cursor-pointer">
    <div
      @mouseover="show = true"
      @mouseleave="show = false"
    >
      <slot />
    </div>

    <span
      :class="[show ? 'visible' : 'invisible', position === 'left' ? '-ml-4' : '']"
      class="absolute z-10 p-2 text-sm text-white text-center bg-gray-600 rounded-lg"
      :style="style"
    >
      {{ text }}
    </span>
  </div>
</template>

<script>
export default {
  props: {
    text: {
      type: String,
      required: true
    },
    position: {
      type: String,
      default: 'center',
      validator: (value) => {
        return ['left', 'center', 'right'].indexOf(value) !== -1
      }
    },
    width: {
      type: Number,
      default: 300
    }
  },
  computed: {
    style () {
      const amount = this.position === 'left' ? '0'
        : this.position === 'center' ? '-50%'
          : '-100%'

      return {
        transform: `translateX(${amount})`,
        width: `${this.width}px`,
        bottom: '100%'
      }
    },
  },
  data: () => ({
    show: false
  })
}
</script>

<template>
  <v-btn
    theme="dark"
    elevation="8"
    class="rounded-custom border text-capitalize"
    style="border-color: #424242 !important"
    variant="flat"
    color="#1E1E1E"
    v-bind="$attrs"
  >
    <slot />
  </v-btn>
</template>

<script setup>
// v-bind="$attrs" allows passed props (like @click, to, etc.) to flow through to v-btn
</script>

<style scoped>
.rounded-custom {
  border-radius: 18px !important;
}
</style>
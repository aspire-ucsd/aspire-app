<script>
export default {
    name: 'LoadingWheel',
    friendly_name: "Loading"
}
</script>

<script setup>
import { defineProps } from 'vue';
const props = defineProps(["loadingText"])
</script>

<template>
    <div class="loading-screen">
        <h3>{{ props.loadingText }}</h3>
        <img class="loading-icon" src="/aspire/static/assets/icon-loading.png" />
    </div>
</template>

<style>
.loading-screen {
    height: 100%;
    width:100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.loading-icon {
    max-height: 80%;
    animation: spin 4s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(360deg); }
    100% { transform: rotate(0deg); }
}
</style>
<script setup>
import { ref } from "vue";
import RegisterStart from "../components/registration_frames/RegisterStart.vue"
import RegisterNew from "../components/registration_frames/RegisterNew.vue"
import RegisterTemplate from "../components/registration_frames/RegisterTemplate.vue"
import NewCourseAssistant from "../components/registration_frames/RegisterTemplate.vue"

const step_options = {
    "start": RegisterStart,
    "new": RegisterNew,
    "template": RegisterTemplate,
    "assistant": NewCourseAssistant
}

const registration_step = ref("start")
</script>

<template>
    <div class="registration-root">
        <component 
            :is="step_options[registration_step]" 
            v-model:reg_step="registration_step"
        />
    </div>
</template>


<style scoped>
.registration-root {
    position: relative;
    height: 100%;
}


</style>
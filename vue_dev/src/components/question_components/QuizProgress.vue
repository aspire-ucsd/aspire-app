<script setup >
import { onMounted, ref, defineProps } from 'vue'
import { ProgressIndicator, ProgressRoot } from 'radix-vue'

const props = defineProps(["quizMetaData"])
const progressValue = ref(10)

onMounted(() => {
    const timer = setTimeout(() => (progressValue.value = 66), 500)
    return () => clearTimeout(timer)
})
</script>

<template>
    <ProgressRoot
        :max="props.quizMetaData.quizLength"
        class="progress-root"
        style="transform: translateZ(0)"
    >
        <ProgressIndicator
        class="progress-indicator"
        :style="`transform: translateX(-${100 - (props.quizMetaData.answerCount / props.quizMetaData.quizLength) * 100}%)`"
        />
    </ProgressRoot>
</template>

<style scoped>
.progress-root{
    position: relative;
    width: 100%;
    height: 1rem;
    background-color: rgb(175, 175, 175);
    border-radius: 1rem;
    overflow: hidden;
    
}

.progress-indicator {
    height: 100%;
    width: 100%;
    border-radius: 1rem;
    background-color: rgb(0, 151, 0);
    transition: transform 660ms cubic-bezier(0.65, 0, 0.35, 1);
}
</style>
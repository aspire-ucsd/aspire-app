<script setup>
import {defineEmits, defineModel, defineProps} from "vue"

const emit = defineEmits(["quizEvent"])
const props = defineProps(["questions"])
const metaModel = defineModel()


const allowNewQuestion = () => {
        return (
            !(Object.keys(props.questions).includes((metaModel.value.currentQuestion + 1).toString()))
            &&
            metaModel.value.currentQuestion === metaModel.value.answerCount
        )
    }

const updatePage = (mode="index", newIndex=1) => {
    switch(mode) {
        case "index":
            metaModel.value.currentQuestion = newIndex
            break;
        case "dec":
            console.log(metaModel.value.currentQuestion, metaModel.value.answerCount)
            if (metaModel.value.currentQuestion > 1) {
                metaModel.value.currentQuestion--
            }
            break;
        case "inc":
            if (allowNewQuestion()) {
                emit('quizEvent', {target: 'new-question'})

            } else if (Object.keys(props.questions).includes((metaModel.value.currentQuestion + 1).toString())){
                metaModel.value.currentQuestion++
            }
    }
}

const range = (currentIndex, separation) => {
    const start = currentIndex - separation
    const stop = currentIndex + separation
    let result = Array.from({length: (stop - start) + 1}, (_, index) => start + index)
    return result
}

const pageIsVisible = (index) => {
    const questionsIndexes = Object.keys(props.questions).map(key => parseInt(key))
    return index === 1 || index === Math.max(...questionsIndexes) || range(metaModel.value.currentQuestion, 1).includes(index)
}

</script>

<template>
    <div class="quiz-nav">
        <button class="next-question-btn" @click="emit('quizEvent', {target: 'new-question'})" :style="{'visibility': allowNewQuestion() ? 'visible' : 'hidden'}">Next Question</button>
        <div class="page-root">
            <img 
                class="page-btn-icon" 
                src="/static/assets/icon-double-chevron-left.png"
                @click="() => updatePage('index', 1)"
            />
            <img 
                class="page-btn-icon" 
                src="/static/assets/icon-chevron-left.png"
                @click="() => updatePage('dec')"
            />
            <template 
                v-for="index in Object.keys(props.questions).map(key => parseInt(key)) " 
                :key="index"
            >
                <span
                    v-if="pageIsVisible(index)"
                    :style="{'user-select': 'none', 'font-weight': metaModel.currentQuestion === index ? 'bold' : ''}"
                    @click="() => updatePage('index', index)"
                >
                    {{index}}
                </span>

            </template>
            <img 
                class="page-btn-icon" 
                src="/static/assets/icon-chevron-right.png"
                @click="() => updatePage('inc')"
            />
            <img 
                class="page-btn-icon" 
                src="/static/assets/icon-double-chevron-right.png"
                @click="() => updatePage('index', Math.max(...Object.keys(props.questions).map(key => parseInt(key))))"
            />
        </div>
    </div>
</template>

<style scoped>
.next-question-btn {
    margin: 1rem;
}
.page-root {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
}
.page-btn {
    margin: 0;
    padding: 0;
    border: none;
    background-color: transparent;
    height: 2rem;
    width: 2rem;
}
.page-btn-icon {
    width: 2rem;
    height: 2rem;
    position: relative;
}
</style>
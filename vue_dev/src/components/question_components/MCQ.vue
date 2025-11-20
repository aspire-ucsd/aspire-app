
<script>
export default {
    name: 'MCQ',
    friendly_name: "MCQ"
}
</script>
<script setup>
import {defineModel, defineProps, defineEmits, ref} from "vue"

const emit = defineEmits(["quizEvent"])
const props = defineProps(["quizMetaData"])
const questionsModel = defineModel()
const tempAnswerSelect = ref()
const feedbackVisible = ref(false)  // To control the visibility of the feedback

const updateQuestion = (key, value) => {
    tempAnswerSelect.value = null
    if (!questionsModel.value[props.quizMetaData.currentQuestion].selected_answer) {
        questionsModel.value[props.quizMetaData.currentQuestion][key] = value
        feedbackVisible.value = true  // Show feedback upon submitting an answer
        emit("quizEvent", {target: "submit"})
    }
}

const getBackgroundAndBorder = (answer) => {
    const selected_answer = questionsModel.value[props.quizMetaData.currentQuestion].selected_answer;
    
    if (selected_answer) {
        // Check the feedback field of the selected answer to determine correctness
        if (selected_answer === answer.answer_text) {
            if (answer.feedback === "Correct") {
                return "background-color: #ADFFB0; border: 2px solid #00D823";  // Correct answer (green)
            } else {
                return "background-color: #FFE3E3; border: 2px solid #FF0000";  // Incorrect answer (red)
            }
        }
        // Highlight the correct answer even if it's not selected
        if (answer.feedback === "Correct") {
            return "background-color: #ADFFB0; border: 2px solid #00D823";  // Correct answer (green)
        }
        return "background-color:#D9D9D9; border: 2px solid #D9D9D9";  // Other answers (default gray)
    }

    // If no answer is selected yet, highlight the currently hovered answer
    if (tempAnswerSelect.value === answer.answer_text) {
        return "background-color: #ffffff; border: 2px solid #000000";  // Hovered answer
    }

    return "background-color:#D9D9D9; border: 2px solid #D9D9D9";  // Default style for unselected answers
};


</script>

<template>
    <div class="mcq-main">
        <div class="mcq-question">
            <p style="font-weight: 700; font-size: larger;">
                The following question has been identified by ASPIRE as related to the concept: 
                <span style="font-weight: 400; text-decoration: underline;">{{ questionsModel[props.quizMetaData.currentQuestion].concept }}</span>
            </p>
            <br />
            <p style="font-weight:300; font-size: larger; text-align: center;">{{ questionsModel[props.quizMetaData.currentQuestion].question_text }}</p>
        </div>
        <hr />
        <div class="mcq-answers">
            <p style="margin-top: 0;">Please select one of the following answers:</p>
            <div 
                v-for="answer in questionsModel[props.quizMetaData.currentQuestion].answers"
                :key="answer.answer_id"
                class="answer-item"
                :style="getBackgroundAndBorder(answer)"
                @click="tempAnswerSelect = answer.id"
            >
                <p>{{ answer.answer_text }}</p>
                <button 
                    v-if="tempAnswerSelect === answer.id && !questionsModel[props.quizMetaData.currentQuestion].selected_answer" 
                    @click="() => updateQuestion('selected_answer', answer.id)"
                    class="submit-btn"
                >
                    Submit
                </button>
            </div>
            <!-- General feedback display with heading -->
            <div v-if="feedbackVisible" class="feedback">
                <p style="font-weight: 700; margin-top: 20px;">Feedback:</p>
                <p>{{ questionsModel[props.quizMetaData.currentQuestion].neutral_comments }}</p>
            </div>
        </div>
    </div>
</template>


<style scoped>
.mcq-main {
    display: flex;
    flex-direction: row;
    width: 100%;
    height: 100%;
    align-items: center;
}
.mcq-main > hr {
    border: 1px solid rgb(193, 193, 193);
    border-radius: 1px;
    height: calc(100% - 1rem);
    color: rgb(0, 0, 0);
    margin: 1rem;
    margin-bottom: 0;
}
.mcq-question{
    width: 30%;
    height: 100%;
}
.mcq-answers{
    width: 70%;
    height: calc(100% - 1rem);
    margin-top: 1rem;
    overflow-y: auto;
    scrollbar-width:thin;
}

.answer-item {
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
    padding: 1rem;
    margin-top: 1rem;
}

.submit-btn {
    font-weight: 700;
    border-radius: 4px;
    border: 1px solid #ffffff00;
    background-color: #ADFFB0;
}
.submit-btn:hover {
    border: 1px solid #00D823;
    background-color: #6dff72;
}
.submit-btn:active {
    border: 1px solid #ffffff00;
    background-color: #ADFFB0;
}

.feedback {
    margin-top: 20px;
    font-style: italic;
    color: #333;
}

</style>
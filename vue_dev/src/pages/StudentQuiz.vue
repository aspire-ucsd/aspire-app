<script>
export default {
    name: 'StudentQuiz',
    view: 'student',
    friendly_name: "Module Quizzes",
    icon: "/aspire/static/assets/icon-QuizAuthoring.png",
    props: {
        msg: String
    }
}
</script>

<script setup>
import axios from "axios"
import QuizProgress from "../components/question_components/QuizProgress.vue"
import QuizLoading from "../components/question_components/QuizLoading.vue"
import QuizNav from "../components/question_components/QuizNav.vue"
import MCQ from "../components/question_components/MCQ.vue"
import QuizStart from "../components/question_components/QuizStart.vue"
import { ref, onMounted } from "vue"

const tabs = { MCQ, QuizStart, QuizLoading }
const currentComp = ref("QuizLoading")
const selectedQuizId = ref(null)
const questions = ref({})
const quizMetaData = ref({})
const lastQuestionMessage = ref("")  // Store the message here

onMounted(() => {
    // Hardcoded quizLength = 5
    quizMetaData.value = {
        answerCount: 0,
        quizLength: 5,
        currentQuestion: null,
    }

    setTimeout(() => {
        currentComp.value = "QuizStart"
    }, 2000)
})

const getNewQuestion = async (quizId) => {
    const questionsIndex = Object.keys(questions.value).length + 1;

    try {
        const response = await axios.post(`http://localhost:8080/qas/quiz/personal/{module_id}/{quiz_type}/question?quiz_id=${quizId}`, {});

        if (response.data && response.data.question && response.data.answers) {
            const questionData = response.data.question;
            const answersData = response.data.answers;

            questions.value[questionsIndex] = {
                question_text: questionData.question_text,
                selected_answer: null,
                question_type: "MCQ",
                concept: questionData.question_name,
                answers: answersData.map(answer => ({
                    answer_text: answer.answer_text,
                    feedback: answer.answer_weight > 0 ? "Correct" : "Incorrect"
                })),
                neutral_comments: questionData.neutral_comments
            };

            return questionsIndex;
        }
    } catch (error) {
        console.error("Failed to fetch question:", error);
    }
}

const eventHandler = async (event) => {
    console.log("Event triggered:", event.target);  // Log the event type

    switch (event.target) {
        case "new-question": {
            console.log("Handling new question event...");

            // Log the current state of selectedQuizId and event.quizId
            console.log("Current selectedQuizId:", selectedQuizId.value);
            console.log("Event quizId (from event):", event.quizId);

            // If selectedQuizId.value is null, use event.quizId and update selectedQuizId
            if (!selectedQuizId.value && event.quizId) {
                selectedQuizId.value = event.quizId;
                console.log("Updated selectedQuizId:", selectedQuizId.value);
            }

            // Ensure the currentQuestion does not exceed quizLength
            if (quizMetaData.value.currentQuestion >= quizMetaData.value.quizLength) {
                lastQuestionMessage.value = "This is the last question.";  // Set the message
                return;
            }

            // Use the selected quiz ID for fetching the new question
            const quizId = selectedQuizId.value;

            if (!quizId) {
                console.error("Quiz ID is null. Please select a quiz before proceeding.");
                return;
            }

            console.log("Starting quiz with Quiz ID:", quizId);
            currentComp.value = "QuizLoading";

            // Fetch the new question using the resolved quizId
            try {
                const questionIndex = await getNewQuestion(quizId);
                quizMetaData.value.currentQuestion = questionIndex;
                console.log("Successfully fetched new question. Current question index:", questionIndex);

                setTimeout(() => {
                    currentComp.value = "MCQ";
                    console.log("Switched to MCQ component");
                }, 2000);
            } catch (error) {
                console.error("Error fetching new question:", error);
            }

            break;
        }

        case "submit": {
            console.log("Handling submit event...");
            quizMetaData.value.answerCount++;
            console.log("Answer count updated:", quizMetaData.value.answerCount);
            break;
        }

        case "quiz-selected": {
            // You can still log when the quiz is selected but no longer update selectedQuizId here
            console.log("Handling quiz-selected event...");
            console.log("Quiz ID received from event:", event.quizId);
            break;
        }
    }
}
</script>

<template>
    <div class="quiz-tab">
        <QuizProgress 
            v-if="currentComp === 'MCQ'"
            :quiz-meta-data="quizMetaData"
        />

        <!-- Show the message if the user is on the last question -->
        <p v-if="lastQuestionMessage" style="font-weight: bold; color: red; text-align: center;">
            {{ lastQuestionMessage }}
        </p>

        <component 
            class="quiz-comp"
            :is="tabs[currentComp]" 
            @quiz-event="eventHandler"
            v-model="questions"
            :quiz-meta-data="quizMetaData"
            :general-feedack="questions[quizMetaData.currentQuestion]?.neutral_comments"
        >
        </component>

        <hr v-if="currentComp === 'MCQ'" />

        <QuizNav
            style="height: 7.5%;" 
            v-if="currentComp === 'MCQ'"
            @quiz-event="eventHandler"
            :questions="questions"
            v-model="quizMetaData"
        />
    </div>
</template>

<style scoped>
.quiz-tab {
    display: flex;
    flex-direction: column;
    height: 100% !important;
    width: 100%;
    min-height: 100% !important;
    background-color: white;
    padding: 1rem;
    border-radius: 8px;
    align-items: center;
}

.quiz-tab  > hr {
    border: 1px solid rgb(193, 193, 193);
    border-radius: 1px;
    width: calc(100% - 1rem);
    color: rgb(0, 0, 0);
    margin: 1rem;
    margin-bottom: 0;
}

.quiz-comp {
    height: 85%;
}
</style>

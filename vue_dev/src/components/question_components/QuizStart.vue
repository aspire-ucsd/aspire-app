<template>
    <div class="quiz-container">
      <div class="quiz-info">
        <header class="quiz-header">
          <h1 class="title">Welcome to Your Personalized Quiz!</h1>
          <h2 class="subtitle">A Journey Through Learning Tailored Just for You</h2>
        </header>
        <section class="quiz-intro">
          <p class="intro-text">
            Get ready to strengthen your knowledge! This quiz is designed to guide you through a customized learning experience.
            We'll start by revisiting essential prerequisites, dive into core topics, and conclude with a review to solidify your understanding.
          </p>
        </section>
        <section class="quiz-structure">
          <h3 class="structure-heading">What to Expect:</h3>
          <ul class="structure-list">
            <li class="quiz-section"><span class="bold-text">Prerequisite Questions:</span> These questions will refresh and reinforce key foundational concepts, helping you prepare for new material with confidence.</li>
            <li class="quiz-section"><span class="bold-text">Preview Questions:</span> Designed to challenge your current level of understanding, these questions introduce upcoming topics, giving you a head start on what's to come.</li>
            <li class="quiz-section"><span class="bold-text">Review Questions:</span> These questions help solidify your knowledge after completing the module, ensuring you're ready to apply what you've learned.</li>
          </ul>
        </section>
        <section class="quiz-instructions">
          <h3 class="instructions-heading">How to Begin:</h3>
          <p class="instructions-text">
            Select a module and Click ‘Start Quiz’ when you’re ready. Remember, this quiz is all about learning—take your time and do your best!
          </p>
          <p class="instructions-note">
            You can navigate between questions, but try to answer each one before moving on. Your progress will be saved as you go.
          </p>
        </section>
      </div>
  
      <div class="quiz-list">
        <AccordionRoot class="quiz-accordion-container" type="single" :collapsible="true">
          <h3 class="quiz-list-heading">Available Quizzes</h3>
          <template v-for="(moduleQuizzes, moduleId) in groupedQuizzes" :key="moduleId">
            <AccordionItem class="quiz-accordion-item" :value="moduleId">
              <AccordionHeader class="quiz-accordion-header">
                <AccordionTrigger class="quiz-accordion-trigger">
                  <span>Module ID: {{ moduleId }}</span>
                  <img src="/static/assets/icon-chevron.png" class="dropdown-btn-icon" :class="{ 'hover': hover }"/>
                </AccordionTrigger>
              </AccordionHeader>
              <AccordionContent class="quiz-accordion-content">
                <AccordionRoot class="nested-accordion" type="single" :collapsible="true" v-model="activeQuizId">
                  <template v-for="quiz in moduleQuizzes" :key="quiz.quiz_id">
                    <AccordionItem class="nested-accordion-item" :value="quiz.quiz_id">
                      <AccordionHeader class="nested-accordion-header">
                        <AccordionTrigger class="nested-accordion-trigger" @click="activeQuizId = quiz.quiz_id">
                          Quiz Type: {{ quiz.quiz_type }}
                        </AccordionTrigger>
                      </AccordionHeader>
                      <AccordionContent class="nested-accordion-content">
                        <p><strong>Number of Questions:</strong> {{ quiz.n_questions }}</p>
                        <p><strong>Due Date:</strong> {{ formatDate(quiz.due_date) }}</p>
                        <button @click="emit('quizEvent', {target: 'new-question', quizId: quiz.quiz_id})">Start Quiz</button>
                      </AccordionContent>
                    </AccordionItem>
                  </template>
                </AccordionRoot>
              </AccordionContent>
            </AccordionItem>
          </template>
        </AccordionRoot>
      </div>
    </div>
  </template>
  
  <script setup>
  import axios from 'axios';
  import { ref, computed, onMounted } from 'vue';
  import { AccordionContent, AccordionHeader, AccordionItem, AccordionRoot, AccordionTrigger } from 'radix-vue';
  
  const quizzes = ref([]);
  const groupedQuizzes = computed(() => {
    const groups = {};
    quizzes.value.forEach(quiz => {
      if (!groups[quiz.module_id]) {
        groups[quiz.module_id] = [];
      }
      groups[quiz.module_id].push(quiz);
    });
    return groups;
  });
  const activeQuizId = ref(null);
  const emit = defineEmits(["quizEvent"]);
  let hover = ref(false);
  
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Intl.DateTimeFormat('en-US', options).format(new Date(dateString));
  };
  
  async function fetchQuizzes() {
    try {
      const response = await axios.get('http://localhost:8080/aspire_quiz/aspire_quiz/get_all_open_quizzes_for_student');
      quizzes.value = response.data || [];
    } catch (error) {
      console.error('Error fetching quizzes:', error);
    }
  }
  
  onMounted(fetchQuizzes);
</script>

<style scoped>
:root {
    --core-primary: #0056b3; /* Primary color for backgrounds */
    --accent-primary: #ffffff; /* Primary accent color for text */
    --bg-color: #f7f7f7; /* Background color */
}

.quiz-container {
    display: flex;
    height: 100vh;
}

.quiz-info, .quiz-list {
    height: 100%;
}

.quiz-info {
    flex: 2;
    padding: 2vw;
    border-right: 1px solid #ccc;
    overflow-y: auto;
}

.quiz-list {
    flex: 1;
    padding: 2vw;
    overflow-y: auto;
}

.quiz-header .title {
    font-size: 2.5rem;
    color: var(--core-primary);
    margin-bottom: 0.5rem;
}

.quiz-header .subtitle {
    font-size: 1.8rem;
    color: var(--core-primary);
    margin-bottom: 2rem;
}

.quiz-intro .intro-text {
    font-size: 1.1rem;
    line-height: 1.5;
    margin-bottom: 2rem;
    color: #333;
}

.quiz-structure .structure-heading {
    font-size: 1.4rem;
    color: var(--core-primary);
    margin-bottom: 1rem;
}

.quiz-instructions .instructions-heading {
    font-size: 1.4rem;
    color: var(--core-primary);
    margin-bottom: 1rem;
}

.quiz-structure .structure-list {
    list-style-type: disc;
    padding-left: 1.5rem;
    color: #555;
}

.quiz-section {
    margin-bottom: 1rem;
}

.quiz-instructions .instructions-text {
    font-size: 1.2rem;
    margin-bottom: 1rem;
    color: #333;
}

.quiz-instructions .instructions-note {
    font-size: 1rem;
    color: #777;
}

.quiz-accordion-container {
    width: 100%;
    height: auto; /* Adjust based on your layout needs */
    overflow: hidden;
}

.quiz-accordion-item {
    background-color: var(--bg-color);
}

.quiz-accordion-header {
    margin: 0;
    width: 100%;
}

.quiz-accordion-trigger {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 20px;
    border: none;
    height: 2rem; /* Ensure consistent height */
    background-color: var(--core-primary);
    color: var(--accent-primary);
    font-weight: bold;
    cursor: pointer;
    width: 100%;    
}

.quiz-accordion-trigger[data-state="open"] .dropdown-btn-icon,
.quiz-accordion-trigger[data-state="closed"] .dropdown-btn-icon {
    transition: transform 300ms linear;
}

.quiz-accordion-content[data-state="open"] {
    border: 2px solid var(--core-primary); /* Visible border when the item is open */
}

.bold-text {
    font-weight: bold; /* Make the text bold */
}

.dropdown-btn-icon {
    height: 32px;  /* Set the height of the icon */
    width: 32px;   /* Set the width of the icon */
    object-fit: contain; /* Keeps the aspect ratio of the icon */
    transition: transform 0.3s ease;
}


.quiz-accordion-trigger[data-state="open"] .dropdown-btn-icon {
    transform: rotate(180deg);
}

.quiz-accordion-trigger[data-state="closed"] .dropdown-btn-icon {
    transform: rotate(0deg);
}

.quiz-accordion-content {
    scrollbar-color: var(--accent-primary) var(--bg-color);
    scrollbar-width: thin;
    overflow-y: scroll;
    overflow-x: hidden;
    padding: 0.5rem; /* Padding inside content area */
    transition: border 300ms ease-in-out; /* Smooth transition for border appearance */
}

.quiz-accordion-content p {
    font-size: 1rem; /* Adjust the font size */
    color: var(--core-primary); /* Use the primary color for text */
    margin-bottom: 0.5rem; /* Space between paragraphs */
    line-height: 1.5; /* Improve readability */
}

.quiz-accordion-content strong {
    font-weight: bold; /* Make labels bold */
    color: var(--accent-primary); /* Use accent color for labels */
    margin-right: 0.5rem; /* Space after label before value */
}

button {
    display: block; /* Make the button a block element to apply margin auto */
    margin: 20px auto 0; /* Top margin of 20px, auto horizontally centers it, 0 on the bottom */
    padding: 10px 20px; /* Padding inside the button */
    background-color: var(--core-primary); /* Background color */
    color: var(--accent-primary); /* Text color */
    border: none; /* No border */
    border-radius: 5px; /* Rounded corners */
    cursor: pointer; /* Pointer cursor on hover */
    font-size: 1rem; /* Font size */
    transition: background-color 0.3s; /* Smooth transition for hover effect */
}

button:disabled {
    background-color: #ccc; /* Disabled state background color */
    cursor: not-allowed; /* Cursor for disabled state */
}

</style>

<template>
  <div class="container">
    <form @submit.prevent="GenerateQuizQuestions" class="quiz-form">
      <h2>Generate Quiz Questions</h2>

      <div class="form-group">
        <label for="model_name">Model Name: <span class="required" title="This field is required">*</span></label>
        <select id="model_name" v-model="form.model_name" required>
          <option value="gpt-3.5-turbo">GPT 3.5</option>
          <option value="gemini-1.5-pro-latest">Gemini 1.5 Pro</option>
        </select>
      </div>

      <div class="form-group">
        <label for="module_id">Module ID: <span class="required" title="This field is required">*</span></label>
        <input type="number" id="module_id" v-model="form.module_id" required min="1" />
      </div>

      <div class="form-group">
        <label for="quiz_type">Quiz Type: <span class="required" title="This field is required">*</span></label>
        <select id = "quiz_type" v-model="form.quiz_type" required>
          <option value="prereq">Prerequisites</option>
          <option value="preview">Preview</option>
          <option value="review">Review</option>
          </select>
      </div>

      <button type="submit" class="submit-button">Generate Quiz Questions</button>
    </form>

    <div v-if="data" class="response-data">
      <h3>Quiz Preview</h3>
      <pre>{{ JSON.stringify(data, null, 2) }}</pre>
    </div>

    <div v-if="error" class="error-data">
      <h3>Error</h3>
      <pre>{{ JSON.stringify(error, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const data = ref(null);
const error = ref(null);
const form = ref({
  module_id: '',
  quiz_type: '',
  model_name: 'gpt-3.5-turbo'
});

const GenerateQuizQuestions = async () => {
  const { module_id, quiz_type, model_name } = form.value;
  const url = `http://localhost:8080/qas/quiz/${module_id}/${quiz_type}?model_name=${model_name}`;
  
  try {
    const response = await axios.get(url, {
      headers: {
        'accept': 'application/json',
      },
    });
    data.value = response.data;
  } catch (err) {
    error.value = err.response ? err.response.data : err;
    console.error('Error fetching quiz preview:', error.value);
  }
};
</script>

<script>
export default {
  name: "QuizCreation",
  friendly_name: "Quiz Creation",
  icon: "/static/assets/icon-quiz.png"
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

body {
  font-family: 'Roboto', sans-serif;
  background-color: #f5f5f5;
  margin: 0;
  padding: 0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.ucsd-logo {
  height: 50px;
}

.quiz-form {
  display: flex;
  flex-direction: column;
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #00356b;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #333;
}

input[type="text"],
input[type="number"],
select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.submit-button {
  padding: 0.75rem 1.5rem;
  background-color: #00356b;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 1rem;
}

.submit-button:hover {
  background-color: #00214d;
}

.response-data,
.error-data {
  margin-top: 2rem;
  padding: 1rem;
  background-color: #f1f1f1;
  border-radius: 4px;
}

.required {
  color: red;
}
</style>

<template>
  <div class="container">
    <form @submit.prevent="saveQuestion" class="question-form">
      <h2>Save Quiz Questions</h2>

      <div class="form-group">
        <label for="json_input">Question JSON: <span class="required" title="This field is required">*</span></label>
        <textarea
          id="json_input"
          v-model="jsonInput"
          placeholder="Paste JSON here"
          required
        ></textarea>
        <small>Example JSON:</small>
        <pre>{{ exampleJson }}</pre>
      </div>

      <button type="submit" class="submit-button">Save Question</button>
    </form>

    <div v-if="data" class="response-data">
      <h3>Response</h3>
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
const jsonInput = ref('');

const exampleJson = JSON.stringify([
  {
    question: {
      id: 0,
      position: 0,
      question_name: "string",
      question_type: "string",
      question_text: "string",
      points_possible: 0,
      correct_comments: "string",
      incorrect_comments: "string",
      neutral_comments: "string"
    },
    answers: [
      {
        answer_text: "string",
        answer_weight: 0
      }
    ]
  }
], null, 2);

const validateJSON = (json) => {
  try {
    const parsed = JSON.parse(json);
    if (!Array.isArray(parsed) || parsed.length === 0) {
      return false;
    }
    const requiredFields = ['question', 'answers'];
    for (const item of parsed) {
      for (const field of requiredFields) {
        if (!(field in item)) {
          return false;
        }
      }
      const questionFields = [
        'id',
        'position',
        'question_name',
        'question_type',
        'question_text',
        'points_possible',
        'correct_comments',
        'incorrect_comments',
        'neutral_comments'
      ];
      for (const field of questionFields) {
        if (!(field in item.question)) {
          return false;
        }
      }
      if (!Array.isArray(item.answers) || item.answers.length === 0) {
        return false;
      }
      for (const answer of item.answers) {
        if (!('answer_text' in answer) || !('answer_weight' in answer)) {
          return false;
        }
      }
    }
    return true;
  } catch (e) {
    return false;
  }
};

const saveQuestion = async () => {
  if (!validateJSON(jsonInput.value)) {
    error.value = { message: 'Invalid JSON structure. Ensure it contains the required fields.' };
    return;
  }
  try {
    const parsedData = JSON.parse(jsonInput.value);
    const response = await axios.post('http://localhost:8080/question/create', parsedData, {
      headers: {
        accept: 'application/json',
        'Content-Type': 'application/json',
      },
    });
    data.value = response.data;
    error.value = null;
  } catch (err) {
    error.value = err.response ? err.response.data : err;
    console.error('Error saving question:', error.value);
  }
};
</script>

<script>
export default {
  name: "QuizEditing",
  friendly_name: "QuizEditing",
  icon: "/static/assets/icon-question.png",
};
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  height: 90vh; /* Full screen height minus some padding */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.question-form {
  display: flex;
  flex-direction: column;
  height: 100%;
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #00356b;
}

.form-group {
  flex: 1;
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #333;
}

textarea {
  width: 100%;
  height: 70%; /* Adjusted to fit the screen better */
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  resize: none; /* Disable resizing */
}

pre {
  background-color: #f1f1f1;
  padding: 1rem;
  border-radius: 4px;
  overflow: auto;
  max-height: 200px;
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
  align-self: center;
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
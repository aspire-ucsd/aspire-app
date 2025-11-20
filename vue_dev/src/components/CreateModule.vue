<template>
    <div class="container">
      <form @submit.prevent="register" class="register-form">
        <h2>Create a New Module</h2>
  
        <div class="form-group">
          <label for="model_name">Model Name: <span class="required" title="This field is required">*</span></label>
          <select id="model_name" v-model="form.model_name" required>
            <option value="gpt-3.5-turbo">GPT 3.5</option>
            <option value="gemini-1.5-pro-latest">Gemini 1.5 Pro</option>
          </select>
        </div>
  
        <div class="form-group">
          <label for="files">Content Files: <span class="required" title="This field is required">*</span></label>
          <input type="file" id="files" @change="handleFileChange" multiple required />
        </div>
  
        <div class="form-group">
          <label for="title">Title: <span class="required" title="This field is required">*</span></label>
          <input type="text" id="title" v-model="form.title" required />
        </div>
  
        <div class="form-group">
          <label for="course_id">Course ID: <span class="required" title="This field is required">*</span></label>
          <input type="number" id="course_id" v-model="form.course_id" required min="1" />
        </div>
  
        <button type="submit" class="submit-button">Create</button>
      </form>
  
      <div v-if="data" class="response-data">
        <pre>{{ JSON.stringify(data, null, 2) }}</pre>
      </div>
  
      <div v-if="error" class="error-data">
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
    model_name: '',
    title: '',
    course_id: '',
    files: [],
  });
  
  const handleFileChange = (event) => {
    form.value.files = Array.from(event.target.files);
  };
  
  const register = async () => {
    const formData = new FormData();
    form.value.files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('title', form.value.title);
    formData.append('course_id', form.value.course_id);
  
    try {
      const response = await axios.post(`http://localhost:8080/qas/module?model_name=${form.value.model_name}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      data.value = response.data;
    } catch (err) {
      error.value = err.response ? err.response.data : err;
      console.error('Error registering:', error.value);
    }
  };
  </script>
  
  <script>
  export default {
    name: "CreateModule",
    friendly_name: "Create Module",
    icon: "/static/assets/icon-course.png"
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
  
  .register-form {
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
  select,
  input[type="file"] {
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
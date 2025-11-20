<template>
    <div class="container">
      <form @submit.prevent="register" class="register-form">
        <h2>Register a New Domain</h2>
  
        <div class="form-group">
          <label for="model_name">Model Name: <span class="required" title="This field is required">*</span></label>
          <select id="model_name" v-model="form.model_name" required>
            <option value="gpt-3.5-turbo">GPT 3.5</option>
            <option value="gemini-1.5-pro-latest">Gemini 1.5 Pro</option>
          </select>
        </div>
  
        <div class="form-group">
          <label for="content_files">Content Files: <span class="required" title="This field is required">*</span></label>
          <input type="file" id="content_files" @change="handleFileChange" multiple required />
        </div>
  
        <div class="form-group">
          <label for="domain_id">Domain ID:</label>
          <input type="text" id="domain_id" v-model="form.domain_id" />
        </div>
  
        <div class="form-group">
          <input type="checkbox" id="empty_domain_id" v-model="isEmptyDomainId" />
          <label for="empty_domain_id">Send empty Domain ID</label>
        </div>
  
        <div class="form-group">
          <label for="instructor">Instructor: <span class="required" title="This field is required">*</span></label>
          <input type="text" id="instructor" v-model="form.instructor" required placeholder="Enter Instructor's Name" />
        </div>
  
        <div class="form-group">
          <label for="quarter">Quarter: <span class="required" title="This field is required">*</span></label>
          <input type="date" id="quarter" v-model="form.quarter" required />
        </div>
  
        <div class="form-group">
          <label for="name">Course Name:</label>
          <input type="text" id="name" v-model="form.name" />
        </div>
  
        <div class="form-group">
          <input type="checkbox" id="empty_name" v-model="isEmptyName" />
          <label for="empty_name">Send empty Course Name</label>
        </div>
  
        <div class="form-group">
          <label for="subject">Subject: <span class="required" title="This field is required">*</span></label>
          <input type="text" id="subject" v-model="form.subject" required />
        </div>
  
        <div class="form-group">
          <label for="difficulty">Difficulty: <span class="required" title="This field is required">*</span></label>
          <input type="number" id="difficulty" v-model="form.difficulty" required min="1" max="5" placeholder="1-5" />
        </div>
  
        <button type="submit" class="submit-button">Register</button>
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
    instructor: '',
    quarter: '',
    name: '',
    subject: '',
    difficulty: '',
    domain_id: '',
    content_files: [],
  });
  
  const isEmptyDomainId = ref(false);
  const isEmptyName = ref(false);
  
  const handleFileChange = (event) => {
    form.value.content_files = Array.from(event.target.files);
  };
  
  const register = async () => {
    const formData = new FormData();
    form.value.content_files.forEach(file => {
      formData.append('content_files', file);
    });
    if (isEmptyDomainId.value) {
      formData.append('domain_id', '');
    } else {
      formData.append('domain_id', form.value.domain_id);
    }
    formData.append('instructor', form.value.instructor);
    formData.append('quarter', form.value.quarter);
    if (isEmptyName.value) {
      formData.append('name', '');
    } else {
      formData.append('name', form.value.name);
    }
    formData.append('subject', form.value.subject);
    formData.append('difficulty', form.value.difficulty);
  
    try {
      const response = await axios.post(`http://localhost:8080/qas/register/new?model_name=${form.value.model_name}`, formData, {
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
    name: "ResgisterDomainModel",
    friendly_name: "Resgister Domain Model",
    icon: "/static/assets/icon-domain.png"
}
</script>
  
  <style scoped>
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }
  
  .register-form {
    display: flex;
    flex-direction: column;
  }
  
  h2 {
    text-align: center;
    margin-bottom: 2rem;
    color: #00356b; /* UCSD Primary Color */
    font-family: 'Arial', sans-serif; /* UCSD Font Family */
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
  input[type="date"],
  input[type="number"],
  select,
  input[type="file"] {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
    font-family: 'Arial', sans-serif; /* UCSD Font Family */
  }
  
  input[type="checkbox"] {
    margin-right: 0.5rem;
  }
  
  .submit-button {
    padding: 0.75rem 1.5rem;
    background-color: #00356b; /* UCSD Primary Color */
    color: #fff;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .submit-button:hover {
    background-color: #00214d; /* UCSD Hover Color */
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
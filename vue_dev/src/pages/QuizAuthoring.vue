<template>
  <div class="container">
    <div class="left-half">
      <div class="form-container">
        <div class="form-group">
          <label for="domain">
            Module<span class="asterisk" title="This field is mandatory">*</span>
          </label>
          <select id="domain" v-model="selectedDomain">
            <option disabled value="">Select a Module</option>
            <option v-for="domain in domains" :key="domain.module_id" :value="domain.module_id">
              {{ domain.title }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="concept">
            Concept<span class="asterisk" title="This field is mandatory">*</span>
          </label>
          <select id="concept" v-model="selectedConcept">
            <option disabled value="">Select A Concept</option>
            <option v-for="concept in concepts" :key="concept" :value="concept">
              {{ concept }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="quiz_type">
            Quiz Type<span class="asterisk" title="This field is mandatory">*</span>
          </label>
          <select id="quiz_type" v-model="selectedQuizType" @change="fetchCustomPrompt">
            <option disabled value="">Select A Quiz Type</option>
            <option v-for="type in types" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
        </div>

        <div class="form-group custom-prompt-group">
          <label for="custom-prompt">Custom Prompt</label>
          <div class="custom-prompt-preview">
            <span>{{ truncatedCustomPrompt }}</span>
            <button class="icon-button edit-button" @click="openEditPromptModal" title="Edit">
              <i class="fas fa-edit"></i>
            </button>
          </div>
        </div>

        <div class="form-group">
          <label for="num-questions">Number of Questions:</label>
          <input type="number" id="num-questions" v-model="numQuestions" min="1">
        </div>

        <button :class="{'discard-button': generateButtonText === 'Discard All Questions and Generate New Set'}" @click="toggleGenerateQuestions">
          {{ generateButtonText }}
        </button>

        <!-- Error message display -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
      </div>
    </div>

    <div class="right-half">
      <div v-if="questions.length" class="questions-container">
        <h3>Generated Questions</h3>
        <div v-if="questions[currentQuestionIndex]">
          <div class="question-indicator">
            Question {{ currentQuestionIndex + 1 }} / {{ questions.length }}
          </div>
          <div v-if="isEditing">
            <div class="form-group">
              <label for="question_text">Question Text:</label>
              <input type="text" v-model="questions[currentQuestionIndex].question.question_text" />
            </div>
            <div class="form-group">
              <label for="answers">Answers:</label>
              <ul>
                <li v-for="(answer, aIndex) in questions[currentQuestionIndex].answers" :key="aIndex">
                  {{ String.fromCharCode(65 + aIndex) }}. <input type="text" v-model="answer.answer_text" />
                  <label>
                    <input type="radio" :name="'correct-answer-' + currentQuestionIndex" :value="100" :checked="answer.answer_weight === 100" @change="setCorrectAnswer(aIndex)" />
                    Correct
                  </label>
                  <div class="feedback-controls">
                    <label for="answer_feedback">Feedback:</label>
                    <textarea v-model="answer.answer_feedback" class="feedback-input"></textarea>
                  </div>
                </li>
              </ul>
            </div>
            <div class="form-group">
              <label for="points_possible">Points Possible:</label>
              <input type="number" v-model="questions[currentQuestionIndex].question.points_possible" />
            </div>
            <div class="form-group">
              <label for="neutral_comments">Neutral Comments:</label>
              <textarea v-model="questions[currentQuestionIndex].question.neutral_comments" style="min-height: 200px;"></textarea>
            </div>
            <div class="question-actions">
              <div class="status-message-container">
                <span v-if="statusMessage && statusMessageType === 'save'" class="status-message save">
                  {{ statusMessage }}
                </span>
                <button class="icon-button save-button" @click="saveQuestion" title="Save">
                  <i class="fas fa-save"></i>
                </button>
              </div>
              <button @click="cancelEdit" class="icon-button reject-button" title="Cancel">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
          <div v-else>
            <p>{{ questions[currentQuestionIndex].question.position }}. {{ questions[currentQuestionIndex].question.question_text }}</p>
            <ul v-if="questions[currentQuestionIndex].question.question_type === 'multiple_choice_question'">
              <li v-for="(answer, aIndex) in questions[currentQuestionIndex].answers" :key="aIndex">
                {{ String.fromCharCode(65 + aIndex) }}. {{ answer.answer_text }}
                <span v-if="answer.answer_weight === 100" style="color: green;">(Correct)</span>
                <p><strong>Feedback:</strong></p>
                <p>{{ answer.answer_feedback }}</p>
              </li>
            </ul>
            <p><strong>Points Possible:</strong> {{ questions[currentQuestionIndex].question.points_possible }}</p>
            <p><strong>Neutral Comments:</strong></p>
            <p>{{ questions[currentQuestionIndex].question.neutral_comments }}</p>
            <div class="question-actions">
              <div class="status-message-container">
                <span v-if="statusMessage && statusMessageType === 'error'" class="status-message error">
                  {{ statusMessage }}
                </span>
                <button class="icon-button reject-button" @click="rejectQuestion" title="Reject">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <button class="icon-button edit-button" @click="editQuestion" title="Edit">
                <i class="fas fa-edit"></i>
              </button>
              <div class="status-message-container">
                <button class="icon-button accept-button" @click="acceptQuestion" title="Accept">
                  <i class="fas fa-check"></i>
                </button>
                <span v-if="statusMessage && statusMessageType === 'success'" class="status-message success">
                  {{ statusMessage }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="navigation-buttons">
          <div class="nav-button">
            <button class="icon-button prev-button" :disabled="currentQuestionIndex === 0" @click="prevQuestion" title="Previous">
              <i class="fas fa-arrow-left"></i>
            </button>
          </div>
          <div class="nav-button">
            <button class="icon-button review-button" @click="reviewQuestions" title="Review Questions">
              <i class="fas fa-eye"></i>
            </button>
          </div>
          <div class="nav-button">
            <button class="icon-button next-button" :disabled="currentQuestionIndex === questions.length - 1" @click="nextQuestion" title="Next">
              <i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>
      </div>
      <div v-if="isLoading" class="loading-overlay">
        <img src="/static/assets/loading-icon.png" class="loading-icon">
        <p>Generating Questions...</p>
      </div>
      <div v-if="showSubmissionMessage" class="submission-message">
        <p>Questions have been successfully submitted to the database.</p>
        <p>If you want to generate more questions, please follow the same process.</p>
        <p>Click here to view all the questions in the database:</p>
        <button @click="viewAllQuestions">View All Questions in Database</button>
      </div>
    </div>

    <div v-if="showReview" class="modal-overlay">
      <div class="modal">
        <h3>Review Questions</h3>
        <p>Pending Questions: {{ pendingCount }}</p>
        <ul>
          <li v-for="(question, qIndex) in questions" :key="qIndex">
            <p>{{ question.question.position }}. {{ question.question.question_text }}</p>
            <ul>
              <li v-for="(answer, aIndex) in question.answers" :key="aIndex">
                {{ String.fromCharCode(65 + aIndex) }}. {{ answer.answer_text }}
                <span v-if="answer.answer_weight === 100" style="color: green;">(Correct)</span>
                <p><strong>Feedback:</strong></p>
                <p>{{ answer.answer_feedback }}</p>
              </li>
            </ul>
            <p><strong>Status:</strong> {{ question.status }}</p>
          </li>
        </ul>
        <div v-if="pendingQuestions.length > 0" class="error-message">
          Please resolve the pending question(s): {{ pendingQuestions.join(', ') }}
        </div>
        <div class="modal-actions">
          <button class="icon-button accept-button" @click="submitQuestions" :disabled="pendingCount > 0">Submit to Database</button>
          <span v-if="submitErrorMessage" class="error-message">{{ submitErrorMessage }}</span>
          <span v-if="submissionStatusMessage" :class="submissionStatusClass">{{ submissionStatusMessage }}</span>
          <button @click="cancelReview">Cancel</button>
        </div>
      </div>
    </div>

    <div v-if="showEditPromptModal" class="modal-overlay">
      <div class="modal" :style="modalStyle">
        <h3>Edit Custom Prompt</h3>
        <div class="form-group">
          <label for="edit-custom-prompt">Custom Prompt</label>
          <textarea id="edit-custom-prompt" v-model="customPrompt" :style="textareaStyle"></textarea>
        </div>
        <div class="modal-actions">
          <button @click="saveCustomPrompt" class="icon-button accept-button">Save</button>
          <button @click="closeEditPromptModal" class="icon-button reject-button">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import axios from 'axios';

// Dynamically load Font Awesome
const loadFontAwesome = () => {
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css';
  document.head.appendChild(link);
};

loadFontAwesome();

const selectedDomain = ref('');
const selectedConcept = ref('');
const selectedQuizType = ref('');
const customPrompt = ref('');
const numQuestions = ref(1);
const domains = ref([]);
const concepts = ref([]);
const types = ref(['prereq', 'preview', 'review']);
const questions = ref([]);
const isLoading = ref(false);
const currentQuestionIndex = ref(0); // Index to track the current question
const isEditing = ref(false); // State to track if a question is being edited
const showReview = ref(false); // State to track if review mode is active
const statusMessage = ref(''); // State for status message
const statusMessageType = ref(''); // State for status message type (success, error, save)
const errorMessage = ref(''); // State for error message
const pendingCount = ref(0); // Count of pending questions
const pendingQuestions = ref([]); // List of pending question numbers
const generateButtonText = ref('Generate Questions');
const showSubmissionMessage = ref(false); // State to track if the submission message is displayed
const submissionStatusMessage = ref(''); // State for submission status message
const submissionStatusClass = ref(''); // State for submission status message class
const showEditPromptModal = ref(false); // State for showing the edit prompt modal
const submitErrorMessage = ref(''); // State for submit error message

const fetchDomains = async () => {
  try {
    const response = await axios.get('http://localhost:8080/module/get/all');
    domains.value = response.data.map(item => ({ title: item.title, module_id: item.module_id }));
  } catch (error) {
    console.error('Error fetching domains:', error);
  }
};

const fetchConcepts = async (moduleId) => {
  try {
    const response = await axios.get(`http://localhost:8080/concept/cm/${moduleId}`);
    concepts.value = response.data.concepts.map(concept => concept.name);
  } catch (error) {
    console.error('Error fetching concepts:', error);
  }
};

const fetchCustomPrompt = async () => {
  if (!selectedQuizType.value) return;

  let url = '';
  if (selectedQuizType.value === 'prereq') {
    url = 'http://localhost:8080/prompt/prereq-questions';
  } else if (selectedQuizType.value === 'preview') {
    url = 'http://localhost:8080/prompt/preview-questions';
  } else if (selectedQuizType.value === 'review') {
    url = 'http://localhost:8080/prompt/review-questions';
  }

  try {
    const response = await axios.get(url);
    customPrompt.value = response.data["editable_part"];  // Extract the 'text' field from the response
  } catch (error) {
    console.error('Error fetching custom prompt:', error);
  }
};

watch(selectedDomain, (newVal) => {
  if (newVal) {
    fetchConcepts(newVal);
  } else {
    concepts.value = [];
  }
});

onMounted(() => {
  fetchDomains();
});

const generateQuestions = async () => {
  const payload = {
    domain: selectedDomain.value,
    concept: selectedConcept.value,
    quizType: selectedQuizType.value,
    numQuestions: numQuestions.value,
    prompt: customPrompt.value,
  };

  // Check for missing fields and set specific error messages
  let errors = [];
  if (!payload.domain) {
    errors.push('Please select a module.');
  }
  if (!payload.concept) {
    errors.push('Please select a concept.');
  }
  if (!payload.quizType) {
    errors.push('Please select a quiz type.');
  }

  if (errors.length) {
    errorMessage.value = errors.join(' ');
    return;
  }

  console.log('Generating questions with payload:', payload);

  isLoading.value = true;
  errorMessage.value = ''; // Clear any previous error message
  try {
    const response = await axios.get(`http://localhost:8080/qas/quiz/${payload.domain}/${payload.quizType}`, {
      params: {
        model_name: 'gpt-4o',
        num_questions: payload.numQuestions,
        prompt: payload.prompt,
      }
    });
    questions.value = response.data.map(q => ({ ...q, status: 'pending' }));
    currentQuestionIndex.value = 0; // Reset to the first question
    generateButtonText.value = 'Discard All Questions and Generate New Set';
    showSubmissionMessage.value = false; // Hide submission message
  } catch (error) {
    console.error('Error generating questions:', error);
    errorMessage.value = 'Failed to generate questions. Please try again.';
  } finally {
    isLoading.value = false;
  }
};

const discardAndGenerateNewQuestions = () => {
  questions.value = [];
  generateButtonText.value = 'Generate Questions';
  generateQuestions();
};

const toggleGenerateQuestions = () => {
  if (generateButtonText.value === 'Generate Questions') {
    generateQuestions();
  } else {
    discardAndGenerateNewQuestions();
  }
};

// Navigation functions
const prevQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
    clearStatusMessage();
  }
};

const nextQuestion = () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++;
    clearStatusMessage();
  }
};

// Question action functions
const rejectQuestion = () => {
  questions.value[currentQuestionIndex.value].status = 'rejected';
  showStatusMessage('Question rejected.', 'error');
  updatePendingCount();
  autoNextOrReview();
};

const acceptQuestion = () => {
  questions.value[currentQuestionIndex.value].status = 'accepted';
  showStatusMessage('Question accepted.', 'success');
  updatePendingCount();
  autoNextOrReview();
};

const saveQuestion = () => {
  questions.value[currentQuestionIndex.value].status = 'saved';
  showStatusMessage('Question saved.', 'save');
  // Exit edit mode
  isEditing.value = false;
  updatePendingCount();
};

// Show status message
const showStatusMessage = (message, type) => {
  statusMessage.value = message;
  statusMessageType.value = type;
  setTimeout(() => {
    statusMessage.value = '';
  }, 3000);
};

const clearStatusMessage = () => {
  statusMessage.value = '';
};

const editQuestion = () => {
  isEditing.value = true;
};

const cancelEdit = () => {
  isEditing.value = false;
};

const setCorrectAnswer = (correctIndex) => {
  questions.value[currentQuestionIndex.value].answers.forEach((answer, index) => {
    answer.answer_weight = index === correctIndex ? 100 : 0;
  });
};

const reviewQuestions = () => {
  updatePendingCount();
  showReview.value = true;
  submissionStatusMessage.value = ''; // Clear previous submission status message
  submissionStatusClass.value = ''; // Clear previous submission status class
  submitErrorMessage.value = ''; // Clear previous submit error message
};

const cancelReview = () => {
  showReview.value = false;
};

const updatePendingCount = () => {
  const pendingList = questions.value.filter(q => q.status === 'pending').map(q => q.question.position);
  pendingCount.value = pendingList.length;
  pendingQuestions.value = pendingList;
};

const autoNextOrReview = () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    setTimeout(() => {
      nextQuestion();
    }, 500); // Adjust the delay time as needed
  } else {
    setTimeout(() => {
      reviewQuestions();
    }, 500); // Adjust the delay time as needed
  }
};

const submitQuestions = async () => {
  const toSave = questions.value.filter(q => q.status === 'accepted'); // Only accepted questions
  if (toSave.length === 0) {
    submitErrorMessage.value = 'No questions to submit. Please accept some questions first.';
    return;
  }
  if (pendingCount.value > 0) {
    errorMessage.value = `Please resolve the pending question(s): ${pendingQuestions.value.join(', ')}`;
    return;
  }
  try {
    await axios.post('http://localhost:8080/question/create', toSave);
    console.log('Questions saved:', toSave);
    submissionStatusMessage.value = 'Questions submitted successfully.';
    submissionStatusClass.value = 'success-message';
    showStatusMessage('Questions submitted successfully.', 'success');
    clearQuestions();
  } catch (error) {
    console.error('Error saving questions:', error);
    submissionStatusMessage.value = 'Failed to submit questions. Please try again.';
    submissionStatusClass.value = 'error-message';
    showStatusMessage('Failed to submit questions. Please try again.', 'error');
  }
};

const clearQuestions = () => {
  questions.value = [];
  showReview.value = false;
  showSubmissionMessage.value = true;
  generateButtonText.value = 'Generate Questions';
};

const viewAllQuestions = () => {
  // Placeholder function for viewing all questions in the database
  showSubmissionMessage.value = false; // Hide submission message
  console.log('View all questions in the database');
};

const openEditPromptModal = () => {
  showEditPromptModal.value = true;
};

const closeEditPromptModal = () => {
  showEditPromptModal.value = false;
};

const saveCustomPrompt = () => {
  showEditPromptModal.value = false;
};

const truncatedCustomPrompt = computed(() => {
  const maxLength = 50; // Adjust the max length as needed
  return customPrompt.value.length > maxLength
    ? customPrompt.value.substring(0, maxLength) + '...'
    : customPrompt.value;
});

const modalStyle = computed(() => {
  const lines = customPrompt.value.split('\n').length;
  const minHeight = 500; // Minimum height for the modal
  const maxHeight = 800; // Maximum height for the modal
  const height = Math.min(maxHeight, Math.max(minHeight, lines * 20)) + 'px'; // Adjust the height calculation as needed
  return { height, width: '80%' }; // Adjust the width as needed
});

const textareaStyle = computed(() => {
  const lines = customPrompt.value.split('\n').length;
  const minHeight = 300; // Minimum height for the textarea
  const maxHeight = 700; // Maximum height for the textarea
  const height = Math.min(maxHeight, Math.max(minHeight, lines * 20)) + 'px'; // Adjust the height calculation as needed
  return { height };
});

</script>

<script>
export default {
  name: "QuizAuthoring",
  friendly_name: "Quiz Authoring",
  icon: "/aspire/static/assets/icon-QuizAuthoring.png"
}
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: row;
  height: 98vh;
}

.left-half {
  flex: 1 1 30%; /* Adjust this value */
  padding: 10px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  border-right: 2px solid #000; /* Add this line */
  overflow: auto;
  height: 98vh;
}

.right-half {
  flex: 1 1 70%; /* Adjust this value */
  padding: 10px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: auto;
  height: 98vh;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #fff;
}

.form-group label {
  font-weight: bold;
  margin-bottom: 5px;
}

.asterisk {
  color: red;
  margin-left: 5px;
  cursor: pointer;
}

.form-group select,
.form-group textarea,
.form-group input {
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.custom-prompt-group {
  display: flex;
  align-items: center;
}

.custom-prompt-preview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.custom-prompt-preview span {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

button,
.icon-button {
  align-self: flex-end;
  padding: 10px 20px;
  font-size: 16px;
  background-color: #ff7f50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.discard-button {
  background-color: red;
}

.icon-button {
  padding: 10px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
}

.icon-button i {
  font-size: 1.2em;
}

.icon-button[title]:hover::after {
  content: attr(title);
  position: absolute;
  background-color: black;
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  top: -30px;
  white-space: nowrap;
  z-index: 100;
}

.icon-button[title]:hover {
  position: relative;
}

button:hover,
.icon-button:hover {
  background-color: #ff6347;
}

.icon-button.reject-button:hover {
  background-color: red;
  color: white;
}

.icon-button.accept-button:hover {
  background-color: green;
  color: white;
}

.icon-button.save-button:hover {
  background-color: blue;
  color: white;
}

.questions-container {
  flex: 1 1 70%; /* Adjust this value */
  padding: 10px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: auto;
  height: 85vh;
  /* margin-top: 20px; */
}

.questions-container h3 {
  margin-bottom: 10px;
}

.questions-container ul {
  list-style-type: none;
  padding: 0;
}

.questions-container li {
  background-color: #f9f9f9;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 5px;
}

.edit-input {
  width: 100%;
  box-sizing: border-box;
  margin-bottom: 10px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-icon {
  width: 50px;
  height: 50px;
  margin-bottom: 10px;
  animation: spin 2s linear infinite;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.nav-button {
  flex: 1;
  display: flex;
  justify-content: center;
}

button:disabled,
.icon-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.question-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  justify-content: center; /* Ensure buttons are centered */
  flex-wrap: wrap; /* Allow buttons to wrap to the next line if needed */
}

.question-indicator {
  font-weight: bold;
  margin-bottom: 10px;
}

.status-message-container {
  position: relative;
}

.status-message {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  padding: 5px 10px;
  border-radius: 5px;
  color: white;
  opacity: 1;
  transition: opacity 0.5s ease-out;
}

.status-message.success {
  left: 110%; /* Position the success message to the right of the Accept button */
  background-color: #28a745;
}

.status-message.error {
  right: 110%; /* Position the error message to the left of the Reject button */
  background-color: #dc3545;
}

.status-message.save {
  right: 110%; /* Position the save message to the left of the Save button */
  background-color: #17a2b8;
}

.success-message {
  color: #28a745;
}

.error-message {
  color: #dc3545;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 80%;
  max-width: 600px;
  max-height: 80%;
  overflow-y: auto;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.review-container {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #fff;
  margin-top: 20px;
}

.right-half .form-group {
  display: flex;
}

.right-half .form-group label {
  margin-bottom: 10px;
}

.right-half .form-group input,
.right-half .form-group textarea {
  flex: 1;
  margin-bottom: 10px;
}

.submission-message {
  margin-top: 20px;
  background-color: #f9f9f9;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.submission-message p {
  margin: 10px 0;
}

.submission-message button {
  margin-top: 10px;
  align-self: center;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.feedback-controls {
  margin-top: 10px;
}

.feedback-input {
  width: 100%;
  min-height: 50px;
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-top: 5px;
}
</style>

<template>
  <div :class="{'container': true, 'expanded': !isSidebarCollapsed, 'collapsed': isSidebarCollapsed}">
    <div class="left-half">
      <div class="form-container">
        <h2>Create a Module</h2>
        <!-- <div class="form-group">
          <label for="courseId">Course ID<span class="asterisk" title="This field is mandatory">*</span></label>
          <input type="text" id="courseId" v-model="courseId" placeholder="Enter Course ID">
        </div> -->
        <div class="form-group">
          <label for="moduleName">Module Name<span class="asterisk" title="This field is mandatory">*</span></label>
          <input type="text" id="moduleName" v-model="moduleName" placeholder="Enter Module Name">
        </div>
        <div class="form-group file-upload">
          <label for="file-upload" class="file-upload-label">
            Click to Upload files <img src="/static/assets/upload-file.png" class="upload-file-icon">
          </label>
          <input type="file" id="file-upload" multiple @change="handleFilesUpload" class="file-input">
          <ul>
            <li v-for="(file, index) in files" :key="file.name">
              {{ file.name }}
              <button @click="removeFile(index)">
                <img src="/static/assets/delete.png" class="delete-icon">
              </button>
            </li>
          </ul>
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
        <button @click="submitModuleForm">Submit</button>
      </div>
    </div>
    <div class="right-half">
      <div class="output-section" v-if="outputReceived">
        <div class="output-box">
          <h2>Summary:</h2>
          <textarea v-model="summary" placeholder="Edit Summary" readonly></textarea>
          <button @click="openEditSummaryModal">Edit Summary</button>
        </div>
        <button @click="saveModuleToDatabase" class="save-module-button">Add Module to Database</button>
        <p v-if="moduleSaved" class="success-message">Module has been successfully added to the database.</p>
        <button v-if="moduleSaved" @click="showConceptPrompt" class="generate-concepts-button">Generate Concepts</button>
        
        <div v-if="conceptPromptVisible" class="concept-prompt-section">
          <label for="concept-prompt">Concept Prompt</label>
          <div class="custom-prompt-preview">
            <span>{{ truncatedConceptPrompt }}</span>
            <button class="icon-button edit-button" @click="openEditConceptPromptModal" title="Edit">
              <i class="fas fa-edit"></i>
            </button>
          </div>
          <button @click="generateConcepts" class="generate-concepts-button">Generate</button>
        </div>

        <div v-if="concepts.length" class="concepts-section">
          <h3>Generated Concepts</h3>
          <ul>
            <li v-for="(concept, index) in concepts" :key="index">{{ concept }}</li>
          </ul>
        </div>
      </div>
      <div v-if="isLoading" class="loading-overlay">
        <img src="/static/assets/loading-icon.png" class="loading-icon">
        <p>Loading...</p>
      </div>
    </div>

    <!-- Edit Summary Modal -->
    <div v-if="showEditSummaryModal" class="modal-overlay">
      <div class="modal">
        <h3>Edit Summary</h3>
        <textarea v-model="summaryEdit"></textarea>
        <div class="modal-actions">
          <button @click="saveSummary" class="icon-button accept-button">Save</button>
          <button @click="closeEditSummaryModal" class="icon-button reject-button">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Edit Custom Prompt Modal -->
    <div v-if="showEditPromptModal" class="modal-overlay">
      <div class="modal">
        <h3>Edit Custom Prompt</h3>
        <textarea id="edit-custom-prompt" v-model="customPrompt" :style="textareaStyle"></textarea>
        <div class="modal-actions">
          <button @click="saveCustomPrompt" class="icon-button accept-button">Save</button>
          <button @click="closeEditPromptModal" class="icon-button reject-button">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Edit Concept Prompt Modal -->
    <div v-if="showEditConceptPromptModal" class="modal-overlay">
      <div class="modal">
        <h3>Edit Concept Prompt</h3>
        <textarea v-model="conceptPromptEdit" :style="textareaStyle"></textarea>
        <div class="modal-actions">
          <button @click="saveConceptPrompt" class="icon-button accept-button">Save</button>
          <button @click="closeEditConceptPromptModal" class="icon-button reject-button">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

export default {
  name: "AdaptiveTutor",
  friendly_name: "Adaptive Tutor",
  icon: "/aspire/static/assets/icon-AdaptiveTutor.png",
  setup() {
    const courseId = ref('60');
    const moduleName = ref('');
    const files = ref([]);
    const summary = ref('');
    const summaryEdit = ref('');
    const customPrompt = ref('');
    const conceptPrompt = ref('');
    const conceptPromptEdit = ref('');
    const concepts = ref([]);
    const isLoading = ref(false);
    const outputReceived = ref(false);
    const showEditSummaryModal = ref(false);
    const showEditPromptModal = ref(false);
    const showEditConceptPromptModal = ref(false);
    const conceptPromptVisible = ref(false);
    const moduleSaved = ref(false);

    const handleFilesUpload = (event) => {
      const uploadedFiles = Array.from(event.target.files);
      files.value = [...files.value, ...uploadedFiles];
    };

    const removeFile = (index) => {
      files.value.splice(index, 1);
    };

    const fetchDefaultPrompt = async () => {
      try {
        const response = await axios.get('http://localhost:8080/prompt/summarize');
        customPrompt.value = response.data.editable_part;
      } catch (error) {
        console.error('Error fetching default prompt:', error);
      }
    };

    const showConceptPrompt = async () => {
      try {
        const response = await axios.get('http://localhost:8080/prompt/create-concepts');
        conceptPrompt.value = response.data.editable_part;
        conceptPromptEdit.value = response.data.editable_part;
        conceptPromptVisible.value = true;
      } catch (error) {
        console.error('Error fetching concept prompt:', error);
      }
    };

    onMounted(() => {
      fetchDefaultPrompt();
    });

    const submitModuleForm = async () => {
      isLoading.value = true;

      if (!courseId.value || !moduleName.value || files.value.length === 0) {
        console.error('Missing required fields');
        isLoading.value = false;
        return;
      }

      const formData = new FormData();
      formData.append('course_id', courseId.value);
      formData.append('title', moduleName.value);
      files.value.forEach(file => {
        formData.append('files', file, file.name);
      });

      try {
        const response = await axios.post(`http://localhost:8080/qas/module/generate-summary?model_name=gpt-4o&prompt=${encodeURIComponent(customPrompt.value)}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        const data = response.data;
        summary.value = data.summary;
        summaryEdit.value = data.summary;
        outputReceived.value = true;
      } catch (error) {
        console.error('Error submitting module form:', error.response?.data || error);
      } finally {
        isLoading.value = false;
      }
    };

    const generateConcepts = async () => {
      isLoading.value = true;

      const formData = new FormData();
      formData.append('course_id', courseId.value);
      formData.append('title', moduleName.value);
      files.value.forEach(file => {
        formData.append('files', file, file.name);
      });

      try {
        const response = await axios.post(`http://localhost:8080/qas/module/generate-concepts?model_name=gpt-3.5-turbo&prompt=${encodeURIComponent(conceptPrompt.value)}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        const data = response.data;
        concepts.value = data.concepts;
      } catch (error) {
        console.error('Error generating concepts:', error.response?.data || error);
      } finally {
        isLoading.value = false;
      }
    };

    const openEditSummaryModal = () => {
      showEditSummaryModal.value = true;
    };

    const closeEditSummaryModal = () => {
      showEditSummaryModal.value = false;
    };

    const saveSummary = async () => {
      try {
        summary.value = summaryEdit.value;
        showEditSummaryModal.value = false;
      } catch (error) {
        console.error('Error saving summary:', error);
      }
    };

    const saveModuleToDatabase = async () => {
      isLoading.value = true;

      const moduleData = {
        course_id: courseId.value,
        title: moduleName.value,
        content_summary: summary.value,
      };

      try {
        await axios.post('http://localhost:8080/module/create/module', moduleData, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        moduleSaved.value = true;
      } catch (error) {
        console.error('Error saving module to database:', error.response?.data || error);
      } finally {
        isLoading.value = false;
      }
    };

    const openEditPromptModal = () => {
      showEditPromptModal.value = true;
    };

    const closeEditPromptModal = () => {
      showEditPromptModal.value = false;
    };

    const openEditConceptPromptModal = () => {
      showEditConceptPromptModal.value = true;
    };

    const closeEditConceptPromptModal = () => {
      showEditConceptPromptModal.value = false;
    };

    const saveCustomPrompt = () => {
      showEditPromptModal.value = false;
    };

    const saveConceptPrompt = () => {
      conceptPrompt.value = conceptPromptEdit.value;
      showEditConceptPromptModal.value = false;
    };

    const truncatedCustomPrompt = computed(() => {
      const maxLength = 50; // Adjust the max length as needed
      return customPrompt.value && customPrompt.value.length > maxLength
        ? customPrompt.value.substring(0, maxLength) + '...'
        : customPrompt.value;
    });

    const truncatedConceptPrompt = computed(() => {
      const maxLength = 50; // Adjust the max length as needed
      return conceptPrompt.value && conceptPrompt.value.length > maxLength
        ? conceptPrompt.value.substring(0, maxLength) + '...'
        : conceptPrompt.value;
    });

    const textareaStyle = computed(() => {
      const lines = customPrompt.value ? customPrompt.value.split('\n').length : 0;
      const minHeight = 300; // Minimum height for the textarea
      const maxHeight = 700; // Maximum height for the textarea
      const height = Math.min(maxHeight, Math.max(minHeight, lines * 20)) + 'px'; // Adjust the height calculation as needed
      return { height };
    });

    return {
      courseId,
      moduleName,
      files,
      summary,
      summaryEdit,
      customPrompt,
      conceptPrompt,
      conceptPromptEdit,
      concepts,
      isLoading,
      outputReceived,
      showEditSummaryModal,
      showEditPromptModal,
      showEditConceptPromptModal,
      conceptPromptVisible,
      moduleSaved,
      handleFilesUpload,
      removeFile,
      submitModuleForm,
      generateConcepts,
      openEditSummaryModal,
      closeEditSummaryModal,
      saveSummary,
      saveModuleToDatabase,
      openEditPromptModal,
      closeEditPromptModal,
      openEditConceptPromptModal,
      closeEditConceptPromptModal,
      saveCustomPrompt,
      saveConceptPrompt,
      truncatedCustomPrompt,
      truncatedConceptPrompt,
      textareaStyle,
      showConceptPrompt
    };
  },
};
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: row;
  height: 98vh;
  transition: width 0.3s ease;
}

.contianer.expanded {
  width: calc(100% - 200px);
}

.container.collapsed {
  width: calc(100% - 50px);
}

.left-half {
  flex: 1 1 30%; 
  padding: 10px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  border-right: 2px solid #000;
  overflow: auto;
  height: 98vh;
}

.right-half {
  flex: 1 1 70%; 
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
.icon-button,
.save-module-button,
.generate-concepts-button {
  align-self: flex-end;
  padding: 10px 20px;
  font-size: 16px;
  background-color: #ff7f50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
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
.icon-button:hover,
.save-module-button:hover,
.generate-concepts-button:hover {
  background-color: #ff6347;
}

.file-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  text-align: center;
  padding: 10px;
  border: 2px solid #ccc;
  border-radius: 8px;
  background-color: #fff;
}

.file-upload-label {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.file-input {
  display: none;
}

.upload-file-icon {
  width: 20px; /* Adjust icon size */
  height: 20px; /* Adjust icon size */
  margin-left: 10px;
}

.file-upload ul {
  list-style: none;
  padding: 0;
  margin-top: 10px;
  width: 100%;
  max-height: 150px;
  overflow-y: scroll;
}

.file-upload li {
  background-color: #f0f0f0;
  padding: 5px; /* Adjust padding */
  margin-bottom: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px; /* Adjust font size */
}

.file-upload li button {
  background: none;
  border: none;
  cursor: pointer;
}

.delete-icon {
  width: 16px; /* Adjust icon size */
  height: 16px; /* Adjust icon size */
}

.output-section {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 100%;
  overflow-y: auto;
}

.output-box {
  margin-bottom: 20px;
}

.output-box h2 {
  margin-bottom: 10px;
}

.output-box textarea {
  width: 100%;
  height: 150px;
  padding: 10px;
  font-size: 1em;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 10px;
}

.output-box ul {
  list-style: none;
  padding: 0;
  margin-bottom: 10px;
}

.output-box ul li {
  background-color: #e9e9e9;
  padding: 10px;
  margin-bottom: 5px;
  border-radius: 4px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-icon {
  width: 50px;
  height: 50px;
  margin-bottom: 10px;
  animation: spin 2s linear infinite;
}

.success-message {
  color: green;
  margin-top: 20px;
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
  z-index: 1000;
}

.modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 900px;
  max-height: 95%;
  height: 95%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal textarea {
  flex: 1;
  width: 100%;
  margin-bottom: 20px;
  font-size: 1em;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 10px;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

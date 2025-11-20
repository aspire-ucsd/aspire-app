<script setup>
import axios from "axios";
import { ref, defineEmits, defineProps, defineModel, onBeforeMount } from 'vue'
import DropdownSelect from '../utility_comps/DropdownSelect.vue';
import SearchableDropdown from "../utility_comps/SearchableDropdown.vue";

const tool_domain = window.contextData.tool_domain

const props = defineProps(["modalOpen", "existingConcepts", "selectedModule"])
const emit = defineEmits(["addNode", "addExistingNode", "updateOpen"])
const activeTab = defineModel('activeTab')

const subjects = ref({})

const selectedConcept = ref()
const conceptSubjectFilters = ref([])
const conceptMap = ref(null)
const conceptForm = ref({name: '', subject: '', difficulty: 1, summary: ''})
const documentLink = ref(null)
const documentLinkArray = ref([])

onBeforeMount(async () => {
    axios.get(`${tool_domain}/domain/subjects`).then((response) => {
        const subjectMapping = {}
        response.data.forEach(item => subjectMapping[item] = item)
        subjects.value = subjectMapping
    })
})

function cancel() {
    emit("updateOpen", false)
    conceptForm.value = {}
    documentLink.value = null
    documentLinkArray.value = []
}

function submit() {
    if (activeTab.value === 'select-existing') {
        let selectedConceptFormatted = conceptMap.value.filter(item => item.id === selectedConcept.value)[0]
        emit('addExistingNode', selectedConceptFormatted)
        
    } else {
        conceptForm.value.module = []
        conceptForm.value.id = conceptForm.value.name
        emit("addNode", conceptForm.value)
        emit("updateOpen", false)
        conceptForm.value = {}
        documentLink.value = null
        documentLinkArray.value = []
    }
}

function searchConcepts() {
    axios.get(`${tool_domain}/domain/concept/filter`, {params: {subjects: conceptSubjectFilters.value.join('|')}}).then((response) => {
        selectedConcept.value = null
        conceptMap.value = response.data.map(item => {
            item['id'] = item.name
            return item
        }).filter(item => !props.existingConcepts.includes(item.name))
        conceptSubjectFilters.value = []
    })
}

function identifyConcepts() {
    axios.post(`${tool_domain}/course/llm/module/concepts?module_id=${props.selectedModule}`, documentLinkArray.value).then(() => {
        emit("updateOpen", false)
        conceptForm.value = {}
        documentLink.value = null
        documentLinkArray.value = []
    })
}

</script>

<template>
    <div v-if="props.modalOpen" class="concept-modal">
        <div class="concept-form">
            <div class="concept-form-header">
                <h3>Add Concepts</h3>
                <img 
                    src="/aspire/static/assets/icon-close-white.png"
                    @click="cancel"
                    />

            </div>
            <hr />
            <div class="settings-tab-buttons">
                <span
                    class="tab-select no-select"
                    @click="() => activeTab = 'select-existing'"
                    :data-state="activeTab === 'select-existing'"
    
                >
                    Select Existing Concept
                </span>
                <span
                    class="tab-select no-select"
                    @click="() => activeTab = 'create-new'"
                    :data-state="activeTab === 'create-new'"
                >
                    Create New Concept
                </span>
                <span
                    class="tab-select no-select"
                    @click="() => activeTab = 'generate-concepts'"
                    :data-state="activeTab === 'generate-concepts'"
                >
                    Identify Concepts from Documents
                </span>
            </div>
            <hr />
            <div
                v-if="activeTab === 'select-existing'"
                class="existing-concepts-menu"
            >
                <label for="concept-subjects">Select Subjects for Concept Search: </label>
                <DropdownSelect 
                id="concept-subjects"
                v-model:selected-value="conceptSubjectFilters"
                :allow_multiple_selections="true"
                :option-mapping="subjects"
                />
                <button
                v-if="conceptSubjectFilters.length > 0"
                @click="searchConcepts"
                >
                    Search
                </button>
                <label v-if="conceptMap && conceptSubjectFilters.length === 0" for="concept-name">Select a Concept: </label>
                <SearchableDropdown 
                    v-if="conceptMap && conceptSubjectFilters.length === 0"
                    v-model:selected-value="selectedConcept"
                    :items="conceptMap"
                />
            </div>
            <div
                v-if="activeTab === 'create-new'"
                class="new-concept-form"

            >
                <label for="concept-name">Concept Name</label>
                <input id="concept-name" :value="conceptForm.name" @input="event => {
                    conceptForm.name = event.target.value
                    
                    }"/>
                <label for="concept-subject">Concept Subject</label>
                <input 
                    id="concept-subject" 
                    :value="conceptForm.subject" 
                    @input="event => {
                        conceptForm.subject = event.target.value
                    }"
                    />
                <label for="concept-difficulty">Concept Difficulty: {{ conceptForm?.difficulty || 0 }}</label>
                <input 
                    id="concept-difficulty" 
                    type="range"
                    min="1"
                    max="10"
                    step="1"
                    :value="conceptForm.difficulty" 
                    @input="event => {
                        conceptForm.difficulty = event.target.value
                    }"
                    />
                <label>Summary</label>
                <textarea 
                    placeholder="Add summary of concept"
                    :value="conceptForm.summary" 
                    @input="event => {
                        conceptForm.summary = event.target.value
                    }"
                >
                </textarea>
            </div>
            <div
                v-if="activeTab === 'generate-concepts'"
                class="existing-concepts-menu"
            >
                <p>
                    <strong>EXPERIMENTAL FEATURE</strong>
                    <br />
                    <br />
                    Please provide download links to any documents used in this module, works best with Google Drive public share links.  
                    <br />
                    <br />
                    ASPIRE will identify all concepts covered in these documents and assign them to the selected module. 
                    <br />
                    This action may take some time to complete, the results can be found and reviewed in your change request drafts tab.
                    <br />
                    <br />
                    <strong>Warning:</strong> 
                    Any documents provided this way are processed in their entirety.
                    <br />
                    Ensure the documents provided contain only the materials related to the selected module to avoid adding concepts outside its scope.
                    <br />
                    <br />
                    <strong>Supported File Types:</strong>
                </p>
                <ul>
                    <li>.pdf</li>
                    <li>.png</li>
                    <li>.txt</li>
                </ul>
                <br />
                <div>
                    <label for="document-links">Add a Link: </label>
                    <input 
                        type="text"
                        :value="documentLink"
                        @change="(event) => documentLink = event.target.value"
                        />
                    <button
                        v-if="documentLink"
                        @click="() => {
                            documentLinkArray = [...documentLinkArray, documentLink]
                            documentLink = null
                            }"
                    >
                        Add Link
                    </button>
                </div>
                <div>
                    <div
                        class="document-link-list"
                        v-for="[index, link] of documentLinkArray.entries()"
                        :key="'document' + index"
                    >
                        <p>{{ link }}</p>
                        <img 
                            class="ui-btn-icon"
                            @click="() => documentLinkArray.splice(index, 1)"
                            src="/aspire/static/assets/delete.png"
                        />
                    </div>
                </div>
                <button
                    v-if="documentLinkArray.length > 0"
                    @click="identifyConcepts"
                >
                    Identify Concepts
                </button>
                
            </div>
            <button 
                class="concept-submit-btn"
                v-if="(conceptForm.name && conceptForm.subject && conceptForm.summary) || selectedConcept && conceptSubjectFilters.length === 0"
                @click="submit"
            >
                Submit
            </button>

        </div>
    </div>
</template>

<style scoped>
.document-link-list {
    height: 2rem;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.25rem;
    background-color: var(--core-primary);
    color: var(--text-secondary);

}
.ui-btn-icon {
    height: 100%;
    aspect-ratio: 1/1;
    text-align: center;
    padding: 0;
    align-items: center;
    justify-content: center;
    margin: 1px;
    position: relative; 
}

.ui-btn-icon:hover {
    height: calc(100% - 3px);
}
.ui-btn-icon:active {
    filter: drop-shadow(0px 0px 4px var(--gold-line-color));
}
.concept-submit-btn {
    margin: 0.5rem;
}
.concept-form-header {
    display: flex;
    flex-direction: row;
    height: 2rem;
    background-color: var(--core-primary);
    color: var(--text-color-alt);
    align-items: center;
    justify-content: space-between;
    padding-left: 0.5rem;
}
.concept-form-header > img {
    aspect-ratio: 1/1;
    height: 100%;
}
.new-concept-form{
    display: flex;
    flex-direction: column;
    padding: 0.5rem;
}
#new-concept-hr {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}
.existing-concepts-menu {
    width: 100%;
    padding: 0.5rem;
}
.concept-modal {
    position: fixed;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(211, 211, 211, 0.565);
    z-index: 999;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
}
.concept-form {
    display: flex;
    flex-direction: column;
    border-radius: 5px;
    border: 1px solid black;
    background-color: white;
}
</style>
<script>
export default {
    name: 'DomainEditor',
    view: 'SME',
    friendly_name: "Domain Editor",
    icon: "/aspire/static/assets/icon-DomainEditor.png",
    props: {
        msg: String
    }
}
</script>

<script setup>
import NewConceptModal from "../components/domain_dag/NewConceptModal.vue";
import NewCollectionModal from "../components/domain_dag/NewCollectionModal.vue";
import DomainDag from "../components/domain_dag/DomainDag.vue"
import DomainDagUtilities from "../utils/DagUtils.js"
import ModuleMenu from "../components/module_menu/ModuleMenu.vue"
import LoadingWheel from "@/components/LoadingWheel.vue";
import DomainMenu from "@/components/domain_dag/DomainMenu.vue";
import ConceptSearch from '@/components/domain_dag/ConceptSearch.vue'
import DropdownSelect from "@/components/utility_comps/DropdownSelect.vue";
import SettingsPopup from "@/components/utility_comps/SettingsPopup.vue";
import DraggableDiv from "@/components/utility_comps/DraggableDiv.vue";

import axios from "axios";
import { ref, onBeforeMount, onBeforeUnmount } from "vue"

const fileInput = ref(null)
const settingsOpen = ref(false)

const tool_domain = window.contextData.tool_domain



let dagUtil = new DomainDagUtilities()

onBeforeMount(async () => {
    axios.get(`${tool_domain}/course/domain`).then((response) => {
        const edges = {}
        response.data.junctions.forEach(item => {
            edges[`edge|${item.prereq_name}|${item.concept_name}`] = {"target": item.concept_name, "source": item.prereq_name}
        })
        dagUtil.initialize(response.data.concepts, edges, response.data.collections)

    })
})

const defaultSettings = {
    nodeColor: "#00629B",
    unsavedColor: "#02d6b3",
    focusColor: "#ffdd00",
    moduleColor: "#FC8900",
    edgeColor: "",
    edgeDeleteColor: "#ff2a00",
    edgeCreateColor: "#00bf1d",
    textColor: "#00000",
    nodeSize: 30,
    selectable: true,
    hoverable: true,
    focusRing: true,
    showModules: true
}

function getColor(obj, mode = "node") {
    let color = "#848fa1"
    switch (mode) {
        case "node":
            color = defaultSettings.nodeColor
            if (obj.params?.focusColor) {
                color = obj.params.focusColor
            }
            else if (dagUtil.selectedNodes.value?.includes(obj.id)) {
                color = defaultSettings.focusColor
            }
            else if (obj.module?.includes(dagUtil.selectedModule.value)) {
                color = defaultSettings.moduleColor
            }
            else if (!obj.is_saved) {
                color = defaultSettings.unsavedColor
            }
            break;

        case "label":
            color = {
                visible: true,
                color: color,
                padding: 2,
                borderRadius: 5
            }
            break;
        case "edge":
            color = "#aaa"
            if (!obj.is_saved && obj.status === "delete") {
                color = defaultSettings.edgeDeleteColor

            } else if (!obj.is_saved && obj.status === "create") {
                color = defaultSettings.edgeCreateColor
            } 
            
            if (dagUtil.selectedEdges.value.includes(`edge|${obj.source}|${obj.target}`)) {
                color = "#dd8800"

            } 
            break;

    }
        return color

}

const conceptModalOpen = ref(false)
const conceptModalActiveTab = ref('select-existing')
const collectionModalOpen = ref(false)
const isMenuOpen = ref(false)

function onDomainMenuEmit(event) {
    switch (event) {
        case "deleteConcepts":
            dagUtil.deleteSelectedNodes()
            break;
        case "addConcept":
            conceptModalActiveTab.value = 'select-existing'
            conceptModalOpen.value = true
            break;
        case "joinConcepts":
            dagUtil.addSelectedEdges()
            break;
        case "moduleConceptAdd":
            dagUtil.addSelectedNodesToModule()
            break;
        case "junctionDelete":
            dagUtil.deleteSelectedEdges()
            break;
        case "moduleConceptDelete":
            dagUtil.RemoveSelectedNodesFromModule()
            break;
        case "transitiveReduction":
            dagUtil.transitiveReduction()
            break;
    }
}

const handleFileChange = (event) => {
    var jsonReader = new FileReader
    jsonReader.onload = onReaderLoad
    jsonReader.readAsText(event.target.files[0])
};

const onReaderLoad = (event) => {
    var obj = JSON.parse(event.target.result);
    dagUtil.uploadDomain(obj)
}

onBeforeUnmount(async () => {
    dagUtil.saveChangeRequests()
})

</script>

<template>
    <div class="domain-editor" v-if="dagUtil.is_initialized.value">
        <div class="left-section" :data-state="isMenuOpen ? 'min' : 'max'">
            <div 
                class="menu-collapse" 
                :data-state="isMenuOpen ? 'min' : 'max'" 
                @click="isMenuOpen = !isMenuOpen"
                :title="isMenuOpen ? 'Collapse Menu' : 'Expand Menu'"
                >
                <img src="/aspire/static/assets/icon-chevron.png"/>
            </div>
            <div class="graph roboto-bold">
                <DomainDag 
                    :nodes="dagUtil.nodes.value" 
                    :edges="dagUtil.edges.value" 
                    :focus-node="dagUtil.focusNode.value"
                    :selectedNodes="dagUtil.selectedNodes.value" 
                    :selectedModule="dagUtil.selectedModule.value"
                    :defaultSettings="defaultSettings"
                    :selected-edges="dagUtil.selectedEdges.value"
                    :getColor="getColor"
                    :graphHandler="dagUtil"

                    >
                    <template #default="{boxSelect, updateLayout}">
                        <div class="settings-menu">
                            <img 
                                @click="() => settingsOpen = !settingsOpen" 
                                class="domain-settings-btn" 
                                src="/aspire/static/assets/icon-settingsPage.png"
                                title="Domain Editor Settings"
                                />
                                <img title="Refresh Layout" aria-label="Refresh Layout" class="refresh-btn-icon"
                                src="/aspire/static/assets/loading-icon.png" @click="updateLayout('BT')" />
                        </div>
                        <DraggableDiv class="menu-wheel">

                            <DomainMenu 
                                :selected-concepts="dagUtil.selectedNodes.value"
                                :selected-edges="dagUtil.selectedEdges.value"
                                :selected-module="dagUtil.selectedModule.value"
                                @box-select="boxSelect"
                                @emitHandler="onDomainMenuEmit"
                            />
                        </DraggableDiv>
                        <div class="display-options">
                            <ConceptSearch 
                                :concepts="dagUtil.nodes.value" 
                                :selected-concepts="dagUtil.selectedNodes.value"
                                @updateSelectedNodes="dagUtil.updateSelectedNodes"
                            />
                        </div>
                    </template>
                </DomainDag>
            </div>
        </div>
        <div class="right-section" :data-state="isMenuOpen ? 'max' : 'min'">
            <ModuleMenu 
                :concepts="dagUtil.nodes.value" 
                :selected-concepts="dagUtil.selectedNodes"
                :module-items="dagUtil.collections.value"
                :selected-module="dagUtil.selectedModule"
                @add-module="collectionModalOpen = true"
                @update-selected-module="dagUtil.updateSelectedModule" 
                @update-selected-nodes="dagUtil.updateSelectedNodes"
                @open-concept-modal="() => {
                    conceptModalActiveTab = 'generate-concepts'
                    conceptModalOpen = true
                }"
                />
        </div>
        <div v-if="dagUtil.saving.value" class="save-overlay">
        </div>

        <NewConceptModal 
            @add-node="dagUtil.addNode" 
            @add-existing-node="dagUtil.addExistingNode"
            @update-open="val => conceptModalOpen = val" 
            :modal-open="conceptModalOpen" 
            :existingConcepts="Object.keys(dagUtil.nodes.value)"
            :selected-module="dagUtil.selectedModule.value"
            v-model:active-tab="conceptModalActiveTab"
            />

        <NewCollectionModal 
            @add-collection="dagUtil.addNewCollection" 
            @update-open="val => collectionModalOpen = val" 
            :modal-open="collectionModalOpen" 
            />

        <SettingsPopup
            v-if="settingsOpen"
            :tabs="[{id: 'layout', name: 'Graph Layout'}, {id:'style', name: 'Node Style'}, {id: 'save', name: 'Options'}]"
        >

            <template v-slot:header>
                <div class="settings-menu-header">
                    <p>Domain Editor Settings</p>
                    <img 
                        src="/aspire/static/assets/icon-close-white.png"
                        @click="() => settingsOpen = false"
                        />
                </div>
            </template>

            <template v-slot:layout>
                <div class="settings-menu-main">
                    <div class="setting-content">
                        <h3>Graph Options</h3>
                        <hr/>
                        <div class="settings-input">
                            <label for="layoutDirection">Layout Direction: </label>
                            <DropdownSelect 
                                id="layoutDirection"
                                v-model:selected-value="dagUtil.layoutConfig.value.direction"
                                :option-mapping="{
                                    'BT': 'Bottom-to-Top',
                                    'TB': 'Top-to-Bottom',
                                    'LR': 'Left-to-Right',
                                    'RL': 'Right-to-Left'
                                    }"
                                />
    
                        </div>
                        <div class="settings-input">
                            <label for="LayoutMethod">Layout Method: </label>
                            <DropdownSelect 
                                id="LayoutMethod"
                                v-model:selected-value="dagUtil.layoutConfig.value.method"
                                :option-mapping="{
                                    'default': 'Default Layout',
                                    'module-wise': 'Module Groups - EXPERIMENTAL'
                                    }"
                                />
                        </div>
                        <div class="settings-input">
                            <label for="layoutAlignment">Alignment: </label>
                            
                            <DropdownSelect 
                                id="layoutAlignment"
                                v-model:selected-value="dagUtil.layoutConfig.value.alignment"
                                :option-mapping="{
                                    '': 'None',
                                    'UL': 'Upper-Left',
                                    'UR': 'Upper-Right',
                                    'DL': 'Lower-Left',
                                    'DR': 'Lower-Right'
                                    }"
                                />
                        </div>
                        <div class="settings-input">
                            <label for="layoutRanker">Ranking Function: </label>
                            
                            <DropdownSelect 
                                id="layoutRanker"
                                v-model:selected-value="dagUtil.layoutConfig.value.ranker"
                                :option-mapping="{
                                    'network-simplex': 'network-simplex',
                                    'tight-tree': 'tight-tree',
                                    'longest-path': 'longest-path'
                                    }"
                                />
                        </div>
                        <div class="settings-input">
                            <label for="nodeSize">Node Size: </label>
                            <input id="nodeSize" v-model="dagUtil.layoutConfig.value.nodeSize" min="1" type="number"/>
                        </div>
                        <div class="settings-input">
                            <label for="nodeSeparation">Node Separation: </label>
                            <input id="nodeSeparation" v-model="dagUtil.layoutConfig.value.nodeSeparation" step="0.1" min="0" type="number"/>
                        </div>
                        <div class="settings-input">
                            <label for="rankSeparation">Rank Separation: </label>
                            <input id="rankSeparation" v-model="dagUtil.layoutConfig.value.rankSeparation" step="0.1" min="0" type="number"/>
                        </div>
                        <div class="settings-input">
                            <label for="groupScalingX">Group Scaling X-Axis: </label>
                            <input id="groupScalingX" v-model="dagUtil.layoutConfig.value.groupScalingX" step="0.1" min="0" type="number"/>
                        </div>
                        <div class="settings-input">
                            <label for="groupScalingY">Group Scaling Y-Axis: </label>
                            <input id="groupScalingY" v-model="dagUtil.layoutConfig.value.groupScalingY" step="0.1" min="0" type="number"/>
                        </div>
                    </div>
                </div>
            </template>

            <template v-slot:style>
                <div class="setting-content">
                    <p>Coming Soon</p>
                </div>
            </template>

            <template v-slot:save>
                <div class="setting-content">
                    <h3>Save Options</h3>
                    <hr/>
                    <div class="setting-content save-options">
                        <div class="label-icon-box">
                            <span>Save to File</span>
                            <img 
                                @click="dagUtil.saveDomainToJSON" 
                                class="domain-file-save-btn" 
                                src="/aspire/static/assets/icon-save.png"
                                title="Save Domain to File"
                                />

                        </div>
                        <div class="label-icon-box">
                            <span>Upload File</span>
                            <img 
                                @click="fileInput.click()" 
                                class="domain-file-upload-btn" 
                                src="/aspire/static/assets/upload-file.png"
                                title="Upload Domain JSON"
                                />
                        </div>
                        <input 
                            type="file" 
                            id="content_files" 
                            @change="handleFileChange" 
                            accept=".json" 
                            style="display: none;"
                            ref="fileInput"
                            >
                    </div>
                </div>    
            </template>

        </SettingsPopup>
    </div>
    <div class="domain-editor" v-else>
        <LoadingWheel :loading-text="'Loading...'"/>

    </div>
</template>

<style scoped>
.settings-menu-header {
    background-color: var(--core-primary);
    color: var(--text-color-alt);
    -webkit-user-select: none; /* Safari */
    -ms-user-select: none; /* IE 10 and IE 11 */
    user-select: none; /* Standard syntax */
    display: flex;
    height: 2rem;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem;
    border-top-right-radius: 1rem;
    border-top-left-radius: 1rem;
}
.settings-menu-header > img {
    aspect-ratio: 1/1;
    height: 100%;

}
.settings-menu-main {
    padding: 0.75rem;
    background-color: var(--bg-color);
    display: flex;
    flex-direction: row;
    border-bottom-right-radius: 1rem;
    border-bottom-left-radius: 1rem;
}
.setting-content {
    width: 100%;
    padding: 0.5rem;
}
.settings-input {
    display: flex;
    flex-direction: column;
    margin-top: 0.5rem;

}
.save-options {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-evenly;
}
.label-icon-box {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.domain-file-save-btn {
    aspect-ratio: 1/1;
    width: 40%;
}

.domain-file-upload-btn{
    aspect-ratio: 1/1;
    width: 40%;
}

.domain-file-upload-btn:hover {
    width: calc(40% + 5px);
}
.domain-file-upload-btn:active {
    filter: drop-shadow(0px 0px 4px var(--gold-line-color));
}

.domain-file-save-btn:hover {
    width: calc(40% + 5px);
}
.domain-file-save-btn:active {
    filter: drop-shadow(0px 0px 4px var(--gold-line-color));
}
.settings-menu {
    position: absolute;
    right: 0.5rem;
    top: 0.5rem;
    width: 2rem;
    height: 5rem;
}
.domain-settings-btn{
    aspect-ratio: 1/1;
    width: 100%;
}



.domain-settings-btn:hover {
    width: calc(100% + 5px);
}
.domain-settings-btn:active {
    filter: drop-shadow(0px 0px 4px var(--gold-line-color));
}

.menu-collapse {
    position: absolute;
    top: calc(50% - 2rem);
    right:-1rem;
    width: 2rem;
    height: 4rem;
    z-index: 999;
    background-color: var(--core-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
}

.menu-collapse > img {
    height: 100%;
}
.menu-collapse[data-state="max"]:hover {
    right: -0.5rem;
}
.menu-collapse[data-state="min"]:hover {
    right: -1.5rem;
}
.left-section[data-state='max'] > .menu-collapse > img {
    transform: rotate(270deg);
    transition: transform .5s ease-out;
}

.left-section[data-state='min'] > .menu-collapse > img {
    transform: rotate(90deg);
    transition: transform .5s ease-out;
}
.save-overlay {
    position: relative;
    top: 0;
    left: 0;
    background-color: rgba(128, 128, 128, 0.508);
    width: 100vw;
    height: 100vh;
    z-index: 999;
}

.domain-editor {
    display: flex;
    flex-direction: row;
    height: 100% !important;
    width: 100%;
    min-height: 100% !important;
}

.left-section[data-state='max'] {
    animation: slide-out 1s ease-out;
    width: 100%;
}
.left-section[data-state='min'] {
    width: 75%;
    animation: slide-in 1s ease-out;
}
.left-section {
    position: relative;
}
@keyframes slide-out {
    from {
        width: 75%;
    }
    to {
        width: 100%;
    }
}

@keyframes slide-in {
    from {
        width: 100%;
    }
    to {
        width: 75%;
    }
}

@keyframes slide-out-menu {
    from {
        width: 0%;
        visibility: collapse;
    }
    to {
        width: 25%;
        visibility: visible;
    }
}

@keyframes slide-in-menu {
    from {
        width: 25%;
        visibility: visible;
    }
    to {
        width: 0%;
        visibility: collapse;
    }
}
.right-section {
    box-shadow: 1px 1px 2px 0px rgb(169, 169, 169);
    display: flex;
    flex-direction: column;
    align-items: center;
    overflow: hidden;
    background-color: var(--bg-color);
    border-radius: 8px;
}

.right-section[data-state='min'] {
    width: 0%;
    margin-left: 0px;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    visibility: collapse;
    animation: slide-in-menu 1s ease-out;
}

.right-section[data-state='max'] {
    margin-left: 5px;
    padding: .5rem;
    width: 25%;
    animation: slide-out-menu 1s ease-out;
}

.bottom-menu {
    margin: .5rem;
}

.graph {
    height: 100%;
    position: relative;
    top: 0;
    left: 0;

}

.display-options {
    position: absolute;
    display: flex;
    flex-direction: column;
    top: 32px;
    left: 6px;
    z-index: 999;
    width: 10rem;
    
}
.options-menu {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
}


.menu-wheel {
    position: absolute;
    display: flex;
    flex-direction: column;
    height: fit-content;
    bottom: 6px;
    left: 6px;
    align-items: center;
    justify-content: center;
}

.refresh-btn-icon {
    border-radius: 50%;
    width: 2rem;
    aspect-ratio: 1/1;
    text-align: center;
    padding: 0;
    color: #C69214;
    margin: 1px;
    position: relative;
}

.refresh-btn-icon:hover {
    border: 1px solid #c6911400;
}

.refresh-btn-icon:active {
    filter: drop-shadow(0px 0px 4px var(--gold-line-color));
}
</style>
